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

import csv
import numpy as np
from utils import util
from utils.clock_utils import make_bufg, MAX_GLOBAL_CLOCKS
from utils.db import Database

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

    bufce_leaf_drivers = {}
    with open('../bufce_leaf_clock_regions.csv') as f:
        for row in csv.DictReader(f):
            clock_region = CMT_XY_FUN(row['clock_region'])

            if clock_region not in bufce_leaf_drivers:
                bufce_leaf_drivers[clock_region] = []

            bufce_leaf_drivers[clock_region].append(row['site'])

    for clock_region in bufce_leaf_drivers:
        bufce_leaf_drivers[clock_region].sort()
        np.random.shuffle(bufce_leaf_drivers[clock_region])

    bufg_drivers = {}
    with open('../bufg_outputs.csv') as f:
        for row in csv.DictReader(f):
            if site_to_site_type[row['site']] != 'BUFGCE_HDIO':
                continue

            clock_region = CMT_XY_FUN(row['clock_region'])
            if clock_region not in bufg_drivers:
                bufg_drivers[clock_region] = []

            bufg_drivers[clock_region].append(row['site'])

    for clock_region in bufg_drivers:
        bufg_drivers[clock_region].sort()
        np.random.shuffle(bufg_drivers[clock_region])

    clock_regions = set()
    for clock_region in bufg_drivers.keys():
        clock_regions.add(clock_region)

    print("""
module top();
        """)

    pair_idx = 0

    bufg_hdistr_sets = []
    for clock_region in bufg_drivers.keys():
        hdistrs_avail = list(range(MAX_GLOBAL_CLOCKS))
        np.random.shuffle(hdistrs_avail)

        for bufg in bufg_drivers[clock_region]:
            hdistr = hdistrs_avail.pop()

            bufg_s, bufg_o_wire = make_bufg(
                site=bufg,
                site_type=site_to_site_type[bufg],
                idx=pair_idx,
                ce_inputs=['1'],
                randlib=np.random)

            print(bufg_s)

            bufce_leaf = bufce_leaf_drivers[clock_region].pop()
            print("""
            (* LOC="{loc}", KEEP, DONT_TOUCH *) BUFCE_LEAF bufce_leaf_{idx} (
                .I({clock_in})
            );""".format(loc=bufce_leaf, idx=pair_idx, clock_in=bufg_o_wire))

            bufg_hdistr_sets.append((bufg, bufce_leaf, hdistr))
            pair_idx += 1

    print('endmodule')

    with open('complete_top.tcl', 'w') as f:
        print(
            """
source $::env(URAY_UTILS_DIR)/utils.tcl
write_checkpoint -force design_reset.dcp
close_design
open_checkpoint design_reset.dcp
""",
            file=f)

        for (bufg, bufce_leaf, hdistr) in bufg_hdistr_sets:
            print(
                'route_bufg_to_bufce_leaf {bufg} {bufce_leaf} {hdistr}'.format(
                    bufg=bufg, bufce_leaf=bufce_leaf, hdistr=hdistr),
                file=f)

        print("""
route_design
""", file=f)
