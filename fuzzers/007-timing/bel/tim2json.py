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

import re
import argparse
import json
import functools

from utils import parse_raw_timing, merged_dict

# =============================================================================

NUMBER_RE = re.compile(r'\d+$')


def get_sdf_type(type):
    """
    Returns a SDF timing type for the given type plus information whether it
    is sequential or not. Returns None, None if the type is unknown
    """

    # Known keywords and their SDF counterparts
    seq_keywords = {
        "Setup": "setup",
        "Hold": "hold",
        "Recov": "recovery",
        "Remov": "removal",
    }

    comb_keywords = {
        "Prop": "iopath",
    }

    # Sequential
    if type in seq_keywords:
        return seq_keywords[type], True

    # Combinational
    if type in comb_keywords:
        return comb_keywords[type], False

    # Unknown
    return None, None


def parse_logical_names(phy_type, log_names, cell_pins):
    """
    Parses logical cell names. Extracts the cell name, input pin  name and
    output pin name. Uses dumped library cell definitions to achive that since
    a logical name string uses "_" as a separator and "_" can also occur in
    cell/pin name.

    Returns a list of tuples with (cell_name, src_pin, dst_pin)
    """

    log_cells = []

    # Process logical names that should correspond to bel timings
    for log_name in log_names.split(","):

        # Since both cell and pin names may also contain "_" the
        # logical name is split iteratively.

        # The timing type is the first, it has to equal the timing
        # type of the speed model
        if not log_name.startswith(phy_type):
            continue
        log_name = log_name[len(phy_type) + 1:]

        # Find the cell name in the library and strip it
        for c in cell_pins:
            if log_name.startswith(c):
                log_cell = c
                log_name = log_name[len(c) + 1:]
                break
        else:
            continue

        log_pins = cell_pins[log_cell]

        # Find the input pin in the library and strip it
        for p in log_pins:
            if log_name.startswith(p):
                log_src = p
                log_name = log_name[len(p) + 1:]
                break
        else:
            continue

        # Find the output pin in the library and strip it
        for p in log_pins:
            if log_name == p:
                log_dst = p
                break
        else:
            continue

        # Append
        log_cells.append((
            log_cell,
            log_src,
            log_dst,
        ))

    return log_cells


