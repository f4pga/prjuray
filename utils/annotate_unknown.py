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
import fasm
from prjuray import bitstream
from prjuray.db import Database
from prjuray.grid_types import BlockType
from utils import util


def main():
    parser = argparse.ArgumentParser()

    util.db_root_arg(parser)
    util.part_arg(parser)

    parser.add_argument('input')

    args = parser.parse_args()

    db = Database(args.db_root, args.part)

    grid = db.grid()

    base_address_to_tiles = {}

    for tile in grid.tiles():
        gridinfo = grid.gridinfo_at_tilename(tile)
        if BlockType.CLB_IO_CLK in gridinfo.bits:
            base_address = gridinfo.bits[BlockType.CLB_IO_CLK].base_address
            if base_address not in base_address_to_tiles:
                base_address_to_tiles[base_address] = []
            base_address_to_tiles[base_address].append(
                (tile, gridinfo.bits[BlockType.CLB_IO_CLK]))

    for line in fasm.parse_fasm_filename(args.input):
        is_unknown = False

        annotation_data = {}
        for annotation in line.annotations:
            annotation_data[annotation.name] = annotation.value

        if 'unknown_bit' not in annotation_data:
            continue

        base_address = int(annotation_data['unknown_segment'], 0)
        frame_offset = int(annotation_data['unknown_segbit'].split('_')[0])
        bit = int(annotation_data['unknown_segbit'].split('_')[1])
        offset = bit // 16

        if base_address not in base_address_to_tiles:
            print('# No tile for base address')
        else:
            for tile, bits in base_address_to_tiles[base_address]:
                if offset >= bits.offset and offset - bits.offset < bits.words:
                    print('# {} : {:02d}_{:02d}'.format(
                        tile, frame_offset,
                        bit - bitstream.WORD_SIZE_BITS * bits.offset))

        for l in fasm.fasm_line_to_string(line):
            print(l)


if __name__ == "__main__":
    main()
