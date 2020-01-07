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
""" Utility to convert from dump features TCL to segmaker. """
import argparse
from utils.segmaker import Segmaker
from utils import util
from utils.db import Database
from utils.grid_types import BlockType


class FeatureTree():
    def __init__(self, part, parent=None):
        try:
            idx = part.index('[')
            self.part = part[:idx]
            self.index = [int(part[idx + 1:-1])]
        except ValueError:
            self.part = part
            self.index = None

        self.parent = parent
        self.children = {}

    def is_leaf(self):
        return len(self.children) == 0

    def __getitem__(self, key):
        if key not in self.children:
            self._add_child(key)

        return self.children[key]

    def _add_child(self, part):
        assert part not in self.children
        self.children[part] = FeatureTree(part, self)

    def __str__(self):
        if self.index is not None:
            if len(self.index) == 1:
                return '{}[{}]'.format(self.part, self.index[0])
            else:
                min_index = min(self.index)
                max_index = max(self.index)
                assert len(self.index) == (max_index - min_index + 1)
                return '{}[{}:{}]'.format(self.part, max_index, min_index)
        else:
            return self.part

    def __iter__(self):
        return iter(self.children.keys())

    def find_feature(self, feature):
        return self.find_feature_list(feature.split('.'))

    def find_feature_list(self, feature_list):
        if len(feature_list) == 0:
            return self
        else:
            idx = feature_list[0].find('[')
            if idx != -1:
                s = feature_list[0][:idx]
            else:
                s = feature_list[0]

            return self.children[s].find_feature_list(feature_list[1:])

    def full_feature(self):
        if self.parent is not None:
            return '{}.{}'.format(self.parent.full_feature(), str(self))
        else:
            return str(self)

    def coalesce(self):
        parts = {}

        for part, child in self.children.items():
            child.coalesce()

        for part, child in self.children.items():
            if child.part not in parts:
                parts[child.part] = child
            else:
                parts[child.part].index.extend(child.index)

        for part, child in parts.items():
            if child.index is not None:
                child.index.sort()

        self.children = parts

    def pip_features(self):
        if 'PIP' in self.children:
            for child in self.children['PIP']:
                yield self.children['PIP'][child]


def read_features(features_file):
    all_features = {}

    with open(features_file) as f:
        for l in f:
            l = l.strip()
            if l.startswith('.tile'):
                tile, tile_type = l[6:].split(':')
                all_features[(tile, tile_type)] = []
            else:
                all_features[(tile, tile_type)].append(l)

    return all_features


