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

import re
import sys


def main():
    line_re = re.compile(r'F(0x[0-9A-Fa-f]+).*')

    outlines = set()

    with open(sys.argv[1], 'r') as f:
        for line in f:
            m = line_re.match(line)
            if not m:
                continue
            frame = int(m.group(1), 16)
            bus = (frame >> 24) & 0x7
            half = (frame >> 23) & 0x1
            row = (frame >> 18) & 0x1F
            col = (frame >> 8) & 0x3FF
            minor = frame & 0xFF
            outlines.add("F=%08x B=%d H=%d R=%03d C=%04d M=%03d" %
                         (frame, bus, half, row, col, minor))

    for o in sorted(outlines):
        print(o)


if __name__ == "__main__":
    main()
