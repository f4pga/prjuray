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

    # Load params
    with open("params.csv", "r") as fp:
        reader = DictReader(fp)
        params = [l for l in reader]

    # Add tags
    for p in params:
        m = p["bel"][0]

        tag = "CARRY8.{}CY0".format(m)
        val = int(p["ncy0"])

        segmk.add_site_tag(p["site"], tag, val)

    segmk.compile()
    segmk.write()


if __name__ == "__main__":
    run()
