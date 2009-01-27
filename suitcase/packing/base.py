"""The default packaging class

All packaging systems with more specific requirements subclass and override
the functionality in this class.

"""

import os
from copy import deepcopy

try:
    import yaml
except ImportError:
    print "pyyaml not installed, see http://pyyaml.org/wiki/PyYAML"

from suitcase.exceptions import (
    SuitcaseImportError,
    SuitcasePackagingError,
    SuitcaseConfigurationError
)
from suitcase.utils.common import (
    dynamic_import,
    get_dynamic_class_instance,
    display_warning,
)
from suitcase.utils.copy import copy_files
from suitcase.utils.singleton import Singleton

CONTROL_FILE_NAME = "debian.yml"
DEBUG = False

class PackageBase(Singleton):
    
    """Packaging base class"""
    
    def __init__(self, config = None, package_config = None):
        self.global_config = config
        self.package_config = package_config

    @staticmethod
    def is_valid_package_name(package_name):
        """Checks the package name format is correct for you packaging system"""
        raise NotImplementedError

    def copy_files_to_package_dir(self):
        """copy files placeholder"""
        raise NotImplementedError

    def build_package(self, conf, filepath, *args, **kwargs):
        """build_package placeholder"""
        raise NotImplementedError

    def make_package_conf_files(self):
        """make package conf files placeholder"""
        raise NotImplementedError

    def pre_build(self, package_config):
        """pre build placeholder"""
        raise NotImplementedError

    @staticmethod
    def make_package_name(base_path, path):
        """make package name placeholder"""
        pass

    def make_package_filename(self, package_config):
        """make package filename placeholder"""
        raise NotImplementedError

    def get_package_version(self, package_config):
        """Gets a version number for the package

        If you don't got a VCS then you probably don't need a packaging system.

        """
        vcs = self.global_config.get('version_control')
        if vcs:
            # dynamically import the vcs code
            vcs_module = 'suitcase.vcs.%s' % vcs
            vcs = get_dynamic_class_instance(vcs_module, vcs.capitalize())

            path = package_config.get('path')
            if path:
                return vcs.get_directory_revision(path)
            else:
                SuitcasePackagingError("Package path is not defined")
        else:
            raise SuitcasePackagingError("No version control system defined")


    def get_package_name(self, config):
        """Works out a package name from the config file

        config is the config object

        Specifying a package_name in the yml file in build directories is
        the default behaviour but alternative approaches can be specified
        in subclasses - see below for more info.

        ALTERNATIVE EXAMPLE OF SUBCLASS OF THIS METHOD:

        you might subclass suitcase.packing.debian.Debian and override
        get_package_name to do some piece of magic awesomeness as the
        following example describes. The only thing to be careful of here
        is magic isn't always a great idea

        get_package_name could workout packagenames based on the directory
        structure of files. This is especially possible with something like
        python name spaces.

        In this way if you have an root namespace of: fandoogle the following
        could be turned into package names:

        fandoogle/apps/noodlegenerator => fandoogle-apps-noodlegenerator
        fandoogle/apps/crazylegs => fandoogle-apps-crazylegs
        fandoogle/templates/common => fandoogle-templates-common

        """

        # Find the package_name
        return config.get('package')

    def find_collection_conf(self, path):
        """given a path, returns the collections """
        collection = None
        if self.global_config.get("collections"):
            collection_path = os.path.abspath(path).replace(
                self.global_config["base_path"], ""
            )[1:]

            if self.global_config.get('collection_mapping'):
                collection = self.global_config['collection_mapping'].get(
                    collection_path
                )

                if collection and \
                    self.global_config["collections"].get(collection):
                    collection = self.global_config["collections"]\
                        [collection]

        if collection is None:
            collection = {}

        return collection


    def find_build_dirs(self, start_path, **kwargs):
        """Does a walk down from path and builds a dictionary of packages

        build_dict is a dictionary keyed from the path of the package
        and will be used  as the master configuration for the package
        building process.

        """
        # Get the package conf filename from the config or defaults to the 
        # name of the packaging system
        package_conf_name = kwargs.get(
            'package_conf_name',
            "%s.yml" % self.global_config['package_format']
        )

        if DEBUG:
            import pprint
            print "GLOBAL_CONFIG:" ,
            pprint.pprint(self.global_config)

        build_dict = {}
        for root, dirs, files in os.walk(start_path):

            exclusions = self.global_config.get('path_exclusions', []) \
                + self.global_config.get("default_path_exclusions", [])

            # Remove exclusions from the walking path
            for exclusion in exclusions:
                if exclusion in dirs:
                    dirs.remove(exclusion)

            # update this key with the collection data
            collection = self.find_collection_conf(root)

            # if foo.yml exists or there's a collection above us...
            if package_conf_name in files or collection:
                package_config = {}

                # get the package_conf file and load the conf
                file_path = os.path.join(root, package_conf_name)
                if os.path.exists(file_path):
                    package_config = yaml.load(open(file_path).read())
                    if package_config is None:
                        raise SuitcaseConfigurationError(
                            "Config file %s is invalid" % file_path
                        )

                # get package name
                package_config['path'] = root

                package_name = self.get_package_name(package_config)
                if DEBUG:
                    print "PACKAGE_NAME: %s" % package_name

                # Check for package dupes
                if build_dict.get(package_name):
                    raise SuitcasePackagingError(
                        "A duplicate package name exists."\
                        " Please check %s" % file_path
                    )
            
                else:

                    build_dict[root] = {}

                    if collection:
                        build_dict[root]=deepcopy(collection)

                    package_config["architecture"] = package_config.get(
                        "architecture", 
                        build_dict[root].get(
                            'architecture',
                            "all"
                        )
                    )
                    
                    package_config['version'] = self.get_package_version(
                        package_config
                    )
                    
                    package_config['package'] = package_name

                    package_config['package_filename'] = \
                        self.make_package_filename(package_config)

                    package_preexists = \
                        self.check_package_file(package_config)[0]

                    if not self.global_config['force_build'] and \
                        package_preexists:
                        if not self.global_config['quiet']:
                            display_warning(
                                "Suitcase Warning: Package %s already "\
                                "exists; skipping build..." \
                                % package_config['package_filename']
                            )
                        del build_dict[root]
                        # update this key with the rest of the data from 
                        # package_config
                    elif package_config['version'] < ("0.%s" % \
                        self.global_config['limit_from']):
                        if not self.global_config['quiet']:
                            display_warning("Suitcase Warning: Package "\
                                "version %s below limit; skipping build..." \
                                % package_config['version']
                            )
                        del build_dict[root]
                    else:
                        build_dict[root].update(deepcopy(package_config))


        if build_dict != {}:
            return build_dict
        else:
            raise SuitcasePackagingError(
                "No packages to build from walking %s" % start_path
            )


    def pack(self, filepath):

        """Wraps the entire packaging process

        Gets all of the config from the path and then loops round the
        config building the packages

        """

        # Calls the base classes find_build_dirs if none is
        build_dict = self.find_build_dirs(filepath)

        # pretty print out the config
        if DEBUG:
            import pprint
            print "BUILD DICT:",
            pprint.pprint(build_dict)

        for path,package_conf in build_dict.items():

            if not self.global_config["quiet"]:
                print "---------------"
                print "Building %s" % path

            # actually call the builder's build method
            builder_class_name = package_conf.get('builder', 'packages')
            builder = 'suitcase.builders.%s' % builder_class_name

            builder_instance = get_dynamic_class_instance(
                builder,
                builder_class_name.capitalize(),
                self.global_config
            )

            builder_instance.pre_build(package_conf)
            builder_instance.build(package_conf)
            self.package_config = {}

    def get_hook(self, method_label):
        """fetches <label> key from configs

        first package level then collection based on path
        returns a list

        """
        conf_methods = []

        package_methods = self.package_config.get(method_label)
        if package_methods:
            if isinstance(package_methods, basestring):
                conf_methods.append(package_methods)
            else:
                conf_methods += package_methods
    
        collection = self.find_collection_conf(self.package_config["path"])
        collection_methods = collection.get(method_label, [])

        if collection_methods:
            # if string cast to list
            if isinstance(collection_methods, basestring):
                collection_methods = [collection_methods]

            # and dedup
            for collection_method in collection_methods:
                if collection_method not in conf_methods:
                    conf_methods.append(collection_method)
        
        return conf_methods

    def run_hook(self, method_label):
        """dynamically call pre/post conf methods as defined in package_conf"""

        for method in self.get_hook(method_label):
            
            conf_module = dynamic_import(".".join(method.split(".")[:-1]))
            try:
                return_val = getattr(
                    conf_module,method.split(".")[-1]
                )(self.global_config,self.package_config)
                
                if return_val:
                    self.package_config = return_val
                    
            except AttributeError, error:
                raise SuitcaseImportError(
                    "%s hook %s not found:\n%s" % (method_label, method, error)
                )
                
        return self.package_config

    def check_package_file(self, package_config):
        """Checks for the existence of package_file"""
        
        package_filename = package_config['package_filename']
        source = os.path.expanduser(
            os.path.join(
                self.global_config['build_directory'],"temp", package_filename
            )
        )
        destination = os.path.expanduser(
            self.global_config.get(
                'package_repo',
                self.global_config['build_directory']
            )
        )
        return os.path.exists(
            os.path.join(destination, package_filename)
        ), source, destination

    def move_package(self):
        """Moves packages from temp dir to a repo dir specified in the config"""

        # Only move if the no_move isn't set
        if not self.global_config['no_move']:
            (exists, source, destination) = \
                self.check_package_file(self.package_config)

            if not os.path.exists(destination):
                try:
                    os.makedirs(destination)
                except OSError, error:
                    raise SuitcasePackagingError(error)
                    
            if exists:
                display_warning(
                    "Suitcase Warning: Package %s already exists in"\
                    " destination; skipping file move..." \
                    % self.package_config['package_filename']
                )
            else:
                copy_files(source, destination)
