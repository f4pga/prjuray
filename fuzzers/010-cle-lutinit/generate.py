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

import sys

from utils.segmaker import Segmaker

segmk = Segmaker("design_%s.bits" % sys.argv[1], bits_per_word=16)

print("Loading tags from design_%s.txt." % sys.argv[1])
with open("design_%s.txt" % sys.argv[1], "r") as f:
    for line in f:
        line = line.split()
        site = line[0]
        bel = line[1]
        init = int(line[2][4:], 16)

        for i in range(64):
            bitname = "%s.INIT[%02d]" % (bel, i)
            bitname = bitname.replace("6LUT", "LUT")
            segmk.add_site_tag(site, bitname, ((init >> i) & 1) != 0)

segmk.compile()
segmk.write(sys.argv[1])
