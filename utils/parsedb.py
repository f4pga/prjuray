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

import sys
import re
import util


def run(fnin, fnout=None, strict=False, verbose=False):
    lines = open(fnin, 'r').read().split('\n')
    tags = dict()
    bitss = dict()
    for line in lines:
        line = line.strip()
        if line == '':
            continue
        # TODO: figure out what to do with masks
        if line.startswith("bit "):
            continue
        tag, bits, mode, _ = util.parse_db_line(line)
        if strict:
            if mode != "always":
                assert not mode, "strict: got ill defined line: %s" % (line, )
            if tag in tags:
                print("Original line: %s" % tags[tag], file=sys.stderr)
                print("New line: %s" % line, file=sys.stderr)
                assert 0, "strict: got duplicate tag %s" % (tag, )
            assert bits not in bitss, "strict: got duplicate bits %s: %s %s" % (
                bits, tag, bitss[bits])
        tags[tag] = line
        if bits != None:
            bitss[bits] = tag

    if fnout:
        with open(fnout, "w") as fout:
            for line in sorted(lines):
                line = line.strip()
                if line == '':
                    continue
                fout.write(line + '\n')


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Parse a db file, checking for consistency")

    util.db_root_arg(parser)
    parser.add_argument('--verbose', action='store_true', help='')
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Complain on unresolved entries (ex: <0 candidates>, <const0>)')
    parser.add_argument('fin', help='')
    parser.add_argument('fout', nargs='?', help='')
    args = parser.parse_args()

    run(args.fin, args.fout, strict=args.strict, verbose=args.verbose)


if __name__ == '__main__':
    main()
