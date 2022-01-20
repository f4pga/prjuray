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

import os
from utils import util
from prjuray.db import Database


def read_allowed_sites():
    l = []
    with open(os.path.join('../general_purpose_io_sites.txt')) as f:
        for line in f:
            l.append(line.strip())
    return l


def gen_sites(tile_type):
    o = {}

    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()

    allowed_sites = read_allowed_sites()

    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)

        if gridinfo.tile_type != tile_type:
            continue

        for site_name, site_type in gridinfo.sites.items():
            if site_type in ['HPIOB_S', 'HPIOB_M', 'HDIOB_S', 'HDIOB_M'
                             ] and site_name in allowed_sites:
                if tile_name not in o:
                    o[tile_name] = []

                o[tile_name].append(site_name)

    for tile_name in o:
        o[tile_name].sort(key=util.create_xy_fun('IOB_'))

    return o


def write_params(params):
    pinstr = 'tile,val,site,pin\n'
    for (tile, site, val, pin) in sorted(params):
        pinstr += '%s,%s,%s,%s\n' % (tile, val, site, pin)
    open('params.csv', 'w').write(pinstr)


def run(tile_type):
    sites_by_tile = gen_sites(tile_type)

    print('''
`define N_DI {}

module top(input wire [`N_DI-1:0] di);
    wire [`N_DI-1:0] di_buf;
    '''.format(len(sites_by_tile)))

    params = []
    print('''
        (* KEEP, DONT_TOUCH *)
        LUT6 dummy_lut();''')

    for idx, (tile_name, isone) in enumerate(
            zip(
                sorted(sites_by_tile.keys()),
                util.gen_fuzz_states(len(sites_by_tile)))):
        site_name = sites_by_tile[tile_name][0]
        params.append((tile_name, site_name, isone, "di[%u]" % idx))

        print('''
        (* KEEP, DONT_TOUCH, LOC="{site_name}" *)
        IBUF #(
        ) ibuf_{site_name} (
            .I(di[{idx}]),
            .O(di_buf[{idx}])
            );'''.format(site_name=site_name, idx=idx))

        if isone:
            print('''
        (* KEEP, DONT_TOUCH *)
        PULLUP #(
        ) pullup_{site_name} (
            .O(di[{idx}])
            );'''.format(site_name=site_name, idx=idx))

    print("endmodule")
    write_params(params)
