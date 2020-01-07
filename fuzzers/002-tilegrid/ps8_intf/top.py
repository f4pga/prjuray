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
import os
import random
random.seed(int(os.getenv("SEED"), 16))
from utils import util
from utils.db import Database
from utils.lut_maker import LutMaker


def pick_ps8_wire(pin_map):
    """ Pick IMUX from PS8 interface with most sinks.

    Return list of tiles the IMUX passes through, and the BEL pin it reaches.

    """
    s = {}

    with open('../ps8_intf.csv') as f:
        for row in csv.DictReader(f):
            if row['ps8_site_pin'] not in pin_map:
                continue

            tile, wire = row['ps8_intf_wire'].split('/')

            assert row['ps8_intf_tile'] == tile, (row['ps8_intf_tile'], tile)

            if wire not in s:
                s[wire] = []

            s[wire].append((tile, pin_map[row['ps8_site_pin']].split('/')[-1]))

    max_wire = max(s.keys(), key=lambda key: len(s[key]))

    return s[max_wire]


def get_ps8_pin_map():
    m = {}
    with open('../ps8_pin_map.csv') as f:
        for row in csv.DictReader(f):
            m[row['site_pin']] = row['pin']

    return m


def gen_lut_sites():
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)
        if gridinfo.tile_type in ['CLEL_L', 'CLEL_R', 'CLEM']:
            site_name = sorted(gridinfo.sites.keys())[0]
            yield site_name


def run():
    site = sorted(gen_lut_sites())[0]
    print('''
module top();
    '''.format(loc=site))

    luts = LutMaker()

    ps8_pin_map = get_ps8_pin_map()

    bus_widths = {}
    for pin in ps8_pin_map.values():
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

    tile_and_bel_pins = pick_ps8_wire(ps8_pin_map)

    sinks = []

    with open('params.csv', 'w') as f:
        print('tile,val', file=f)
        pins = []
        for (tile,
             pin), isone in zip(tile_and_bel_pins,
                                util.gen_fuzz_states(len(tile_and_bel_pins))):
            print('{tile},{isone}'.format(tile=tile, isone=isone), file=f)

            if isone:
                sinks.append(luts.get_next_input_net())
                pins.append(pin)

    print('\n'.join(luts.create_wires_and_luts()))

    sinks.sort()
    random.shuffle(sinks)

    busses = set()

    for pin in pins:
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

    for pin in pins:
        print('assign {} = {};'.format(pin, sinks.pop()))

    print('endmodule')


if __name__ == '__main__':
    run()
