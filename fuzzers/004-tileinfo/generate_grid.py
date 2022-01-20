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
""" Generate grid from database dump """

from __future__ import print_function
import argparse
import multiprocessing
import progressbar
import os.path
import json
import datetime
import pickle
import sys
from collections import namedtuple

from utils import util, tile_sizes
from utils.xjson import extract_numbers

from prjuray import lib, connections

TileConnection = namedtuple('TileConnection',
                            'grid_deltas tile_types wire_pair')
WireInfo = namedtuple('WireInfo', 'tile type shortname')


def get_tile_grid_info(fname):
    with open(fname, 'r') as f:
        tile = json.load(f)

    tile_type = tile['type']

    return {
        tile['tile']: {
            'type':
            tile_type,
            'grid_x':
            tile['x'],
            'grid_y':
            tile['y'],
            'sites':
            dict((site['site'], site['type']) for site in tile['sites'][:-1]),
            'wires':
            set((wire['wire'] for wire in tile['wires'][:-1]))
        },
    }


def next_wire_in_dimension(wire1, tile1, wire2, tile2, tiles, x_wires, y_wires,
                           wire_map, wires_in_node):
    """ next_wire_in_dimension returns true if tile1 and tile2 are in the same
  row and column, and must be adjcent.
  """
    tile1_info = tiles[tile1]
    tile2_info = tiles[tile2]

    tile1_x = tile1_info['grid_x']
    tile2_x = tile2_info['grid_x']
    tile1_y = tile1_info['grid_y']
    tile2_y = tile2_info['grid_y']

    # All wires are in the same row or column or if the each wire lies in its own
    # row or column.
    if len(y_wires) == 1 or len(x_wires) == len(wires_in_node) or abs(
            tile1_y - tile2_y) == 0:
        ordered_wires = sorted(x_wires.keys())

        idx1 = ordered_wires.index(tile1_x)
        idx2 = ordered_wires.index(tile2_x)

        if len(x_wires[tile1_x]) == 1 and len(x_wires[tile2_x]) == 1:
            return abs(idx1 - idx2) == 1

    if len(x_wires) == 1 or len(y_wires) == len(wires_in_node) or abs(
            tile1_x - tile2_x) == 0:
        ordered_wires = sorted(y_wires.keys())

        idx1 = ordered_wires.index(tile1_y)
        idx2 = ordered_wires.index(tile2_y)

        if len(y_wires[tile1_y]) == 1 and len(y_wires[tile2_y]) == 1:
            return abs(idx1 - idx2) == 1

    return None


def only_wire(tile1, tile2, tiles, x_wires, y_wires):
    """ only_wire returns true if tile1 and tile2 only have 1 wire in their respective x or y dimension.
  """
    tile1_info = tiles[tile1]
    tile2_info = tiles[tile2]

    tile1_x = tile1_info['grid_x']
    tile2_x = tile2_info['grid_x']

    tiles_x_adjacent = abs(tile1_x - tile2_x) == 1
    if tiles_x_adjacent and len(x_wires[tile1_x]) == 1 and len(
            x_wires[tile2_x]) == 1:
        return True

    tile1_y = tile1_info['grid_y']
    tile2_y = tile2_info['grid_y']

    tiles_y_adjacent = abs(tile1_y - tile2_y) == 1
    if tiles_y_adjacent and len(y_wires[tile1_y]) == 1 and len(
            y_wires[tile2_y]) == 1:
        return True

    return None


def is_directly_connected(node, node_tree, wire1, wire2):
    if 'wires' in node_tree:
        node_tree_wires = node_tree['wires']
    else:
        if len(node_tree['edges']) == 1 and len(node_tree['joins']) == 0:
            node_tree_wires = node_tree['edges'][0]
        else:
            return None

    if wire1 not in node_tree_wires:
        return None
    if wire2 not in node_tree_wires:
        return None

    # Is there than edge that has wire1 next to wire2?
    for edge in node_tree['edges']:
        idx1 = None
        idx2 = None
        try:
            idx1 = edge.index(wire1)
        except ValueError:
            pass

        try:
            idx2 = edge.index(wire2)
        except ValueError:
            pass

        if idx1 is not None and idx2 is not None:
            return abs(idx1 - idx2) == 1

        if idx1 is not None and (idx1 != 0 and idx1 != len(edge) - 1):
            return False

        if idx2 is not None and (idx2 != 0 and idx2 != len(edge) - 1):
            return False

    # Is there a join of nodes between wire1 and wire2?
    if wire1 in node_tree['joins']:
        return wire2 in node_tree['joins'][wire1]

    if wire2 in node_tree['joins']:
        assert wire1 not in node_tree['joins'][wire2]

    return None


