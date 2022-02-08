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
import glob
import os
import subprocess


def unify_tile_types(tile):
    """ Some tile types share bits, and can be solved together.

    This function maps specific tile types to their more generic name.
    """

    if tile in ['rclk_int_l', 'rclk_int_r']:
        return 'rclk_int'

    if tile in ['rclk_clel_l_l', 'rclk_clem_r', 'rclk_clem_l']:
        return 'rclk_cle'

    if tile in [
            'rclk_bram_intf_l', 'rclk_bram_intf_td_l', 'rclk_bram_intf_td_r'
    ]:
        return 'rclk_bram_intf'

    if tile in ['rclk_dsp_intf_l', 'rclk_dsp_intf_r']:
        return 'rclk_dsp_intf'

    return tile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--filter_across_groups',
        help='Filter out bits that match between groups',
        action='store_true')
    parser.add_argument(
        '--filter_solution_width',
        help='Filter out bits based on the number of bits found')
    parser.add_argument(
        '--filter_out',
        help='Filter out bits based on supplied regular expressions in a file')
    parser.add_argument(
        '--iob_features',
        help=
        'Cleanup IOB features using a regular expressions to identify IOB features.'
    )
    parser.add_argument('-c', '--max_count', type=int, default=None)

    args = parser.parse_args()

    types = set()

    for p in glob.glob('**/segdata_*.txt', recursive=True):
        s = os.path.basename(p)
        types.add(s[s.find('_') + 1:-4])

    procs = []
    unified_tile_types = {}
    for t in sorted(types):
        input_files = glob.glob('**/segdata_{}.txt'.format(t), recursive=True)

        unified_type = unify_tile_types(t)

        if unified_type not in unified_tile_types:
            unified_tile_types[unified_type] = []

        unified_tile_types[unified_type].extend(input_files)

    segmatch_opts = ''
    if args.max_count is not None:
        segmatch_opts = '-c {}'.format(args.max_count)

    for t in sorted(unified_tile_types.keys()):
        cmd = '$URAY_SEGMATCH {} -o segbits_{}.rdb {}'.format(
            segmatch_opts, t, ' '.join(sorted(unified_tile_types[t])))
        procs.append(
            subprocess.Popen(
                cmd,
                shell=True,
                stdout=open('segmatch_{}.txt'.format(t), 'wb')))

    for p in procs:
        p.wait()

    procs = []

    for t in sorted(unified_tile_types.keys()):
        root_to_group = {}
        with open('segbits_{}.rdb'.format(t)) as f:
            for l in f:
                l = l.strip()
                feature = l.split(' ')[0]
                if '[' in feature:
                    continue

                parts = feature.split('.')
                if len(parts) > 2:
                    root = '.'.join(parts[:-1])

                    if root not in root_to_group:
                        root_to_group[root] = set()

                    root_to_group[root].add(feature)

        with open('{}_groups.txt'.format(t), 'w') as fout:
            for group in root_to_group.values():
                if len(group) > 1:
                    print(' '.join(group), file=fout)

        extra_args = []

        rdb_ext = 'rdb'

        if args.filter_solution_width:
            subprocess.check_call(
                'python3 $URAY_UTILS_DIR/filter_solution_width.py --input_rdb segbits_{t}.{rdb_ext} --output_rdb segbits_{t}.rdb2 --solution_widths {filter_solution_width} --filtered_features segbits_{t}.filtered'
                .format(
                    t=t,
                    rdb_ext=rdb_ext,
                    filter_solution_width=args.filter_solution_width),
                shell=True)
            rdb_ext = 'rdb2'

        if args.filter_out:
            subprocess.check_call(
                'python3 $URAY_UTILS_DIR/filter_features.py --input_rdb segbits_{t}.{rdb_ext}  --output_rdb segbits_{t}.rdb3 --filters {filter_out}'
                .format(t=t, rdb_ext=rdb_ext, filter_out=args.filter_out),
                shell=True)
            rdb_ext = 'rdb3'

        if args.iob_features:
            subprocess.check_call(
                'python3 $URAY_UTILS_DIR/iob_cleanup.py --rdb_in segbits_{t}.{rdb_ext} --rdb_out segbits_{t}.rdb4 --iob_features {iob_features}'
                .format(t=t, rdb_ext=rdb_ext, iob_features=args.iob_features),
                shell=True,
                stdout=open('iob_cleanup_{}.txt'.format(t), 'wb'))
            rdb_ext = 'rdb4'

        if args.filter_across_groups:
            extra_args.append('--filter_across_groups')

        procs.append(
            subprocess.Popen(
                'python3 $URAY_UTILS_DIR/dbfixup.py --seg-fn-in segbits_{t}.{rdb_ext} --seg-fn-out segbits_{t}.db -g {t}_groups.txt {extra_args}'
                .format(t=t, rdb_ext=rdb_ext, extra_args=' '.join(extra_args)),
                shell=True,
                stdout=open('dbfixup_{}.txt'.format(t), 'wb')))

    for p in procs:
        p.wait()


if __name__ == "__main__":
    main()
