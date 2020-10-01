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

import csv
import numpy as np
from utils import util
from utils.clock_utils import MAX_GLOBAL_CLOCKS
from prjuray.db import Database


def ps8_bufg_pin_map_by_tile():
    tiles = {}
    with open('../ps8_bufg_pin_map.csv') as f:
        for row in csv.DictReader(f):
            clock_tiles = row['clock_tiles'].split(' ')
            assert len(clock_tiles) == 1, (row['pin'], clock_tiles)

            tile = clock_tiles[0]

            if tile not in tiles:
                tiles[tile] = []

            tiles[tile].append(row['pin'].split('/')[1])

    return tiles


def get_ps8_pin_map():
    with open('../ps8_pin_map.csv') as f:
        for row in csv.DictReader(f):
            yield row['pin']


def print_top(seed):
    np.random.seed(seed)

    options_by_tile = {}

    with open('../permutations.csv') as f:
        for row in csv.DictReader(f):
            tile = row['tile']

            opt = {}

            for bufg_idx in range(MAX_GLOBAL_CLOCKS):
                input_idx = row['bufg{}_input'.format(bufg_idx)]

                if input_idx == "":
                    continue

                opt[bufg_idx] = int(input_idx)

            if tile not in options_by_tile:
                options_by_tile[tile] = []
            options_by_tile[tile].append(opt)

    ps8_pins = sorted(get_ps8_pin_map())
    bus_widths = {}
    for pin in ps8_pins:
        parts = pin.split('/')[-1].split('[')

        if len(parts) == 1:
            bus_widths[parts[0]] = 1
        elif len(parts) == 2:
            if parts[0] not in bus_widths:
                bus_widths[parts[0]] = 0

            width = int(parts[1][:-1]) + 1
            if width > bus_widths[parts[0]]:
                bus_widths[parts[0]] = width
        else:
            assert False, pin

    tiles = ps8_bufg_pin_map_by_tile()
    for tile in tiles:
        tiles[tile].sort()

    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()

    bufgs_by_tile = {}

    for tile in tiles:
        bufgs_by_tile[tile] = []

        gridinfo = grid.gridinfo_at_tilename(tile)

        for site, site_type in gridinfo.sites.items():
            if site_type == 'BUFG_PS':
                bufgs_by_tile[tile].append(site)

    for tile in tiles:
        bufgs_by_tile[tile].sort()
        assert len(bufgs_by_tile[tile]) == MAX_GLOBAL_CLOCKS, tile

    opins = []
    sinks = []

    print('''
module top();
    ''')

    spec_num = util.specn() - 1

    for tile in tiles:
        opts = options_by_tile[tile]

        if spec_num < len(opts):
            # Use permutation from permutations.csv
            opt = opts[spec_num]
        else:
            # Use a random permutation.
            opt = {}
            bufgs = set(range(MAX_GLOBAL_CLOCKS))
            for input_idx in range(len(tiles[tile])):
                bufg_idx = np.random.choice(sorted(bufgs))
                bufgs.remove(bufg_idx)
                opt[bufg_idx] = input_idx

        for bufg_idx, input_idx in opt.items():
            bufg = bufgs_by_tile[tile][bufg_idx]
            input_pin = tiles[tile][input_idx]

            idx = len(opins)
            print("""
            wire bufg_{idx};

            (* LOC="{loc}", KEEP, DONT_TOUCH *)
            BUFG_PS bufg_{idx} (
                .I(bufg_{idx})
            );
            """.format(loc=bufg, idx=idx))

            sinks.append('bufg_{idx}'.format(idx=idx))
            opins.append(input_pin)

    busses = set()
    for pin in opins:
        busses.add(pin.split('[')[0])

    for bus in busses:
        print('wire [{width}-1:0] {bus};'.format(
            bus=bus, width=bus_widths[bus]))

    print('PS8 ps8 (')

    connections = []
    for bus in busses:
        connections.append('  .{bus}({bus})'.format(bus=bus))
    print(',\n'.join(connections))

    print('\n);')

    for pin, sink in zip(opins, sinks):
        print('assign {sink} = {pin};'.format(pin=pin, sink=sink))

    print('endmodule')
