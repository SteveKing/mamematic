#! /usr/bin/env python
################################################################################
##
##  mamematic.py
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
import ConfigParser

from gamelist import Game, GameList

################################################################################
##
##  Main
##
################################################################################
class Main(object):
    VERSION = '%prog 1.0'

    ############################################################################
    ##  _log_setup
    ############################################################################
    def _log_setup(self, loglevel=logging.INFO, stdout=False, stderr=False, syslog=False, logfile=None):
        class MainFormatter(logging.Formatter):
            _default = logging.Formatter(fmt='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
            _debug   = logging.Formatter(fmt='%(asctime)s %(levelname)s (%(module)s:%(lineno)d) %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
            def format(self, record):
                fmt = self._debug if record.levelno < logging.INFO else self._default
                return fmt.format(record)
            def add(self, log, hdl):
                hdl.setFormatter(self)
                log.addHandler(hdl)

        logging.addLevelName(logging.FATAL,   '[F]')
        logging.addLevelName(logging.ERROR,   '[E]')
        logging.addLevelName(logging.WARNING, '[W]')
        logging.addLevelName(logging.INFO,    '[I]')
        logging.addLevelName(logging.DEBUG,   '[D]')

        try:
            logging.captureWarnings(True)   # Doesn't exist before 2.7
        except AttributeError:
            pass

        global log
        log = logging.getLogger()
        fmt = MainFormatter()

        if stdout:  fmt.add(log, logging.StreamHandler(sys.stdout))
        if stderr:  fmt.add(log, logging.StreamHandler(sys.stderr))
        if syslog:  fmt.add(log, logging.handlers.SysLogFileHandler())
        if logfile: fmt.add(log, logging.FileHandler(logfile, mode='a'))

        log.setLevel(loglevel)
        log.info(self.parser.get_version())
        log.debug('Verbose logging enabled')

    ############################################################################
    ##  _opt_setup
    ############################################################################
    def _opt_setup(self):
        usage = "%prog [options]"
        descr = """
MAME Front-end.
""".strip()
        defaults = {
            'verbose' : False,
            'directory' : '.',
            'xml' : None,
        }

        parser = optparse.OptionParser(usage=usage, description=descr, version=Main.VERSION)
        parser.set_defaults(**defaults)

        parser.add_option('-v', '--verbose',
                dest='verbose', action='store_true',
                help='Verbose output [def: %s]'%parser.defaults.get('verbose', None))
        parser.add_option('-d', '--directory',
                dest='directory', action='store',
                help='Config directory [def: %s]'%parser.defaults.get('directory', None))
        parser.add_option('-x', '--xml',
                dest='xml', action='store',
                help='Read MAME game list from file [def: %s]'%parser.defaults.get('xml', None))


        return parser

    ############################################################################
    ##  __init__
    ############################################################################
    def __init__(self):
        self.parser = self._opt_setup()
        (self.opts, self.args) = self.parser.parse_args()

        level = logging.DEBUG if self.opts.verbose else logging.INFO
        self._log_setup(loglevel=level, stderr=True, logfile='mamematic.log')

    ############################################################################
    ##  main
    ############################################################################
    def main(self):
        self.opts.directory = os.path.normpath(self.opts.directory)
        os.chdir(self.opts.directory)
        self.config = ConfigParser.SafeConfigParser()
        self.config.read('mamematic.ini')

        gamelist = GameList()
        if self.opts.xml:
            gamelist.readxml(self.opts.xml)
        else:
            gamelist.readxml(self.config.get('mame','exec'))

        for g in gamelist:
            log.info(g)

        return(0)

################################################################################
##
##  __main__
##
################################################################################
if __name__ == '__main__':
    main = Main()
    try:
        sys.exit(main.main())
    except (Exception, KeyboardInterrupt) as e:
        logging.getLogger().fatal('ERROR: %s %s', e.__class__.__name__, e, exc_info=True)
        sys.exit(1)
