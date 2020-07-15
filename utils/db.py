#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

import os.path
import simplejson as json
from utils import grid
from utils import tile
from utils import tile_segbits
from utils import site_type
from utils import connections


def get_available_databases(prjxray_root):
    """ Return set of available directory to databases given the root directory
      of prjxray-db
  """
    db_types = set()
    for d in os.listdir(prjxray_root):
        if d.startswith("."):
            continue

        dpath = os.path.join(prjxray_root, d)

        if os.path.exists(os.path.join(dpath, "settings.sh")):
            db_types.add(dpath)

    return db_types


class Database(object):
    def __init__(self, db_root, part):
        """ Create project x-ray Database at given db_root.

    db_root: Path to directory containing settings.sh, *.db, tilegrid.json and
             tileconn.json

    """
        self.db_root = db_root
        self.part = part
        # tilegrid.json JSON object
        self.tilegrid = None
        self.tileconn = None
        self.tile_types = None

        self.tile_types = {}
        self.tile_segbits = {}
        self.site_types = {}

        self.required_features = {}

        for f in os.listdir(os.path.join(self.db_root, 'tile_types')):
            if f.endswith('.json') and f.startswith('tile_type_'):
                tile_type = f[len('tile_type_'):-len('.json')].lower()

                segbits = os.path.join(self.db_root,
                                       'segbits_{}.db'.format(tile_type))
                if not os.path.isfile(segbits):
                    segbits = None

                block_ram_segbits = os.path.join(
                    self.db_root, 'segbits_{}.block_ram.db'.format(tile_type))
                if not os.path.isfile(block_ram_segbits):
                    block_ram_segbits = None

                ppips = os.path.join(self.db_root,
                                     'ppips_{}.db'.format(tile_type))
                if not os.path.isfile(ppips):
                    ppips = None

                mask = os.path.join(self.db_root,
                                    'mask_{}.db'.format(tile_type))
                if not os.path.isfile(mask):
                    mask = None

                tile_type_file = os.path.join(
                    self.db_root, 'tile_types',
                    'tile_type_{}.json'.format(tile_type.upper()))
                if not os.path.isfile(tile_type_file):
                    tile_type_file = None

                self.tile_types[tile_type.upper()] = tile.TileDbs(
                    segbits=segbits,
                    block_ram_segbits=block_ram_segbits,
                    ppips=ppips,
                    mask=mask,
                    tile_type=tile_type_file,
                )

        for f in os.listdir(os.path.join(self.db_root, 'site_types')):
            if f.endswith('.json') and f.startswith('site_type_'):
                site_type_name = f[len('site_type_'):-len('.json')]

                self.site_types[site_type_name] = os.path.join(
                    self.db_root, 'site_types', f)

        required_features_path = os.path.join(self.db_root, self.part,
                                              "required_features.fasm")
        if os.path.isfile(required_features_path):
            with open(required_features_path, "r") as fp:
                features = []
                for line in fp:
                    line = line.strip()
                    if len(line) > 0:
                        features.append(line)

                self.required_features[self.part] = set(features)

        self.tile_types_obj = {}

    def get_tile_types(self):
        """ Return list of tile types """
        return self.tile_types.keys()

    def get_tile_type(self, tile_type):
        """ Return Tile object for given tilename. """
        if tile_type not in self.tile_types_obj:
            self.tile_types_obj[tile_type] = tile.Tile(
                tile_type, self.tile_types[tile_type])

        return self.tile_types_obj[tile_type]

    def _read_tilegrid(self):
        """ Read tilegrid database if not already read. """
        if not self.tilegrid:
            with open(os.path.join(self.db_root, self.part,
                                   'tilegrid.json')) as f:
                self.tilegrid = json.load(f)

    def _read_tileconn(self):
        """ Read tileconn database if not already read. """
        if not self.tileconn:
            with open(os.path.join(self.db_root, self.part,
                                   'tileconn.json')) as f:
                self.tileconn = json.load(f)

    def grid(self):
        """ Return Grid object for database. """
        self._read_tilegrid()
        return grid.Grid(self, self.tilegrid)

    def _read_tile_types(self):
        for tile_type, db in self.tile_types.items():
            with open(db.tile_type) as f:
                self.tile_types[tile_type] = json.load(f)

    def connections(self):
        self._read_tilegrid()
        self._read_tileconn()
        self._read_tile_types()

        tile_wires = dict((tile_type, db['wires'])
                          for tile_type, db in self.tile_types.items())
        return connections.Connections(self.tilegrid, self.tileconn,
                                       tile_wires)

    def get_site_types(self):
        return self.site_types.keys()

    def get_site_type(self, site_type_name):
        with open(self.site_types[site_type_name]) as f:
            site_type_data = json.load(f)

        return site_type.SiteType(site_type_data)

    def get_tile_segbits(self, tile_type):
        if tile_type not in self.tile_segbits:
            self.tile_segbits[tile_type] = tile_segbits.TileSegbits(
                self.tile_types[tile_type.upper()])

        return self.tile_segbits[tile_type]

    def get_required_fasm_features(self, part=None):
        """
        Assembles a set of required fasm features for given part. Returns a list
        of fasm features.
        """

        # No required features in the db, return empty list
        if self.required_features is None:
            return set()

        # Return list of part specific features
        return self.required_features.get(part, set())
