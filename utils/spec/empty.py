#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2020 Project U-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file.
#
# SPDX-License-Identifier: ISC

import numpy as np
import sys
from utils import util
from utils.db import Database


def gen_sites():
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()

    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)

        for site, site_type in gridinfo.sites.items():
            if site_type in ['SLICEM', 'SLICEL']:
                yield site


def print_top(seed, fout=sys.stdout):
    np.random.seed(seed)

    slices = sorted(gen_sites())
    np.random.shuffle(slices)
    site = slices.pop()

    print(
        """
module top();

(* KEEP, DONT_TOUCH, LOC="{site}", BEL="A6LUT" *)
LUT2 lut();

endmodule
""".format(site=site),
        file=fout)
