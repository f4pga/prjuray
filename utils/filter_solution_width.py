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
""" Filters solution segbits files based on number of bits in solution.

Once the structure of solutions are identified, it is likely the number of
bits expected in the solution can be specified.  This tool consumes an input
segbits files and filters output lines that violates one of specified rules.
Rules are specified as a pair of a regular express and the maximum number of
expected bit allowed.

Filters are applied in the order in which they are defined.

A default width can be specified with the expression ".default_width"

Example solution_widths file:

    .default_width 2
    RCLK_[^.]+\.PIP\.[^.]+.CLK_CMT_DRVR_TRI_ESD_[0-9]{1,2}_CLK_OUT_SCHMITT_B 2

"""
import argparse
import re


def parse_solution_widths(solution_widths):
    default_width = None
    filters = []

    with open(solution_widths) as f:
        for l in f:
            l = l.strip()

            parts = l.split(' ')
            assert len(parts) == 2

            if parts[0] == '.default_width':
                assert default_width is None
                default_width = int(parts[1])
            else:
                filters.append((re.compile(parts[0]), int(parts[1])))

    return default_width, filters


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input_rdb', required=True)
    parser.add_argument('--solution_widths', required=True)
    parser.add_argument('--output_rdb', required=True)
    parser.add_argument('--filtered_features', required=True)

    args = parser.parse_args()
    default_width, filters = parse_solution_widths(args.solution_widths)

    with open(args.input_rdb) as f, open(args.output_rdb, 'w') as f_out, open(
            args.filtered_features, 'w') as f_filtered:
        for l in f:
            if '<' in l:
                print(l.strip(), file=f_out)
                continue

            parts = l.strip().split(' ')

            found_filter = False

            for filter_re, max_bits in filters:
                if filter_re.fullmatch(parts[0]) is not None:
                    if len(parts) - 1 > max_bits:
                        print(l.strip(), file=f_filtered)
                    else:
                        print(l.strip(), file=f_out)
                    found_filter = True
                    break

            if not found_filter:
                if len(parts) - 1 > default_width:
                    print(l.strip(), file=f_filtered)
                else:
                    print(l.strip(), file=f_out)


if __name__ == '__main__':
    main()
