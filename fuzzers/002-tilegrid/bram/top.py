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
import random
random.seed(int(os.getenv("SEED"), 16))
from utils import util
from prjuray.db import Database


def gen_sites():
    o = []
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)

        for site_name, site_type in gridinfo.sites.items():
            if site_type in ['RAMBFIFO18']:
                o.append((tile_name, site_name))

    return o


def write_params(params):
    pinstr = 'tile,val,site\n'
    for tile, (site, val) in sorted(params.items()):
        pinstr += '%s,%s,%s\n' % (tile, val, site)
    open('params.csv', 'w').write(pinstr)


def run():
    print('''
module top(input clk, stb, di, output do);
    localparam integer DIN_N = 8;
    localparam integer DOUT_N = 8;

    reg [DIN_N-1:0] din;
    wire [DOUT_N-1:0] dout;

    reg [DIN_N-1:0] din_shr;
    reg [DOUT_N-1:0] dout_shr;

    always @(posedge clk) begin
        din_shr <= {din_shr, di};
        dout_shr <= {dout_shr, din_shr[DIN_N-1]};
        if (stb) begin
            din <= din_shr;
            dout_shr <= dout;
        end
    end

    assign do = dout_shr[DOUT_N-1];
    ''')

    params = {}

    sites = list(gen_sites())
    for (tile_name, site_name), isone in zip(sites,
                                             util.gen_fuzz_states(len(sites))):
        params[tile_name] = (site_name, isone)

        print('''
            (* KEEP, DONT_TOUCH, LOC = "%s" *)
            RAMB18E2 #(
                    .DOA_REG(%u)
                ) bram_%s (
                    .CLKARDCLK(),
                    .CLKBWRCLK(),
                    .ENARDEN(),
                    .ENBWREN(),
                    .REGCEAREGCE(),
                    .REGCEB(),
                    .RSTRAMARSTRAM(),
                    .RSTRAMB(),
                    .RSTREGARSTREG(),
                    .RSTREGB(),
                    .ADDRARDADDR(),
                    .ADDRBWRADDR(),
                    .DINADIN(),
                    .DINBDIN(),
                    .DINPADINP(),
                    .WEA(),
                    .WEBWE(),
                    .DOUTADOUT(),
                    .DOUTBDOUT(),
                    .DOUTPADOUTP(),
                    .DOUTPBDOUTP());
''' % (site_name, isone, site_name))

    print("endmodule")
    write_params(params)


if __name__ == '__main__':
    run()
