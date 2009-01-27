"""Generates dependencies for Django apps"""

import os

from suitcase.packing.debian import Debian
from suitcase.utils.common import merge_and_de_dupe


def generate_depends(global_config, package_config):
    """Generates the app dependencies automagically"""
    
    apps_path = package_config["path"].replace("apps","assets/apps")
    
    package_config["depends"] = merge_and_de_dupe(package_config["depends"])

    if os.path.isdir(apps_path):
        package_config["depends"] = merge_and_de_dupe(
            package_config["depends"],
            Debian.make_package_name(
                global_config["base_path"], 
                apps_path, 
                global_config.get("prefix"),
                global_config.get("package_name_filters")
            ) 
        )

    app_template_path = package_config["path"].replace(
        "apps", "templates/root/apps"
    )
    
    if os.path.isdir(app_template_path):
        
        package_config["depends"] = merge_and_de_dupe( 
            package_config["depends"],
            Debian.make_package_name(
                global_config["base_path"], 
                app_template_path, 
                global_config.get("prefix"),
                global_config.get("package_name_filters")
            ) 
        )
    
    return package_config
