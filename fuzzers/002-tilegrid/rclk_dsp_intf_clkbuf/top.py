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


def get_random_leaf(gridinfo):
    leafs = []

    for site, site_type in gridinfo.sites.items():
        if site_type == 'BUFCE_LEAF':
            leafs.append(site)

    leafs.sort()

    return random.choice(leafs)


def gen_sites():
    """ RCLK_DSP_INTF_CLKBUF_L connects HDISTR and HROUTE clock resources from
    neighbooring left/right clock regions.

    gen_sites finds RCLK_DSP_INTF_CLKBUF_L tiles, and then locates a BUFCE_ROW
    driver from the left side, and then finds a BUFCE_ROW driver from the
    right side that drives the same HDISTR.  A BUFCE_ROW only drives a
    particular HDISTR node within the clock region (0-23).

    A random BUFCE_LEAF from both the left and the right of
    RCLK_DSP_INTF_CLKBUF_L are chosen.  This randomness decouples
    non-RCLK_DSP_INTF_CLKBUF_L bits from the solution.
    """
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()

    # Create a mapping from site to tile
    site_to_tile = {}
    for tile_name in grid.tiles():
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)
        for site in gridinfo.sites:
            site_to_tile[site] = tile_name

    # Load BUFCE_ROW site data, which includes:
    # - The BUFCE_ROW site name
    # - The clock region the BUFCE_ROW participates in
    # - Which HDISTR wire is driven by the BUFCE_ROW.
    loc_to_bufce_row = {}
    with open('../active_bufce_row.csv') as f:
        for bufce_row in csv.DictReader(f):
            site = bufce_row['site']
            tile = site_to_tile[site]
            loc = grid.loc_of_tilename(tile)

            if loc not in loc_to_bufce_row:
                loc_to_bufce_row[loc] = []

            loc_to_bufce_row[loc].append(bufce_row)

    o = []
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)

        if gridinfo.tile_type != "RCLK_DSP_INTF_CLKBUF_L":
            continue

        # Find a BUFCE_ROW driver that is left of the current
        # RCLK_DSP_INTF_CLKBUF_L tile.
        x, y = loc
        left_bufce_out = None
        hdistr_number = None
        while left_bufce_out is None:
            x -= 1
            if (x, y) in loc_to_bufce_row:
                left_bufce_out = loc_to_bufce_row[(x, y)][0]['site']
                hdistr_number = loc_to_bufce_row[(x, y)][0]['hdistr_number']
                break

        # Find a BUFCE_ROW driver that is right of the current
        # RCLK_DSP_INTF_CLKBUF_L tile, and is on the same HDISTR wire.
        x, y = loc
        right_bufce_out = None
        while right_bufce_out is None:
            x += 1
            if (x, y) in loc_to_bufce_row:
                for bufce_row in loc_to_bufce_row[(x, y)]:
                    if hdistr_number == bufce_row['hdistr_number']:
                        right_bufce_out = bufce_row['site']
                        break

        # Find a random BUFCE_LEAF driver that is to the left of the current
        # RCLK_DSP_INTF_CLKBUF_L.
        x, y = loc
        left_site = None
        while left_site is None:
            x -= 1

            gridinfo = grid.gridinfo_at_loc((x, y))
            for site, site_type in gridinfo.sites.items():
                if site_type == 'BUFCE_LEAF':
                    left_site = get_random_leaf(gridinfo)
                    break

        # Find a random BUFCE_LEAF driver that is to the right of the current
        # RCLK_DSP_INTF_CLKBUF_L.
        x, y = loc
        right_site = None
        while right_site is None:
            x += 1

            gridinfo = grid.gridinfo_at_loc((x, y))
            for site, site_type in gridinfo.sites.items():
                if site_type == 'BUFCE_LEAF':
                    right_site = get_random_leaf(gridinfo)
                    break

        assert left_bufce_out is not None
        assert right_bufce_out is not None
        assert left_site is not None
        assert right_site is not None

        o.append((tile_name, left_bufce_out, right_bufce_out, left_site,
                  right_site))

    return o


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

    site_pairs = gen_sites()

    # The placer will not accept BUFCE_LEAF or BUFCE_ROW instances, so create
    # and connect those cells after placement.
    with open('params.csv', 'w') as f:
        print(
            'tile,val,left_bufce_out,right_bufce_out,left_site,right_site',
            file=f)
        for (tile, left_bufce_out, right_bufce_out, left_site,
             right_site), isone in zip(site_pairs,
                                       util.gen_fuzz_states(len(site_pairs))):
            print(
                ','.join((tile, str(isone), left_bufce_out, right_bufce_out,
                          left_site, right_site)),
                file=f)


if __name__ == '__main__':
    run()
