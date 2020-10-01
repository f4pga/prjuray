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
import re
import random
random.seed(int(os.getenv("SEED"), 16))

from utils import util
from prjuray.db import Database

# =============================================================================


def gen_sites():
    """
    Generates all possible SLICE sites
    """
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)
        if gridinfo.tile_type in ['CLEL_L', 'CLEL_R', 'CLEM', 'CLEM_R']:
            site_name = sorted(gridinfo.sites.keys())[0]
            yield tile_name, site_name


# =============================================================================


def run():

    # Requested number of SLICEs within the specimen
    num_slices = 200

    # Number of inputs. Assigned to SLICEs randomly
    num_inputs = 64
    # Number of outputs. Unconnected...
    num_outputs = 8

    mod_names = ("slice_NCY0_MX", "slice_NCY0_O5")
    bel_names = ("A6LUT", "B6LUT", "C6LUT", "D6LUT", \
                 "E6LUT", "F6LUT", "G6LUT", "H6LUT")

    def slice_filter(slice):
        """
        Filters only a range from all available SLICEs
        """
        tile_name, site_name = slice

        match = re.match(r"SLICE_X([0-9]+)Y([0-9]+)", site_name)
        assert match is not None

        x, y = int(match.group(1)), int(match.group(2))

        # FIXME: Allow only bottom half of the X0Y0 clock region.
        # For that regions SLICE rows 30 and 31 seems to be addressed
        # differently
        if y < 0 or y > 29:
            return False

        return True

    all_slices = list(filter(slice_filter, gen_sites()))

    slices = random.sample(all_slices, min(num_slices, len(all_slices)))
    print("// Requested {} slices, got {}".format(num_slices, len(slices)))

    # Header
    print("""
module top(input clk, input[{ni}:0] di, output [{no}:0] do);
""".format(ni=num_inputs, no=num_outputs))

    # Generate SLICEs
    with open("params.csv", "w") as fp:
        fp.write("tile,site,bel,ncy0\n")

        for i, (tile_name, site_name) in enumerate(slices):
            ncy0 = random.randint(0, 1)

            bel_idx = random.randint(0, 7)
            bel_name = bel_names[bel_idx]

            inps = random.sample(range(num_inputs), 16)

            print("  {} # (.LOC(\"{}\"), .BEL(\"{}\"), .N({}))".format(
                mod_names[ncy0],
                site_name,
                bel_name,
                bel_idx,
            ))

            print("    slice_{:04d} (.clk(clk), .di({}), .do({}));\n".format(
                i,
                "{" + ",".join(["di[{}]".format(x) for x in inps]) + "}",
                "",
            ))

            fp.write("{},{},{},{}\n".format(
                tile_name,
                site_name,
                bel_name,
                ncy0,
            ))

    # Footer
    print("""endmodule
""")

    # Modules
    print("""
module slice_NCY0_MX(
    input  wire        clk,
    input  wire [15:0] di,
    output wire [ 7:0] do
);

    parameter LOC = "";
    parameter BEL = "";
    parameter N   = -1;

    wire o5;
    wire o6;

    (* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
    LUT6_2 # (.INIT(64'd1)) lut (
        .I0 (di[0]),
        .I1 (di[1]),
        .I2 (di[2]),
        .I3 (di[3]),
        .I4 (di[4]),
        .I5 (di[5]),
        .O5 (o5),
        .O6 (o6)
    );

    reg  [7:0] s;
    wire [7:0] o;

    always @(*) begin
        s = di;
        s[N] = o6;
    end

	(* LOC=LOC, KEEP, DONT_TOUCH *)
    CARRY8 # (.CARRY_TYPE("SINGLE_CY8")) carry8 (
        .CI     (1'b1),
        .CI_TOP (1'b0),
        .DI     (di),
        .S      (s),
        .CO     (),
        .O      (o)
    );

    (* LOC=LOC, BEL="AFF", KEEP, DONT_TOUCH *)
    FDRE aff (.D(o[0]), .C(clk), .CE(), .R(), .Q(do[0]));
    (* LOC=LOC, BEL="BFF", KEEP, DONT_TOUCH *)
    FDRE bff (.D(o[1]), .C(clk), .CE(), .R(), .Q(do[1]));
    (* LOC=LOC, BEL="CFF", KEEP, DONT_TOUCH *)
    FDRE cff (.D(o[2]), .C(clk), .CE(), .R(), .Q(do[2]));
    (* LOC=LOC, BEL="DFF", KEEP, DONT_TOUCH *)
    FDRE dff (.D(o[3]), .C(clk), .CE(), .R(), .Q(do[3]));
    (* LOC=LOC, BEL="EFF", KEEP, DONT_TOUCH *)
    FDRE eff (.D(o[4]), .C(clk), .CE(), .R(), .Q(do[4]));
    (* LOC=LOC, BEL="FFF", KEEP, DONT_TOUCH *)
    FDRE fff (.D(o[5]), .C(clk), .CE(), .R(), .Q(do[5]));
    (* LOC=LOC, BEL="GFF", KEEP, DONT_TOUCH *)
    FDRE gff (.D(o[6]), .C(clk), .CE(), .R(), .Q(do[6]));
    (* LOC=LOC, BEL="HFF", KEEP, DONT_TOUCH *)
    FDRE hff (.D(o[7]), .C(clk), .CE(), .R(), .Q(do[7]));

endmodule
""")

    print("""
module slice_NCY0_O5(
    input  wire        clk,
    input  wire [15:0] di,
    output wire [ 7:0] do
);

    parameter LOC = "";
    parameter BEL = "";
    parameter N   = -1;

    wire o5;
    wire o6;

    (* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
    LUT6_2 # (.INIT(64'd1)) lut (
        .I0 (di[0]),
        .I1 (di[1]),
        .I2 (di[2]),
        .I3 (di[3]),
        .I4 (di[4]),
        .I5 (di[5]),
        .O5 (o5),
        .O6 (o6)
    );

    reg  [7:0] s;
    reg  [7:0] d;
    wire [7:0] o;

    always @(*) begin
        s = di[15:8];
        s[N] = o6;
    end

    always @(*) begin
        d = di[ 7:0];
        d[N] = o5;
    end

	(* LOC=LOC, KEEP, DONT_TOUCH *)
    CARRY8 # (.CARRY_TYPE("SINGLE_CY8")) carry8 (
        .CI     (1'b1),
        .CI_TOP (1'b0),
        .DI     (d),
        .S      (s),
        .CO     (),
        .O      (o)
    );

    (* LOC=LOC, BEL="AFF", KEEP, DONT_TOUCH *)
    FDRE aff (.D(o[0]), .C(clk), .CE(), .R(), .Q(do[0]));
    (* LOC=LOC, BEL="BFF", KEEP, DONT_TOUCH *)
    FDRE bff (.D(o[1]), .C(clk), .CE(), .R(), .Q(do[1]));
    (* LOC=LOC, BEL="CFF", KEEP, DONT_TOUCH *)
    FDRE cff (.D(o[2]), .C(clk), .CE(), .R(), .Q(do[2]));
    (* LOC=LOC, BEL="DFF", KEEP, DONT_TOUCH *)
    FDRE dff (.D(o[3]), .C(clk), .CE(), .R(), .Q(do[3]));
    (* LOC=LOC, BEL="EFF", KEEP, DONT_TOUCH *)
    FDRE eff (.D(o[4]), .C(clk), .CE(), .R(), .Q(do[4]));
    (* LOC=LOC, BEL="FFF", KEEP, DONT_TOUCH *)
    FDRE fff (.D(o[5]), .C(clk), .CE(), .R(), .Q(do[5]));
    (* LOC=LOC, BEL="GFF", KEEP, DONT_TOUCH *)
    FDRE gff (.D(o[6]), .C(clk), .CE(), .R(), .Q(do[6]));
    (* LOC=LOC, BEL="HFF", KEEP, DONT_TOUCH *)
    FDRE hff (.D(o[7]), .C(clk), .CE(), .R(), .Q(do[7]));

endmodule
""")


if __name__ == "__main__":
    run()
