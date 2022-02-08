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
""" Reduce sites types to prototypes that are always correct.

reduce_tile_types.py generates per tile type site types.  reduce_site_types.py
takes all site types across all tiles and creates generic site types that are
valid for all tile types.

"""

import argparse
import prjuray.lib
import os
import os.path
import re
import json


def main():
    parser = argparse.ArgumentParser(
        description="Reduces per tile site types to generic site types.")
    parser.add_argument('--output_dir', required=True)

    args = parser.parse_args()

    SITE_TYPE = re.compile('^tile_type_(.+)_site_type_(.+)\.json$')
    site_types = {}
    for path in os.listdir(args.output_dir):
        match = SITE_TYPE.fullmatch(path)
        if match is None:
            continue

        site_type = match.group(2)
        if site_type not in site_types:
            site_types[site_type] = []

        site_types[site_type].append(path)

    os.makedirs(
        name=os.path.join(args.output_dir, 'site_types'), exist_ok=True)

    for site_type in site_types:
        proto_site_type = None
        for instance in site_types[site_type]:
            with open(os.path.join(args.output_dir, instance)) as f:
                instance_site_type = json.load(f)

                for site_pin in instance_site_type['site_pins'].values():
                    if 'index_in_site' in site_pin:
                        del site_pin['index_in_site']

            if proto_site_type is None:
                proto_site_type = instance_site_type
            else:
                prjuray.lib.compare_prototype_site(
                    proto_site_type,
                    instance_site_type,
                )

        with open(
                os.path.join(args.output_dir, 'site_types',
                             'site_type_{}.json'.format(site_type)), 'w') as f:
            json.dump(proto_site_type, f)


if __name__ == '__main__':
    main()
