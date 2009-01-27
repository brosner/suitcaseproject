Collections
=========================

Collections are ways to make a configuration apply to multiple packages. There are really useful for places where you want to build lots of packages and they share common configuration options.

Collections allow ways to apply multiple processing hooks. File destination mappings and common dependencies. They are able to run with all of the default set of configuration parameters.

Collections Specific Config
******************************

"dirs" is the only parameter which is collection specific for now; see :ref:`configuration` for more details


Examples
*******************************

.. code-block:: yaml

    collections:
       default:
           dirs: ['ext/*', 'lib/*','migrations', 'templates/root/admin','templates/root/apps/*','templates/root/common','templates/root/domains/*']
       apps:
           depends: ['gcap-apps-common']
           pre_conf: suitcase.plugins.django.apps.generate_depends
           dirs: ['apps/*']
       configs:
           depends: ['gcap-configs-common']

