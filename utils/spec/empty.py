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
import sys
from utils import util
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