def read_raw_timings(fin, cell_pins):
    """
    Reads and parses raw timings, converts them into data used for SDF
    generation.
    """

    REGEX_CFG = re.compile(r".*__CFG([0-9]+)$")

    def inner():

        raw = list(parse_raw_timing(fin))
        for slice, site_name, bel_name, speed_model, properties in raw:

            # Check if we have a bel timing
            # TODO: There are other naming conventions for eg. BRAM and DSP
            if not speed_model.startswith("bel_"):
                continue

            # Get timings from properties
            timings = [(k, properties[k]) for k in [
                "DELAY",
                "FAST_MAX",
                "FAST_MIN",
                "SLOW_MAX",
                "SLOW_MIN",
            ]]

            # Get edge from the model name
            if "RISING" in speed_model:
                edge = "rising"
            elif "FALLING" in speed_model:
                edge = "falling"
            else:
                # Supposedly means either edge
                edge = None

            # Get configuration. Look for "__CFG<n>"
            # FIXME: How to correlate that with a configuration name ?
            match = REGEX_CFG.match(speed_model)
            if match is not None:
                cfg = match.group(1)
            else:
                cfg = None

            # Process physical names for the timing model. These should
            # correspond to site timings
            phy_names = properties["NAME"].split(",")
            for phy_name in phy_names:

                # Extract data from the name. Each name field should hava the
                # format: "<type>_<bel>_<site>_<src_pin>_<dst_pin>". The split
                # has to be done in complex way as the bel name may have "_"
                # within.
                phy_type, phy_name = phy_name.split("_", maxsplit=1)

                if 'URAM288' in phy_name:
                    uram_info = speed_model.split("__")
                    site = 'URAM288'
                    bel = uram_info[1]
                    phy_src = uram_info[2]
                    phy_dst = uram_info[3]
                else:
                    phy_name, phy_src, phy_dst = phy_name.rsplit(
                        "_", maxsplit=2)
                    bel_site = phy_name.rsplit("_", maxsplit=1)
                    if len(bel_site) == 2:
                        bel, site = bel_site
                    else:
                        continue

                sdf_type, is_seq = get_sdf_type(phy_type)
                if sdf_type is None:
                    continue

                # Process logical names that should correspond to bel timings
                log_cells = parse_logical_names(
                    phy_type, properties["NAME_LOGICAL"], cell_pins)

                # If we have log cells then yield them
                for log_cell, log_src, log_dst in log_cells:

                    # Format cell type
                    cell_type = log_cell

                    if edge is not None:
                        cell_type += "_{}_{}".format(log_src, edge)

                    # Format cell location
                    location = "{}/{}".format(site, bel)

                    # Yield stuff
                    key = (site_name, location, cell_type, speed_model)
                    yield (*key, "type"), cell_type.upper()
                    yield (*key, "location"), location.upper()
                    yield (*key, "model"), speed_model

                    if is_seq:
                        yield (*key, "clock"), log_src.upper()
                        yield (*key, "input"), log_dst.upper()

                    else:
                        yield (*key, "input"), log_src.upper()
                        yield (*key, "output"), log_dst.upper()

                    if is_seq:
                        yield (*key, "sequential"), sdf_type

                    for t, v in timings:
                        yield (*key, t), v

                # We don't have any logical cells, stick to the bel
                #
                # TODO: This can be modified so we always dump timing for the
                # bel regardless of if we can decode logical cells. This way
                # we may have SDFs with both bels and logical cells.
                if not len(log_cells):

                    # Format cell type
                    cell_type = bel

                    if cfg is not None:
                        cell_type += "_CFG{}".format(cfg)

                    if edge is not None:
                        cell_type += "_{}_{}".format(phy_src, edge)

                    # Format cell location
                    location = "{}/{}".format(site, bel)

                    # Yield stuff
                    key = (site_name, location, cell_type, speed_model)
                    yield (*key, "type"), cell_type.upper()
                    yield (*key, "location"), location.upper()
                    yield (*key, "model"), speed_model

                    if is_seq:
                        yield (*key, "clock"), phy_src.upper()
                        yield (*key, "input"), phy_dst.upper()

                    else:
                        yield (*key, "input"), phy_src.upper()
                        yield (*key, "output"), phy_dst.upper()

                    if is_seq:
                        yield (*key, "sequential"), sdf_type

                    for t, v in timings:
                        yield (*key, t), v

    return merged_dict(inner())


def read_cell_pins(pins_file):
    """
    Read definitions of library cell pins as extracted from Vivado
    """

    def inner():
        with open(pins_file, 'r') as f:
            for line in f:
                raw_pins = line.split()

                loc = 0
                num_cells = int(raw_pins[loc])
                loc += 1

                for cell in range(num_cells):
                    cell_name = raw_pins[loc]
                    num_pins = int(raw_pins[loc + 1])
                    loc += 2

                    for pin in range(num_pins):
                        pin_name = raw_pins[loc]
                        loc += 1

                        yield cell_name, pin_name

    cell_pins = {}
    for cell_name, pin_name in inner():

        if cell_name not in cell_pins:
            cell_pins[cell_name] = []
        cell_pins[cell_name].append(pin_name)

    return cell_pins


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--timings', type=str, help='Raw timing input file')
    parser.add_argument('--json', type=str, help='json output file')
    parser.add_argument(
        '--cellpins', type=str, help='Library cell pins input file')
    parser.add_argument(
        '--debug', action="store_true", help='Enable debug json dumps')

    args = parser.parse_args()

    cell_pins = read_cell_pins(args.cellpins)
    if args.debug:
        with open("debug_cells.json", 'w') as fp:
            json.dump(cell_pins, fp, indent=4, sort_keys=True)

    timings = read_raw_timings(args.timings, cell_pins)

    with open(args.json, 'w') as fp:
        json.dump(timings, fp, indent=4, sort_keys=True)


if __name__ == '__main__':
    main()
