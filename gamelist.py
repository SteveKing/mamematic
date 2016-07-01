################################################################################
##
##  gamelist.py
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
import collections
import json
import xml.etree.ElementTree as ET

from mameutil import *

################################################################################
##
##  OmniEncoder
##
################################################################################
class OmniEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return obj.to_serializable()
        except AttributeError:
            pass
        return json.JSONEncoder.default(self, obj)

################################################################################
##
##  Game
##
################################################################################
class Game(object):
    def __init__(self):
        self.name         = None
        self.sourcefile   = None
        self.isbios       = None
        self.isdevice     = None
        self.ismechanical = None
        self.runnable     = None
        self.cloneof      = None
        self.romof        = None
        self.sampleof     = None
        self.description  = None
        self.year         = None
        self.manufacturer = None
        self.status       = None
        self.emulation    = None
        self.color        = None
        self.sound        = None
        self.graphic      = None
        self.cocktail     = None
        self.protection   = None
        self.savestate    = None
        self.category     = None
        self.subcat       = None
        self.mature       = None

    @classmethod
    def from_xml(cls, elem):
        def _bool(val):
            assert(val in ('yes','no',True,False,None))
            return bool(val in ('yes',True))

        def _find(machine, field):
            elem = machine.find(field)
            if elem is not None:
                return elem.text
            else:
                return ''

        def _driver_attrib(driver, field):
            if driver is not None:
                return driver.attrib.get(field, '')
            else:
                return ''

        self = cls()
        machine = elem
        driver = machine.find('driver')
        input = machine.find('input')
        controls = []
        if input is not None:
            for elem in input.findall('control'):
                controls.append(elem)

        self.name         = machine.attrib.get('name', None)
        self.sourcefile   = machine.attrib.get('sourcefile', None)
        self.isbios       = _bool(machine.attrib.get('isbios', False))
        self.isdevice     = _bool(machine.attrib.get('isdevice', False))
        self.ismechanical = _bool(machine.attrib.get('ismechanical', False))
        self.runnable     = _bool(machine.attrib.get('runnable', True))
        self.cloneof      = machine.attrib.get('cloneof', self.name)
        self.romof        = machine.attrib.get('romof', None)
        self.sampleof     = machine.attrib.get('sampleof', None)
        self.description  = _find(machine, 'description')
        self.year         = _find(machine, 'year')
        self.manufacturer = _find(machine, 'manufacturer')
        self.status       = _driver_attrib(driver, 'status')
        self.emulation    = _driver_attrib(driver, 'emulation')
        self.color        = _driver_attrib(driver, 'color')
        self.sound        = _driver_attrib(driver, 'sound')
        self.graphic      = _driver_attrib(driver, 'graphic')
        self.cocktail     = _driver_attrib(driver, 'cocktail')
        self.protection   = _driver_attrib(driver, 'protection')
        self.savestate    = _driver_attrib(driver, 'savestate')
        #self.category     = category
        #self.subcat       = subcat
        #self.mature       = mature

        #genre = self._genre.get(self.name, (None,None,None))
        #self._category = genre[0]
        #self._subcat   = genre[1]
        #self._mature   = genre[2]

        return self

    @classmethod
    def genre_init(cls, fname):
        cls._genre = {}
        with open(fname) as fh:
            for line in fh:
                line = line.strip()
                if line == '[VerAdded]':
                    break
                mo = re.search(r'^(.*?)=(.*?)(/(.*?))?(\* Mature \*)?$', line)
                if mo:
                    name = mo.group(1)
                    category = mo.group(2)
                    subcat = mo.group(4)
                    mature = bool(mo.group(5) is not None)
                    assert(name)
                    if name:
                        name = name.strip()
                        assert(name not in cls._genre)
                        if category: category = category.strip()
                        if subcat: subcat = subcat.strip()
                        cls._genre[name] = (category, subcat, mature)

################################################################################
##
##  GameList
##
################################################################################
class GameList(collections.MutableMapping):
    __getitem__ = property(lambda s:s._data.__getitem__)
    __setitem__ = property(lambda s:s._data.__setitem__)
    __delitem__ = property(lambda s:s._data.__delitem__)
    __iter__    = property(lambda s:s._data.__iter__)
    __len__     = property(lambda s:s._data.__len__)

    def __init__(self):
        self._data = {}

    def readxml(self, fname):
        log = logging.getLogger()
        log.info('Reading gamelist from %r', fname)
        chrono = Chronolog().start()

        try:
            source = 'file'
            tree = ET.parse(open(fname))
        except ET.ParseError:
            source = 'MAME executable'
            cmd = [fname, '-listxml']
            sub = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            tree = ET.parse(sub.stdout)

        root = tree.getroot()
        for machine in root.iter('machine'):
            m = Game.from_xml(machine)
            self[m.name] = m

        log.info('Read %d games from %s in %0.1fs', len(self), source, chrono.stop())

    def read(self, path):
        jdata = json.load(open(path))
        for jobj in jdata:
            game = Game.from_json(jobj)
            self[game.name] = game

    def write(self, path):
        json.dump(self._data, open(path, 'w'), cls=OmniEncoder)
