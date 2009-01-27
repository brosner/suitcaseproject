"""Provides ways to concatenate files"""

import os
from suitcase.exceptions import SuitcasePackagingError

def js(global_config, package_config):
    """Concatenates JavaScript files"""
    
    files_to_generate = package_config.get("concat_js")
    
    if files_to_generate:
        
        for (target_file, files_to_concatenate) in files_to_generate.items():

            target_file = os.path.join(
                package_config["working_dir"],
                package_config["destination_mapping"]["root"],
                target_file
            )
            
            target_dir = os.path.split(target_file)[0]

            if not os.path.exists(target_dir):
                try:
                    os.makedirs(target_dir)
                except OSError, error:
                    raise SuitcasePackagingError(error)

            concatenated_file = open(target_file,"w")
            
            for js_file in files_to_concatenate:
                js_file_path = os.path.join(global_config["base_path"], js_file)
                if not os.path.exists(js_file_path):
                    
                    raise SuitcasePackagingError(
                        "Js file for concatenation %s is missing" % js_file_path
                    )
                    
                else:
                    concatenated_file.write(open(js_file_path).read())
                    
            concatenated_file.close()
