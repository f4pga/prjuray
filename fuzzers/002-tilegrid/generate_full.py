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

import json
import os
from utils import xjson
'''
Historically we grouped data into "segments"
These were a region of the bitstream that encoded one or more tiles
However, this didn't scale with certain tiles like BRAM
Some sites had multiple bitstream areas and also occupied multiple tiles

Decoding was then shifted to instead describe how each title is encoded
A post processing step verifies that two tiles don't reference the same bitstream area
'''

import util as localutil


def nolr(tile_type):
    '''
    Remove _L or _R suffix tile_type suffix, if present
    Ex: BRAM_INT_INTERFACE_L => BRAM_INT_INTERFACE
    Ex: VBRK => VBRK
    '''
    postfix = tile_type[-2:]
    if postfix in ('_L', '_R'):
        return tile_type[:-2]
    else:
        return tile_type


def make_tiles_by_grid(database):
    # lookup tile names by (X, Y)
    tiles_by_grid = dict()

    for tile_name in database:
        tile = database[tile_name]
        tiles_by_grid[(tile["grid_x"], tile["grid_y"])] = tile_name

    return tiles_by_grid


def propagate_INT_bits_in_column(database, tiles_by_grid, tile_frames_map):
    """ Propigate INT offsets up and down INT columns.

    INT columns appear to be fairly regular, where starting from offset 0,
    INT tiles next to INT tiles increase the word offset by 3.

    """
    int_frames, int_words = localutil.get_int_params()

    propagate_bits_in_column(
        database=database,
        tiles_by_grid=tiles_by_grid,
        tile_type='INT',
        term_b='INT_TERM_B',
        term_t='INT_TERM_T',
        rbrk='INT_RBRK',
        rclk_types=['RCLK_INT_L', 'RCLK_INT_R'],
        tile_frames=int_frames,
        tile_words=int_words,
        tile_frames_map=tile_frames_map)


def propagate_PS8_INTF_bits_in_column(database, tiles_by_grid,
                                      tile_frames_map):
    """ Propigate INT_INTF_LEFT_TERM_PSS offsets up and down columns.

    INT_INTF_LEFT_TERM_PSS columns appear to be fairly regular, where starting
    from offset 0,
    INT_INTF_LEFT_TERM_PSS tiles next to INT_INTF_LEFT_TERM_PSS tiles increase
    the word offset by 3.

    """
    ps8_intf_frames, ps8_intf_words = localutil.get_entry(
        'PS8_INTF', 'CLB_IO_CLK')

    propagate_bits_in_column(
        database=database,
        tiles_by_grid=tiles_by_grid,
        tile_type='INT_INTF_LEFT_TERM_PSS',
        term_b='INT_INTF_LEFT_TERM_PSS_TERM_B',
        term_t='INT_INTF_LEFT_TERM_PSS_TERM_T',
        rbrk='INT_INTF_LEFT_TERM_PSS_RBRK',
        rclk_types=['RCLK_INTF_LEFT_TERM_ALTO'],
        tile_frames=ps8_intf_frames,
        tile_words=ps8_intf_words,
        tile_frames_map=tile_frames_map)


def propagate_bits_in_column(database, tiles_by_grid, tile_type, term_b,
                             term_t, rbrk, rclk_types, tile_frames, tile_words,
                             tile_frames_map):
    """ Propigate offsets up and down columns, based on a fixed pattern. """

    rclk_frames, rclk_words = localutil.get_entry('RCLK_INT_L', 'CLB_IO_CLK')
    _, ecc_words = localutil.get_entry('ECC', 'CLB_IO_CLK')
    seen_int = set()

    for tile_name in sorted(database.keys()):
        tile = database[tile_name]

        if tile['type'] != tile_type:
            continue

        if not tile['bits']:
            continue

        if tile_name in seen_int:
            continue

        # Walk down column
        while True:
            seen_int.add(tile_name)

            next_tile = tiles_by_grid[(tile['grid_x'], tile['grid_y'] + 1)]
            next_tile_type = database[next_tile]['type']

            if tile['bits']['CLB_IO_CLK']['offset'] == 0:
                assert next_tile_type in [term_b, rbrk], next_tile_type
                break

            baseaddr = int(tile['bits']['CLB_IO_CLK']['baseaddr'], 0)
            offset = tile['bits']['CLB_IO_CLK']['offset']

            if tile['type'] == tile_type and next_tile_type == tile['type']:
                # INT next to INT
                offset -= tile_words
                localutil.add_tile_bits(next_tile, database[next_tile],
                                        baseaddr, offset, tile_frames,
                                        tile_words, tile_frames_map)
            elif tile['type'] == tile_type:
                # INT above RCLK
                assert next_tile_type in rclk_types, next_tile_type

                offset -= rclk_words
                localutil.add_tile_bits(next_tile, database[next_tile],
                                        baseaddr, offset, rclk_frames,
                                        rclk_words, tile_frames_map)
                offset -= ecc_words
            else:
                # RCLK above INT
                assert tile['type'] in rclk_types, tile['type']
                if next_tile_type == tile_type:
                    offset -= ecc_words
                    offset -= tile_words
                    localutil.add_tile_bits(next_tile, database[next_tile],
                                            baseaddr, offset, tile_frames,
                                            tile_words, tile_frames_map)
                else:
                    assert next_tile_type in [], next_tile_type
                    break

            tile_name = next_tile
            tile = database[tile_name]

        # Walk up INT column
        while True:
            seen_int.add(tile_name)

            next_tile = tiles_by_grid[(tile['grid_x'], tile['grid_y'] - 1)]
            next_tile_type = database[next_tile]['type']

            if tile['bits']['CLB_IO_CLK']['offset'] == (
                    183
                    if os.getenv('URAY_ARCH') == 'UltraScalePlus' else 121):
                assert next_tile_type in [term_t, rbrk], next_tile_type
                break

            baseaddr = int(tile['bits']['CLB_IO_CLK']['baseaddr'], 0)
            offset = tile['bits']['CLB_IO_CLK']['offset']

            if tile['type'] == tile_type and next_tile_type == tile['type']:
                # INT next to INT
                offset += tile_words
                localutil.add_tile_bits(next_tile, database[next_tile],
                                        baseaddr, offset, tile_frames,
                                        tile_words, tile_frames_map)
            elif tile['type'] == tile_type:
                # INT below RCLK
                assert next_tile_type in rclk_types, next_tile_type

                offset += tile_words
                offset += ecc_words

                localutil.add_tile_bits(next_tile, database[next_tile],
                                        baseaddr, offset, rclk_frames,
                                        rclk_words, tile_frames_map)
            else:
                # RCLK below INT
                assert tile['type'] in rclk_types, tile['type']
                assert next_tile_type == tile_type, next_tile_type

                offset += rclk_words
                localutil.add_tile_bits(next_tile, database[next_tile],
                                        baseaddr, offset, tile_frames,
                                        tile_words, tile_frames_map)

            tile_name = next_tile
            tile = database[tile_name]


