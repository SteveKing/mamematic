################################################################################
##
##  mameutil.py
##
##  Copyright (c) 2016 Steve King
##
################################################################################
import logging
import logging.handlers
import optparse
import os
import re
import subprocess
import sys
import time
import unittest

class ChronologNotStarted(Exception): pass

class Chronolog(object):
    def __init__(self):
        self._started = None
        self._stopped = None

    started = property(lambda s:s._started)
    stopped = property(lambda s:s._stopped)

    def start(self):
        self._started = time.time()
        self._stopped = None
        return self

    def stop(self):
        if self._stopped or not self._started:
            raise ChronologNotStarted()
        self._stopped = time.time()
        return self.elapsed()

    def elapsed(self):
        if not self._started:
            raise ChronologNotStarted()
        if self._stopped:
            elapsed = self._stopped - self._started
        else:
            elapsed = time.time() - self._started
        return elapsed
