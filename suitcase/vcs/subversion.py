"""Subversion helpers"""

import commands
import os
import re

from suitcase.exceptions import SuitcaseVcsError
from suitcase.vcs.base import VcsBase

class Subversion(VcsBase):
    
    """Class interface to subversion"""

    def get_remote_branch_location(self, directory):
    
        """Works out the URL of remote branch"""
        result = commands.getstatusoutput("svn info %s" % directory)
        if result[0] > 0:
            raise SuitcaseVcsError("Can't find svn version for %s (%s)\n"\
                "Command exited with error (%s), %s" % (
                    directory,
                    os.getcwd(),
                    result[0],
                    result[1],
                )
            )
            
        else:
            match = re.search(r"^URL: (.*?)$", result[1], re.M)
            if match is None:
                raise SuitcaseVcsError("Can't find svn url for %s" % directory)
            url = match.group(1)
                
            return url

    def get_directory_revision(self, directory):
    
        """Works out the revno for a path by querying the remote repo"""
        remote_dir = self.get_remote_branch_location(directory)
        result = commands.getstatusoutput(
            "svn log -q --limit 1 %s" % remote_dir
        )
        
        if result[0] > 0:
            raise SuitcaseVcsError("Can't find svn version for %s (%s)\n"\
                "Command exited with error (%s), %s" % (
                    directory, 
                    os.getcwd(), 
                    result[0], 
                    result[1]
                )
            )
        else:
            match = re.search(r"^r(\d+) ", result[1], re.MULTILINE)
            if match is None:
                raise SuitcaseVcsError(
                    "Can't find svn version for %s" % directory
                )
            rev = match.group(1)
            return "0.%s" % rev
