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

import random
random.seed(0)
import os
import re
from utils import util
from utils import verilog
from prjuray.db import Database


def gen_sites():
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)
        if gridinfo.tile_type in ['CLEL_L', 'CLEL_R', 'CLEM']:
            site_name = sorted(gridinfo.sites.keys())[0]
            yield tile_name, site_name


def write_params(params):
    pinstr = 'site,bel,rs_inv\n'
    for param in params:
        pinstr += "{},{},{}\n".format(param['site'], param['bel'],
                                      param['rs_inv'])
    open('params.csv', 'w').write(pinstr)


def run():
    sites_params = []
    sites = list(gen_sites())[0:20]
    CLBN = len(sites)
    DIN_N = CLBN * 4
    DOUT_N = CLBN * 1
    ffprim = 'FDRE'
    ff_bels = (
        'AFF',
        'EFF',
    )
    for (tile_name, site_name) in sites:
        params = {}
        params['name'] = 'clb_{}'.format(ffprim)
        params['site'] = site_name
        params['bel'] = random.choice(ff_bels)
        params['rs_inv'] = random.randint(0, 1)
        sites_params.append(params)
    print(
        util.render_template(
            os.path.join(os.getenv("FUZDIR"), "top.tpl"), {
                "parameters": sites_params,
                "din_index": DIN_N - 1,
                "dout_index": DOUT_N - 1
            }))
    write_params(sites_params)


if __name__ == "__main__":
    run()
