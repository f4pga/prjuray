#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2020  The Project X-Ray Authors.
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
        if gridinfo.tile_type in ['PSS_ALTO']:
            for site_name, site_type in gridinfo.sites.items():
                if site_type == 'PS8':
                    yield tile_name, site_name


def write_params(params):
    pinstr = 'tile,val,site\n'
    for tile, (site, val) in sorted(params.items()):
        pinstr += '%s,%s,%s\n' % (tile, val, site)
    open('params.csv', 'w').write(pinstr)


def run():
    params = {}
    sites = list(gen_sites())
    assert len(sites) == 1
    itr = iter(util.gen_fuzz_states(len(sites)))
    for (tile_name, site_name) in sites:
        isone = next(itr)
        params[tile_name] = (site_name, isone)
        print(
            util.render_template(
                os.path.join(os.getenv("FUZDIR"), "top.tpl"),
                {"isone": isone}))

    write_params(params)


if __name__ == '__main__':
    run()
