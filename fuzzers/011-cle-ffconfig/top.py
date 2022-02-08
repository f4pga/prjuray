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

import os
import random
import re

from utils import util
from prjuray.db import Database

from prims import ff_bels, ff_bels_ffl, ffprims, isff

random.seed(0)


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
            yield site_name


def run():
    # Requested number of SLICEs within the specimen
    num_slices = 200

    # Number of inputs. Assigned to SLICEs randomly
    num_inputs = 64
    # Number of outputs. Unconnected...
    num_outputs = 8

    def slice_filter(slice):
        """
        Filters only a range from all available SLICEs
        """
        site_name = slice

        match = re.match(r"SLICE_X([0-9]+)Y([0-9]+)", site_name)
        assert match is not None

        x, y = int(match.group(1)), int(match.group(2))

        # FIXME: Allow only bottom half of the X0Y0 clock region.
        # For that regions SLICE rows 30 and 31 seems to be addressed
        # differently
        if x < 0 or x > 28:
            return False
        if y < 0 or y > 30:
            return False

        return True

    all_slices = list(filter(slice_filter, gen_sites()))

    slices = random.sample(all_slices, min(num_slices, len(all_slices)))

    f = open("top.txt", "w")
    f.write("i,prim,loc,bel,init\n")

    instances = []
    for i, site in enumerate(slices):
        instance = dict()

        instance['type'] = random.choice(ffprims)
        instance['loc'] = site

        # Latch can't go in 2s
        if isff(instance['type']):
            instance['bel'] = random.choice(ff_bels)
        else:
            instance['bel'] = random.choice(ff_bels_ffl)

        instance['init'] = random.choice((0, 1))
        instance['number'] = i
        instance['din'] = 4 * i
        instance['dout'] = i

        instances.append(instance)

        f.write("%d,%s,%s,%s,%d\n" %
                (instance['number'], instance['type'], instance['loc'],
                 instance['bel'], instance['init']))

    parameters = '''parameter LOC = "SLICE_X16Y106";
        parameter BEL = "AFF";
        parameter INIT = 1'b0;
    '''

    loc = '(* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH, INIT=INIT *)'

    ios = 'input clk, input [3:0] din, output dout'

    fuzdir = os.getenv('FUZDIR', None)

    templated = util.render_template(
        '{}/top.tpl'.format(fuzdir), {
            "parameters": parameters,
            "loc": loc,
            "ios": ios,
            "dout": num_slices,
            "instances": instances
        })

    print(templated)


if __name__ == "__main__":
    run()
