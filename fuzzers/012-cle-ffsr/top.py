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

import random
random.seed(0)
import os
import re
from utils import util
from utils import verilog
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
    pinstr = 'site,bel,rs_inv\n'
    for param in params:
        pinstr += "{},{},{}\n".format(param['site'], param['bel'],
                                      param['rs_inv'])
    open('params.csv', 'w').write(pinstr)


def run():
    sites_params = []
    sites = list(gen_sites())[0:20]
    CLBN = len(sites)
    DIN_N = CLBN * 4
    DOUT_N = CLBN * 1
    ffprim = 'FDRE'
    ff_bels = (
        'AFF',
        'EFF',
    )
    for (tile_name, site_name) in sites:
        params = {}
        params['name'] = 'clb_{}'.format(ffprim)
        params['site'] = site_name
        params['bel'] = random.choice(ff_bels)
        params['rs_inv'] = random.randint(0, 1)
        sites_params.append(params)
    print(
        util.render_template(
            os.path.join(os.getenv("FUZDIR"), "top.tpl"), {
                "parameters": sites_params,
                "din_index": DIN_N - 1,
                "dout_index": DOUT_N - 1
            }))
    write_params(sites_params)


if __name__ == "__main__":
    run()
