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

import numpy as np

from utils import util
from utils.db import Database
from utils.clock_utils import GlobalClockBuffers, populate_leafs, MAX_GLOBAL_CLOCKS


def gen_sites(grid):
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)

        for site, site_type in gridinfo.sites.items():
            if site_type in ['SLICEM', 'SLICEL']:
                yield site


def print_top(seed):
    np.random.seed(seed)

    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()
    slices = sorted(gen_sites(grid))
    np.random.shuffle(slices)

    print("""
module top();
        """)
    print("""
    (* BEL="A6LUT", LOC="{loc}", KEEP, DONT_TOUCH *) LUT5 lut ();
    """.format(loc=slices.pop()))
    print('endmodule')

    leafs = populate_leafs(grid)

    site_to_site_type = {}
    site_to_tile = {}
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)

        for site, site_type in gridinfo.sites.items():
            site_to_site_type[site] = site_type
            site_to_tile[site] = tile_name

    bufgs = GlobalClockBuffers('../bufg_outputs.csv')

    clock_column = sorted(leafs.keys())
    np.random.shuffle(clock_column)

    bufg_leaf = util.create_xy_fun(prefix='BUFCE_LEAF_')

    delays = [0, 1, 2, 4, 8]

    global_clocks = list(range(MAX_GLOBAL_CLOCKS))
    np.random.shuffle(global_clocks)

    with open('complete_top.tcl', 'w') as f:
        print('place_design -directive Quick', file=f)
        print('source $::env(URAY_UTILS_DIR)/utils.tcl', file=f)

        for idx, global_clock in enumerate(global_clocks):
            bufg_list = [
                bufg for bufg in bufgs.bufgs[global_clock]
                if bufg.startswith('BUFGCE_X')
            ]
            bufg_list.sort()
            np.random.shuffle(bufg_list)

            bufg = bufg_list.pop()

            loc, column_direction = clock_column.pop()
            print('# {} {}'.format(loc, column_direction), file=f)

            gridinfo = grid.gridinfo_at_loc(loc)

            coords = []

            for site in gridinfo.sites.keys():
                x, y = bufg_leaf(site)
                coords.append((x, y))

            coords.sort()
            y_min = coords[0][1]

            buf_leafs = []
            for site in gridinfo.sites.keys():
                _, y = bufg_leaf(site)

                if y - y_min < 2 and column_direction > 0:
                    buf_leafs.append(site)

                if y - y_min >= 2 and column_direction < 0:
                    buf_leafs.append(site)

            buf_leafs.sort()
            np.random.shuffle(buf_leafs)

            bufce_leaf = buf_leafs.pop()

            slices = list(leafs[loc, column_direction])
            slices.sort()
            np.random.shuffle(slices)

            slice_site = slices.pop()

            delay = np.random.choice(delays)

            print(
                "create_leaf_delay {idx} {delay} {bufgce_site} {bufce_leaf_site} {slice_site}"
                .format(
                    idx=idx,
                    delay=delay,
                    bufgce_site=bufg,
                    bufce_leaf_site=bufce_leaf,
                    slice_site=slice_site,
                ),
                file=f)

        print('route_design -directive Quick', file=f)

        print('set_property IS_ENABLED 0 [get_drc_checks {RTRES-2}]', file=f)
