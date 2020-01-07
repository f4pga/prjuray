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

from csv import DictReader
from utils.segmaker import Segmaker

# =============================================================================


def run():

    segmk = Segmaker("design.bits", bits_per_word=16)

    precyinit_bot_opts = ("C0", "C1", "AX", "CIN")
    precyinit_top_opts = ("C0", "C1", "EX", "CO3")

    # Load params
    with open("params.csv", "r") as fp:
        reader = DictReader(fp)
        params = [l for l in reader]

    # Add tags
    for p in params:
        site = p["site"]

        for opt in precyinit_bot_opts:
            tag = "CARRY8.PRECYINIT_BOT.{}".format(opt)
            val = int(p["precyinit_bot"] == opt)
            segmk.add_site_tag(site, tag, val)

        for opt in precyinit_top_opts:
            tag = "CARRY8.PRECYINIT_TOP.{}".format(opt)
            val = int(p["precyinit_top"] == opt)
            segmk.add_site_tag(site, tag, val)

        is_split = int(p["is_split"])
        segmk.add_site_tag(site, "CARRY8.DUAL_CY4", is_split)

    segmk.compile()
    segmk.write()


if __name__ == "__main__":
    run()
