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

import os
import random
random.seed(int(os.getenv("SEED"), 16))
from utils import util
from utils.db import Database


def gen_sites():
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)

        tile_type = gridinfo.tile_type
        if tile_type in ['CLEM', 'CLEM_R', 'CLE_M', 'CLE_M_R']:
            # Don't fuzz the top and bottom of the grid, the interconnect
            # there behaves differently.
            _, _, y_min, y_max = grid.dims()
            if loc.grid_y <= y_min + 1 or loc.grid_y >= y_max - 1:
                continue

            site_name = sorted(gridinfo.sites.keys())[0]

            int_tile_loc = (loc.grid_x + 1, loc.grid_y)

            int_tile_name = grid.tilename_at_loc(int_tile_loc)

            if not int_tile_name.startswith('INT_'):
                continue

            if os.getenv('URAY_ARCH') == 'UltraScalePlus':
                if int_tile_name.endswith('Y31') or \
                    int_tile_name.endswith('Y91') or \
                    int_tile_name.endswith('Y151'):
                    continue

            yield int_tile_name, site_name


def write_params(params):
    pinstr = 'tile,val\n'
    for tile, (site, val) in sorted(params.items()):
        pinstr += '%s,%s,%s\n' % (tile, val, site)
    open('params.csv', 'w').write(pinstr)


def run():
    print('''
module top();
    ''')

    params = {}

    sites = sorted(list(gen_sites()))
    for (tile_name, site_name), isone in zip(sites,
                                             util.gen_fuzz_states(len(sites))):
        params[tile_name] = (site_name, isone)

        print('''
            (* KEEP, DONT_TOUCH, LOC = "{loc}", LOCK_PINS="I0:A1, I1:A2, I2:A3, I3:A4, I4:A5, I5:A6" *)
            wire loop_{loc};
            LUT6 #(.INIT(64'hFFFFFFFFFFFFFFFF) ) lutc_{loc} (
                .I0(1),
                .I1(1),
                .I2(1),
                .I3({loop}),
                .I4(loop_{loc}),
                .I5(1),
                .O(loop_{loc})
                );

            (* KEEP, DONT_TOUCH, LOC = "{loc}", LOCK_PINS="I0:A1, I1:A2, I2:A3, I3:A4, I4:A5, I5:A6" *)
            LUT6 #(.INIT(64'hFFFFFFFFFFFFFFFF) ) lutd_{loc} (
                .I0(1),
                .I1(1),
                .I2(1),
                .I3(loop_{loc}),
                .I4(loop_{loc}),
                .I5(1)
                );
'''.format(loc=site_name, loop=1 if isone else ('loop_' + site_name)))

    print("endmodule")
    write_params(params)


if __name__ == '__main__':
    run()
