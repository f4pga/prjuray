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
import sys

from utils import util
from utils.verilog import top_harness_clk
from utils.db import Database


def gen_sites():
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()

    bufgces = []
    slices = []

    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)

        for site, site_type in gridinfo.sites.items():
            if "BUFGCE" in site and "HDIO" not in site:
                bufgces.append(site)

            if "SLICEM" in site or "SLICEL" in site:
                slices.append(site)

    return bufgces, slices


def print_top(seed, f=sys.stdout):
    np.random.seed(seed)

    DCLK_N = 10
    DIN_N = (40 * 1 + 1)
    DOUT_N = 1
    top_harness_clk(DCLK_N, DIN_N, DOUT_N)

    bufgces, slices = gen_sites()
    orig_bufgces = list(bufgces)
    np.random.shuffle(bufgces)
    np.random.shuffle(slices)

    bufg_prob = np.random.randint(15, 20)

    N = 256
    M = 16
    for m in range(M):
        print(
            "module layer_1_%d(input [31:0] clk, input [71:0] cen, input d, output q);"
            % m,
            file=f)
        print("    wire [%d:0] r;" % N, file=f)
        print("    assign r[0] = d;", file=f)
        print("    assign q = r[%d];" % N, file=f)
        print("", file=f)
        for i in range(N):
            if N == 0 and len(slices) > 0:
                loc = slices.pop()
                print("(* LOC=\"%s\" *)" % loc, file=f)
            print(
                "    FDCE ff_%d (.C(clk[%d]), .CLR(1'b0), .CE(cen[%d]), .D(r[%d]), .Q(r[%d]));"
                % (i, (i * 32) // N, np.random.randint(72), i, i + 1),
                file=f)
        print("endmodule", file=f)

    print("""
        module roi(input [{DCLK_N}-1:0] clk, input [{DIN_N}-1:0] din, output [{DOUT_N}:0] dout);

        wire [39:0] cen;
        wire d;
        wire q;

        assign cen = din[0+:40];
        assign d = din[40+:1];
        assign dout = q;

        """.format(DCLK_N=DCLK_N, DIN_N=DIN_N, DOUT_N=DOUT_N))

    num_inputs = np.random.randint(8, 40)
    print("    wire [511:0] clk_int;", file=f)
    print("    wire [71:0] cen_int;", file=f)

    for start_idx in range(0, num_inputs, DCLK_N):
        end_idx = min(start_idx + DCLK_N, num_inputs) - 1
        end_clk_idx = min(DCLK_N, num_inputs - start_idx) - 1
        print(
            "    assign clk_int[{end_idx}:{start_idx}] = clk[{end_clk_idx}:0];"
            .format(
                start_idx=start_idx, end_idx=end_idx, end_clk_idx=end_clk_idx),
            file=f)

    print("    assign cen_int[%d:0] = cen;" % (num_inputs - 1), file=f)
    print("    assign cen_int[71:64] = 8'hFF;", file=f)

    bufgces = list(orig_bufgces)
    np.random.shuffle(bufgces)

    for i in range(num_inputs, 512):
        a = np.random.randint(num_inputs)
        b = None
        while b is None or b == a:
            b = np.random.randint(num_inputs)
        c = None
        while c is None or c == a or c == b:
            c = np.random.randint(num_inputs)
        bg = None
        if len(bufgces) > 0:
            bg = bufgces.pop()
        if bg is not None and np.random.randint(20) >= bufg_prob or (
                bg is not None and "DIV" in bg
                and np.random.randint(19) >= bufg_prob):
            if "DIV" in bg:
                print(
                    "    BUFGCE_DIV #(.BUFGCE_DIVIDE(%d), .IS_I_INVERTED(%d), .IS_CE_INVERTED(%d), .IS_CLR_INVERTED(%d)) bufg_%d (.I(clk[%d] ^ clk[%d] ^ clk[%d]), .CLR(!cen[%d]), .CE(cen[%d]), .O(clk_int[%d]));"
                    % (np.random.randint(1, 9), np.random.randint(2),
                       np.random.randint(2), np.random.randint(2), i, a, b, c,
                       np.random.randint(40), np.random.randint(40), i),
                    file=f)
            else:
                ctype = np.random.choice(["", "_1"])
                params = " #(.IS_I_INVERTED(%d), .IS_CE_INVERTED(%d), .CE_TYPE(\"%s\")) " % (
                    np.random.randint(2), np.random.randint(2),
                    np.random.choice(["SYNC", "ASYNC", "HARD_SYNC"
                                      ])) if ctype == "" else ""
                print(
                    "    BUFGCE%s %s bufg_%d (.I(clk[%d] ^ clk[%d] ^ clk[%d]), .CE(cen[%d]), .O(clk_int[%d]));"
                    % (ctype, params, i, a, b, c, np.random.randint(40), i),
                    file=f)
        else:
            print(
                "    assign clk_int[%d] = clk[%d] ^ clk[%d] ^ clk[%d];" %
                (i, a, b, c),
                file=f)
        if i < 64:
            print(
                "    assign cen_int[%d] = cen[%d] ^ cen[%d];" % (i, a, b),
                file=f)
    print("", file=f)
    print("    wire [%d:0] r;" % M, file=f)
    print("    assign r[0] = d;", file=f)
    print("    assign q = r[%d];" % M, file=f)
    for i in range(M):
        print(
            "    layer_1_%d submod_%d(.clk(clk_int[%d +: 32]), .cen(cen_int), .d(r[%d]), .q(r[%d]));"
            % (i, i, 32 * i, i, i + 1),
            file=f)
    print("endmodule", file=f)
