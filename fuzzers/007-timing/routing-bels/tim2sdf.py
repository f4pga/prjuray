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
import os
import re
from sdf_timing import sdfparse
from sdf_timing import utils

from utils import parse_raw_timing, merged_dict

# =============================================================================


def read_raw_timings(fin):
    """
    Reads and processes raw timings.
    """

    REGEX_CFG = re.compile(r".*__CFG([0-9]+)$")

    def inner():
        raw = list(parse_raw_timing(fin))
        for slice_name, site_name, bel_name, speed_model, properties in raw:

            # Get timings from properties
            timings = [(k, properties[k]) for k in [
                "DELAY",
                "FAST_MAX",
                "FAST_MIN",
                "SLOW_MAX",
                "SLOW_MIN",
            ]]

            speed_model_orig = speed_model

            # There are "bel" and "net" delays
            if speed_model.startswith("bel_"):
                is_net = False
                speed_model = speed_model[4:]

            elif speed_model.startswith("net_"):
                is_net = True
                speed_model = speed_model[4:]

            else:
                continue

            # Get configuration. Look for "__CFG<n>"
            # FIXME: How to correlate that with a configuration name ?
            match = REGEX_CFG.match(speed_model)
            if match is not None:
                cfg = match.group(1)
            else:
                cfg = None

            # Parse the rest of the model name
            fields = speed_model.split("__")
            src_pin, dst_pin = fields[2:4]

            # Cell type
            if is_net:
                cell_type = "NET"

            else:
                cell_type = bel_name
                if cfg is not None:
                    cell_type += "_CFG{}".format(cfg)

            # Cell instance
            if is_net:
                instance = site_name
            else:
                instance = "{}/{}".format(site_name, bel_name)

            # Yield stuff
            key = (site_name, cell_type, instance, speed_model)
            yield (*key, "cell_type"), cell_type.upper()
            yield (*key, "instance"), instance.upper()
            yield (*key, "input"), src_pin.upper()
            yield (*key, "output"), dst_pin.upper()
            yield (*key, "model"), speed_model
            yield (*key, "is_net"), is_net

            for t, v in timings:
                yield (*key, t), v

    return merged_dict(inner())


def add_timing_paths_entry(paths, type, values):
    """
    Builds a timing paths entry for the SDF writer
    """
    paths[type] = dict()
    paths[type]['min'] = values[0]
    paths[type]['avg'] = values[1]
    paths[type]['max'] = values[2]

    return paths


def generate_sdfs(timing_data, sdf_path):
    """
    Builds and writes SDF files using the given timing data.
    """

    def make_speed_model(data):
        """
        Makes a speed model structure for the SDF writer
        """
        model = dict()

        # Create entry for sdf writer
        iport = dict()
        iport['port'] = data["input"]
        iport['port_edge'] = None
        oport = dict()
        oport['port'] = data["output"]
        oport['port_edge'] = None

        paths = dict()
        paths = add_timing_paths_entry(
            paths, 'slow', [data['SLOW_MIN'], None, data['SLOW_MAX']])
        paths = add_timing_paths_entry(
            paths, 'fast', [data['FAST_MIN'], None, data['FAST_MAX']])

        # Net delay
        if data["is_net"]:
            model = utils.add_interconnect(iport, oport, paths)
            model["is_absolute"] = True

        # Routing bel delay
        else:
            model = utils.add_iopath(iport, oport, paths)
            model["is_absolute"] = True

        return model

    # Build SDF structures
    sdf_data = dict()
    for site_name, site_data in timing_data.items():

        # New SDF
        if site_name not in sdf_data:
            sdf_data[site_name] = dict()
            sdf_data[site_name]["cells"] = dict()

        for cell_type, cell_data in site_data.items():

            # New celltype
            if cell_type not in sdf_data[site_name]["cells"]:
                sdf_data[site_name]["cells"][cell_type] = dict()

            for instance, instance_data in cell_data.items():

                # New cell instance
                if instance not in sdf_data[site_name]["cells"][cell_type]:
                    sdf_data[site_name]["cells"][cell_type][instance] = dict()

                # Add speed models
                for speed_model, speed_data in instance_data.items():
                    sdf_data[site_name]["cells"][cell_type][instance][
                        speed_model] = make_speed_model(speed_data)

    # Emit SDFs
    for name, data in sdf_data.items():
        fname = os.path.join(sdf_path, name.upper() + ".sdf")
        fdata = sdfparse.emit(data, timescale='1ns')

        with open(fname, "w") as fp:
            fp.write(fdata)


# =============================================================================


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--timings', type=str, help='Raw timing input file')
    parser.add_argument('--sdf', type=str, help='output sdf directory')
    parser.add_argument(
        '--debug', action="store_true", help='Enable debug json dumps')
    args = parser.parse_args()

    timings = read_raw_timings(args.timings)
    if args.debug:
        with open("debug.json", 'w') as fp:
            json.dump(timings, fp, indent=4, sort_keys=True)

    generate_sdfs(timings, args.sdf)


if __name__ == '__main__':
    main()