def is_connected(wire1, tile1, wire2, tile2, node, wires_in_tiles, wire_map,
                 node_tree, tiles, x_wires, y_wires, wires_in_node):
    """ Check if two wires are directly connected. """

    # Because there are multiple possible wire connections between these two
    # tiles, consult the node_tree to determine if the two wires are actually connected.
    #
    # Warning: The node_tree is incomplete because it is not know how to extract
    # ordered wire information from the node.
    #
    # Example node CLK_BUFG_REBUF_X60Y142/CLK_BUFG_REBUF_R_CK_GCLK0_BOT
    # It does not appear to be possible to get ordered wire connection information
    # for the first two wires connected to PIP
    # CLK_BUFG_REBUF_X60Y117/CLK_BUFG_REBUF.CLK_BUFG_REBUF_R_CK_GCLK0_BOT<<->>CLK_BUFG_REBUF_R_CK_GCLK0_TOP
    #
    # However, it happens to be that theses wires are the only wires in their
    # tiles, so the earlier "only wires in tile" check will pass.

    connected = is_directly_connected(node['node'], node_tree[node['node']],
                                      wire1, wire2)
    if connected is not None:
        return connected

    is_only_wire = only_wire(tile1, tile2, tiles, x_wires, y_wires)
    if is_only_wire is not None:
        return is_only_wire

    # The node_tree didn't specify these wires, and the wires are not
    # unambiguously connected.
    return None


def weird_nodes(node_name):
    """ Returns true if the node has connections that skip tiles.

    Most nodes are made up of wires that only touch adjcent tiles.  However
    some nodes fly over tiles.

    """

    # Only about 1% of all nodes in the graph behave this way, so hopefully
    # the overall tileconn affect is small!
    _, wire = node_name.split('/')

    weird_prefixes = [
        # ~400 instances
        'CLK_HROUTE',
        # ~200 instances
        'CLK_HDISTR',
        # ~500 instances
        'CLK_TEST_BUF',
        # ~300 instances
        'CLK_VDISTR',
        # ~200 instances
        'CLK_VROUTE',
        # ~1500 instances
        'HDIO_IOBPAIR',
        # 4k instances
        'HPIO_IOBPAIR',
        # ~200 instances
        'HPIO_IOBSNGL',
        # ~12k instances
        'GND_WIRE',
        # ~40k instances
        'VCC_WIRE',
    ]

    for prefix in weird_prefixes:
        if wire.startswith(prefix):
            return True

    return False


def process_node(tileconn, key_history, node, wire_map, grid, tile_type_sizes):
    node_name = node['node']
    is_weird_node = weird_nodes(node_name)

    wires = [wire['wire'] for wire in node['wires'][:-1]]

    for idx, wire1 in enumerate(wires):
        wire_info1 = wire_map[wire1]
        tile1 = wire_info1.tile

        for wire2 in wires[idx + 1:]:
            wire_info2 = wire_map[wire2]
            tile2 = wire_info2.tile

            same_tile = tile1 == tile2
            adjcent_tile = tile_sizes.tiles_are_adjcent(
                grid[tile1], grid[tile2], tile_type_sizes)

            if same_tile or adjcent_tile or is_weird_node:
                update_tile_conn(tileconn, key_history, wire1, wire_info1,
                                 wire2, wire_info2, grid)


