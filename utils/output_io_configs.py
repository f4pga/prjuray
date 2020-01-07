#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2020 Project U-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file.
#
# SPDX-License-Identifier: ISC

from utils.io_utils import bank_planner2, read_io_pins
import numpy as np


def main():
    with open('../iopins.csv') as f:
        bank_type_to_tiles, tile_to_pins, pin_to_banks, pin_to_site_offsets, pin_to_tile_types = read_io_pins(
            f)

    pin_to_tiles = {}

    for bank_type, tiles in bank_type_to_tiles.items():
        pins = []
        for tile in tiles:
            pins.extend(tile_to_pins[tile])

            for pin in tile_to_pins[tile]:
                pin_to_tiles[pin] = tile

        count = 0
        for _ in bank_planner2(
                random_lib=np.random,
                bank_type=bank_type,
                single_ended=True,
                pins=pins,
                pin_to_banks=pin_to_banks,
                pin_to_site_offsets=pin_to_site_offsets,
                pin_to_tile_types=pin_to_tile_types,
                pin_to_tiles=pin_to_tiles,
        ):
            count += 1

        print(bank_type, count)


if __name__ == "__main__":
    main()
