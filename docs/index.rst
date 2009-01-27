.. Suitcase documentation master file, created by sphinx-quickstart on Tue Oct 28 19:50:00 2008.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Suitcase's documentation!
====================================


Introduction
***************

Suitcase is an extensible and flexible code packaging system to build packages for deployment. It was primarily built for assisting with the deployment of web applications but as an app it really doesn't care about what you are building.

Suitcase is architected to be flexible so that it's possible to extend it to suit your packaging requirement. It's also designed to be package system and version control agnostic.

Suitcase depends on the user making use of version control in order to be able to determine package versions. This design decision was made because if you're not using a VCS then you probably won't need a packaging system. However if required it's technically possible that someone could create a replacement of the VCS backend with a system that tracks versions of files without a VCS.

Suitcase was initially designed to build debian packages but the codebase is strcutured with the intention that should be possible to support any arbitrary packaging system as required.


Contents
****************

.. toctree::
   :maxdepth: 3
   
   overview
   concepts
   configuration
   collections
   hooks_and_plugins
   code
   faq
   

Indices and tables
*********************

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Authors:
    Suitcase was designed and written by Stuart Colville and Alex Knowles of GCAP Media Ltd.