def update_tile_conn(tileconn, key_history, wirename1, wire1, wirename2, wire2,
                     tiles):
    # Ensure that (wire1, wire2) is sorted, so we can easy check if a connection
    # already exists.

    tile1 = tiles[wire1.tile]
    tile2 = tiles[wire2.tile]
    if ((wire1.type, wire1.shortname, tile1['grid_x'], tile1['grid_y']) >
        (wire2.type, wire2.shortname, tile2['grid_x'], tile2['grid_y'])):
        wire1, tile1, wire2, tile2 = wire2, tile2, wire1, tile1

    tileconn.add(
        TileConnection(
            grid_deltas=(
                tile2['grid_x'] - tile1['grid_x'],
                tile2['grid_y'] - tile1['grid_y'],
            ),
            tile_types=(
                tile1['type'],
                tile2['type'],
            ),
            wire_pair=(
                wire1.shortname,
                wire2.shortname,
            ),
        ))


def flatten_tile_conn(tileconn):
    """ Convert tileconn that is key'd to identify specific wire pairs between tiles
  key (tile1_type, wire1_name, tile2_type, wire2_name) to flat tile connect list
  that relates tile types and relative coordinates and a full list of wires to
  connect. """
    flat_tileconn = {}

    for conn in tileconn:
        key = (tuple(conn.tile_types), tuple(conn.grid_deltas))

        if key not in flat_tileconn:
            flat_tileconn[key] = {
                'tile_types': conn.tile_types,
                'grid_deltas': conn.grid_deltas,
                'wire_pairs': set()
            }

        flat_tileconn[key]['wire_pairs'].add(tuple(conn.wire_pair))

    def inner():
        for output in flat_tileconn.values():
            yield {
                'tile_types': output['tile_types'],
                'grid_deltas': output['grid_deltas'],
                'wire_pairs': tuple(output['wire_pairs']),
            }

    return tuple(inner())


def is_tile_type(tiles, coord_to_tile, coord, tile_type):
    if coord not in coord_to_tile:
        return False

    target_tile = tiles[coord_to_tile[coord]]
    return target_tile['type'] == tile_type


def make_connection(wire_nodes, wire1, wire2):
    if wire_nodes[wire1] is wire_nodes[wire2]:
        assert wire1 in wire_nodes[wire1]
        assert wire2 in wire_nodes[wire2]
        return

    new_node = wire_nodes[wire1] | wire_nodes[wire2]

    for wire in new_node:
        wire_nodes[wire] = new_node


def create_coord_to_tile(tiles):
    coord_to_tile = {}
    for tile, tileinfo in tiles.items():
        coord_to_tile[(tileinfo['grid_x'], tileinfo['grid_y'])] = tile

    return coord_to_tile


def connect_wires(tiles, tileconn, wire_map):
    """ Connect individual wires into groups of wires called nodes. """

    # Map of tile type to list of wires in tile type
    tile_wires = {}
    for tile_info in tiles.values():
        tile_wires[tile_info['type']] = set()

    for wire, wire_info in wire_map.items():
        tile = tiles[wire_info.tile]
        tile_type = tile['type']
        tile_wires[tile_type].add(wire_info.shortname)

    # Initialize all nodes to originally only contain the wire by itself.
    wire_nodes = {}
    for wire in wire_map:
        wire_nodes[wire] = set([wire])

    conns = connections.Connections(tiles, tileconn, tile_wires)
    for wire_a, wire_b in conns.get_connections():
        full_wire_a = wire_a.tile + '/' + wire_a.wire
        full_wire_b = wire_b.tile + '/' + wire_b.wire
        make_connection(wire_nodes, full_wire_a, full_wire_b)

    # Find unique nodes
    nodes = {}
    for node in wire_nodes.values():
        nodes[id(node)] = node

    # Flatten to list of lists.
    return tuple(tuple(node) for node in nodes.values())


def generate_tilegrid(pool, tiles):
    wire_map = {}

    grid = {}

    num_tiles = 0
    for tile_type in tiles:
        num_tiles += len(tiles[tile_type])

    idx = 0
    with progressbar.ProgressBar(max_value=num_tiles) as bar:
        for tile_type in tiles:
            for tile in pool.imap_unordered(
                    get_tile_grid_info,
                    tiles[tile_type],
                    chunksize=20,
            ):
                bar.update(idx)

                assert len(tile) == 1, tile
                tilename = tuple(tile.keys())[0]

                for wire in tile[tilename]['wires']:
                    assert wire not in wire_map, (wire, wire_map)
                    assert wire.startswith(tilename + '/'), (wire, tilename)

                    wire_map[wire] = WireInfo(
                        tile=tilename,
                        type=tile[tilename]['type'],
                        shortname=wire[len(tilename) + 1:],
                    )

                del tile[tilename]['wires']
                grid.update(tile)

                idx += 1
                bar.update(idx)

    return grid, wire_map


