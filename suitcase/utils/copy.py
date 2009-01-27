"""
To start with I'm going to simply implement this as an rsync call.

Later this should be replaced by a recursive copy function using shutil.

"""

import os

from suitcase.utils.common import run_command
from suitcase.exceptions import SuitcaseCopyError

DEBUG = False

def copy_files(source, destination, exclusions=None):

    """rsync copy of files from source to destination

    This should be ideally replaced later with a recursive copy function
    implemented in python.

    """

    if exclusions is None:
        exclusions = []

    if not os.path.exists(source):
        raise SuitcaseCopyError('Source directory does not exist')

    if not os.path.isdir(destination):
        try:
            os.makedirs(destination)    
        except OSError, error:
            raise SuitcaseCopyError(error)

    excludes_str = " ".join(
        ["--exclude '%s'" % exclusion for exclusion in exclusions]
    )

    if DEBUG:
        print "SOURCE: %s" % source
        print "DEST: %s" % destination

    rsync_str = "/usr/bin/rsync -r %s '%s' '%s'" % (
        excludes_str,
        source,
        destination
    )

    return run_command(rsync_str)

