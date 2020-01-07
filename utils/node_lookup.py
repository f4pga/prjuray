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

import sqlite3
import json
import progressbar
import os.path


def create_tables(conn):
    c = conn.cursor()

    c.execute("""CREATE TABLE tile(
    pkey INTEGER PRIMARY KEY,
    name TEXT
    );""")
    c.execute("""CREATE TABLE node(
    pkey INTEGER PRIMARY KEY,
    name TEXT
    );""")
    c.execute("""CREATE TABLE wire(
    pkey INTEGER PRIMARY KEY,
    name TEXT,
    node_pkey INTEGER,
    tile_pkey INTEGER,
    FOREIGN KEY(node_pkey) REFERENCES node(pkey),
    FOREIGN KEY(tile_pkey) REFERENCES tile(pkey)
    );""")

    conn.commit()


def read_json(fname):
    with open(fname) as f:
        return json.load(f)


class NodeLookup(object):
    def __init__(self, database):
        self.conn = sqlite3.connect(database)

    def build_database(self, nodes, tiles, pool):
        create_tables(self.conn)

        c = self.conn.cursor()
        tile_names = []
        for tile_type in tiles:
            for tile in tiles[tile_type]:
                tile_names.append(tile)

        tile_pkeys = {}
        for tile_file in progressbar.progressbar(tile_names):
            # build/specimen_001/tile_DSP_L_X34Y145.tmp.json
            root, _ = os.path.splitext(os.path.basename(tile_file))
            root, _ = os.path.splitext(root)
            tile = root[5:]
            c.execute("INSERT INTO tile(name) VALUES (?);", (tile, ))
            tile_pkeys[tile] = c.lastrowid

        nodes_processed = set()
        for node in progressbar.progressbar(nodes):
            with open(node) as f:
                nodes = json.load(f)

            for node_wires in nodes[:-1]:
                assert node_wires['node'] not in nodes_processed
                nodes_processed.add(node_wires['node'])

                c.execute("INSERT INTO node(name) VALUES (?);",
                          (node_wires['node'], ))
                node_pkey = c.lastrowid

                for wire in node_wires['wires'][:-1]:
                    tile = wire['wire'].split('/')[0]

                    tile_pkey = tile_pkeys[tile]
                    c.execute(
                        """
INSERT INTO wire(name, tile_pkey, node_pkey) VALUES (?, ?, ?);""",
                        (wire['wire'], tile_pkey, node_pkey))

        self.conn.commit()

        c = self.conn.cursor()
        c.execute("CREATE INDEX tile_names ON tile(name);")
        c.execute("CREATE INDEX node_names ON node(name);")
        c.execute("CREATE INDEX wire_node_tile ON wire(node_pkey, tile_pkey);")
        c.execute("CREATE INDEX wire_tile ON wire(tile_pkey);")
        self.conn.commit()

    def site_pin_node_to_wires(self, tile, node):
        if node is None:
            return

        c = self.conn.cursor()
        c.execute(
            """
WITH
    the_tile(tile_pkey) AS (SELECT pkey AS tile_pkey FROM tile WHERE name = ?),
    the_node(node_pkey) AS (SELECT pkey AS node_pkey FROM node WHERE name = ?)
SELECT wire.name FROM wire
    INNER JOIN the_tile ON the_tile.tile_pkey = wire.tile_pkey
    INNER JOIN the_node ON the_node.node_pkey = wire.node_pkey;
""", (tile, node))

        for row in c:
            yield row[0][len(tile) + 1:]

    def wires_for_tile(self, tile):
        c = self.conn.cursor()
        c.execute(
            """
WITH
    the_tile(tile_pkey) AS (SELECT pkey AS tile_pkey FROM tile WHERE name = ?)
SELECT wire.name FROM wire
    INNER JOIN the_tile ON the_tile.tile_pkey = wire.tile_pkey;
""", (tile, ))
        for row in c:
            yield row[0][len(tile) + 1:]
