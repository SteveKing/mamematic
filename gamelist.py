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
import collections
import json
import xml.etree.ElementTree as ET

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
        pass

    @classmethod
    def from_xml(cls, elem):
        self = cls()
        self._machine = elem
        self._driver = self._machine.find('driver')
        self._input = self._machine.find('input')
        self.controls = []
        if self._input is not None:
            for elem in self._input.findall('control'):
                self.controls.append(Control(elem))

        genre = self._genre.get(self.name, (None,None,None))
        self._category = genre[0]
        self._subcat   = genre[1]
        self._mature   = genre[2]

    def _bool(self, val):
        assert(val in ('yes','no',True,False,None))
        return bool(val in ('yes',True))

    def _find(self, field):
        elem = self._machine.find(field)
        if elem is not None:
            return elem.text
        else:
            return ''

    def _driver_attrib(self, field):
        if self._driver is not None:
            return self._driver.attrib.get(field, '')
        else:
            return ''

    name         = property(lambda s:s._machine.attrib.get('name', None))
    sourcefile   = property(lambda s:s._machine.attrib.get('sourcefile', None))
    isbios       = property(lambda s:s._bool(s._machine.attrib.get('isbios', False)))
    isdevice     = property(lambda s:s._bool(s._machine.attrib.get('isdevice', False)))
    ismechanical = property(lambda s:s._bool(s._machine.attrib.get('ismechanical', False)))
    runnable     = property(lambda s:s._bool(s._machine.attrib.get('runnable', True)))
    cloneof      = property(lambda s:s._machine.attrib.get('cloneof', s.name))
    romof        = property(lambda s:s._machine.attrib.get('romof', None))
    sampleof     = property(lambda s:s._machine.attrib.get('sampleof', None))

    description  = property(lambda s:s._find('description'))
    year         = property(lambda s:s._find('year'))
    manufacturer = property(lambda s:s._find('manufacturer'))

    status       = property(lambda s:s._driver_attrib('status'))
    emulation    = property(lambda s:s._driver_attrib('emulation'))
    color        = property(lambda s:s._driver_attrib('color'))
    sound        = property(lambda s:s._driver_attrib('sound'))
    graphic      = property(lambda s:s._driver_attrib('graphic'))
    cocktail     = property(lambda s:s._driver_attrib('cocktail'))
    protection   = property(lambda s:s._driver_attrib('protection'))
    savestate    = property(lambda s:s._driver_attrib('savestate'))

    category     = property(lambda s:s._category)
    subcat       = property(lambda s:s._subcat)
    mature       = property(lambda s:s._mature)

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

    def readxml(self, exe):
        log = logging.getLogger()
        cmd = [exe, '-listxml']
        log.info('Reading XML from %s...', exe)
        beg = time.time()
        sub = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        tree = ET.parse(sub.stdout)
        log.info('Parsing took %0.1fs', time.time()-beg)
        root = tree.getroot()
        for machine in root.iter('machine'):
            m = Game.from_xml(machine)
            self[m.name] = m

    def read(self, path):
        jdata = json.load(open(path))
        for jobj in jdata:
            game = Game.from_json(jobj)
            self[game.name] = game

    def write(self, path):
        json.dump(self._data, open(path, 'w'), cls=OmniEncoder)
