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

import numpy as np

from utils import util
from utils.clock_utils import ClockColumns, GlobalClockBuffers, MAX_GLOBAL_CLOCKS, make_bufg
from prjuray.db import Database


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

    clocks = ClockColumns(grid)

    disabled_columns = set()
    for key in clocks.columns():
        if np.random.choice([1, 0], p=[.25, .75]):
            disabled_columns.add(key)

    clocks.remove_column(disabled_columns)

    site_to_site_type = {}
    site_to_tile = {}
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)

        for site, site_type in gridinfo.sites.items():
            site_to_site_type[site] = site_type
            site_to_tile[site] = tile_name

    bufgs = GlobalClockBuffers('../bufg_outputs.csv')

    slices = sorted(gen_sites(grid))
    np.random.shuffle(slices)

    with open('complete_top.tcl', 'w') as f:
        print(
            """
set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets]
place_design
route_design
""",
            file=f)

    print("""
module top();
        """)

    N_LUTS = 4

    ce_inputs = [0, 1]
    for idx in range(N_LUTS):

        print("""
        wire lut_o_{idx};
        (* BEL="A6LUT", LOC="{loc}", KEEP, DONT_TOUCH *) LUT5 lut{idx} (.O(lut_o_{idx}));
        """.format(idx=idx, loc=slices.pop()))

        ce_inputs.append('lut_o_{}'.format(idx))

    N_GCLK = np.random.randint(1, MAX_GLOBAL_CLOCKS)
    assert N_GCLK <= MAX_GLOBAL_CLOCKS
    assert N_GCLK >= 1
    bufg_wires = {}
    bufg_str = {}
    for idx in range(N_GCLK):
        bufg, hroute_number = bufgs.random_bufg(np.random.choice)

        site_type = site_to_site_type[bufg]
        bufg_str[hroute_number], bufg_wires[hroute_number] = make_bufg(
            bufg, site_type, idx, ce_inputs, np.random)

    bufg_used = set()
    slices = sorted(clocks.sites.keys())

    num_slices = np.random.randint(1, len(slices) + 1)

    for idx, slice_loc in enumerate(slices):
        if idx >= num_slices:
            break

        all_clocks = list(bufg_wires.keys())
        np.random.shuffle(all_clocks)
        while True:
            hroute_number = all_clocks.pop()
            clock_str = bufg_wires[hroute_number]
            if clocks.add_clock(slice_loc, clock_str):
                if hroute_number not in bufg_used:
                    print(bufg_str[hroute_number])
                    bufg_used.add(hroute_number)

                print(
                    '    (* LOC="{loc}", KEEP, DONT_TOUCH *) FDCE ff_{i}(.C({clock_str}));'
                    .format(loc=slice_loc, i=idx, clock_str=clock_str))
                break

    print('endmodule')
