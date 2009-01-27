"""Bazaar helpers"""

import commands
import os
import re

from suitcase.exceptions import SuitcaseVcsError
from suitcase.vcs.base import VcsBase

class Bazaar(VcsBase):
    
    """Class for handling the interface to the bazaar vcs"""
    
    def get_directory_revision(self, directory):
    
        """Works on the basis of looking up from the local checkout"""
        result = commands.getstatusoutput("bzr log -q -l 1 %s" % directory)
        if result[0] > 0:
            raise SuitcaseVcsError("Can't find bzr version for %s (%s)\n"\
                "Command exited with error (%s), %s" % (
                    directory, 
                    os.getcwd(), 
                    result[0], 
                    result[1]
                )
            )
            
        else:
            match = re.search(r"^revno: (\d+)$", result[1], re.M)
            if match is None:
                raise SuitcaseVcsError(
                    "Can't find svn version for %s" % directory
                )
                
            rev = match.group(1)
            return "0.%s" % rev