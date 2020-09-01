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

import os
import random
random.seed(int(os.getenv("SEED"), 16))
from utils import util
from prjuray.db import Database


def gen_sites():
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()

    xy_fun = util.create_xy_fun('BITSLICE_RX_TX_')

    o = {}
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)

        for site_name, site_type in gridinfo.sites.items():
            if site_type == 'BITSLICE_RX_TX':
                if tile_name not in o:
                    o[tile_name] = []

                o[tile_name].append(site_name)

        if tile_name in o:
            o[tile_name].sort(key=lambda site: xy_fun(site))

    return o


def write_params(params):
    pinstr = 'tile,val\n'
    for tile, val in params:
        pinstr += '%s,%s\n' % (tile, val)
    open('params.csv', 'w').write(pinstr)


def run():
    sites_by_tile = gen_sites()

    print('''
module top(output [{number_outputs}-1:0] out);
    wire o;

    (* KEEP, DONT_TOUCH *)
    LUT6 #(.INIT(0) ) lut (
        .I0(1),
        .I1(1),
        .I2(1),
        .I3(1),
        .I4(1),
        .I5(1),
        .O(o)
        );
        '''.format(number_outputs=len(sites_by_tile)))

    itr = iter(util.gen_fuzz_states(len(sites_by_tile)))

    if os.environ['URAY_ARCH'] == "UltraScalePlus":
        device = "ULTRASCALE_PLUS"
    elif os.environ['URAY_ARCH'] == "UltraScale":
        device = "ULTRASCALE"
    else:
        assert False, device

    params = []
    for idx, (tile, isone) in enumerate(
            zip(sorted(sites_by_tile.keys()), itr)):
        params.append((tile, isone))
        print("""
        (* KEEP, DONT_TOUCH, LOC="{loc}" *)
        TX_BITSLICE #(
            .INIT({isone}),
            .SIM_DEVICE("{device}")
        ) tx_{idx} (
            .O(out[{idx}])
        );
        """.format(
            loc=sites_by_tile[tile][0], isone=isone, device=device, idx=idx))

    print('endmodule')

    write_params(params)


if __name__ == '__main__':
    run()
