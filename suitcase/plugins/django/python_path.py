"""Python path plugin"""

import os

from suitcase.utils.common import run_fakeroot

def chown(global_config, package_config):
    
    """Special chown for python path"""
    source_dir = package_config["working_dir"]
    uploaded_dir = os.path.join(source_dir, "uploaded")
    run_fakeroot("chgrp -R www-data %s" % uploaded_dir)
    run_fakeroot("chmod g+sw %s" % uploaded_dir)

