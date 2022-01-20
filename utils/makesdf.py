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

import json
import argparse


def get_elems_count(timings, slice, site, bel_type):
    combinational = 0
    sequential = 0
    for delay in timings[slice][site][bel_type]:
        if 'sequential' in timings[slice][site][bel_type][delay]:
            sequential += 1
        else:
            combinational += 1
    return combinational, sequential


def produce_sdf(timings, outdir):

    for slice in timings:
        sdf = \
"""
(DELAYFILE
    (SDFVERSION \"3.0\")
    (TIMESCALE 1ns)
"""
        for site in sorted(timings[slice]):
            for bel_type in sorted(timings[slice][site]):
                combinational, sequential = get_elems_count(
                    timings, slice, site, bel_type)
                #define CELL
                cell= \
"""
    (CELL
        (CELLTYPE \"{name}\")
        (INSTANCE {location})""".format(name=bel_type.upper(), location=site)
                sdf += cell

                #define delay header (if needed)
                if combinational > 0:
                    delay_hdr = \
"""
        (DELAY
            (ABSOLUTE"""
                    sdf += delay_hdr
                    # add all delays definitions
                    for delay in sorted(timings[slice][site][bel_type]):
                        if 'sequential' in timings[slice][site][bel_type][
                                delay]:
                            continue
                        dly = \
"""
                (IOPATH {input} {output} ({FAST_MIN}::{FAST_MAX})({SLOW_MIN}::{SLOW_MAX}))""".format(**timings[slice][site][bel_type][delay])
                        if 'extra_ports' in timings[slice][site][bel_type][
                                delay] is not None:
                            dly += \
""" #extra ports {}""".format(timings[slice][site][bel_type][delay]['extra_ports'])

                        sdf += dly

                    # close DELAY definition
                    enddelay = \
"""
            )
        )"""
                    sdf += enddelay

                # define TIMINGCHECK header (if needed)
                if sequential > 0:
                    timingcheck_hdr = \
"""
        (TIMINGCHECK"""
                    sdf += timingcheck_hdr

                    for delay in sorted(timings[slice][site][bel_type]):
                        if 'sequential' not in timings[slice][site][bel_type][
                                delay]:
                            continue
                        timingcheck = \
"""
            ({prop} {input} (posedge {clock}) ({SLOW_MIN}::{SLOW_MAX}))""".format(
                        prop=timings[slice][site][bel_type][delay]['sequential'].upper(),
                        **timings[slice][site][bel_type][delay])

                        if 'extra_ports' in timings[slice][site][bel_type][
                                delay] is not None:
                            timingcheck += \
""" #extra ports {}""".format(timings[slice][site][bel_type][delay]['extra_ports'])

                        sdf += timingcheck

                    # close TIMINGCHECK definition
                    endtimingcheck = \
"""
        )"""
                    sdf += endtimingcheck

                endcell = \
"""
    )"""
                sdf += endcell
        # end of SDF
        sdf += \
"""
)"""

        with open(outdir + '/' + slice + '.sdf', "w") as fp:
            fp.write(sdf)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--json', type=str, help="Input JSON file")
    parser.add_argument('--sdf', type=str, help="SDF files output directory")

    args = parser.parse_args()

    with open(args.json, 'r') as fp:
        timings = json.load(fp)

    produce_sdf(timings, args.sdf)


if __name__ == '__main__':
    main()
