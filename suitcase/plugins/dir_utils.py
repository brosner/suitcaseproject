import os
from suitcase.utils.common import run_fakeroot

def create_directory(global_config, package_config):
    """
    Creates Directory and any subdirectories
    
    Set 'dir_to_create' in your package config
    """
    directory_to_create = package_config["directory_to_create"]
    run_fakeroot("mkdir -p %s" % directory_to_create)

def chown_directory(global_config, package_config):
    """
    Chown Directories
    
    Set 'chown_user' in your package config
    Set 'chown_directory' in your package config
    """
    chown_user = package_config["chown_user"]
    chown_directory = package_config["chown_directory"]
    
    run_fakeroot("chown %s %s" % (chown_user, chown_directory))