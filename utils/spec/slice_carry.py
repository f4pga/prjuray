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
import re
import os

from utils import util
from utils.verilog import top_harness_clk
from prjuray.db import Database


def gen_sites():
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()

    tiles = {}
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)

        for site, site_type in gridinfo.sites.items():
            if site_type in ['SLICEM', 'SLICEL']:
                if gridinfo.tile_type not in tiles:
                    tiles[gridinfo.tile_type] = set()

                tiles[gridinfo.tile_type].add(site)

    return tiles


SLICE_XY = re.compile(r'SLICE_X(\d+)Y(\d+)')


def print_top(seed):
    np.random.seed(seed)
    DCLK_N = 10
    DIN_N = (16 * 2 + 8)
    DOUT_N = 32
    top_harness_clk(DCLK_N, DIN_N, DOUT_N)

    print("")
    print("""
        module roi(input [{DCLK_N}-1:0] clk, input [{DIN_N}-1:0] din, output [31:0] dout);

        wire [15:0] sr;
        wire [15:0] ce;
        wire [7:0] d;
        wire [31:0] q;

        assign sr = din[0+:16];
        assign ce = din[16+:16];
        assign d = din[32+:8];

        assign dout = q;
        """.format(DCLK_N=DCLK_N, DIN_N=DIN_N, DOUT_N=DOUT_N))

    N = 200
    D = ["d[%d]" % i for i in range(16)]

    slices = gen_sites()

    for i in range(N):
        tile_type = np.random.choice(sorted(slices.keys()))
        sl = np.random.choice(sorted(slices[tile_type]))
        slices[tile_type].remove(sl)

        m = SLICE_XY.match(sl)
        assert m is not None
        x = int(m.group(1))
        y = int(m.group(2))
        sl_up = 'SLICE_X{}Y{}'.format(x, y + 1)
        if sl_up not in slices[tile_type]:
            sl_up = ''

        ffmode = np.random.randint(3, size=2)
        clk = tuple(np.random.randint(DCLK_N, size=2))
        sr = tuple([
            "1'b1" if y >= 16 else "sr[%d]" % y
            for y in np.random.randint(25, size=2)
        ])
        ce = tuple([
            "1'b1" if y >= 16 else "ce[%d]" % y
            for y in np.random.randint(25, size=4)
        ])

        def random_fftype(mode):
            if mode == 0:
                return np.random.choice(["FDSE", "FDRE"])
            elif mode == 1:
                return np.random.choice(["FDPE", "FDCE"])
            elif mode == 2:
                return np.random.choice(["LDPE", "LDCE"])

        def random_bit():
            return np.random.choice(D)

        def random_data(width):
            return "{%s}" % (", ".join([random_bit() for k in range(width)]))

        fftypes = [random_fftype(ffmode[j // 8]) for j in range(16)]
        used_outroute = [
            np.random.choice(["FF", "FF2", "MUX"]) for k in range(8)
        ]
        for j in range(8):
            if used_outroute[j] == "FF":
                fftypes[2 * j + 1] = "NONE"
            elif used_outroute[j] == "FF2":
                fftypes[2 * j] = "NONE"
            else:
                fftypes[2 * j] = "NONE"
                fftypes[2 * j + 1] = "NONE"
        cmode = np.random.choice(["NONE", "SINGLE_CY8", "DUAL_CY4"],
                                 p=[0.1, 0.7, 0.2])
        carry_used = False

        if cmode == "SINGLE_CY8" and sl_up:
            if np.random.randint(2):
                carry_used = True
                slices[tile_type].remove(sl_up)
            else:
                sl_up = ''

        print('   wire [31:0] d%d;' % i)
        print('   ultra_slice_carry #(')
        print('      .LOC("%s"),' % sl)
        print('      .LOC2("%s"),' % sl_up)
        print('      .CARRY_USED(%d),' % carry_used)
        for lut in "ABCDEFGH":
            print("      .%sLUT_INIT(64'b%s)," % (lut, "".join(
                str(_) for _ in np.random.randint(2, size=64))))
        for j in range(16):
            print('      .%sFF%s_TYPE("%s"),' %
                  ("ABCDEFGH" [j // 2], "2" if
                   (j % 2) == 1 else "", fftypes[j]))
        print("      .FF_INIT(16'b%s)," % "".join(
            str(_) for _ in np.random.randint(2, size=16)))
        for j1 in "ABCDEFGH":
            for j2 in ("1", "2"):
                print('        .FFMUX%s%s("%s"),' %
                      (j1, j2,
                       np.random.choice(
                           ["XORIN", "CY"] if cmode != "NONE" else ["D6"])))
        for j in range(8):
            print('        .OUTMUX%s("%s"),' %
                  ("ABCDEFGH" [j],
                   ("D6" if used_outroute[j] != "MUX" else np.random.choice(
                       ["D6", "XORIN", "CY"] if cmode != "NONE" else ["D6"]))))
        print("      .CLKINV(2'd%d)," % np.random.randint(4))
        print("      .SRINV(2'd%d)," % np.random.randint(4))
        print('      .CARRY_TYPE("%s"),' % cmode)
        for j in range(8):
            print('      .DI%dMUX("%s"),' % (j, np.random.choice(["DI", "X"])))
        print('      .CIMUX("%s"),' % np.random.choice(["1", "0", "X"]))
        print('      .CITOPMUX("%s")' % (np.random.choice(["1", "0", "X"])
                                         if cmode == "DUAL_CY4" else "CI"))
        print('   ) slice%d (' % i)
        for j in range(1, 7):
            print("      .A%d(%s)," % (j, random_data(8)))
        print("      .I(%s)," % random_data(8))
        print("      .X(%s)," % random_data(8))
        print("      .CLK({clk[%d], clk[%d]})," % clk)
        print("      .SR({%s, %s})," % sr)
        print("      .CE({%s, %s, %s, %s})," % ce)
        print("      .O(d%d[7:0])," % i)
        print("      .Q(d%d[15:8])," % i)
        print("      .Q2(d%d[23:16])," % i)
        print("      .MUX(d%d[31:24])" % i)
        print('   );')
        print()

        D.clear()
        for j in range(8):
            D.append("d%d[%d]" % (i, j))
            D.append("d%d[%d]" % (i, 24 + j))
            if fftypes[2 * j] != "NONE":
                D.append("d%d[%d]" % (i, 8 + j))
            if fftypes[2 * j + 1] != "NONE":
                D.append("d%d[%d]" % (i, 16 + j))
    print("    assign q = d%d;" % (N - 1))
    print("endmodule")
    print("")

    with open(os.path.join(os.getenv('URAY_DIR'), 'spec',
                           'slice_carry.v')) as f:
        for l in f:
            print(l.rstrip())

    with open('top.tcl', 'w') as f:
        f.write('opt_design')
