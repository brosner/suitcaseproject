An Overview of Suitcase
===============================================

- Suitcase is a generic packaging and build solution for web application deployment. 
- Makes it possible to build a number of packages from any branch of code.
- High level goals are for this system to be flexible enough to work with any software that's to be deployed onto a server.

Core Features
**********************************

- Can support any packaging systems that there are package subclasses. Default is Debian packaging but other can be supported in time.
- Version Control agnostic - can theoretically support any VCS. Though to start with only subversion and bazaar are supported
- Asset (image, CSS, JS) versioning plugin available
- Plugin interface to facilitate auto-dependencies for different software and frameworks and languages which are implemented as a number of configurable hooks

Assumptions and Requirements 
**********************************

- Suitcase is designed to only work for branches of code. This is because it's unlikely you'll need packaging if you don't use VCS.
- Suitcase assumes you have tools for building packages on the system you run it on. Though errors will be raised if the appropriate commands cannot be found.
- You'll need python >= 2.4 to run it.



