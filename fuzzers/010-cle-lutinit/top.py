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
from prjuray.db import Database


def gen_sites():
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)
        if gridinfo.tile_type in ['CLEL_L', 'CLEL_R', 'CLEM']:
            site_name = sorted(gridinfo.sites.keys())[0]
            yield tile_name, site_name


def write_params(params):
    pinstr = 'tile,site\n'
    for tile, site in sorted(params.items()):
        pinstr += '%s,%s\n' % (tile, site)
    open('params.csv', 'w').write(pinstr)


def run():
    sites_params = []
    sites = list(gen_sites())[0:30]
    # One specimen can solve bits for 2 BEL types
    # Therefore the generated netlist contains
    # A-B LUTs/FFs or C-D, E-F or G-H LUTs/FFs
    seedn = int(os.getenv("SEEDN")) % 4
    bels = ['E', 'F', 'G', 'H', 'A', 'B', 'C', 'D']
    for (tile_name, site_name) in sites:
        bel = bels[seedn * 2 + random.randrange(2)]
        params = {}
        params['tile_name'] = tile_name
        params['site_name'] = site_name
        params['bel_lut6'] = bel + "6LUT"
        params['bel_ff'] = bel + "FF"
        sites_params.append(params)
    print(
        util.render_template(
            os.path.join(os.getenv("FUZDIR"), "top.tpl"),
            {"parameters": sites_params}))
    write_params(params)


if __name__ == '__main__':
    run()
