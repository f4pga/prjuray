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
import os.path
import numpy as np
from utils import util
from utils.verilog import top_harness_clk
from utils.db import Database


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

    N = 100
    D = ["d[%d]" % i for i in range(8)]

    slices = gen_sites()

    for i in range(N):
        tile_type = np.random.choice(sorted(slices.keys()))
        sl = np.random.choice(sorted(slices[tile_type]))
        slices[tile_type].remove(sl)

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
                return np.random.choice(["NONE", "FDSE", "FDRE"])
            elif mode == 1:
                return np.random.choice(["NONE", "FDPE", "FDCE"])
            elif mode == 2:
                return np.random.choice(["NONE", "LDPE", "LDCE"])

        def random_bit():
            return np.random.choice(D)

        def random_data(width):
            return "{%s}" % (", ".join([random_bit() for k in range(width)]))

        fftypes = [random_fftype(ffmode[j // 8]) for j in range(16)]

        print('   wire [31:0] d%d;' % i)
        print('   ultra_slice_logic #(')
        print('      .LOC("%s"),' % sl)
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
                      (j1, j2, np.random.choice(["F7F8", "D6", "D5", "BYP"])))
        for j in "ABCDEFGH":
            print('        .OUTMUX%s("%s"),' %
                  (j, np.random.choice(["F7F8", "D6", "D5"])))
        print("      .CLKINV(2'd%d)," % np.random.randint(4))
        print("      .SRINV(2'd%d)" % np.random.randint(4))
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

    with open(os.path.join(os.getenv('URAY_DIR'), 'spec', 'slice.v')) as f:
        for l in f:
            print(l.rstrip())
