#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2020-2022 F4PGA Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

import re
import os
import random
random.seed(int(os.getenv("SEED"), 16))
from utils import util
from prjuray.db import Database


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
            if site_type == 'BUFCE_LEAF':
                if tile_name not in o:
                    o[tile_name] = []

                o[tile_name].append(site_name)

    return o


# BUFCE_LEAF_X32Y11 -> (32, 11)
RE_BUFCE_LEAF = re.compile(r'BUFCE_LEAF_X(\d+)Y(\d+)')


def get_site_xy(site):
    """ Return x, y for site

    >>> get_site_xy('BUFCE_LEAF_X32Y11')
    (32, 11)
    >>> get_site_xy('BUFCE_LEAF_X0Y0')
    (0, 0)
    >>> get_site_xy('BUFCE_LEAF_X10Y10')
    (10, 10)
    >>> get_site_xy('BUFCE_LEAF_X10Y15')
    (10, 15)
    >>> get_site_xy('BUFCE_LEAF_X15Y10')
    (15, 10)

    """
    m = RE_BUFCE_LEAF.match(site)
    assert m is not None
    return int(m.group(1)), int(m.group(2))


def write_params(params):
    pinstr = 'tile,val,site\n'
    for tile, (site, val) in sorted(params.items()):
        pinstr += '%s,%s,%s\n' % (tile, val, site)
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
        for site in sorted(
                bufce_leaf_sites[tile],
                key=lambda site: get_site_xy(site))[:1]:
            params[tile] = (site, next(itr))

    write_params(params)


if __name__ == '__main__':
    run()
