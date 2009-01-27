"""Versioning of assets"""

import os
import re
import pprint

from suitcase.exceptions import SuitcaseVcsError, SuitcasePackagingError

from suitcase.utils.common import (
    get_dynamic_class_instance, 
    remove_leading_slash, 
    display_warning
)

ASSET_REGEX = re.compile('^(.*?(?:url\\((?:[\'"])?|["\']))(?P<path>.*\\.(?:jpe?g|png|gif|js|css))((?:\\)|["\']{1}).*?)$', re.MULTILINE)

def assets(global_config, package_config):

    """Generates a dictionary of asset versions"""

    vcs = global_config.get('version_control')
    if vcs:
        # dynamically import the vcs code
        vcs_module = 'suitcase.vcs.%s' % vcs
        vcs_instance = get_dynamic_class_instance(vcs_module, vcs.capitalize())

    asset_dir = os.path.abspath(
        os.path.join(package_config["working_dir"],
        package_config["destination_mapping"]["root"])
    )
    
    target_dir = os.path.abspath(os.path.join(asset_dir,"../"))
    if os.path.exists(target_dir):
        asset_versions = {}
        for path, dirs, files in os.walk(target_dir):
            if 'tiny_mce' in dirs:
                dirs.remove('tiny_mce')

            for file_path in files:
                original_path = os.path.join(path, file_path)
                original_path = original_path.replace(target_dir, "")
                
                file_path = os.path.join(path, file_path)\
                    .replace(package_config["working_dir"], "")

                branch_path = file_path
                while len(branch_path) > 0:
                    if global_config["reverse_destination_mapping"]\
                        .get(branch_path):
                        
                        remainder = file_path.replace(branch_path, "")
                        remainder = remove_leading_slash(remainder)

                        file_path = os.path.join(
                            global_config["base_path"],
                            global_config["reverse_destination_mapping"]\
                                [branch_path],
                            remainder
                        )
                        
                        break
                    branch_path = "/".join(branch_path.split("/")[:-1])    

                non_minified_file = file_path.replace('-minified.js', '.js')
                if file_path.endswith("-minified.js") and \
                    os.path.exists(non_minified_file):

                    file_path = non_minified_file

                try:
                    version = vcs_instance.get_directory_revision(file_path)
                    
                except SuitcaseVcsError:
                    display_warning(
                        "Suitcase Warning: Can't find version "\
                        "for %s setting to package version: %s" % \
                        (original_path,package_config["version"])
                    )
                    version = package_config["version"]

                asset_versions[original_path] = version

        asset_versions[asset_dir.replace(target_dir, "")] = \
            package_config["version"]
        
        asset_version_file = os.path.join(
            package_config["working_dir"], 
            "etc/suitcase/asset_versions/",
            "%s.py"%package_config["package"]
        )
        
        asset_version_dir = os.path.split(asset_version_file)[0]
        
        if not os.path.exists(asset_version_dir):
            try:
                os.makedirs(asset_version_dir)
            except OSError, error:
                raise SuitcasePackagingError(error)
            
        open(asset_version_file,"w").write(
            "asset_versions=%s" % pprint.pformat(asset_versions)
        )
         
        package_config["configs"] = package_config.get("configs", [])
        package_config["configs"].append(asset_version_file)
        package_config["asset_versions"] = asset_versions
        return package_config


def add_versions_to_css(global_config, package_config):
    
    """Changes the version of each asset
    
    found in the CSS file with the latest version out of the VCS
    
    """

    vcs = global_config.get('version_control')
    if vcs:
        # dynamically import the vcs code
        vcs_module = 'suitcase.vcs.%s' % vcs
        vcs_instance = get_dynamic_class_instance(vcs_module, vcs.capitalize())


    def add_asset_version_to_path(match):
        
        """Callback to make this a one-pass replace"""
        
        version_path = os.path.abspath(
            os.path.join(
                path, 
                match.group("path")
            )).replace(package_config["working_dir"], 
            ""
        )
        
        branch_path = version_path
        
        while len(branch_path) > 0:
            if global_config["reverse_destination_mapping"].\
                get(branch_path):
                
                remainder = version_path.replace(branch_path,"")
                remainder = remove_leading_slash(remainder)
                branch_path = os.path.join(
                    global_config["base_path"],
                    global_config["reverse_destination_mapping"][branch_path],
                    remainder
                )
                break
                
            branch_path = "/".join(branch_path.split("/")[:-1])    

        new_path = version_path.replace(
            global_config["destination_mapping"]["assets"],
            "",
        )
        version = None

        if package_config.get("asset_versions"):
            version = package_config["asset_versions"].get(new_path)

        if version is None:
            try:
                version = vcs_instance.get_directory_revision(file_path)
            except SuitcaseVcsError:
                version = package_config["version"]


        return "%s/%s%s%s" % (
            match.group(1), 
            version.replace(".",""),
            new_path, 
            match.group(3)
        )

        # walk up version path to find which svn area its in

    top_level = os.path.join(
        package_config["working_dir"],
        package_config["destination_mapping"]["root"]
    )

    target_dir = os.path.join(top_level,"css")

    for path, dirs, files in os.walk(target_dir):
        for file_path in files:
            full_path = os.path.join(path, file_path)
            if file_path.endswith(".css") and not "admin" in full_path:

                css_file = full_path
                css_file_handle = open(css_file)
                contents = css_file_handle.read()
                contents = ASSET_REGEX.sub(add_asset_version_to_path, contents)
                css_file_handle = open(css_file,"w")
                css_file_handle.write(contents)
                css_file_handle.close()
