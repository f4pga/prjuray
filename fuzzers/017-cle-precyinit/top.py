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
from collections import namedtuple
import random
random.seed(int(os.getenv("SEED"), 16))

from utils import util
from prjuray.db import Database

# =============================================================================

Site = namedtuple("Site", "tile_name name loc")


def gen_sites():
    """
    Generates all possible SLICE sites
    """
    SLICE_RE = re.compile(r"SLICE_X([0-9]+)Y([0-9]+)")

    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)
        if gridinfo.tile_type in ['CLEL_L', 'CLEL_R', 'CLEM', 'CLEM_R']:
            site_name = sorted(gridinfo.sites.keys())[0]
            match = SLICE_RE.match(site_name)
            if match is not None:
                site_loc = int(match.group(1)), int(match.group(2))
                yield Site(tile_name, site_name, site_loc)


# =============================================================================


def run():

    # Requested number of SLICEs within the specimen
    num_slices = 600

    # Number of inputs. Assigned to SLICEs randomly
    num_inputs = 64
    # Number of outputs. Unconnected...
    num_outputs = 8

    def slice_filter(site):
        """
        Filters only a range from all available SLICEs
        """
        # FIXME: Allow only bottom half of the X0Y0 clock region.
        # For that regions SLICE rows 30 and 31 seems to be addressed
        # differently
        if site.loc[1] < 0 or site.loc[1] > 29:
            return False

        return True

    all_sites = filter(slice_filter, gen_sites())

    free_sites = {s.loc: s for s in all_sites}
    used_sites = {}

    # Template parameters
    tpl_params = {"ni": num_inputs, "no": num_outputs, "mods": []}

    # Generate
    params = []
    for i in range(num_slices):

        # No more free sites
        if not len(free_sites):
            break

        # Choices
        is_split = random.random() > 0.20
        if is_split:
            precyinit_top = random.choice(("C0", "C1", "EX"))
        else:
            precyinit_top = "CO3"

        precyinit_bot = random.choice(("C0", "C1", "AX", "CIN"))

        # Pick a random site
        site = random.choice(list(free_sites.values()))

        del free_sites[site.loc]
        used_sites[site.loc] = site

        # Choose a co-located site when "CIN" is used.
        if precyinit_bot == "CIN":

            # When bottom precyinit is set to CIN then the site next to the
            # chosen one has to be free
            loc = (site.loc[0], site.loc[1] - 1)
            if loc in used_sites or loc not in free_sites:
                precyinit_bot = "AX"
                co_site = None

                inps = random.sample(range(num_inputs), 16)

            else:
                co_site = free_sites[loc]

                del free_sites[co_site.loc]
                used_sites[co_site.loc] = co_site

                inps = random.sample(range(num_inputs), 32)

        # A single CARRY8, no CIN
        else:
            co_site = None

            inps = random.sample(range(num_inputs), 16)

        # Add a module instance
        mod_params = {
            "type": "PRECYINIT" if precyinit_bot != "CIN" else "PRECYINIT_CIN",
            "name": "precyinit_{:03d}".format(i),
            "loc_ci": site.name,
            "loc_co": co_site.name if co_site else "",
            "carry_type": "DUAL_CY4" if is_split else "SINGLE_CY8",
            "inp": "{" + ",".join(["di[{}]".format(x) for x in inps]) + "}",
            "out": "",
            "precyinit_bot": precyinit_bot,
            "precyinit_top": precyinit_top,
        }

        tpl_params["mods"].append(mod_params)

        params.append("{},{},{},{},{}".format(
            site.tile_name,
            site.name,
            precyinit_bot,
            precyinit_top,
            int(is_split),
        ))

    # Render the template
    print(
        util.render_template(
            os.path.join(os.getenv("FUZDIR"), "top.tpl"),
            {"params": tpl_params}))

    # Save parameters
    with open("params.csv", "w") as fp:
        fp.write("tile,site,precyinit_bot,precyinit_top,is_split\n")
        for l in params:
            fp.write(l + "\n")


if __name__ == "__main__":
    run()
