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

from __future__ import print_function

import fasm
import argparse
import json

from utils import fasm_assembler, util
from utils.bitstream import WORD_SIZE_BITS
from prjuray.db import Database
from utils.roi import Roi

import sys


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


class FASMSyntaxError(SyntaxError):
    pass


def dump_frames_verbose(frames):
    print()
    print("Frames: %d" % len(frames))
    for addr in sorted(frames.keys()):
        words = frames[addr]
        print('0x%08X ' % addr + ', '.join(['0x%08X' % w
                                            for w in words]) + '...')


def dump_frames_sparse(frames):
    print()
    print("Frames: %d" % len(frames))
    for addr in sorted(frames.keys()):
        words = frames[addr]

        # Skip frames without filled words
        for w in words:
            if w:
                break
        else:
            continue

        print('Frame @ 0x%08X' % addr)
        for i, w in enumerate(words):
            if w:
                print('  % 3d: 0x%08X' % (i, w))


def dump_frm(f, frames):
    '''Write a .frm file given a list of frames, containing all words within the frame'''
    for addr in sorted(frames.keys()):
        words = frames[addr]
        f.write('0x%08X ' % addr + ','.join(['0x%08X' % w
                                             for w in words]) + '\n')


def output_bits(f, frames):
    """Write a .bits file given a list of frames, with each set bit written as bit_%08x_%03d_%02d """
    for addr in sorted(frames.keys()):
        for word_idx, word in enumerate(frames[addr]):
            for bit_idx in range(WORD_SIZE_BITS):
                if (word & (1 << bit_idx)) != 0:
                    # FIXME: Convert from 16 to 32 bit words for the bits format.
                    bit32_idx = bit_idx + (word_idx & 0x1) * WORD_SIZE_BITS
                    word32_idx = (word_idx >> 1)
                    f.write('bit_{:08x}_{:03d}_{:02d}\n'.format(
                        addr, word32_idx, bit32_idx))


def run(db_root,
        part,
        filename_in,
        f_out,
        sparse=False,
        roi=None,
        debug=False,
        dump_bits=False):
    db = Database(db_root, part)
    assembler = fasm_assembler.FasmAssembler(db)

    set_features = set()

    def feature_callback(feature):
        set_features.add(feature)

    assembler.set_feature_callback(feature_callback)

    extra_features = []
    if roi:
        with open(roi) as f:
            roi_j = json.load(f)
        x1 = roi_j['info']['GRID_X_MIN']
        x2 = roi_j['info']['GRID_X_MAX']
        y1 = roi_j['info']['GRID_Y_MIN']
        y2 = roi_j['info']['GRID_Y_MAX']

        assembler.mark_roi_frames(Roi(db=db, x1=x1, x2=x2, y1=y1, y2=y2))

        if 'required_features' in roi_j:
            extra_features = list(
                fasm.parse_fasm_string('\n'.join(roi_j['required_features'])))

    # Get required extra features for the part
    required_features = db.get_required_fasm_features(part)
    extra_features += list(
        fasm.parse_fasm_string('\n'.join(required_features)))

    assembler.parse_fasm_filename(filename_in, extra_features=extra_features)

    frames = assembler.get_frames(sparse=sparse)

    if debug:
        dump_frames_sparse(frames)

    if dump_bits:
        output_bits(f_out, frames)
    else:
        dump_frm(f_out, frames)


def main():
    parser = argparse.ArgumentParser(
        description=
        'Convert FPGA configuration description ("FPGA assembly") into binary frame equivalent'
    )

    util.db_root_arg(parser)
    util.part_arg(parser)
    parser.add_argument(
        '--sparse', action='store_true', help="Don't zero fill all frames")
    parser.add_argument(
        '--roi',
        help="ROI design.json file defining which tiles are within the ROI.")
    parser.add_argument(
        '--debug', action='store_true', help="Print debug dump")
    parser.add_argument(
        '--dump_bits',
        action='store_true',
        help="Output in bits format (bit_%08x_%03d_%02d)")
    parser.add_argument('fn_in', help='Input FPGA assembly (.fasm) file')
    parser.add_argument(
        'fn_out',
        default='/dev/stdout',
        nargs='?',
        help='Output FPGA frame (.frm) file')

    args = parser.parse_args()
    run(db_root=args.db_root,
        part=args.part,
        filename_in=args.fn_in,
        f_out=open(args.fn_out, 'w'),
        sparse=args.sparse,
        roi=args.roi,
        dump_bits=args.dump_bits,
        debug=args.debug)


if __name__ == '__main__':
    main()
