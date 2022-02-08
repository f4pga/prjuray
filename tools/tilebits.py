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

tiles = {}
site_to_tile = {}
tile_to_bits = {}  # (frame, bit start, bit size)


def main():
    with open(sys.argv[1], 'r') as tilef:
        for line in tilef:
            sl = line.strip().split(",")
            if len(sl) < 4:
                continue
            x = int(sl[0])
            y = int(sl[1])
            name = sl[2]
            ttype = sl[3]
            tiles[(x, y)] = (name + ":" + ttype, ttype, [])
            for site in sl[4:]:
                sitename, sitetype = site.split(":")
                tiles[(x, y)][2].append((sitename, sitetype))
                site_to_tile[sitename] = (x, y)

    ll_line_re = re.compile(
        r'Bit\s+\d+\s+(0x[0-9A-Fa-f]+)\s+(\d+)\s+SLR\d\s+\d+\s+Block=([A-Za-z0-9_]+).*'
    )
    site_re = re.compile(r'SLICE_X(\d+)Y(\d+)')
    with open(sys.argv[2], 'r') as llf:
        for line in llf:
            m = ll_line_re.match(line)
            if not m:
                continue
            frame = int(m.group(1), 16)
            bit = int(m.group(2))
            start_bit = bit - 2
            site = m.group(3)
            bus = (frame >> 24) & 0x7
            half = (frame >> 23) & 0x1
            row = (frame >> 18) & 0x1F
            col = (frame >> 8) & 0x3FF
            m = frame & 0xFF

            sm = site_re.match(site)
            site_x = int(sm.group(1))
            site_y = int(sm.group(2))
            frame_upper = frame & ~0xFF

            if site not in site_to_tile:
                continue
            tx, ty = site_to_tile[site]
            tiledata = tiles[tx, ty]
            tile_to_bits[tiledata[0]] = []
            for m in range(16):
                tile_to_bits[tiledata[0]].append((frame_upper | m, start_bit,
                                                  48))

            def process_nonlogic(x, y, icol):
                if (x, y) not in tiles:
                    return
                itiledata = tiles[x, y]
                if itiledata[1] == "INT":
                    if (x + 1, y) not in tiles:
                        return

                    int_frame_base = (frame_upper & ~0x3FFFF) | (icol << 8)
                    tile_to_bits[itiledata[0]] = []
                    for m in range(76):
                        tile_to_bits[itiledata[0]].append((int_frame_base | m,
                                                           start_bit, 48))
                    process_clock(x, y - 1, int_frame_base, start_bit + 48, 76)
                    process_cmt(x - 2, y, icol - 2)
                    process_int_intf(x - 1, y, icol - 1)
                elif itiledata[1] == "BRAM":
                    bram_frame_base = (frame_upper & ~0x3FFFF) | (icol << 8)
                    tile_to_bits[itiledata[0]] = []
                    for m in range(6):
                        tile_to_bits[itiledata[0]].append((bram_frame_base | m,
                                                           start_bit, 5 * 48))
                    process_clock(x, y - 5, bram_frame_base,
                                  start_bit + 5 * 48, 6)
                elif itiledata[1] == "DSP":
                    dsp_frame_base = (frame_upper & ~0x3FFFF) | (icol << 8)
                    tile_to_bits[itiledata[0]] = []
                    for m in range(8):
                        tile_to_bits[itiledata[0]].append((dsp_frame_base | m,
                                                           start_bit, 5 * 48))
                    process_clock(x, y - 5, dsp_frame_base, start_bit + 5 * 48,
                                  8)

                    if (x - 1,
                            y) in tiles and "INT_INTF" in tiles[x - 1, y][1]:
                        process_clock(x - 1, y - 5, dsp_frame_base,
                                      start_bit + 5 * 48, 8)

            def process_clock(cx, cy, frame_base, end_bit, height):
                if (cx, cy) not in tiles:
                    return
                if end_bit != (1392 + 48):
                    return
                ctiledata = tiles[cx, cy]
                if not ctiledata[1].startswith("RCLK"):
                    return
                tile_to_bits[ctiledata[0]] = []
                for m in range(height):
                    tile_to_bits[ctiledata[0]].append((frame_base | m,
                                                       end_bit + 48, 48))

            def process_cmt(x, y, icol):
                if (x, y) not in tiles:
                    return
                ctiledata = tiles[x, y]
                if not ctiledata[1] in ("CMT_L", "CMT_RIGHT"):
                    return
                cmt_frame_base = (frame_upper & ~0x3FFFF) | (icol << 8)
                tile_to_bits[ctiledata[0]] = []
                for m in range(12):
                    tile_to_bits[ctiledata[0]].append((cmt_frame_base | m,
                                                       start_bit, 60 * 48))

            def process_int_intf(x, y, icol):
                if (x, y) not in tiles:
                    return
                itiledata = tiles[x, y]
                if not itiledata[1] in ("INT_INTF_L_IO", "INT_INTF_R_IO"):
                    return
                int_frame_base = (frame_upper & ~0x3FFFF) | (icol << 8)
                tile_to_bits[itiledata[0]] = []
                for m in range(4):
                    tile_to_bits[itiledata[0]].append((int_frame_base | m,
                                                       start_bit, 48))

            process_nonlogic(tx - 1, ty, col - 1)
            process_nonlogic(tx + 1, ty, col + 1)
            process_clock(tx, ty - 1, frame_upper, start_bit + 48, 16)
    # Original JSON
    with open(sys.argv[3], 'w') as tj:
        tj.write(
            json.dumps(
                tile_to_bits, sort_keys=True, indent=4, separators=(',',
                                                                    ': ')))
        tj.write("\n")

    # New simplified text format
    with open(sys.argv[4], 'w') as tf:
        for loc, tiledata in sorted(tiles.items()):
            print(
                ".tile %s %s %d %d" % (tiledata[0].split(":")[0], tiledata[1],
                                       loc[0], loc[1]),
                file=tf)
            for site in tiledata[2]:
                print("site %s %s" % site, file=tf)
            if tiledata[0] in tile_to_bits:
                for frame, offset, size in tile_to_bits[tiledata[0]]:
                    print(
                        "frame 0x%08x bits %d +: %d" % (frame, offset, size),
                        file=tf)


if __name__ == "__main__":
    main()
