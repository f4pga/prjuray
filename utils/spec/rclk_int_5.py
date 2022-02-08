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
from prjuray.db import Database
from csv import DictReader
from utils.clock_utils import GlobalClockBuffers, make_bufg


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

    site_to_site_type = {}
    site_to_tile = {}
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)

        for site, site_type in gridinfo.sites.items():
            site_to_site_type[site] = site_type
            site_to_tile[site] = tile_name

    slices = sorted(gen_sites(grid))
    np.random.shuffle(slices)

    with open('../active_bufce_row.csv') as f:
        bufce_rows = [row for row in DictReader(f)]

    np.random.shuffle(bufce_rows)

    with open('../bufce_leaf_clock_regions.csv') as f:
        bufce_leafs = [row for row in DictReader(f)]

    bufgs = GlobalClockBuffers('../bufg_outputs.csv')

    with open('complete_top.tcl', 'w') as f:
        #print('place_design -directive Quick', file=f)
        print(
            """
write_checkpoint -force design_reset.dcp
close_design
open_checkpoint design_reset.dcp
route_design

set route_status [struct::set union [get_property ROUTE_STATUS [get_nets -hierarchical ]] []]

if { [llength $route_status] > 1 } {
    set_property ROUTE "" [get_nets -hierarchical]
    route_design -nets [get_nets bufce_row_out_*]
    route_design -nets [concat [get_nets lut_*] [get_nets -filter "TYPE == POWER || TYPE == GROUND"]]
    route_design
}
""",
            file=f)

    print("""
module top();
        """)

    N_LUTS = 3

    ce_inputs = [0, 1]
    for idx in range(N_LUTS):

        print("""
        wire lut_o_{idx};
        (* BEL="A6LUT", LOC="{loc}", KEEP, DONT_TOUCH *) LUT5 lut{idx} (.O(lut_o_{idx}));
        """.format(idx=idx, loc=slices.pop()))

        ce_inputs.append('lut_o_{}'.format(idx))

    clock_resource_in_use = set()

    bufg_for_hroute = {}
    bufce_rows_by_cmt = {}
    for idx, bufce_row in enumerate(bufce_rows):
        if np.random.choice([0, 1], p=[.75, .25]):
            continue

        clock_region = bufce_row['site_clock_region']
        if clock_region not in bufce_rows_by_cmt:
            bufce_rows_by_cmt[clock_region] = []

        # Don't overuse HDISTR resources!
        key = (bufce_row['site_clock_region'], bufce_row['hdistr_number'])
        if key in clock_resource_in_use:
            continue

        hdistr_number = int(bufce_row['hdistr_number'])
        if hdistr_number not in bufg_for_hroute:
            while True:
                site = np.random.choice(bufgs.bufgs[hdistr_number])
                site_type = site_to_site_type[site]

                if site_type == 'BUFGCE':
                    break

            s, bufg_for_hroute[hdistr_number] = make_bufg(
                site=site,
                site_type=site_type,
                idx=len(bufg_for_hroute),
                ce_inputs=['1'],
                randlib=np.random)

            print(s)

        clock_resource_in_use.add(key)

        bufce_rows_by_cmt[clock_region].append(idx)

        if np.random.choice([0, 1], p=[.9, .1]):
            bufg_in = '1'
            ce_type = 'ASYNC'
        else:
            bufg_in = bufg_for_hroute[hdistr_number]
            ce_type = np.random.choice(["SYNC", "ASYNC"])

        print("""
        wire bufce_row_out_{idx};
        (* LOC="{loc}", KEEP, DONT_TOUCH *) BUFCE_ROW #(
            .IS_I_INVERTED({invert_i}),
            .IS_CE_INVERTED({invert_ce}),
            .CE_TYPE("{ce_type}")
            )
        bufce_row_{idx} (
            .I({bufg_in}),
            .O(bufce_row_out_{idx}),
            .CE({ce})
        );""".format(
            loc=bufce_row['site'],
            invert_i=np.random.randint(2),
            invert_ce=np.random.randint(2),
            ce_type=ce_type,
            ce=np.random.choice(ce_inputs),
            bufg_in=bufg_in,
            idx=idx))

    for idx, bufce_leaf in enumerate(bufce_leafs):
        if np.random.choice([0, 1], p=[.75, .25]):
            continue

        clock_region = bufce_leaf['clock_region']
        if clock_region not in bufce_rows_by_cmt:
            continue

        clock_in_idx = np.random.choice(bufce_rows_by_cmt[clock_region])

        print("""
        (* LOC="{loc}", KEEP, DONT_TOUCH *) BUFCE_LEAF #(
            .IS_I_INVERTED({invert_i}),
            .IS_CE_INVERTED({invert_ce}),
            .CE_TYPE("{ce_type}")
        )
        bufce_leaf_{idx} (
            .I({clock_in}),
            .CE({ce})
        );""".format(
            loc=bufce_leaf['site'],
            invert_i=np.random.randint(2),
            invert_ce=np.random.randint(2),
            ce_type=np.random.choice(["SYNC", "ASYNC"]),
            ce=np.random.choice(ce_inputs),
            idx=idx,
            clock_in='bufce_row_out_{}'.format(clock_in_idx)))

    print('endmodule')
