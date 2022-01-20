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