def clean_tileconn(tileconn, nodes, grid):
    tileconn = list(set(tileconn))

    print('{} Pruning bad connections, have {} connections'.format(
        datetime.datetime.now(), len(tileconn)))

    # Construct map from (tile_type, wire) -> list of tiles
    tile_type_instances = {}
    tile_at_loc = {}
    for tile, gridinfo in grid.items():
        if gridinfo['type'] not in tile_type_instances:
            tile_type_instances[gridinfo['type']] = []
        tile_type_instances[gridinfo['type']].append(tile)

        loc = gridinfo['grid_x'], gridinfo['grid_y']
        assert loc not in tile_at_loc
        tile_at_loc[loc] = tile

    # Prune bad connections
    bad_connections = set()
    for idx, conn in enumerate(progressbar.progressbar(tileconn)):
        tile1_type, tile2_type = conn.tile_types
        wire1, wire2 = conn.wire_pair

        for tile1 in tile_type_instances[tile1_type]:
            tile1_info = grid[tile1]
            assert tile1_info['type'] == tile1_type

            dx, dy = conn.grid_deltas
            tile2_grid_x = tile1_info['grid_x'] + dx
            tile2_grid_y = tile1_info['grid_y'] + dy

            loc = tile2_grid_x, tile2_grid_y
            if loc not in tile_at_loc:
                continue

            tile2 = tile_at_loc[loc]
            tile2_info = grid[tile2]

            if tile2_info['type'] != tile2_type:
                continue

            fullwire1 = tile1 + '/' + wire1
            fullwire2 = tile2 + '/' + wire2

            if fullwire1 not in nodes or fullwire2 not in nodes:
                bad_connections.add(idx)
                break

            # tileconn says these two wires should form a node.  If these wires
            # are a node, they will have the same set object representing
            # the node.
            if nodes[fullwire1] is not nodes[fullwire2]:
                bad_connections.add(idx)
                break

    print('{} Found {} bad connections'.format(datetime.datetime.now(),
                                               len(bad_connections)))

    # Delete from highest index to lowest index to preverse deletion order
    output_tileconn = []
    for idx, conn in enumerate(progressbar.progressbar(tileconn)):
        if idx in bad_connections:
            continue

        output_tileconn.append(conn)

    print('{} Removed {} bad connections'.format(datetime.datetime.now(),
                                                 len(bad_connections)))

    return output_tileconn


def generate_tileconn(pool, nodes, wire_map, grid, tile_type_sizes):
    tileconn = set()
    key_history = {}
    raw_node_data = []

    wire_nodes = {}
    for node_file in progressbar.progressbar(nodes):
        with open(node_file) as f:
            raw_nodes = json.load(f)
        raw_node_data.extend(raw_nodes[:-1])

        for raw_node in raw_nodes[:-1]:
            process_node(tileconn, key_history, raw_node, wire_map, grid,
                         tile_type_sizes)

            node = set(wire['wire'] for wire in raw_node['wires'][:-1])
            for wire in node:
                assert wire not in wire_nodes
                wire_nodes[wire] = node

    tileconn = clean_tileconn(tileconn, wire_nodes, grid)

    tileconn = flatten_tile_conn(tileconn)

    return tileconn, raw_node_data


