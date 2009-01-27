"""Handles configs for django apps"""

import os

from suitcase.packing.debian import Debian
from suitcase.utils.common import (
    relative_import, 
    dynamic_import,
    merge_and_de_dupe,
    display_warning
)

def generate_depends(global_config, package_config):
    """Generates the config dependencies automagically"""

    # now export the root as whatever is in export_base_path_as
    if global_config.get("export_base_path_as"):
        
        relative_import(
            global_config["base_path"],
            global_config["export_base_path_as"]
        )
    
        # now load the config.settings file 
        config_path = package_config["path"]

        if config_path.endswith("/"):
            config_path = config_path[:-1]

        # make the config module name
        config_module = "configs.%s.settings" % config_path.split("/")[-1]

        if global_config.get("prefix"):
            config_module = "%s.%s" % (global_config["prefix"], config_module)

        package_config["depends"] = merge_and_de_dupe(
            package_config["depends"]
        )

        try:
            config_settings = dynamic_import(config_module)
            for app in config_settings.INSTALLED_APPS:
                if "django.contrib.admin" in app:
                    
                    migration_package = Debian.make_package_name(
                        global_config["base_path"],
                        os.path.join(global_config["base_path"],"migrations"), 
                        global_config.get("prefix"),
                        global_config.get("package_name_filters")
                    )
                    
                    # work out migration package
                    migration_config = {
                        "path":os.path.join(global_config["base_path"],"migrations")
                    }
                    
                    migration_version = Debian(global_config).get_package_version(
                        migration_config
                    )
                    
                    package_config["depends"] = merge_and_de_dupe(
                        package_config["depends"],
                        "%s (>=%s)" % (
                            migration_package,
                            migration_version
                        )
                    )

                elif not app.startswith("django"):
                    app_package = Debian.normalise_package_name(
                        app,
                        global_config.get("package_name_filters")
                    )
                    
                    package_config["depends"] = merge_and_de_dupe(
                        package_config["depends"],app_package
                    )
        except:
            display_warning('Suitcase Warning: No settings file found for config package %s' % package_config["package"])

    if package_config.get("target_hosts"):
        
        for host in package_config["target_hosts"]:
            asset_path = os.path.join(
                global_config["base_path"],
                "assets",
                "domains",
                host
            )
            
            if os.path.exists(asset_path):
                
                package_config["depends"] = merge_and_de_dupe(
                    package_config["depends"],
                    Debian.make_package_name(
                        global_config["base_path"],
                        asset_path, 
                        global_config.get("prefix"),
                        global_config.get("package_name_filters")
                    )
                )

            template_path = os.path.join(
                global_config["base_path"], 
                "templates", 
                "root",
                "domains",
                host
            )
            
            if os.path.exists(template_path):
                package_config["depends"] = merge_and_de_dupe(
                    package_config["depends"],
                    Debian.make_package_name(
                        global_config["base_path"],
                        template_path, 
                        global_config.get("prefix"),
                        global_config.get("package_name_filters")
                    )
                )

    return package_config

