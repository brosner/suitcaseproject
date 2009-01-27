"""Class to handle the minification of JS/CSS"""

import os
from suitcase.plugins.assets.bin.jsmin import jsmin

def javascript(global_config, package_config):
    """Minifies JavaScript"""
    
    target_dir = os.path.join(
        package_config["working_dir"], 
        package_config["destination_mapping"]["root"],
        "js",
    )

    if os.path.exists(target_dir):
        for path, dirs, files in os.walk(target_dir):

            if 'tiny_mce' in dirs:
                dirs.remove('tiny_mce')

            for filename in files:
                js_file = os.path.join(path, filename)
                if not js_file.endswith(".js"):
                    continue

                if not global_config["quiet"]:
                    print "MINIFYING " + js_file

                new_file = js_file.replace(".js","-minified.js")
                original_contents = open(js_file).read()
                minified_contents = jsmin(original_contents)
                if not minified_contents:
                    minified_contents = original_contents

                open(new_file,"w").write(minified_contents)
    else:
        print "No Javascript dir - no minification "
