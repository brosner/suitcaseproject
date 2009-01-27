Hooks and Plugins
=================================

These hooks allow code to be run which can affect the configuration prior to building the package.

Hooks are specified in the configuration as fully namespaced methods. The assumption is made that anything you put in the configuration will be found by Python in order to be executed.

Basic Example
*******************

All hooks take the configuration dictionary as their argument:

.. code-block:: python

   def example_hook(global_config, package_config):
        """An example hook"""
        # Your code here.
        # ...
        return package_config # return the package config
        
Configuration is added to the YAML file like so.
        
.. code-block:: yaml

   post_permissions: [suitcase.plugins.welovelocal.chown]

Hook types
******************

pre_conf
    This is a hook that makes it possible to manipulate the configuration dictionary or run arbitrary code before the package configuration is generated.
    
post_conf
    This is a hook to run arbitrary code after the configuration step. It is also possible to manipulate the configuration dictionary at this point.
    
pre_copy
    This is a hook executes code prior to copying the code into build directories.

post_copy
    Executes after the files have been copied into the build directory. This gives the possibility of being able to manipulate the files prior to build. For example this is a way to hook in plugins such as asset versioning etc.

post_permissions
    A hook run after the permissions are changed. This hook is run so that extra permissions can be set.