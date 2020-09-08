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


def gen_sites():
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)

        for site, site_type in gridinfo.sites.items():
            if site_type in ['SLICEM', 'SLICEL']:
                yield site


def print_top(seed):
    np.random.seed(seed)
    DCLK_N = 10
    DIN_N = (16 * 2 + 7)
    DOUT_N = 1
    top_harness_clk(DCLK_N, DIN_N, DOUT_N)

    print("""
        module roi(input [{DCLK_N}-1:0] clk, input [{DIN_N}-1:0] din, output [{DOUT_N}:0] dout);

        wire [15:0] rst;
        wire [15:0] cen;
        wire [6:0] d;
        wire q;

        assign rst = din[0+:16];
        assign cen = din[16+:16];
        assign d = din[32+:7];
        assign dout = q;

        """.format(DCLK_N=DCLK_N, DIN_N=DIN_N, DOUT_N=DOUT_N))

    N = 1000
    print("    wire [%d:0] int_d;" % N)
    print("    assign int_d[6:0] = d;")
    print("    assign q = int_d[%d];" % N)

    slices = sorted(gen_sites())

    for i in range(6, N):
        fftype, srsig = np.random.choice(
            ["FDPE,PRE", "FDCE,CLR", "FDSE,S", "FDRE,R"]).split(",")
        sl = slices.pop()
        if np.random.ranf() < 0.5:
            data = "int_d[%d]" % i
        else:
            lutsize = np.random.randint(2, 10)
            if lutsize > 6:
                lutsize = 6
            print("    wire lut_q_%d;" % i)

            print(
                "     (* BEL=\"%s%dLUT\" *) (* LOC=\"%s\" *) LUT%d #(" %
                (np.random.choice(list("ABCDEFGH")),
                 np.random.randint(6 if lutsize == 6 else 5, 7), sl, lutsize))
            print("         .INIT(%d'h%016x)" %
                  (2**lutsize, np.random.randint(1,
                                                 (2**((2**lutsize) - 1) - 1))))
            print("     ) lut_%d (" % i)
            for j in range(lutsize):
                print("         .I%d(int_d[%d])," % (j, i - j))
            print("         .O(lut_q_%d)" % i)
            print("     );")
            data = "lut_q_%d" % i

        print("    (* BEL=\"%sFF%s\" *) (* LOC=\"%s\" *) %s #(" %
              (np.random.choice(list("ABCDEFGH")), np.random.choice(["", "2"]),
               sl, fftype))
        print("          .IS_C_INVERTED(%s)," % np.random.choice(["0", "1"]))
        print("          .IS_%s_INVERTED(%s)," %
              (srsig, np.random.choice(["0", "1"])))
        print("          .INIT(%s)" % np.random.choice(["1'b0", "1'b1"]))
        print("     ) ff_%d (" % i)
        print("          .C(clk[%d])," % np.random.randint(0, DCLK_N))
        print("          .CE(cen[%d])," % np.random.randint(0, 16))
        print("          .%s(rst[%d])," % (srsig, np.random.randint(0, 16)))
        print("          .D(%s)," % (data))
        print("          .Q(int_d[%d])" % (i + 1))
        print("     );")
    print("endmodule")
