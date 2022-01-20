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

import csv
from utils.clock_utils import MAX_GLOBAL_CLOCKS
import random


def output_iteration(tile, bufg_inputs, bufg_outputs):
    """ Output 1 iteration of BUFG_PS inputs -> BUFG_PS outputs.

    This function generates a set of permutations of 1-18 BUFG input pins to
    one of the 24 BUFG_PS output pins.  Each iteration ensures that each input
    reachs each of the outputs.

    Only 1 iteration of this function is required to ensure that all available
    inputs reach all available outputs, but this function does not ensure
    uncorrelated solutions.  More iterations increase the change of an
    uncorrelated solution.

    """
    inputs_to_sinks = {}

    for idx, _ in enumerate(bufg_inputs):
        inputs_to_sinks[idx] = sorted(bufg_outputs)
        random.shuffle(inputs_to_sinks[idx])

    while True:
        outputs = {}

        inputs = sorted(inputs_to_sinks.keys())
        random.shuffle(inputs)

        for idx in inputs:
            for output in inputs_to_sinks[idx]:
                if output not in outputs:
                    outputs[output] = idx
                    break

            if output in outputs and outputs[output] == idx:
                inputs_to_sinks[idx].remove(output)

        if len(outputs) == 0:
            break

        output_str = ["" for _ in bufg_outputs]
        for output in outputs:
            output_str[output] = str(outputs[output])

        print('{},{}'.format(tile, ','.join(output_str)))


def main():
    random.seed(0)
    bufg_inputs_to_tiles = {}
    with open('ps8_bufg_pin_map.csv') as f:
        for row in csv.DictReader(f):
            clock_tiles = row['clock_tiles'].split(' ')
            assert len(clock_tiles) == 1, (row['pin'], clock_tiles)

            tile = clock_tiles[0]

            if tile not in bufg_inputs_to_tiles:
                bufg_inputs_to_tiles[tile] = []

            bufg_inputs_to_tiles[tile].append(row['pin'].split('/')[0])

    bufg_outputs = list(range(MAX_GLOBAL_CLOCKS))

    print('tile,{}'.format(','.join(
        'bufg{}_input'.format(output) for output in bufg_outputs)))

    NUM_ITERATIONS = 3
    for _ in range(NUM_ITERATIONS):
        for tile in bufg_inputs_to_tiles:
            output_iteration(tile, bufg_inputs_to_tiles[tile], bufg_outputs)


if __name__ == "__main__":
    main()
