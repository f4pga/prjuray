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
import numpy as np

from utils.lut_maker import LutMaker


def get_ps8_pin_map():
    m = {}
    with open('../ps8_pin_map.csv') as f:
        for row in csv.DictReader(f):
            m[row['site_pin']] = row['pin']

    return m


def print_top(seed):
    np.random.seed(seed)

    ps8_pin_map = get_ps8_pin_map()

    print('''
module top();
    ''')

    luts = LutMaker()

    ps8_pin_map = get_ps8_pin_map()

    bus_widths = {}
    for pin in ps8_pin_map.values():
        parts = pin.split('/')[-1].split('[')

        if len(parts) == 1:
            bus_widths[parts[0]] = 1
        elif len(parts) == 2:
            if parts[0] not in bus_widths:
                bus_widths[parts[0]] = 0

            width = int(parts[1][:-1]) + 1
            if width > bus_widths[parts[0]]:
                bus_widths[parts[0]] = width
        else:
            assert False, pin

    sinks = []

    ipins = []
    opins = []

    ipin_source = []

    ps8_inputs = []
    ps8_outputs = []

    ps8_interface_tiles = {}
    ps8_outputs_per_tile = {}

    with open('../ps8_intf.csv') as f:
        for row in csv.DictReader(f):
            ps8_outputs.append(row)
            ps8_interface_tiles[row['ps8_intf_tile']] = None

    with open('../ps8_intf_inputs.csv') as f:
        for row in csv.DictReader(f):
            ps8_inputs.append(row)
            ps8_interface_tiles[row['ps8_intf_tile']] = None

    for tile in sorted(ps8_interface_tiles.keys()):
        ps8_interface_tiles[tile] = np.random.choice(('I', 'O', 'IO', None))
        if ps8_interface_tiles[tile] in ['O', 'IO']:
            ps8_outputs_per_tile[tile] = np.random.randint(1, 8)

    for row in ps8_outputs:
        tile, wire = row['ps8_intf_wire'].split('/')
        assert row['ps8_intf_tile'] == tile, (row['ps8_intf_tile'], tile)

        if row['ps8_site_pin'] not in ps8_pin_map:
            continue

        if ps8_interface_tiles[tile] not in ['O', 'IO']:
            continue

        if ps8_outputs_per_tile[tile] <= 0:
            continue

        ps8_outputs_per_tile[tile] -= 1

        pin = ps8_pin_map[row['ps8_site_pin']].split('/')[-1]

        if np.random.randint(2):
            sinks.append(luts.get_next_input_net())
            opins.append(pin)

    input_nodes = {}
    for row in ps8_inputs:
        tile, wire = row['ps8_intf_wire'].split('/')
        assert row['ps8_intf_tile'] == tile, (row['ps8_intf_tile'], tile)

        if row['ps8_site_pin'] not in ps8_pin_map:
            continue

        if ps8_interface_tiles[tile] not in ['I', 'IO']:
            continue

        pin = ps8_pin_map[row['ps8_site_pin']].split('/')[-1]

        ipins.append(pin)
        ipin_source.append((pin, luts.get_next_output_net()))
        input_nodes[pin] = (row['xiphy_node'], row['int_node'],
                            row['input_node'])

    print('\n'.join(luts.create_wires_and_luts()))

    sinks.sort()
    np.random.shuffle(sinks)

    busses = set()

    for pin in opins:
        busses.add(pin.split('[')[0])

    for pin in ipins:
        busses.add(pin.split('[')[0])

    for bus in busses:
        print('wire [{width}-1:0] {bus};'.format(
            bus=bus, width=bus_widths[bus]))

    print('PS8 ps8 (')

    connections = []
    for bus in busses:
        connections.append('  .{bus}({bus})'.format(bus=bus))
    print(',\n'.join(connections))

    print('\n);')

    for pin in opins:
        print('assign {sink} = {pin};'.format(pin=pin, sink=sinks.pop()))

    ipin_source.sort()
    np.random.shuffle(ipin_source)

    with open('complete_top.tcl', 'w') as f:
        print('source $::env(URAY_UTILS_DIR)/utils.tcl', file=f)
        print('place_design -directive Quick', file=f)

        for idx, (pin, source) in enumerate(ipin_source):
            if idx > 100:
                print('assign {pin} = 0;'.format(pin=pin, source=source))
                continue

            print('assign {pin} = {source};'.format(pin=pin, source=source))
            xiphy_node, int_node, input_node = input_nodes[pin]

            print(
                'optionally_route_ps8_interface {source_bel} {int_node} {xiphy_node} {input_node} {isone}'
                .format(
                    source_bel='_'.join(source.split('_')[:-1]),
                    int_node=int_node,
                    xiphy_node=xiphy_node,
                    input_node=input_node,
                    isone=np.random.randint(2)),
                file=f)

        print('route_design -directive Quick', file=f)

    print('endmodule')
