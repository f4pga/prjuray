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
        if gridinfo.tile_type in ['CLEM_R']:
            site_name = sorted(gridinfo.sites.keys())[0]
            yield tile_name, site_name


def write_params(params):
    pinstr = 'tile,val,site\n'
    for tile, (site, val) in sorted(params.items()):
        pinstr += '%s,%s,%s\n' % (tile, val, site)
    open('params.csv', 'w').write(pinstr)


def run():
    print('''
module top();
    ''')

    params = {}

    sites = list(gen_sites())
    for (tile_name, site_name), isone in zip(sites,
                                             util.gen_fuzz_states(len(sites))):
        params[tile_name] = (site_name, isone)

        print('''
            (* KEEP, DONT_TOUCH, LOC = "{loc}", LOCK_PINS="I0:A1 I1:A2 I2:A3 I3:A4 I4:A5 I5:A6" *)
            wire loop_{loc};
            LUT6 #(.INIT(64'b{isone}) ) lut_{loc} (
                .I0(loop_{loc}),
                .I1(1),
                .I2(1),
                .I3(1),
                .I4(1),
                .I5(1),
                .O(loop_{loc})
                );
'''.format(
            loc=site_name,
            isone=isone,
        ))

    print("endmodule")
    write_params(params)


if __name__ == '__main__':
    run()
