#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2020  The Project X-Ray Authors.
# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

import argparse
import fasm
from utils import bitstream
from utils.db import Database
from utils.grid_types import BlockType
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
