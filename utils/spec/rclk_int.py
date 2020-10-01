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

import numpy as np

from utils import util
from utils.verilog import top_harness_clk
from prjuray.db import Database


def gen_bufgs():
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)

        for site, site_type in gridinfo.sites.items():
            if "BUFGCE" in site and "HDIO" not in site:
                yield site


def print_top(seed):
    np.random.seed(seed)
    DCLK_N = 10
    DIN_N = (16 * 1 + 1)
    DOUT_N = 1
    top_harness_clk(DCLK_N, DIN_N, DOUT_N)

    N = 5000
    bufgces = list(gen_bufgs())

    print(
        "module layer_1(input [31:0] clk, input [71:0] cen, input d, output q);"
    )
    print("    wire [%d:0] r;" % N)
    print("    assign r[0] = d;")
    print("    assign q = r[%d];" % N)
    print()
    for i in range(N):
        print(
            "    FDCE ff_%d (.C(clk[%d]), .CLR(1'b0), .CE(cen[%d]), .D(r[%d]), .Q(r[%d]));"
            % (i, (i * 32) // N, np.random.randint(72), i, i + 1))
        print()
    print("endmodule")

    M = 16

    print("""
        module roi(input [{DCLK_N}-1:0] clk, input [{DIN_N}-1:0] din, output [{DOUT_N}:0] dout);

        wire [15:0] cen;
        wire d;
        wire q;

        assign cen = din[0+:16];
        assign d = din[16+:1];
        assign dout = q;

        """.format(DCLK_N=DCLK_N, DIN_N=DIN_N, DOUT_N=DOUT_N))

    print("    wire [511:0] clk_int;")
    print("    wire [71:0] cen_int;")
    print("    assign clk_int[9:0] = clk;")
    print("    assign clk_int[15:10] = clk;")
    print("    assign cen_int[15:0] = cen;")
    print("    assign cen_int[71:64] = 8'hFF;")

    for i in range(16, 512):
        a = np.random.randint(16)
        b = None
        while b is None or b == a:
            b = np.random.randint(16)
        c = None
        while c is None or c == a or c == b:
            c = np.random.randint(16)
        bg = None
        if len(bufgces) > 0:
            bg = bufgces.pop()
        if bg is not None and np.random.randint(3) > 0:
            if "DIV" in bg:
                print(
                    "    BUFGCE_DIV #(.BUFGCE_DIVIDE(3)) bufg_%d (.I(clk[%d] ^ clk[%d] ^ clk[%d]), .CLR(0), .CE(1'b1), .O(clk_int[%d]));"
                    % (i, a, b, c, i))
            else:
                print(
                    "    BUFGCE bufg_%d (.I(clk[%d] ^ clk[%d] ^ clk[%d]), .CE(1'b1), .O(clk_int[%d]));"
                    % (i, a, b, c, i))
        else:
            print("    assign clk_int[%d] = clk[%d] ^ clk[%d] ^ clk[%d];" %
                  (i, a, b, c))
        if i < 64:
            print("    assign cen_int[%d] = cen[%d] ^ cen[%d];" % (i, a, b))
    print()
    print("    wire [%d:0] r;" % M)
    print("    assign r[0] = d;")
    print("    assign q = r[%d];" % M)
    for i in range(M):
        print(
            "    layer_1 submod_%d(.clk(clk_int[%d +: 32]), .cen(cen_int), .d(r[%d]), .q(r[%d]));"
            % (i, 32 * i, i, i + 1))
    print("endmodule")
