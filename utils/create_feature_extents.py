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
