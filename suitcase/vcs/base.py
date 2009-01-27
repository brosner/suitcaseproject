"""base class for vcs"""

from suitcase.utils.singleton import Singleton

class VcsBase(Singleton):
    
    """Base class for VCS.
    
    inherits the Singleton pattern
    
    """
    
    def get_directory_revision(self):
        """Placeholder for getting revs"""
        raise NotImplementedError
