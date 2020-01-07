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

    # Always write these tiles to avoid correlation issues
    # (distinguishing between all/no bits)
    for tilename, tiledata in tbj.items():
        if "INT_INTF_L_IO" in tilename:
            tile_bits[tilename] = set()

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
                if framebit >= start and framebit < (start + size):
                    if tile not in tile_bits:
                        tile_bits[tile] = set()
                    tile_bits[tile].add(toff + (framebit - start))

    for tile, bits in sorted(tile_bits.items()):
        print(".tile %s" % tile)
        for b in sorted(bits):
            print(b)


if __name__ == "__main__":
    main()
