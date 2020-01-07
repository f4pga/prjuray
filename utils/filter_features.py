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
