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

import contextlib
import fasm
import argparse
import os
import tempfile
import subprocess

from utils import fasm_assembler, util
from utils.bitstream import WORD_SIZE_BITS
from prjuray.db import Database


def dump_frm(f, frames):
    '''Write a .frm file given a list of frames, containing all words within the frame'''
    for addr in sorted(frames.keys()):
        words = frames[addr]

        # FIXME: Convert from 16 to 32 bit words for the bits format.
        words32 = []
        for word0, word1 in zip(words[::2], words[1::2]):
            words32.append((word1 << WORD_SIZE_BITS) | word0)

        f.write('0x%08X ' % addr + ','.join(['0x%08X' % w
                                             for w in words32]) + '\n')


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


def fasm_to_frames(
        db_root,
        part,
        filename_in,
        sparse,
        bits_file,
        frames_file,
):
    db = Database(db_root, part)
    assembler = fasm_assembler.FasmAssembler(db)

    set_features = set()

    def feature_callback(feature):
        set_features.add(feature)

    assembler.set_feature_callback(feature_callback)

    extra_features = []

    # Get required extra features for the part
    required_features = db.get_required_fasm_features(part)
    extra_features += list(
        fasm.parse_fasm_string('\n'.join(required_features)))

    assembler.parse_fasm_filename(filename_in, extra_features=extra_features)

    frames = assembler.get_frames(sparse=sparse)

    print('Have {} frames'.format(len(frames)))

    if bits_file:
        output_bits(bits_file, frames)

    dump_frm(frames_file, frames)


def frames_to_bit(xcframes2bit, arch, part, part_yaml, frames_filename,
                  bit_filename):
    subprocess.check_output(
        '{xcframes2bit} -part_file {part_yaml} -part_name {part} -architecture {arch} -frm_file {frames_filename} -output_file {bit_filename}'
        .format(
            xcframes2bit=xcframes2bit,
            part_yaml=part_yaml,
            part=part,
            arch=arch,
            frames_filename=frames_filename,
            bit_filename=bit_filename),
        shell=True)


def main():
    parser = argparse.ArgumentParser(
        description=
        'Convert FPGA configuration description ("FPGA assembly") into bitstream.'
    )

    util.db_root_arg(parser)
    util.part_arg(parser)
    parser.add_argument(
        '--sparse', action='store_true', help="Don't zero fill all frames")
    parser.add_argument(
        '--frames-file',
        help=
        'Output filename for frame data output, default is deleted tempfile.',
        default=None)
    parser.add_argument(
        '--bits-file',
        help=
        'Output filename for frame data output, default is deleted tempfile.',
        default=None)
    parser.add_argument('fn_in', help='Input FPGA assembly (.fasm) file')
    parser.add_argument('fn_out', help='Output FPGA bitstream (.bit) file')

    if os.getenv("URAY_ARCH") is None:
        default_arch = "UltraScale"
    else:
        default_arch = os.getenv("URAY_ARCH")
    parser.add_argument(
        '--architecture',
        help=
        "Name of the device architecture family (e.g. UltraScale, Series7, etc.)",
        default=default_arch)

    if os.getenv("URAY_TOOLS_DIR") is None:
        default_xcframes2bit = 'xcframes2bit'
    else:
        default_xcframes2bit = os.path.join(
            os.getenv("URAY_TOOLS_DIR"), 'xcframes2bit')
    parser.add_argument(
        '--xcframes2bit',
        help="Path to xcframes2bit executable.",
        default=default_xcframes2bit)

    args = parser.parse_args()

    with contextlib.ExitStack() as stack:
        if args.frames_file:
            frames_file = stack.enter_context(open(args.frames_file, 'w'))
        else:
            frames_file = stack.enter_context(tempfile.NamedTemporaryFile())

        if args.bits_file:
            bits_file = stack.enter_context(open(args.bits_file, 'w'))
        else:
            bits_file = None

        fasm_to_frames(
            db_root=args.db_root,
            part=args.part,
            filename_in=args.fn_in,
            sparse=args.sparse,
            frames_file=frames_file,
            bits_file=bits_file,
        )

        frames_to_bit(
            xcframes2bit=args.xcframes2bit,
            arch=args.architecture,
            part=args.part,
            part_yaml=os.path.join(args.db_root, args.part, "part.yaml"),
            frames_filename=frames_file.name,
            bit_filename=args.fn_out)


if __name__ == '__main__':
    main()
