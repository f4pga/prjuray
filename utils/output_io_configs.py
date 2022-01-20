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
