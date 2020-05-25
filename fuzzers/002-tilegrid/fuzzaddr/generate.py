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

from utils import bitsmaker
import os

FRAME_ADDRESS_ALIGNMENT = 0x80 if (
    os.getenv('URAY_ARCH') == 'UltraScale') else 0x100


def run(bits_fn,
        design_fn,
        fnout,
        oneval,
        dframe,
        auto_frame,
        dword,
        dbit,
        multi=False,
        filter_words=None,
        filter_frames=None,
        verbose=False):
    # mimicing tag names, wasn't sure if it would break things otherwise
    metastr = "DWORD:%u" % dword
    if dbit is not None:
        metastr += ".DBIT:%u" % dbit
    if dframe is not None:
        metastr += ".DFRAME:%02x" % dframe
    if multi:
        metastr += ".MULTI"
    if auto_frame:
        metastr += ".AUTO_FRAME"

    tags = dict()
    f = open(design_fn, 'r')
    f.readline()
    for l in f:
        l = l.strip()
        # Additional values reserved / for debugging
        tile, val = l.split(',')[0:2]
        tags["%s.%s" % (tile, metastr)] = val == oneval

    bitfilter = None

    if filter_words is not None or filter_frames is not None:
        bitfilter = lambda frame, word: not ((filter_frames is not None and (frame % FRAME_ADDRESS_ALIGNMENT) in filter_frames) or (filter_words is not None and word in filter_words))

    bitsmaker.write(bits_fn, fnout, tags, bitfilter)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description=
        "Solve bits (like segmaker) on raw .bits file without segments")
    parser.add_argument("--bits-file", default="design.bits", help="")
    parser.add_argument("--verbose", action="store_true", help="")
    parser.add_argument("--design", default="design.csv", help="")
    parser.add_argument("--fnout", default="/dev/stdout", help="")
    parser.add_argument(
        "--oneval",
        required=True,
        help="Parameter value that correspodns to a set bit")
    #
    parser.add_argument(
        "--multi", action="store_true", help="Are multiple bits expected?")
    parser.add_argument(
        "--dframe",
        type=str,
        required=False,
        default="",
        help="Reference frame delta (base 16)")
    parser.add_argument(
        "--auto_frame",
        action='store_true',
        help="Auto align frame address to next lowest multiple of 0x80")
    parser.add_argument(
        "--dword",
        type=str,
        required=True,
        help="Reference word delta (base 10)")
    parser.add_argument(
        "--dbit",
        type=str,
        required=False,
        default="",
        help="Reference bit delta (base 10)")
    parser.add_argument(
        "--filter_words",
        required=False,
        default=None,
        help="Filter out word from bit data")
    parser.add_argument(
        "--filter_frames",
        required=False,
        default=None,
        help="Filter out frames from bit data")
    args = parser.parse_args()

    filter_words = None
    if args.filter_words is not None:
        filter_words = list(map(int, args.filter_words.split(',')))

    filter_frames = None
    if args.filter_frames is not None:
        filter_frames = list(
            map(lambda x: int(x, 16), args.filter_frames.split(',')))

    run(args.bits_file,
        args.design,
        args.fnout,
        args.oneval,
        None if args.dframe == "" else int(args.dframe, 16),
        args.auto_frame,
        int(args.dword, 10),
        None if args.dbit == "" else int(args.dbit, 10),
        multi=args.multi,
        filter_words=filter_words,
        filter_frames=filter_frames,
        verbose=args.verbose)


if __name__ == "__main__":
    main()