def main():
    parser = argparse.ArgumentParser(
        description=
        "Reduces raw database dump into prototype tiles, grid, and connections."
    )
    parser.add_argument('--root_dir', required=True)
    parser.add_argument('--output_dir', required=True)
    parser.add_argument('--verify_only', action='store_true')
    parser.add_argument('--ignored_wires')
    parser.add_argument('--max_cpu', type=int, default=10)

    args = parser.parse_args()

    now = datetime.datetime.now
    tiles, nodes = lib.read_root_csv(args.root_dir)

    processes = min(multiprocessing.cpu_count(), args.max_cpu)
    print('{} Running {} processes'.format(now(), processes))
    pool = multiprocessing.Pool(processes=processes)

    tileconn_file = os.path.join(args.output_dir, 'tileconn.json')
    wire_map_file = os.path.join(args.output_dir, 'wiremap.pickle')

    print('{} Reading tilegrid'.format(now()))
    with open(
            os.path.join(util.get_db_root(), util.get_part(),
                         'tilegrid.json')) as f:
        grid = json.load(f)

    if not args.verify_only:
        print('{} Creating tile map'.format(now()))
        grid2, wire_map = generate_tilegrid(pool, tiles)

        # Make sure tilegrid from 005-tilegrid matches tilegrid from
        # generate_tilegrid.
        db_grid_keys = set(grid.keys())
        generated_grid_keys = set(grid2.keys())
        assert db_grid_keys == generated_grid_keys, (
            db_grid_keys ^ generated_grid_keys)

        for tile in db_grid_keys:
            for k in grid2[tile]:
                assert k in grid[tile], k
                assert grid[tile][k] == grid2[tile][k], (tile, k,
                                                         grid[tile][k],
                                                         grid2[tile][k])

        print('{} Estimating tile sizes'.format(now()))
        tile_type_sizes = tile_sizes.guess_tile_type_sizes(grid)

        with open(wire_map_file, 'wb') as f:
            pickle.dump(wire_map, f)

        print('{} Creating tile connections'.format(now()))
        tileconn, raw_node_data = generate_tileconn(pool, nodes, wire_map,
                                                    grid, tile_type_sizes)

        for data in tileconn:
            data['wire_pairs'] = tuple(
                sorted(
                    data['wire_pairs'],
                    key=lambda x: tuple(extract_numbers(s) for s in x)))

        tileconn = tuple(
            sorted(
                tileconn, key=lambda x: (x['tile_types'], x['grid_deltas'])))

        print('{} Writing tileconn'.format(now()))
        with open(tileconn_file, 'w') as f:
            json.dump(tileconn, f, indent=2, sort_keys=True)
    else:
        with open(wire_map_file, 'rb') as f:
            wire_map = pickle.load(f)

        print('{} Reading raw_node_data'.format(now()))
        raw_node_data = []
        for node_file in progressbar.progressbar(nodes):
            with open(node_file) as f:
                raw_node_data.extend(json.load(f)[:-1])

        print('{} Reading tileconn'.format(now()))
        with open(tileconn_file) as f:
            tileconn = json.load(f)

    wire_nodes_file = os.path.join(args.output_dir, 'wire_nodes.pickle')
    if os.path.exists(wire_nodes_file) and args.verify_only:
        with open(wire_nodes_file, 'rb') as f:
            wire_nodes = pickle.load(f)
    else:
        print("{} Connecting wires to verify tileconn".format(now()))
        wire_nodes = connect_wires(grid, tileconn, wire_map)
        with open(wire_nodes_file, 'wb') as f:
            pickle.dump(wire_nodes, f)

    print('{} Verifing tileconn'.format(now()))
    error_nodes = []
    lib.verify_nodes(
        [(node['node'], tuple(wire['wire'] for wire in node['wires'][:-1]))
         for node in raw_node_data], wire_nodes, error_nodes)

    if len(error_nodes) > 0:
        error_nodes_file = os.path.join(args.output_dir, 'error_nodes.json')
        with open(error_nodes_file, 'w') as f:
            json.dump(error_nodes, f, indent=2, sort_keys=True)

        ignored_wires = []
        ignored_wires_file = args.ignored_wires
        if os.path.exists(ignored_wires_file):
            with open(ignored_wires_file) as f:
                ignored_wires = set(l.strip() for l in f)

        if not lib.check_errors(error_nodes, ignored_wires):
            print('{} errors detected, see {} for details.'.format(
                len(error_nodes), error_nodes_file))
            sys.exit(1)
        else:
            print(
                '{} errors ignored because of {}\nSee {} for details.'.format(
                    len(error_nodes), ignored_wires_file, error_nodes_file))


if __name__ == '__main__':
    main()
