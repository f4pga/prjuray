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
import json


def main():
    line_re = re.compile(r'F(0x[0-9A-Fa-f]+)W(\d+)B(\d+)')
    frames_to_tiles = {}  # (start, size, tile, tile offset)

    with open(sys.argv[1]) as tb_f:
        tbj = json.load(tb_f)

    for tilename, tiledata in tbj.items():
        tile_offset = 0
        for chunk in tiledata:
            frame, start, size = chunk
            if frame not in frames_to_tiles:
                frames_to_tiles[frame] = []
            frames_to_tiles[frame].append((start, size, tilename, tile_offset))
            tile_offset += size

    tile_bits = {}

    with open(sys.argv[2]) as df:
        for line in df:
            m = line_re.match(line)
            if not m:
                continue
            frame = int(m[1], 16)
            if frame not in frames_to_tiles:
                continue
            framebit = int(m[2]) * 32 + int(m[3])
            for fb in frames_to_tiles[frame]:
                start, size, tile, toff = fb
                if framebit > start and framebit < (start + size):
                    if tile not in tile_bits:
                        tile_bits[tile] = set()
                    tile_bits[tile].add(toff + (framebit - start))

    for tile, bits in sorted(tile_bits.items()):
        if "CLE" in tile:
            if 152 not in bits:
                print(tile)
        if "INT" in tile:
            if 3640 not in bits:
                print(tile)


if __name__ == "__main__":
    main()
