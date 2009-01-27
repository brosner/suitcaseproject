.. _configuration:


Configuration
**********************************

.. _suitcase-cli-options:

CLI Options
---------------------------

.. code-block:: sh


    usage: suitcase [options] <Package Directory 1>,<Package Directory 2>...<Package Directory n> etc

    options:
      -d DIRECTORY, --directory=DIRECTORY
                            Directory to start from. Defaults to current working
                            directory. This is assumed to be the root of your
                            branch.
      -c CONFIGURATION, --config=CONFIGURATION
                            Provides a location of a configuration YAML file.
                            (Defaults to suitcase.yml within the root of your
                            branch).
      -q, --quiet           suppress output
      --no-clean            Tells suitcase to NOT clean up after itself by
                            deleting the temp dir after building. Good for
                            analysing where your package creation went wrong
      --no-move             Do NOT attempt to move package after building.
      -y, --assume-yes      Assume yes for all things that would otherwise be
                            interactive
      --force-build         Forces build even if package is already built
      --version             show program's version number and exit
      -h, --help            show this help message and exit
  

.. _suitcase-config-options:

Suitcase Configuration Options
-----------------------------------

Configuration can be determined at several levels to make it easier to configure how suitcase works with your code.

The closer you get to the files being packaged the higher the specificity of the configuration.

suitcase.yml
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

suitcase.yml - is the default configuration which sets-up the global configuration for building packages from a branch.

Here you can set sensible defaults which are used unless overridden lower down in the configuration

Collections
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Package collections are defined in the top-level config (suitcase.yml) collections are ways to define a common set of configuration options to several parts of the branch at once.

Package-level configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Package level configuration overrides everything higher up as necessary.


Configuration Parameters
--------------------------------------

All configuration is specified in yaml files. You can find out more about YAML_ on the YAML_ site.

These are the configuration parameters for each configuration section. First up is the global settings which applies to all configuration file locations

Global Parameters:
~~~~~~~~~~~~~~~~~~~~~~~~~~

package
    The name of the package
package_format
    The packaging system e.g: debian
maintainer
    The person who maintains this package set in the format: Mr packages Maintainer <somedude@test.com>
build_directory
    The directory where the packages are built. Note: a temp directory will be added to this path.
version_control
    The Version Control System (VCS) you are using e.g: subversion or bazaar. 

Destination Mapping 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Destination mappings are a way of preventing your packaging system from dictating to you how you organise your code.

This means that you organise your code in your branches in the way you want to and suitcase will take care of putting your code in the right place for packaging via the destination mapping.

Here's a basic example YAML config:

.. code-block:: yaml

    destination_mapping:
        root: /srv/stuff
        etc/: /etc/

The root is where all files should end up on the target system. (The target system being where you install your package.)

So if your package code layout in the branch looks like this:

.. code-block:: sh

    foo
        lib
        htdocs
        etc
        file.txt

With the example config taken into consideration the build directory layout will look like this:

.. code-block:: sh

    srv/stuff
            lib
            htdocs
            file.txt
    etc
    
Relative paths
.................................
    
If the leading slash is omitted in the destination directory then those paths will be relative to the root.

.. code-block:: yaml

    destination_mapping:
        root: /srv/stuff
        etc/: etc/

Which in turn results in:

.. code-block:: sh

    foo
        lib
        htdocs
        etc
        file.txt

With the example config taken into consideration the build directory layout will look like this:

.. code-block:: sh

    srv/stuff
            lib
            htdocs
            file.txt
            etc



Collection Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Collections are ways of grouping configuration

Here's an example:

.. code-block:: yaml

    collections: 
        fandoogle:
            dirs: ["foo/*", "bar"]
            destination_mapping:
                root: /srv/stuff
                etc/: etc/
                
In the example above the key "fandoogle" doesn't mean anything it's simply a way for you to be able to define a name for your collection that means something.


            
"dirs" setting
.................................

*Note: This is specific to collections only*

Dirs is a list of paths that suitcase can apply the collection's configuration to. Dirs supports `globbing <http://en.wikipedia.org/wiki/Globbing>`_

.. code-block:: yaml

    dirs: ["foo/*", "bar"]

Exclusions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are several types of exclusions

:path_exlusions:
    Excludes files and directories from being looked at when suitcase walks the  branch looking for things to build.
    
:build_exclusions:
    Excludes files and directories from being built


    
    
    
.. _YAML: http://www.yaml.org/    