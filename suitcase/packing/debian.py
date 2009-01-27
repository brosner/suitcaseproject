"""Debian packaging class

Class that can build debian packages by wrapping the dpkg command

Control Files in debian packages have the following fields which are mandated:

Package
Version
Architecture
Maintainer
Description
"""

import os
import re

from suitcase.utils.common import (
    run_command, 
    dynamic_import, 
    remove_leading_slash,
    add_trailing_slash, 
    run_fakeroot, 
    clean_fakeroot, 
    merge_and_de_dupe,
)
from suitcase.packing.base import PackageBase 
from suitcase.utils.copy import copy_files
from suitcase.exceptions import SuitcasePackagingError

DEBUG = False
CONTROL_FILE_NAME = "debian.yml"

class Debian(PackageBase):
    """Debian specific packaging class for building .deb packages"""

    @staticmethod
    def is_valid_description_length(description):
        """Checks package name description length"""
        return len(description) < 60

    @staticmethod
    def is_valid_package_name(package_name):
        """Validates package name against debian packaging requirements"""
        
        if package_name is not None and \
            re.match(r'^[a-z\d\-+]+$', package_name):

            return True
        else:
            return False

    def pre_build(self, package_config):
        """Carrys out pre-build tasks - this is a generic hook"""
        
        self.package_config = package_config
        if package_config.get("package") is None:
            package_config["package"] = self.make_package_name(
                self.global_config["base_path"],
                package_config["path"],
                self.global_config["prefix"]
            )

    @staticmethod
    def normalise_package_name(package_name, filters = None):
        """removes whitespace underscores and periods and replaces with -"""
        
        package_name = re.sub("[\s_\.]", "-", package_name)

        if filters:
            for filter_string, replacement in filters.items():
                package_name = package_name.replace(filter_string, replacement)

        return package_name

    @staticmethod
    def make_package_name(base_path, path, prefix=None, filters=None):
        """Builds a package name based on the path"""
        
        package_name = os.path.abspath(path).replace(base_path, "")
        package_name = remove_leading_slash(package_name)
            
        package_parts = package_name.split("/")
        
        if prefix:
            package_parts = [prefix] + package_parts
        
        package_name = "-".join(package_parts)
        return Debian.normalise_package_name(package_name, filters)


    def get_package_name(self, package_config):
        """Get package name out of config and fallback to the name generation"""
        
        name =  package_config.get('package')
        
        if name is None:
            name = self.make_package_name(
                self.global_config['base_path'],
                package_config['path'],
                self.global_config.get('prefix'),
                self.global_config.get('package_name_filters')
            )
        return name

    def  make_package_filename(self, package_config):
        """builds the deb package file name"""
        
        try:
            return "%s_%s_%s.deb" % (
                package_config['package'],
                package_config["version"],
                package_config["architecture"]
            )
        except KeyError, error:
            raise SuitcasePackagingError("Key %s does not exist" % error)

    def build_package(self):
        """Builds a debian package

        Actually does the call outs to dpkg so that we can actually build
        a package
        
        """
        source_dir = "%s" % self.package_config['working_dir']

        # makes sure root owns the files
        run_fakeroot("chown -R root.root %s" % source_dir)
        # remove all sticky bits - a deb requirement.
        run_fakeroot("chmod -R a-s %s" % source_dir)

        self.run_hook('post_permissions')

        if not self.global_config['quiet']:
            print "Building package %s" % self.package_config['package']
            print "From %s" % self.package_config['path']


        run_fakeroot("dpkg -b %s %s/temp/%s" % (
            source_dir,
            self.global_config['build_directory'],
            self.package_config['package_filename'])
        )
        
        clean_fakeroot()

        # Cleans up assuming the no-clean flag isn't set
        if not self.global_config["no_clean"]:
            run_command("rm -rf %s" % source_dir)


    def copy_files_to_package_dir(self, extra_excludes=None):
        """Copys files from the branch into the destination file layout

        ready for packaging

        """
        if extra_excludes is None:
            extra_excludes = []

        package_config = self.package_config
        to_dir = package_config['working_dir']
        from_dir = package_config['path']

        build_exclusions = self.global_config["default_build_exclusions"] + \
            self.global_config.get("build_exclusions",[])

        # config based excludes
        if package_config.get('build_exclusions'):
            build_exclusions += package_config["build_exclusions"]

        mapped_files = []


        file_mapping = package_config.get('destination_mapping', {})

        # find which global_destination_map applies
        if self.global_config.get("destination_mapping"):

            global_mapping = self.global_config["destination_mapping"]
            global_mapping["root"] = global_mapping.get("root","")

            # Create reverse destination mapping
            self.global_config["reverse_destination_mapping"] = {}
            
            for key, value in global_mapping.items():
                self.global_config["reverse_destination_mapping"]\
                    [os.path.join(global_mapping["root"], value)] = key

            package_path = os.path.abspath(self.package_config["path"]).\
                replace(self.global_config["base_path"],"")
                
            package_path = remove_leading_slash(package_path)

            # this is so we can walk up the path from the package root dir:
            # apps/blah wants to match the destination mapping for apps as well
            test_path = package_path 
            global_mapping_root = global_mapping.get("root","")
            found_mapping = False

            while len(test_path) > 0:
                # if we find something
                if global_mapping.get(test_path):
                    path_remainder = package_path.replace(test_path,"")
                    path_remainder = remove_leading_slash(path_remainder)

                    # append the relative path (from the matched key)
                    # so in the above example:
                    # in global:
                    # destination_mapping:
                    # apps: /foo/bar/apps

                    # so apps/blah wants to go to /foo/bar/apps/blah
                    global_mapping_root = os.path.join(
                        global_mapping_root, 
                        global_mapping[test_path],
                        path_remainder
                    )
                    found_mapping = True
                    
                    break
                # walk up
                test_path = "/".join(test_path.split("/")[:-1])


            # check that something was actually added else the path_remainder 
            # is value.
            if not found_mapping:
                global_mapping_root = os.path.join(
                    global_mapping_root,
                    package_path
                )

            # overwrite the root mapping (if it starts with / ignore)
            root = file_mapping.get("root","")
            file_mapping["root"] = os.path.join(global_mapping_root, root)

        # Check if file mapping exists
        
        if file_mapping != {}:

            if DEBUG:
                print "USING MAPPING"
            for key, value in file_mapping.items():

                if key == 'root':
                    continue

                if not value.startswith("/"):
                    try:
                        value = os.path.join(file_mapping["root"], value)
                    except KeyError:
                        raise SuitcasePackagingError(
                            "You are using relative mapping settings in your "\
                            "debian file without setting a root"
                        )


                value = remove_leading_slash(value)


                # Joining paths to make absolute
                source = os.path.join(from_dir, key)
                destination = os.path.join(to_dir, value)

                mapped_files.append("/%s" % key)

                # do the magic
                if os.path.exists(source):
                    copy_files(source, destination, build_exclusions)

            file_mapping['root'] = file_mapping.get('root',"/")
            file_mapping["root"] = remove_leading_slash(file_mapping["root"])
            
            # AWOOGA - be careful with slashes as this tells rsync
            # whether it's creating the last dir in the destination or not
            # Now copy root (which will normally be everything)
            if len(mapped_files) > 0:
                build_exclusions += mapped_files
                

            copy_files(
                add_trailing_slash(from_dir),
                os.path.join(to_dir, file_mapping['root']),
                build_exclusions
            )

            self.package_config["destination_mapping"] = file_mapping
        else:
            from_dir = add_trailing_slash(from_dir)
            extra_build_exclusions = package_config.get('build_exclusions', [])

            if extra_excludes:
                build_exclusions += extra_build_exclusions

            copy_files(from_dir, to_dir, build_exclusions)
            self.package_config["destination_mapping"] = {"root":""}


    def make_package_conf_files(self):
        """Write out the control file and the configfiles for the deb package"""

        if DEBUG:
            import pprint
            pprint.pprint(self.package_config)

        # Write the control file
        control_dir = "%s/DEBIAN" % self.package_config["working_dir"]
        
        if not os.path.exists(control_dir):
            os.mkdir(control_dir)
        
        control_file = open("%s/control" % control_dir, "w")
        
        control_template = self.global_config.get(
            "control_template", 
            os.path.join(
                os.path.dirname(__file__),
                "../templates/debian/control_minimum.template",
            )
        )
        
        if not os.path.exists(control_template):
            raise SuitcasePackagingError(
                "Missing control template file: %s" \
                    % os.path.abspath(control_template)
            )
            
        template = open( "%s" % control_template ).read()

        self.package_config["maintainer"] = self.package_config.get(
            "maintainer",
            self.global_config.get("maintainer")
        )
        self.package_config["description"] = self.package_config.get(
            "description",
            "%s package" % (self.package_config["package"])
        )


        # deal with depends - make a deduped, comma separated list, without 
        # the package itself in
        depends = merge_and_de_dupe(
            self.package_config.get('depends',[])
        )

        if self.package_config["package"] in depends:
            depends.remove(self.package_config["package"])

        if depends is None:
            depends = []

        self.package_config['depends'] = ", ".join(depends)
        if not self.package_config['depends']:
            template=template.replace("Depends: %(depends)s\n","")

        try:
            control_file.write(template % self.package_config)
        except KeyError, error:
            raise SuitcasePackagingError("%s missing from config" % error)

        # do config files
        config_items = {}
        config_files = self.package_config.get("conffiles")
        if config_files:
            for config_item in config_files:

                config_item = os.path.join(
                    self.package_config["working_dir"],
                    config_item
                )

                print "FOUND CONFIG" 
                print config_item
                if os.path.isdir(config_item):
                    for root, dirs, files in os.walk(config_item):

                        path_exclusions = self.global_config.get(
                            'default_path_exclusions', []
                        ) + self.package_config.get('path_exclusions',[])

                        # Remove exclusions from the walking path
                        for exclusion in path_exclusions:
                            if exclusion in dirs:
                                dirs.remove(exclusion)

                        for file_path in files:
                            config_items[os.path.join(root, file_path)] = 1

                elif os.path.isfile(config_item):
                    config_items[config_item] = 1

            config_file = open(os.path.join(
                self.package_config["working_dir"],
                "DEBIAN",
                "conffiles"
            ), "w")

            for file_path in config_items.keys():
                config_items[file_path] = file_path.replace(
                    self.package_config["working_dir"], ""
                )
            config_file.write("\n".join(config_items.values()))
            config_file.write("\n")

        # now do copyright
        copyright_dir = "%s/usr/share/doc/%s" % (
            self.package_config["working_dir"],
            self.package_config["package"]
        )
        
        try:
            os.makedirs(copyright_dir)
        except OSError, error:
            raise SuitcasePackagingError(error)
        
        run_command("cp %s %s/copyright" % (
            os.path.join(
                os.path.dirname(__file__), 
                "../templates/debian/copyright_minimum.template",
            ),
            copyright_dir)
        )
