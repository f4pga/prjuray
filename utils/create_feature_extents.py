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
import os


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--extent_features', required=True)
    parser.add_argument('--root_dir', required=True)

    args = parser.parse_args()

    feature_data = {}

    for root, _, _ in os.walk(args.root_dir):
        path = os.path.join(root, 'design.features')
        if os.path.exists(path):
            with open(path) as f:
                tile_type = None
                for l in f:
                    l = l.strip()
                    if len(l) == 0:
                        continue
                    elif l.startswith('.tile'):
                        tile_type = l.split(' ')[1].split(':')[1]

                        if tile_type not in feature_data:
                            feature_data[tile_type] = set()
                    else:
                        feature_data[tile_type].add(l)

    with open(args.extent_features, 'w') as f:
        for tile_type in sorted(feature_data.keys()):
            print('.tiletype {}'.format(tile_type), file=f)
            for feature in sorted(feature_data[tile_type]):
                print(feature, file=f)


if __name__ == "__main__":
    main()
