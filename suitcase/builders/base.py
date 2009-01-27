"""Base builder class"""

import sys
import os

from suitcase.utils.common import (
    run_command, 
    get_user_input, 
    get_dynamic_class_instance
)
    
from suitcase.exceptions import (
    SuitcaseException,
    SuitcaseImportError,
    SuitcasePackagingError,
    SuitcaseCommandError,
    SuitcaseVcsError,
    SuitcaseCopyError,
    SuitcaseConfigurationError
)

DEBUG = False

class BuilderBase:
    
    """Base builder class to subclass from"""
    
    def __init__(self, global_config):
        self.global_config = global_config
        package_format = global_config['package_format']
        package_module = "suitcase.packing.%s" % package_format
        self.packer = get_dynamic_class_instance(
            package_module, 
            package_format.capitalize(), 
            config = global_config
        )

    def pre_build(self, package_config):
        """pre built hook"""
        pass

    def build(self, package_config):
        """build method placeholder"""
        raise NotImplementedError

    def make_working_dir(self):
        """Makes a working directory under global build dir"""

        working_dir = os.path.expanduser("%s/temp/%s" % (
            self.global_config["build_directory"], 
            self.package_config["package"]
        ))

        if os.path.exists(working_dir):
            if not self.global_config['assume_yes']:
                result = get_user_input(
                    'Suitcase Warning: %s will be deleted. Are you sure?' \
                        % working_dir, ['yes','no'], 'yes',
                )
                
                if result == 'no':
                    sys.exit(1)
                    
            run_command("rm -rf %s" % working_dir)

        if DEBUG:
            print "MAKING: " + working_dir
            
        try:    
            os.makedirs(working_dir)
        except OSError, error:
            raise SuitcasePackagingError(error)
            
        return working_dir
