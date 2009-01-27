"""Suitcase Exception classes

For errors use a classname of the format: 
"Suitcase<Foo>Exception" and subclass SuitcaseException.

"""

from suitcase.utils.terminal import TerminalController

class SuitcaseException(Exception):
    
    """The generic suitcase exception class
    
    This exception is raised when your suitcase falls open and spills 
    everything on the floor!
    
    """
    
    def __init__(self, value=""):
        """Set's the message on instantiation"""
        self.term = TerminalController()
        
        if not hasattr(self, "message_prefix"):
            self.message_prefix = "Suitcase Error:"
        self.message = "%s %s" % (self.message_prefix, value)
        
    def __str__(self):
        """Returns the error message"""
        try:
            return self.term.render('${RED}%s${NORMAL}' % self.message)
        except ValueError:
            return self.message

#=============================================================================
# ERRORS
#=============================================================================
class SuitcaseImportError(SuitcaseException):
    """Exception for when imports fail"""
    
    def __init__(self, value):
        self.message_prefix = "Suitcase Import Error:"
        SuitcaseException.__init__(self, value)

class SuitcasePackagingError(SuitcaseException):
    """This exception is raised when packaging fails"""
    
    def __init__(self, value):
        self.message_prefix = "Suitcase Packaging Error:"
        SuitcaseException.__init__(self, value)
    
class SuitcaseCommandError(SuitcaseException):
    """This exception is raised a command run returns an error status"""
    def __init__(self, result, value):
        self.message_prefix = "Suitcase Command Error:"
        SuitcaseException.__init__(self, value)
        self.exit_code = result[0]
        self.output = result[1]
        
class SuitcaseVcsError(SuitcaseException):
    
    """Exception raised when there's a terminal issue with vcs integration"""
    def __init__(self, value):
        self.message_prefix = "Suitcase VCS Error:"
        SuitcaseException.__init__(self, value)
        
class SuitcaseCopyError(SuitcaseException):

    """Exception raised when there's a problem with copying files"""
    def __init__(self, value):
        self.message_prefix = "Suitcase File Copy Error:"
        SuitcaseException.__init__(self, value)        
    
class SuitcaseConfigurationError(SuitcaseException):
    
    """Exception raised when there's a problem with the configuration"""
    def __init__(self, value):
        self.message_prefix = "Suitcase Configuration Error:"
        SuitcaseException.__init__(self, value)
