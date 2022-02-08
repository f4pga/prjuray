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

import json
import os
from utils import util

# Break frames into WORD_SIZE bit words.
from prjuray.bitstream import WORD_SIZE_BITS

# How many 16-bit words for frame in a US+ bitstream?
from prjuray.bitstream import FRAME_WORD_COUNT

# What alignment is expect for columns.
from prjuray.bitstream import FRAME_ALIGNMENT
'''
Sample:
bit_0002000f_079_06

Where:
-0002000f: FDRI address
-079: FDIR word number (0-100)
-06: bit index (0-31)
'''


def load_bitdata(f, word_size_bits):
    """ Read bit file and return bitdata map.
    Similar to segbits file

    bitdata is a map of of two sets.
    The map key is the frame address.
    The first sets are the word columns that have any bits set.
    Word columsn are word_size_bits wide.
    The second sets are bit index within the frame and word if it is set.
    """
    bitdata = dict()

    for line in f:
        line = line.split("_")
        frame = int(line[1], 16)
        wordidx = int(line[2], 10) * (32 // word_size_bits) + int(
            line[3], 10) // word_size_bits
        bitidx = int(line[3], 10) % word_size_bits

        if frame not in bitdata:
            bitdata[frame] = set(), set()

        bitdata[frame][0].add(wordidx)
        bitdata[frame][1].add(wordidx * word_size_bits + bitidx)

    return bitdata


# used by segprint
# TODO: merge these
def load_bitdata2(f):
    '''
    return as bitdata[frame][wordidx].add(bitidx)
    ie indexed by frame, word index, and then a set with bit indexes
    Similar to .bits file: bit_00020012_014_20
    '''

    bitdata = dict()

    for lineraw in f:
        lineraw = lineraw.strip()
        line = lineraw.split("_")
        try:
            frame = int(line[1], 16)
            wordidx = int(line[2], 10)
            bitidx = int(line[3], 10)
        except:
            print("Invalid line %s" % lineraw)
            raise

        if frame not in bitdata:
            bitdata[frame] = dict()

        if wordidx not in bitdata[frame]:
            bitdata[frame][wordidx] = set()

        bitdata[frame][wordidx].add(bitidx)
    return bitdata


def gen_part_base_addrs():
    """
    Return (block_type, top_bottom, cfg_row, cfg_col, frame_count)
    Where:
    -block_type ("bus"): typically CLB_IO_CLK, sometimes BLOCK_RAM
    -top_bottom: either "top" or "bottom"
    -cfg_row: a relative row
    -cfg_col: a relative column
    -frame_count: number of frames to fully configure this minor address

    Example:
    ('CLB_IO_CLK', 'bottom', 0, 3, 36)
    ('BLOCK_RAM', 'top', 0, 1, 128)
    ('CLB_IO_CLK', 'top', 1, 34, 28)
    """
    fn = os.getenv("URAY_PART_YAML").replace(".yaml", ".json")
    j = json.load(open(fn, "r"))
    for tbk, tbv in j["global_clock_regions"].items():
        for rowk, rowv in tbv["rows"].items():
            for busk, busv in rowv["configuration_buses"].items():
                for colk, colv in busv["configuration_columns"].items():
                    yield (busk, tbk, int(rowk), int(colk),
                           colv["frame_count"])


def addr_bits2word(block_type, top_bottom, cfg_row, cfg_col, minor_addr):
    """Convert a deconstructed address to a 32 bit word"""
    # https://www.xilinx.com/support/documentation/user_guides/ug470_7Series_Config.pdf
    ret = 0
    ret |= util.block_type_s2i[block_type] << 23
    ret |= {"top": 0, "bottom": 1}[top_bottom] << 22
    ret |= cfg_row << 17
    ret |= cfg_col << 7
    ret |= minor_addr
    return ret
