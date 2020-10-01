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
'''
Take bitstream .bit files and decode them to FASM.
'''

import contextlib
import os
import fasm
import fasm.output
from prjuray.db import Database
import fasm_disassembler
import bitstream
import subprocess
import tempfile


def bit_to_bits(bitread,
                part_yaml,
                arch,
                bit_file,
                bits_file,
                frame_range=None):
    """ Calls bitread to create bits (ASCII) from bit file (binary) """
    if frame_range:
        frame_range_arg = '-F {}'.format(frame_range)
    else:
        frame_range_arg = ''

    subprocess.check_output(
        '{} -E --part_file {} --architecture {} {} -o {} -z -y {}'.format(
            bitread, part_yaml, arch, frame_range_arg, bits_file, bit_file),
        shell=True)


def bits_to_fasm(db_root, part, bits_file, verbose, canonical,
                 suppress_zero_features):
    db = Database(db_root, part)
    grid = db.grid()
    disassembler = fasm_disassembler.FasmDisassembler(db)

    with open(bits_file) as f:
        bitdata = bitstream.load_bitdata(f, bitstream.WORD_SIZE_BITS)

    model = fasm.output.merge_and_sort(
        disassembler.find_features_in_bitstream(bitdata, verbose=verbose),
        zero_function=disassembler.is_zero_feature,
        sort_key=grid.tile_key,
    )

    if suppress_zero_features:
        output_lines = []

        for line in model:
            if line.set_feature is None:
                output_lines.append(line)
            elif not disassembler.is_zero_feature(line.set_feature.feature):
                output_lines.append(line)

        print(
            fasm.fasm_tuple_to_string(output_lines, canonical=canonical),
            end='')
    else:
        print(fasm.fasm_tuple_to_string(model, canonical=canonical), end='')


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Convert UltraScale/UltraScalePlus bit file to FASM.')

    database_dir = os.getenv("URAY_DATABASE_DIR")
    database = os.getenv("URAY_DATABASE")
    db_root_kwargs = {}
    if database_dir is None or database is None:
        db_root_kwargs['required'] = True
    else:
        db_root_kwargs['required'] = False
        db_root_kwargs['default'] = os.path.join(database_dir, database)

    default_part = os.getenv("URAY_PART")
    part_kwargs = {}
    if default_part is None:
        part_kwargs['required'] = True
    else:
        part_kwargs['required'] = False
        part_kwargs['default'] = default_part

    if os.getenv("URAY_TOOLS_DIR") is None:
        default_bitread = 'bitread'
    else:
        default_bitread = os.path.join(os.getenv("URAY_TOOLS_DIR"), 'bitread')

    if os.getenv("URAY_ARCH") is None:
        default_arch = "UltraScale"
    else:
        default_arch = os.getenv("URAY_ARCH")

    parser.add_argument('--db-root', help="Database root.", **db_root_kwargs)
    parser.add_argument(
        '--bits-file',
        help="Output filename for bitread output, default is deleted tempfile.",
        default=None)
    parser.add_argument(
        '--part', help="Name of part being targetted.", **part_kwargs)
    parser.add_argument(
        '--bitread',
        help="Name of part being targetted.",
        default=default_bitread)
    parser.add_argument(
        '--architecture',
        help=
        "Name of the device architecture family (e.g. UltraScale, Series7, etc.)",
        default=default_arch)
    parser.add_argument(
        '--frame_range', help="Frame range to use with bitread.")
    parser.add_argument('bit_file', help='')
    parser.add_argument(
        '--verbose',
        help='Print lines for unknown tiles and bits',
        action='store_true')
    parser.add_argument(
        '--canonical', help='Output canonical bitstream.', action='store_true')
    parser.add_argument(
        '--suppress_zero_features',
        help='Supress zero features.',
        action='store_true')
    args = parser.parse_args()

    with contextlib.ExitStack() as stack:
        if args.bits_file:
            bits_file = stack.enter_context(open(args.bits_file, 'wb'))
        else:
            bits_file = stack.enter_context(tempfile.NamedTemporaryFile())

        bit_to_bits(
            bitread=args.bitread,
            part_yaml=os.path.join(args.db_root, args.part, "part.yaml"),
            arch=args.architecture,
            bit_file=args.bit_file,
            bits_file=bits_file.name,
            frame_range=args.frame_range,
        )

        bits_to_fasm(
            db_root=args.db_root,
            part=args.part,
            bits_file=bits_file.name,
            verbose=args.verbose,
            canonical=args.canonical,
            suppress_zero_features=args.suppress_zero_features)


if __name__ == '__main__':
    main()
