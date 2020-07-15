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

import re
import os
import random
random.seed(int(os.getenv("SEED"), 16))
from utils import util
from utils.db import Database


def gen_lut_sites():
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)
        if gridinfo.tile_type in ['CLEL_L', 'CLEL_R', 'CLEM']:
            site_name = sorted(gridinfo.sites.keys())[0]
            yield site_name


def gen_sites():
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()

    o = {}
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)

        for site_name, site_type in gridinfo.sites.items():
            if site_type == 'BUFG_PS':
                if tile_name not in o:
                    o[tile_name] = []

                o[tile_name].append(site_name)

    return o


# BUFCE_ROW -> (32, 11)
RE_BUFG_PS = re.compile(r'BUFG_PS_X(\d+)Y(\d+)')


def get_site_xy(site):
    """ Return x, y for site

    >>> get_site_xy('BUFG_PS_X32Y11')
    (32, 11)
    >>> get_site_xy('BUFG_PS_X0Y0')
    (0, 0)
    >>> get_site_xy('BUFG_PS_X10Y10')
    (10, 10)
    >>> get_site_xy('BUFG_PS_X10Y15')
    (10, 15)
    >>> get_site_xy('BUFG_PS_X15Y10')
    (15, 10)

    """
    m = RE_BUFG_PS.match(site)
    assert m is not None
    return int(m.group(1)), int(m.group(2))


def write_params(params):
    pinstr = 'tile,val,site\n'
    for tile, (site, val, site2) in sorted(params.items()):
        pinstr += '%s,%s,%s,%s\n' % (tile, val, site, site2)
    open('params.csv', 'w').write(pinstr)


def run():
    site = sorted(gen_lut_sites())[0]
    print('''
module top();
    wire o;

    (* KEEP, DONT_TOUCH, LOC = "{loc}" *)
    LUT6 #(.INIT(0) ) lut (
        .I0(1),
        .I1(1),
        .I2(1),
        .I3(1),
        .I4(1),
        .I5(1),
        .O(o)
        );
endmodule
    '''.format(loc=site))

    bufce_leaf_sites = gen_sites()

    params = {}
    num_tiles = len(bufce_leaf_sites)
    itr = iter(util.gen_fuzz_states(num_tiles))
    for tile in sorted(bufce_leaf_sites.keys()):
        sites = sorted(
            bufce_leaf_sites[tile], key=lambda site: get_site_xy(site))[:2]
        site, site2 = sites
        params[tile] = (site, next(itr), site2)

    write_params(params)


if __name__ == '__main__':
    run()
