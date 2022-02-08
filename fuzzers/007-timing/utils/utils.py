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


def merged_dict(itr):
    """ Create a merged dict of dict (of dict) based on input.

    Input is an iteratable of (keys, value).

    Return value is root dictionary

    Keys are successive dictionaries indicies.  For example:
    (('a', 'b', 'c'), 1)

    would set:

    output['a']['b']['c'] = 1

    This function returns an error if two values conflict.

    >>> merged_dict(((('a', 'b', 'c'), 1), (('a', 'b', 'd'), 2)))
    {'a': {'b': {'c': 1, 'd': 2}}}

    """

    output = {}
    for keys, value in itr:
        target = output
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]

        if keys[-1] in target:
            assert target[keys[-1]] == value, (keys, value, target[keys[-1]])
        else:
            target[keys[-1]] = value

    return output


def parse_raw_timing(fin):
    """
    Parses raw timing data as dumped from Vivado.
    """

    with open(fin, "r") as f:
        for line in f:
            raw_data = line.split()
            slice = raw_data[0]

            sites_count = int(raw_data[1])
            loc = 2
            for site in range(0, sites_count):

                site_name = raw_data[loc]
                bels_count = int(raw_data[loc + 1])

                # read all BELs data within
                loc += 2
                for bel in range(0, bels_count):
                    bel = raw_data[loc]
                    delay_count = int(raw_data[loc + 1])

                    # get all the speed models
                    loc += 2
                    for delay in range(0, delay_count):
                        speed_model = raw_data[loc]
                        property_count = int(raw_data[loc + 1])

                        # Get all properties
                        properties = {}
                        loc += 2
                        for i in range(property_count):
                            k, v = raw_data[loc].split(":")
                            properties[k] = v
                            loc += 1

                        yield slice, site_name, bel, speed_model, properties