def output_empty_pips(tree, pip_sources, pip_active_per_tile):
    def extra_tags(tilename):
        pip_active = pip_active_per_tile[tilename]
        for dest, active in pip_active.items():
            if active:
                continue

            for src in pip_sources[dest]:
                tag = 'PIP.{}.{}'.format(dest, src)
                yield tag, 0

    return extra_tags


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bits_file', default='design.bits')
    parser.add_argument('--features_file', default='design.features')
    parser.add_argument('--extent_features_file', default=None)
    parser.add_argument('--block_type', default='CLB_IO_CLK')
    parser.add_argument(
        '--zero_feature_enums',
        help=
        "File containing features that are zero enums, and which parameter is the zero."
    )

    args = parser.parse_args()

    zero_features = {}

    if args.zero_feature_enums:
        with open(args.zero_feature_enums) as f:
            for l in f:
                parts = l.strip().split('=')
                assert len(parts) == 2, "Expected line with ="
                zero_features[parts[0]] = parts[1]

    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()

    feature_data = {}
    feature_trees = {}
    if args.extent_features_file:
        with open(args.extent_features_file) as f:
            tile_type = None
            for l in f:
                l = l.strip()

                if l.startswith('.tiletype'):
                    tile_type = l.split(' ')[1]
                    assert tile_type not in feature_data
                    feature_data[tile_type] = set()

                feature_data[tile_type].add(l.strip())

        for tile_type in feature_data:
            features = feature_data[tile_type]

            split_features = []

            for feature in features:
                split_features.append(feature.split('.'))

            split_features.sort(key=lambda x: -len(x))

            tree = FeatureTree(part=tile_type)
            for split_feature in split_features:
                child = tree
                for part in split_feature:
                    child = child[part]

            tree.coalesce()

            feature_trees[tile_type] = tree

    all_features = read_features(args.features_file)

    tile_types = set()
    for _, tile_type in all_features.keys():
        tile_types.add(tile_type)

    for tile_type in tile_types:
        segmk = Segmaker(args.bits_file, bits_per_word=16)
        segmk.set_def_bt(args.block_type)

        tree = feature_trees[tile_type]
        pip_active = {}
        pip_sources = {}
        pip_active_per_tile = {}
        for pip_feature in tree.pip_features():
            dest = pip_feature.part
            assert dest not in pip_active
            assert dest not in pip_sources

            pip_active[dest] = 0

            sources = []
            for child in pip_feature:
                child_feature = pip_feature[child]
                parts = child_feature.full_feature().split('.')
                assert parts[1] == 'PIP'

                if child_feature.is_leaf():
                    sources.append(parts[-1])
                else:
                    src = child_feature.part
                    children = set(child for child in child_feature)
                    assert len(set(('FWD', 'REV')) | children) == 2, children
                    sources.extend([
                        '{}.FWD'.format(src),
                        '{}.REV'.format(src),
                    ])

            pip_sources[dest] = sources

        proto_pip_active = pip_active

        for (tile, a_type), features in all_features.items():
            if tile_type != a_type:
                continue

            loc = grid.loc_of_tilename(tile)
            gridinfo = grid.gridinfo_at_loc(loc)

            if BlockType.CLB_IO_CLK not in gridinfo.bits:
                print('*** WARNING *** Tile {} is missing bits!'.format(tile))
                continue

            pip_active = dict(proto_pip_active)

            indicies = {}

            for l in features:
                parts = l.split('.')
                feature = tree.find_feature(l)

                # Mark active indices on vector features
                if feature.index is not None and len(feature.index) > 1:
                    current_index = int(parts[-1].split('[')[1][:-1])

                    if id(feature) not in indicies:
                        indicies[id(feature)] = (feature, set())
                    indicies[id(feature)][1].add(current_index)

                segmk.add_tile_tag(tile, l, 1)

                if parts[0] == "PIP":
                    assert feature.is_leaf()
                    assert parts[1] in pip_active
                    pip_active[parts[1]] = 1
                elif feature.is_leaf() and feature.index is None:
                    parent = feature.parent

                    should_emit_enum_zero = True

                    # Only emit 0 tags if this is not a zero feature, or if
                    # this is feature is the zero enum.
                    if parent.part in zero_features:
                        if zero_features[parent.part] != feature.part:
                            should_emit_enum_zero = False
                            parts = parent.full_feature().split('.')[1:]
                            parts.append(zero_features[parent.part])
                            s = '.'.join(parts)
                            segmk.add_tile_tag(tile, s, 0)

                    if should_emit_enum_zero:
                        for child in parent:
                            child_feature = parent[child]
                            if child_feature is not feature:
                                if not child_feature.is_leaf():
                                    continue

                                parts = child_feature.full_feature().split(
                                    '.')[1:]
                                s = '.'.join(parts)
                                segmk.add_tile_tag(tile, s, 0)

            for feature, active_indicies in indicies.values():
                min_index = min(active_indicies)
                if min(feature.index) + 1 == min_index:
                    min_index = min(feature.index)

                max_index = max(active_indicies)
                if max(feature.index) - 1 == max_index:
                    max_index = max(feature.index)

                s = '.'.join(feature.full_feature().split('.')[1:])
                s = '['.join(s.split('[')[:-1])

                for idx in range(min_index, max_index + 1):
                    if idx in active_indicies:
                        continue

                    segmk.add_tile_tag(tile, '{}[{}]'.format(s, idx), 0)

            # Output disable features for pips.
            pip_active_per_tile[tile] = pip_active

        segmk.compile()
        segmk.write(
            allow_empty=True,
            extra_tags=output_empty_pips(tree, pip_sources,
                                         pip_active_per_tile))


if __name__ == "__main__":
    run()
