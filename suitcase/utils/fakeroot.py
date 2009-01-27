"""Set's up a shared temp file cache for fakeroot"""

from suitcase.utils.singleton import Singleton
from tempfile import mkstemp

class Fakeroot(Singleton):
    
    """singleton for maintaining a cache for fakeroot"""
    def __init__(self):
        if not "cache_filename" in self.__dict__:
            self.cache_filename = mkstemp()[1]
