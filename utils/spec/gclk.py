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

from utils import util
from prjuray.db import Database


def gen_bufgs():
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)

        for site, site_type in gridinfo.sites.items():
            if "BUFGCE" in site and "HDIO" not in site and "DIV" not in site:
                yield site


def print_top(seed):
    np.random.seed(seed)

    bufgces = list(gen_bufgs())
    np.random.shuffle(bufgces)

    print("module top(input i, output o);")
    N = int(len(bufgces) * 0.08)
    print("    wire [%d:0] r;" % N)
    print("    assign r[0] = i;")
    print("    assign o = r[%d];" % N)
    for i in range(N):
        site = bufgces[i]
        print("(* LOC=\"%s\" *)" % site)
        if "BUFGCTRL" in site:
            print(
                "    BUFGCTRL bufg_%d (.I0(r[%d]), .I1(r[%d]), .S0(1'b1), .S1(1'b0), .CE0(1'b1), .O(r[%d]));"
                % (i, i, i, i + 1))
        elif "DIV" in site:
            print(
                "    BUFGCE_DIV #(.BUFGCE_DIVIDE(3)) bufg_%d (.I(r[%d]), .CLR(0), .CE(1'b1), .O(r[%d]));"
                % (i, i, i + 1))
        else:
            print("    BUFGCE bufg_%d (.I(r[%d]), .CE(1'b1), .O(r[%d]));" %
                  (i, i, i + 1))
    print("endmodule")

    with open('top.tcl', 'w') as f:
        print('set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets]', file=f)
        print('opt_design', file=f)
