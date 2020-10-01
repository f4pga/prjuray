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
from utils.clock_utils import ClockColumns
from prjuray.db import Database


def gen_bufgs(grid):
    sites_by_tiles = {}
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)

        for site, site_type in gridinfo.sites.items():
            if "BUFGCE" == site_type:
                if tile_name not in sites_by_tiles:
                    sites_by_tiles[tile_name] = []
                sites_by_tiles[tile_name].append(site)

    return sites_by_tiles


def print_top(seed):
    np.random.seed(seed)

    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()

    clocks = ClockColumns(grid)

    disabled_columns = set()
    for key in clocks.columns():
        if np.random.choice([1, 0], p=[.25, .75]):
            disabled_columns.add(key)

    clocks.remove_column(disabled_columns)

    print("""
module top(input clk, stb, di, output do);
        """)

    bufg_by_tile = gen_bufgs(grid)
    tile = np.random.choice(sorted(bufg_by_tile.keys()))
    bufgs = bufg_by_tile[tile]
    assert len(bufgs) > 0
    bufgs.sort()
    np.random.shuffle(bufgs)

    slices = sorted(clocks.sites.keys())
    np.random.shuffle(slices)

    num_bufgs = np.random.randint(1, min(len(bufgs) + 1, 25))
    assert num_bufgs > 0
    print('    wire [{}:0] bufg_clk;'.format(num_bufgs))

    for idx, site in enumerate(bufgs):
        if idx >= num_bufgs:
            break

        print(
            '    (* LOC="{loc}", KEEP, DONT_TOUCH *) BUFGCE bufg_{i} ( .CE(1\'b1), .O(bufg_clk[{i}]) );'
            .format(i=idx, loc=site))

    num_slices = np.random.randint(1, len(slices) + 1)

    for idx, slice_loc in enumerate(slices):
        if idx >= num_slices:
            break

        all_clocks = list(range(0, num_bufgs))
        np.random.shuffle(all_clocks)
        while True:
            clock_str = 'bufg_clk[{}]'.format(all_clocks.pop())

            if clocks.add_clock(slice_loc, clock_str):
                print(
                    '    (* LOC="{loc}", KEEP, DONT_TOUCH *) FDCE ff_{i}(.C({clock_str}));'
                    .format(loc=slice_loc, i=idx, clock_str=clock_str))
                break

    print('endmodule')

    with open('top.tcl', 'w') as f:
        print("set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets]", file=f)
