"""
Progress.py  - Created by Stuart Colville on 2007-11-29
Muffin Research Labs. http://muffinresearch.co.uk
Released under a BSD license
"""

try:
    import threading as _threading
except ImportError:
    import dummy_threading as _threading

import sys, time

class Progress(_threading.Thread):
    """A very simple progress indicator class"""
    
    INTERVAL = 0.1
    SPINCHARS = ['/', '-', '\\', '|']
    TIMEOUT = 10

    def __init__(self):
        _threading.Thread.__init__(self)
        self._pos = 0
        self.inprogress = False

    def run(self):
        """Start the spinning cursor"""
        
        self.inprogress = True
        while self.inprogress:
            sys.stderr.write('\r%s' % self.SPINCHARS[self._pos])
            self._pos = self._pos + 1
            if self._pos == len(self.SPINCHARS):
                self._pos = 0
            time.sleep(self.INTERVAL)
        sys.stderr.write('\r')

    def stop(self):
        """Stop the spinning cursor"""
        self.inprogress = False
        self.join()
