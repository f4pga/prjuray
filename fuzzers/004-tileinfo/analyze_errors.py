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
import pprint


def main():
    parser = argparse.ArgumentParser(description="")

    parser.add_argument('--error_nodes', default='output/error_nodes.json')
    parser.add_argument('--output_ignore_list', action='store_true')

    args = parser.parse_args()

    with open(args.error_nodes) as f:
        flat_error_nodes = json.load(f)

    error_nodes = {}
    for node, raw_node, generated_nodes in flat_error_nodes:
        if node not in error_nodes:
            error_nodes[node] = {
                'raw_node': set(raw_node),
                'generated_nodes': set(),
            }

        assert error_nodes[node]['raw_node'] == set(raw_node)
        error_nodes[node]['generated_nodes'].add(
            tuple(sorted(generated_nodes)))

    ignored_wires = set()

    for node, error in error_nodes.items():
        combined_generated_nodes = set()
        for generated_node in error['generated_nodes']:
            combined_generated_nodes |= set(generated_node)

        # Make sure there are not extra wires in nodes.
        assert error['raw_node'] == combined_generated_nodes, pprint.pformat(
            (node, error))

        good_node = max(error['generated_nodes'], key=lambda x: len(x))
        bad_nodes = error['generated_nodes'] - set((good_node, ))

        if args.output_ignore_list:
            for generated_node in bad_nodes:
                for wire in generated_node:
                    ignored_wires.add(wire)

            continue

        if max(len(generated_node) for generated_node in bad_nodes) > 1:
            assert False, node
        else:
            not_pcie = False
            for generated_node in bad_nodes:
                for wire in generated_node:
                    if not wire.startswith('PCIE'):
                        not_pcie = True
            if not_pcie:
                #print(node, good_node, map(tuple, bad_nodes))
                print(repr((node, tuple(map(tuple, bad_nodes)))))
                pass
            else:
                #print(repr((node, map(tuple, bad_nodes))))
                pass

    if args.output_ignore_list:
        for wire in ignored_wires:
            print(wire)


if __name__ == '__main__':
    main()
