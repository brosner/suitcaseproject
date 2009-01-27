"""Singleton class for creating singletons"""

class Singleton(object):
    
    """Sets up singleton classes"""
    def __new__(cls, *args, **kwargs):
        if not '_the_instance' in cls.__dict__:
            cls._the_instance = object.__new__(cls)
        return cls._the_instance
