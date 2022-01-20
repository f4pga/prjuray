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
import re


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_rdb', required=True)
    parser.add_argument('--output_rdb', required=True)
    parser.add_argument('--filters', required=True)

    args = parser.parse_args()

    filters = []
    with open(args.filters) as f:
        for l in f:
            filters.append(re.compile(l.strip()))

    with open(args.input_rdb) as f_in, open(args.output_rdb, 'w') as f_out:
        for l in f_in:
            filter_out = False
            for filt in filters:
                if filt.fullmatch(l.strip()) is not None:
                    filter_out = True
                    break

            if filter_out:
                continue

            f_out.write(l)


if __name__ == "__main__":
    main()
