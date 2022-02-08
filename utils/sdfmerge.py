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
