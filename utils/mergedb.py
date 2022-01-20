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

import os, sys
from utils import util


def run(fn_ins, fn_out, strict=False, track_origin=False, verbose=False):
    # tag to bits
    entries = {}
    # tag to (bits, line)
    tags = dict()
    # bits to (tag, line)
    bitss = dict()

    for fn_in in fn_ins:
        for line, (tag, bits, mode, origin) in util.parse_db_lines(fn_in):
            line = line.strip()
            assert mode is not None or mode != "always", "strict: got ill defined line: %s" % (
                line, )

            if tag in tags:
                orig_bits, orig_line, orig_origin = tags[tag]
                if orig_bits != bits:
                    print(
                        "WARNING: got duplicate tag %s" % (tag, ),
                        file=sys.stderr)
                    print("  Orig line: %s" % orig_line, file=sys.stderr)
                    print("  New line : %s" % line, file=sys.stderr)
                    assert not strict, "strict: got duplicate tag"
                origin = os.path.basename(os.getcwd())
                if track_origin and orig_origin != origin:
                    origin = orig_origin + "," + origin
            if bits in bitss:
                orig_tag, orig_line = bitss[bits]
                if orig_tag != tag:
                    print(
                        "WARNING: got duplicate bits %s" % (bits, ),
                        file=sys.stderr)
                    print("  Orig line: %s" % orig_line, file=sys.stderr)
                    print("  New line : %s" % line, file=sys.stderr)
                    assert not strict, "strict: got duplicate bits"

            if track_origin and origin is None:
                origin = os.path.basename(os.getcwd())
            entries[tag] = (bits, origin)
            tags[tag] = (bits, line, origin)
            if bits != None:
                bitss[bits] = (tag, line)

    util.write_db_lines(fn_out, entries, track_origin)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Combine multiple .db files")

    util.db_root_arg(parser)
    parser.add_argument('--verbose', action='store_true', help='')
    parser.add_argument('--track_origin', action='store_true', help='')
    parser.add_argument('--out', help='')
    parser.add_argument('ins', nargs='+', help='Last takes precedence')
    args = parser.parse_args()

    run(args.ins,
        args.out,
        strict=int(os.getenv("MERGEDB_STRICT", "1")),
        track_origin=args.track_origin,
        verbose=args.verbose)


if __name__ == '__main__':
    main()
