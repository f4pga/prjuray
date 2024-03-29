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

import argparse
from prjuray.db import Database
from prjuray.grid import BlockType
from utils import util


def main():
    parser = argparse.ArgumentParser(
        description="Tool for checking which tiles have bits defined.")

    util.db_root_arg(parser)
    util.part_arg(parser)
    parser.add_argument('--show-only-missing', action='store_true')
    parser.add_argument('--verbose', action='store_true')

    args = parser.parse_args()

    db = Database(args.db_root, args.part)
    grid = db.grid()

    tile_types = {}
    for tile in grid.tiles():
        gridinfo = grid.gridinfo_at_tilename(tile)
        if gridinfo.tile_type not in tile_types:
            tile_types[gridinfo.tile_type] = []

        tile_types[gridinfo.tile_type].append((tile, gridinfo))

    total_tile_count = 0
    total_have_bits = 0

    for tile_type, tiles in sorted(tile_types.items()):
        try:
            tile_type_info = db.get_tile_type(tile_type)

            # Skip empty tiles, as no base address is requied.
            if len(tile_type_info.get_pips()) == 0 and len(
                    tile_type_info.get_sites()) == 0:
                continue
        except KeyError:
            pass

        # INT_INTERFACE tiles likely don't contain configuration?  Remove this
        # if this ends up false.
        if 'INT_INTERFACE' in tile_type:
            continue

        if 'BRKH' in tile_type:
            continue

        have_bits = 0
        for tile_name, gridinfo in tiles:
            total_tile_count += 1
            if BlockType.CLB_IO_CLK in gridinfo.bits:
                have_bits += 1
                total_have_bits += 1

        if args.show_only_missing and have_bits == len(tiles):
            continue

        print('{}: {}/{} ({:.2f} %)'.format(
            tile_type, have_bits, len(tiles),
            100. * float(have_bits) / len(tiles)))

        if args.verbose:
            tiles_with_missing_bits = []
            for tile_name, gridinfo in tiles:
                total_tile_count += 1
                if BlockType.CLB_IO_CLK not in gridinfo.bits:
                    tiles_with_missing_bits.append(tile_name)

            for tile_name in sorted(tiles_with_missing_bits):
                print('{} is missing CLB_IO_CLK'.format(tile_name))

    print('')
    print('Summary: {}/{} ({:.2f} %)'.format(
        total_have_bits, total_tile_count,
        100. * float(total_have_bits) / total_tile_count))


if __name__ == "__main__":
    main()
