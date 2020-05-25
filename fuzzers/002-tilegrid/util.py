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

from utils import util
import os
import json
'''
Local utils script to hold shared code of the 005-tilegrid fuzzer scripts
'''
WORDS_IN_FRAME = 93 if os.getenv('URAY_ARCH') == 'UltraScalePlus' else 123
BITS_PER_WORD = 16 if os.getenv('URAY_ARCH') == 'UltraScalePlus' else 32


class TileFrames:
    """
    Class for getting the number of frames used for configuring a tile
    with the specified baseaddress using the information from the part's json file
    """

    def __init__(self):
        self.tile_address_to_frames = dict()

    def get_baseaddress(self, bus, row, column):
        assert bus == 'BLOCK_RAM' or bus == 'CLB_IO_CLK', 'Incorrect block type'
        if os.getenv('URAY_ARCH') == 'UltraScalePlus':
            address = (row << 18) + (column << 8) + (
                (1 << 24) if bus == 'BLOCK_RAM' else 0)
        else:
            address = (row << 17) + (column << 7) + (
                (1 << 23) if bus == 'BLOCK_RAM' else 0)
        return address

    def initialize_address_to_frames(self):
        with open(
                os.path.join(
                    os.getenv('URAY_FAMILY_DIR'), os.getenv('URAY_PART'),
                    'part.json')) as pf:
            part_json = json.load(pf)
        for row, buses in part_json['rows'].items():
            for bus, columns in buses['configuration_buses'].items():
                for column, frames in columns['configuration_columns'].items():
                    address = self.get_baseaddress(bus, int(row), int(column))
                    assert address not in self.tile_address_to_frames
                    self.tile_address_to_frames[address] = frames[
                        'frame_count']

    def get_tile_frames(self, baseaddress):
        if len(self.tile_address_to_frames) == 0:
            self.initialize_address_to_frames()
        assert baseaddress in self.tile_address_to_frames, "Base address not found in the part's json file"
        return self.tile_address_to_frames[baseaddress]


def get_entry(tile_type, block_type):
    """ Get frames and words for a given tile_type (e.g. CLBLL) and block_type (CLB_IO_CLK, BLOCK_RAM, etc). """
    return {
        # (architecture, tile_type, block_type): (frames, words)
        ("UltraScalePlus", "CLE", "CLB_IO_CLK"): (16, 3),
        ("UltraScalePlus", "INT", "CLB_IO_CLK"): (76, 3),
        ("UltraScalePlus", "PS8_INTF", "CLB_IO_CLK"): (76, 3),
        ("UltraScalePlus", "RCLK_INT_L", "CLB_IO_CLK"): (76, 3),
        ("UltraScalePlus", "ECC", "CLB_IO_CLK"): (None, 3),
        ("UltraScalePlus", "XIPHY", "CLB_IO_CLK"): (76, 45),
        ("UltraScalePlus", "BRAM", "CLB_IO_CLK"): (16, 15),
        ("UltraScalePlus", "BRAM", "BRAM_BLOCK"): (255, 15),
        ("UltraScale", "CLE", "CLB_IO_CLK"): (16, 2),
        ("UltraScale", "INT", "CLB_IO_CLK"): (17, 2),
        ("UltraScale", "RCLK_INT_L", "CLB_IO_CLK"): (62, 3),
        ("UltraScale", "ECC", "CLB_IO_CLK"): (None, 0),
        ("UltraScale", "XIPHY", "CLB_IO_CLK"): (76, 45),
        ("UltraScale", "BRAM", "CLB_IO_CLK"): (16, 10),
        ("UltraScale", "BRAM", "BRAM_BLOCK"): (255, 10),
    }.get((os.getenv("URAY_ARCH"), tile_type, block_type), None)


def get_int_params():
    int_frames, int_words = get_entry('INT', 'CLB_IO_CLK')
    return int_frames, int_words


def add_tile_bits(tile_name,
                  tile_db,
                  baseaddr,
                  offset,
                  frames,
                  words,
                  tile_frames,
                  verbose=False):
    '''
    Record data structure geometry for the given tile baseaddr
    For most tiles there is only one baseaddr, but some like BRAM have multiple
    Notes on multiple block types:
    https://github.com/SymbiFlow/prjxray/issues/145
    '''
    bits = tile_db['bits']
    block_type = util.addr2btype(baseaddr)
    if frames is None:
        frames = tile_frames.get_tile_frames(baseaddr)

    assert offset <= WORDS_IN_FRAME * 32 // BITS_PER_WORD, (tile_name, offset)
    # Few rare cases at X=0 for double width tiles split in half => small negative offset
    assert offset >= 0 or "IOB" in tile_name, (tile_name, hex(baseaddr),
                                               offset)
    assert 1 <= words <= WORDS_IN_FRAME * 32 // BITS_PER_WORD, words
    assert offset + words <= WORDS_IN_FRAME * 32 // BITS_PER_WORD, (
        tile_name, offset + words, offset, words, block_type)

    baseaddr_str = '0x%08X' % baseaddr
    block = bits.get(block_type, None)
    if block is not None:
        verbose and print(
            "%s: existing defintion for %s" % (tile_name, block_type))
        assert block["baseaddr"] == baseaddr_str
        assert block["frames"] == frames, (block, frames)
        assert block["offset"] == offset, "%s; orig offset %s, new %s" % (
            tile_name, block["offset"], offset)
        assert block["words"] == words
        return
    block = bits.setdefault(block_type, {})

    # FDRI address
    block["baseaddr"] = baseaddr_str
    # Number of frames this entry is sretched across
    # that is the following FDRI addresses are used: range(baseaddr, baseaddr + frames)
    block["frames"] = frames

    # Index of first word used within each frame
    block["offset"] = int(offset)

    # Number of words used by tile.
    block["words"] = words