def propagate_RCLK_bits_in_row(database, tiles_by_grid, tile_frames_map):
    """ Propigate base address to some RCLK tiles that are hard to get base
    addresses directly for.

    It appears that RCLK <-> RCLK base addresses can be predicted by the x
    coordinate in some cases, so depend on that assumption for now.

    """
    rclk_frames, rclk_words = localutil.get_entry('RCLK_INT_L', 'CLB_IO_CLK')
    _, ecc_words = localutil.get_entry('ECC', 'CLB_IO_CLK')

    for tile_name in sorted(database.keys()):
        tile = database[tile_name]

        if tile['type'] != 'RCLK_AMS_CFGIO':
            continue

        if 'CLB_IO_CLK' in tile['bits']:
            continue

        dx = 1
        while True:
            other_tile = database[tiles_by_grid[(tile['grid_x'] - dx,
                                                 tile['grid_y'])]]

            if other_tile['type'].startswith(
                    'RCLK_') and 'CLB_IO_CLK' in other_tile['bits']:
                break

            dx += 1

        baseaddr = int(other_tile['bits']['CLB_IO_CLK']['baseaddr'], 0)
        offset = other_tile['bits']['CLB_IO_CLK']['offset']
        localutil.add_tile_bits(tile_name, database[tile_name],
                                baseaddr + dx * 0x100, offset, rclk_frames,
                                rclk_words, tile_frames_map)


def propagate_XIPHY_bits_in_column(database, tiles_by_grid, tile_frames_map):
    xiphy_frames, xiphy_words = localutil.get_entry('XIPHY', 'CLB_IO_CLK')
    rclk_frames, rclk_words = localutil.get_entry('RCLK_INT_L', 'CLB_IO_CLK')
    _, ecc_words = localutil.get_entry('ECC', 'CLB_IO_CLK')

    for tile, tile_data in database.items():
        if tile_data['type'] != 'RCLK_XIPHY_OUTER_RIGHT':
            continue

        above_tile = tiles_by_grid[tile_data['grid_x'], tile_data['grid_y'] -
                                   1]
        below_tile = tiles_by_grid[tile_data['grid_x'], tile_data['grid_y'] +
                                   15]

        assert database[above_tile]['type'] == 'XIPHY_BYTE_RIGHT'
        assert database[below_tile]['type'] == 'XIPHY_BYTE_RIGHT'

        baseaddr1 = int(database[above_tile]['bits']['CLB_IO_CLK']['baseaddr'],
                        0)
        offset1 = database[above_tile]['bits']['CLB_IO_CLK']['offset']
        offset1 -= rclk_words
        localutil.add_tile_bits(tile, database[tile], baseaddr1, offset1,
                                rclk_frames, rclk_words, tile_frames_map)

        baseaddr2 = int(database[below_tile]['bits']['CLB_IO_CLK']['baseaddr'],
                        0)
        offset2 = database[below_tile]['bits']['CLB_IO_CLK']['offset']
        offset2 += xiphy_words
        offset2 += ecc_words
        localutil.add_tile_bits(tile, database[tile], baseaddr2, offset2,
                                rclk_frames, rclk_words, tile_frames_map)


def run(json_in_fn, json_out_fn, verbose=False):
    # Load input files
    database = json.load(open(json_in_fn, "r"))
    tiles_by_grid = make_tiles_by_grid(database)

    tile_frames_map = localutil.TileFrames()
    propagate_INT_bits_in_column(database, tiles_by_grid, tile_frames_map)
    if os.getenv('URAY_ARCH') == "UltraScalePlus":
        propagate_PS8_INTF_bits_in_column(database, tiles_by_grid, tile_frames_map)
    propagate_RCLK_bits_in_row(database, tiles_by_grid, tile_frames_map)
    propagate_XIPHY_bits_in_column(database, tiles_by_grid, tile_frames_map)

    # Save
    xjson.pprint(open(json_out_fn, "w"), database)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate tilegrid.json from bitstream deltas")

    parser.add_argument("--verbose", action="store_true", help="")
    parser.add_argument(
        "--json-in",
        default="tiles_basic.json",
        help="Input .json without addresses")
    parser.add_argument(
        "--json-out", default="tilegrid.json", help="Output JSON")
    args = parser.parse_args()

    run(args.json_in, args.json_out, verbose=args.verbose)


if __name__ == "__main__":
    main()
