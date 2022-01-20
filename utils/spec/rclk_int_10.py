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

import csv
import numpy as np
from utils import util
from utils.clock_utils import make_bufg, MAX_GLOBAL_CLOCKS
from prjuray.db import Database

CMT_XY_FUN = util.create_xy_fun('')


def print_top(seed):
    np.random.seed(seed)

    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()

    site_to_tile = {}
    site_to_site_type = {}
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)

        for site, site_type in gridinfo.sites.items():
            site_to_site_type[site] = site_type
            site_to_tile[site] = tile_name

    bufce_row_drivers = {}

    with open('../active_bufce_row.csv') as f:
        for row in csv.DictReader(f):
            tile = site_to_tile[row['site']]

            gridinfo = grid.gridinfo_at_tilename(tile)
            if gridinfo.tile_type == 'CMT_RIGHT':
                continue

            clock_region = CMT_XY_FUN(row['site_clock_region'])

            key = clock_region, int(row['hdistr_number'])
            assert key not in bufce_row_drivers
            bufce_row_drivers[key] = row['site']

    bufg_drivers = {}

    with open('../bufg_outputs.csv') as f:
        for row in csv.DictReader(f):
            if row['hroute_output'] == 'all':
                continue

            clock_region = CMT_XY_FUN(row['clock_region'])

            key = clock_region, int(row['hroute_output'])
            assert key not in bufg_drivers
            bufg_drivers[key] = row['site']

    clock_regions = set()
    for clock_region, _ in bufce_row_drivers.keys():
        clock_regions.add(clock_region)

    for clock_region, _ in bufg_drivers.keys():
        clock_regions.add(clock_region)

    print("""
module top();
        """)

    for hroute in range(MAX_GLOBAL_CLOCKS):
        if np.random.randint(2):
            continue

        select_clock_regions = sorted(clock_regions)
        np.random.shuffle(select_clock_regions)

        bufg = None
        while True:
            clock_region = select_clock_regions.pop()
            key = clock_region, hroute

            if key in bufg_drivers:
                bufg = bufg_drivers[key]
                break

        if bufg is None:
            continue

        sel_x, sel_y = clock_region
        clock_regions_for_bufg = []
        for x, y in clock_regions:
            if y == sel_y:
                clock_regions_for_bufg.append((x, y))

        clock_regions_for_bufg.sort()
        np.random.shuffle(clock_regions_for_bufg)

        bufce_row = None
        while True:
            clock_region = clock_regions_for_bufg.pop()
            key = clock_region, hroute

            if key in bufce_row_drivers:
                bufce_row = bufce_row_drivers[key]
                break

        if bufce_row is None:
            continue

        bufg_s, bufg_o_wire = make_bufg(
            site=bufg,
            site_type=site_to_site_type[bufg],
            idx=hroute,
            ce_inputs=['1'],
            randlib=np.random)

        print(bufg_s)

        print("""
        (* LOC="{loc}", KEEP, DONT_TOUCH *) BUFCE_ROW row{idx} (
            .I({bufg_o_wire})
        );""".format(
            loc=bufce_row,
            idx=hroute,
            bufg_o_wire=bufg_o_wire,
        ))

    print('endmodule')

    with open('complete_top.tcl', 'w') as f:
        print(
            """
write_checkpoint -force design_reset.dcp
close_design
open_checkpoint design_reset.dcp
route_design
""",
            file=f)
