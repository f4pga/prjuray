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

import argparse
import json
from sdf_timing import sdfparse


def merge(timings_list, site):

    merged_timings = dict()

    for timings in timings_list:
        divider = '/'
        if 'divider' in timings['header']:
            divider = timings['header']['divider']

        for cell in timings['cells']:
            for cell_instance in timings['cells'][cell]:
                if site in cell_instance.split(divider):
                    if 'cells' not in merged_timings:
                        merged_timings['cells'] = dict()
                    if cell not in merged_timings['cells']:
                        merged_timings['cells'][cell] = dict()
                    if cell_instance not in merged_timings['cells'][cell]:
                        merged_timings['cells'][cell][cell_instance] = dict()

                    if cell_instance in merged_timings['cells'][cell][
                            cell_instance]:
                        assert merged_timings['cells'][cell][cell_instance] == \
                               timings['cells'][cell][cell_instance],          \
                               "Attempting to merge differing cells"

                    merged_timings['cells'][cell][cell_instance] = timings[
                        'cells'][cell][cell_instance]

    return merged_timings


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--sdfs', nargs='+', type=str, help="List of sdf files to merge")
    parser.add_argument('--site', type=str, help="Site we want to merge")
    parser.add_argument('--json', type=str, help="Debug JSON")
    parser.add_argument('--out', type=str, help="Merged sdf name")

    args = parser.parse_args()

    timings_list = list()

    for sdf in args.sdfs:
        with open(sdf, 'r') as fp:
            timing = sdfparse.parse(fp.read())
            timings_list.append(timing)

    merged_sdf = merge(timings_list, args.site)
    open(args.out, 'w').write(sdfparse.emit(merged_sdf, timescale='1ns'))

    if args.json is not None:
        with open(args.json, 'w') as fp:
            json.dump(merged_sdf, fp, indent=4, sort_keys=True)


if __name__ == '__main__':
    main()
