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


def print_top(seed, f=sys.stdout):
    np.random.seed(seed)

    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()

    bufgces_by_tile = {}
    rclk_int_l = []
    slices_by_tile = {}

    for tile in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile)

        if tile.startswith("RCLK_INT_L"):
            rclk_int_l.append((loc.grid_x, loc.grid_y, tile))

        gridinfo = grid.gridinfo_at_loc(loc)
        for site, site_type in gridinfo.sites.items():
            if ("BUFGCE" in site or "BUFGCTRL" in site) and "HDIO" not in site:
                if tile not in bufgces_by_tile:
                    bufgces_by_tile[tile] = []
                bufgces_by_tile[tile].append((site, site_type))
            elif "SLICE_" in site:
                slices_by_tile[loc.grid_x, loc.grid_y] = site

    halfcolumn_slices_by_row = {}
    for x, y, rclk in rclk_int_l:
        hc_up = []
        hc_down = []
        if y not in halfcolumn_slices_by_row:
            halfcolumn_slices_by_row[y] = []

        for yplus in range(y + 1, y + 31):
            if (x, yplus) not in grid.loc:
                continue

            tile = grid.tilename_at_loc((x, yplus))
            if not tile.startswith("INT_"):
                break

            slice_x = x + np.random.choice([+1, -1])
            if (slice_x, yplus) not in slices_by_tile:
                continue
            hc_up.append(slices_by_tile[slice_x, yplus])

        for yminus in range(y - 1, y - 31, -1):
            if (x, yminus) not in grid.loc:
                continue

            tile = grid.tilename_at_loc((x, yminus))
            if not tile.startswith("INT_"):
                break
            slice_x = x + np.random.choice([+1, -1])
            if (slice_x, yminus) not in slices_by_tile:
                continue
            hc_down.append(slices_by_tile[slice_x, yminus])

        halfcolumn_slices_by_row[y].append(hc_up)
        halfcolumn_slices_by_row[y].append(hc_down)

    buffers = []

    tiles = list(sorted(bufgces_by_tile.keys()))
    np.random.shuffle(tiles)

    for tile in tiles:
        shuffled_bufs = list(bufgces_by_tile[tile])
        np.random.shuffle(shuffled_bufs)
        target_type = np.random.choice(
            ["BUFGCE", "BUFGCE_DIV", "BUFGCTRL"]
            if len(buffers) > 0 else ["BUFGCE", "BUFGCE_DIV"])
        tile_buffers = np.random.randint(6)
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

    CCIO_CLKS = 24
    print(
        "module top(input [{CCIO_CLKS}-1:0] i, input [9:0] aux, input d, output o, q);"
        .format(CCIO_CLKS=CCIO_CLKS),
        file=f)
    print("    wire [71:0] r;", file=f)
    # print("    assign r[0] = i;", file=f)
    # print("    assign o = r[%d];" % N, file=f)
    # for i in range(N):
    # 	bg, buftype = buffers[i]
    # 	#print("(* LOC=\"%s\" *)" % bg, file=f)
    # 	if "BUFGCTRL" in buftype:
    # 		print("    BUFGCTRL #(", file=f)
    # 		print("        %s," % random_inversion(["I0", "I1", "S0", "S1", "CE0", "CE1", "IGNORE0", "IGNORE1"]), file=f)
    # 		print("        .INIT_OUT(%d), .PRESELECT_I0(\"%s\"), .PRESELECT_I1(\"%s\")" %
    # 				(np.random.randint(2), np.random.choice(["TRUE", "FALSE"]), np.random.choice(["TRUE", "FALSE"])), file=f)
    # 		print("    ) bufgctrl_%d (" % i, file=f)
    # 		print("        .I0(r[%d]), .I1(r[%d]), " % (i, np.random.randint(i+1)), file=f)
    # 		print("        %s," % random_control(["S0", "S1", "CE0", "CE1", "IGNORE0", "IGNORE1"]), file=f)
    # 		print("        .O(r[%d])" % (i+1), file=f)
    # 		print("    );", file=f)
    print(
        "    assign r[{CCIO_CLKS}-1:0] = i;".format(CCIO_CLKS=CCIO_CLKS),
        file=f)
    for i in range(12):
        print("    BUFGCE_DIV #(", file=f)
        print("        .BUFGCE_DIVIDE(%d)," % np.random.randint(1, 9), file=f)
        print("        %s" % random_inversion(["I", "CE", "CLR"]), file=f)
        print("    ) bufgce_div_%d (" % i, file=f)
        print("        .I(i[%d])," % i, file=f)
        print("        %s," % random_control(["CE", "CLR"]), file=f)
        print("        .O(r[%d])" % (CCIO_CLKS + i), file=f)
        print("    );", file=f)
    for i in range(12):
        print("    BUFGCE #(", file=f)
        print(
            "        .CE_TYPE(\"%s\")," % np.random.choice(["SYNC", "ASYNC"]),
            file=f)
        print("        %s" % random_inversion(["I", "CE"]), file=f)
        print("    ) bufgce_%d (" % i, file=f)
        print("        .I(i[%d])," % np.random.randint(CCIO_CLKS), file=f)
        print("        %s," % random_control(["CE"]), file=f)
        print("        .O(r[%d])" % (i + 36), file=f)
        print("    );", file=f)

    R2 = 0
    NS = 16
    ffs = ""
    for row, hcs in sorted(halfcolumn_slices_by_row.items()):
        row_clks = np.random.randint(16, 25)
        clks = [np.random.randint(72) for k in range(row_clks)]
        halfs = [hcs[np.random.randint(len(hcs))] for k in range(NS)]
        for h in halfs:
            half_clks = np.random.randint(8, 17)
            rclks = [np.random.choice(clks) for k in range(half_clks)]
            for sl in h:
                ffs += "(* LOC=\"%s\" *) FDCE ff_%d (.C(r[%d]), .CE(aux[%d]), .CLR(1'b0), .D(r2[%d]), .Q(r2[%d]));\n" % (
                    sl, R2, np.random.choice(rclks), np.random.randint(5), R2,
                    R2 + 1)
                R2 += 1
    print("    wire [%d:0] r2;" % R2, file=f)
    print("    assign r2[0] = d;", file=f)
    print("    assign q = r2[%d];" % R2, file=f)
    print(ffs, file=f)
    print("endmodule", file=f)

    with open("top.tcl", "w") as f:
        print('opt_design', file=f)
