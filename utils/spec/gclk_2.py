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
from utils.db import Database


def gen_bufgs():

    bufgces_by_tile = {}
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()
    for tile in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile)
        gridinfo = grid.gridinfo_at_loc(loc)

        for site, site_type in gridinfo.sites.items():
            if ("BUFGCE" in site or "BUFGCTRL" in site) and "HDIO" not in site:
                if tile not in bufgces_by_tile:
                    bufgces_by_tile[tile] = []

                bufgces_by_tile[tile].append((site, site_type))

    return bufgces_by_tile


def print_top(seed, f=sys.stdout):
    np.random.seed(seed)

    bufgces_by_tile = gen_bufgs()

    buffers = []

    tiles = list(sorted(bufgces_by_tile.keys()))
    np.random.shuffle(tiles)

    for tile in tiles:
        shuffled_bufs = list(bufgces_by_tile[tile])
        np.random.shuffle(shuffled_bufs)
        target_type = np.random.choice(
            ["BUFGCE", "BUFGCE_DIV", "BUFGCTRL"]
            if len(buffers) > 0 else ["BUFGCE", "BUFGCE_DIV"])
        tile_buffers = np.random.randint(8)
        found_buffers = 0
        for buf, buftype in shuffled_bufs:
            if found_buffers >= tile_buffers:
                break
            if buftype != target_type:
                continue
            buffers.append((buf, buftype))
            found_buffers += 1

    def random_inversion(pins):
        return ", ".join(
            [".IS_%s_INVERTED(%d)" % (p, np.random.randint(2)) for p in pins])

    def random_control(pins):
        return ", ".join(
            [".%s(aux[%d])" % (p, np.random.randint(10)) for p in pins])

    print("module top(input i, input [9:0] aux, d, output o, q);", file=f)
    N = len(buffers)
    print("    wire [%d:0] r;" % N, file=f)
    print("    assign r[0] = i;", file=f)
    print("    assign o = r[%d];" % N, file=f)
    print("    wire [%d:0] r2;" % (2 * N), file=f)
    print("    assign r2[0] = d;", file=f)
    print("    assign q = r2[%d];" % (2 * N), file=f)
    for i in range(N):
        bg, buftype = buffers[i]
        print("(* LOC=\"%s\" *)" % bg, file=f)
        if "BUFGCTRL" in buftype:
            print("    BUFGCTRL #(", file=f)
            print(
                "        %s," % random_inversion([
                    "I0", "I1", "S0", "S1", "CE0", "CE1", "IGNORE0", "IGNORE1"
                ]),
                file=f)
            print(
                "        .INIT_OUT(%d), .PRESELECT_I0(\"%s\"), .PRESELECT_I1(\"%s\")"
                % (np.random.randint(2), np.random.choice(["TRUE", "FALSE"]),
                   np.random.choice(["TRUE", "FALSE"])),
                file=f)
            print("    ) bufgctrl_%d (" % i, file=f)
            #print(
            #    "        .I0(r[%d]), .I1(r[%d]), " %
            #    (i, np.random.randint(i + 1)),
            #    file=f)
            print(
                "        %s," % random_control(
                    ["S0", "S1", "CE0", "CE1", "IGNORE0", "IGNORE1"]),
                file=f)
            print("        .O(r[%d])" % (i + 1), file=f)
            print("    );", file=f)
        elif "DIV" in buftype:
            print("    BUFGCE_DIV #(", file=f)
            print(
                "        .BUFGCE_DIVIDE(%d)," % np.random.randint(1, 9),
                file=f)
            print("        %s" % random_inversion(["I", "CE", "CLR"]), file=f)
            print("    ) bufgce_div_%d (" % i, file=f)
            #print("        .I(r[%d])," % i, file=f)
            print("        %s," % random_control(["CE", "CLR"]), file=f)
            print("        .O(r[%d])" % (i + 1), file=f)
            print("    );", file=f)
        else:
            print("    BUFGCE #(", file=f)
            print(
                "        .CE_TYPE(\"%s\")," % np.random.choice(
                    ["SYNC", "ASYNC"]),
                file=f)
            print("        %s" % random_inversion(["I", "CE"]), file=f)
            print("    ) bufgce_div_%d (" % i, file=f)
            #print("        .I(r[%d])," % i, file=f)
            print("        %s," % random_control(["CE"]), file=f)
            print("        .O(r[%d])" % (i + 1), file=f)
            print("    );", file=f)

        if np.random.randint(2) == 1:
            print(
                "FDCE ff_%d(.C(r[%d]), .CE(1'b1), .CLR(1'b0), .D(r2[%d]), .Q(r2[%d]));"
                % (i, i, 2 * i, 2 * i + 1),
                file=f)
        else:
            print("assign r2[%d] = r2[%d];" % (2 * i + 1, 2 * i), file=f)

        if np.random.randint(2) == 1:
            print(
                "SRLC32E srl_%d(.CLK(r[%d]), .CE(1'b1), .A(aux[4:0]), .D(r2[%d]), .Q(r2[%d]));"
                % (i, i, 2 * i + 1, 2 * i + 2),
                file=f)
        else:
            print("assign r2[%d] = r2[%d];" % (2 * i + 2, 2 * i + 1), file=f)

        print("", file=f)
    print("endmodule", file=f)

    with open('top.tcl', 'w') as f:
        print('set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets]', file=f)
        print('opt_design', file=f)
