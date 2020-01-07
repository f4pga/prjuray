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

import argparse
import copy
import json


def is_edge_shared(edge1, edge2):
    """ Returns true if edge1 or edge2 overlap

  >>> is_edge_shared((0, 1), (0, 1))
  True
  >>> is_edge_shared((0, 2), (0, 1))
  True
  >>> is_edge_shared((0, 1), (0, 2))
  True
  >>> is_edge_shared((1, 2), (0, 3))
  True
  >>> is_edge_shared((0, 3), (1, 2))
  True
  >>> is_edge_shared((1, 2), (0, 2))
  True
  >>> is_edge_shared((0, 2), (1, 2))
  True
  >>> is_edge_shared((0, 2), (1, 3))
  True
  >>> is_edge_shared((1, 3), (0, 2))
  True
  >>> is_edge_shared((0, 1), (1, 2))
  False
  >>> is_edge_shared((1, 2), (0, 1))
  False
  >>> is_edge_shared((0, 1), (2, 3))
  False
  >>> is_edge_shared((2, 3), (0, 1))
  False
  """
    assert edge1[0] < edge1[1], edge1
    assert edge2[0] < edge2[1], edge2

    if edge1[0] <= edge2[0]:
        return edge2[0] < edge1[1]
    else:
        return edge1[0] < edge2[1]


def share_edge(a, b):
    """ Returns true if box defined by a and b share any edge.

  Box is defined as (x-min, y-min, x-max, y-max).

  >>> share_edge((0, 0, 1, 1), (1, 0, 2, 1))
  True
  >>> share_edge((1, 0, 2, 1), (0, 0, 1, 1))
  True
  >>> share_edge((0, 0, 1, 1), (0, 1, 1, 2))
  True
  >>> share_edge((0, 1, 1, 2), (0, 0, 1, 1))
  True
  >>> share_edge((0, 0, 1, 3), (1, 0, 2, 1))
  True
  >>> share_edge((1, 0, 2, 1), (0, 0, 1, 3))
  True
  >>> share_edge((0, 0, 3, 1), (0, 1, 1, 2))
  True
  >>> share_edge((0, 1, 1, 2), (0, 0, 3, 1))
  True
  >>> share_edge((0, 0, 1, 1), (1, 1, 2, 2))
  False
  >>> share_edge((1, 1, 2, 2), (0, 0, 1, 1))
  False
  >>> share_edge((0, 0, 1, 3), (1, 3, 2, 4))
  False
  >>> share_edge((0, 0, 1, 3), (1, 2, 2, 4))
  True
  """

    a_x_min, a_y_min, a_x_max, a_y_max = a
    b_x_min, b_y_min, b_x_max, b_y_max = b

    if a_x_min == b_x_max or a_x_max == b_x_min:
        return is_edge_shared((a_y_min, a_y_max), (b_y_min, b_y_max))
    if a_y_min == b_y_max or a_y_max == b_y_min:
        return is_edge_shared((a_x_min, a_x_max), (b_x_min, b_x_max))


def edge_overlap(low1, high1, low2, high2):
    """ Returns true if two lines have >0 overlap

    >>> edge_overlap(0, 1, 1, 2)
    False
    >>> edge_overlap(0, 2, 1, 2)
    True
    >>> edge_overlap(1, 2, 1, 2)
    True
    >>> edge_overlap(1, 2, 0, 1)
    False
    >>> edge_overlap(1, 2, 0, 2)
    True
    >>> edge_overlap(0, 1, 0, 1)
    True
    """
    if low1 < low2:
        return low2 < high1
    else:
        return low1 < high2


def box_share_edge(box1, box2):
    """ Return true if the two boxes share any edge.

    >>> box_share_edge(((0, 1), (0, 1)), ((0, 1), (1, 2)))
    True
    >>> box_share_edge(((0, 1), (0, 1)), ((1, 2), (1, 2)))
    False
    >>> box_share_edge(((0, 1), (0, 3)), ((1, 2), (2, 5)))
    True
    >>> box_share_edge(((0, 1), (0, 3)), ((1, 2), (3, 6)))
    False
    >>> box_share_edge(((0, 3), (0, 1)), ((2, 5), (1, 2)))
    True
    >>> box_share_edge(((0, 3), (0, 1)), ((3, 6), (1, 2)))
    False
    >>> box_share_edge(((0, 3), (0, 3)), ((0, 3), (3, 6)))
    True
    >>> box_share_edge(((0, 3), (0, 3)), ((3, 6), (0, 3)))
    True
    >>> box_share_edge(((0, 3), (0, 3)), ((3, 6), (3, 6)))
    False

    """
    ((box1_xlow, box1_xhigh), (box1_ylow, box1_yhigh)) = box1
    ((box2_xlow, box2_xhigh), (box2_ylow, box2_yhigh)) = box2

    if box1_xlow == box2_xhigh or box2_xlow == box1_xhigh:
        # box 1 left edge may touch box 2 right edge
        #  or
        # box 2 left edge may touch box 1 right edge
        if edge_overlap(box1_ylow, box1_yhigh, box2_ylow, box2_yhigh):
            return True

    if box1_ylow == box2_yhigh or box2_ylow == box1_yhigh:
        # box 1 bottom edge may touch box 1 top edge
        #  or
        # box 2 bottom edge may touch box 2 top edge
        if edge_overlap(box1_xlow, box1_xhigh, box2_xlow, box2_xhigh):
            return True

    return False


def tiles_are_adjcent(tile1, tile2, tile_type_sizes):
    width1, height1 = tile_type_sizes[tile1['type']]
    tile1_xlow = tile1['grid_x']
    tile1_ylow = tile1['grid_y'] - height1
    tile1_xhigh = tile1['grid_x'] + width1
    tile1_yhigh = tile1['grid_y']

    width2, height2 = tile_type_sizes[tile2['type']]
    tile2_xlow = tile2['grid_x']
    tile2_ylow = tile2['grid_y'] - height2
    tile2_xhigh = tile2['grid_x'] + width2
    tile2_yhigh = tile2['grid_y']

    return box_share_edge(
        ((tile1_xlow, tile1_xhigh), (tile1_ylow, tile1_yhigh)),
        ((tile2_xlow, tile2_xhigh), (tile2_ylow, tile2_yhigh)),
    )


def max_size_for_tile(tile, grid, tile_by_loc, rclk_rows):
    """ Guess maximum size for a tile. """
    tile_type = grid[tile]['type']
    if tile_type == 'NULL':
        return (1, 1)

    # Pos X, Neg Y
    base_grid_x = grid[tile]['grid_x']
    base_grid_y = grid[tile]['grid_y']

    # Walk up X
    grid_x = base_grid_x
    grid_y = base_grid_y
    while True:
        try:
            next_tile = tile_by_loc[(grid_x + 1, grid_y)]
        except KeyError:
            break

        if grid[next_tile]['type'] != 'NULL':
            break

        grid_x += 1

    max_grid_x = grid_x

    # Walk down Y
    grid_x = base_grid_x
    grid_y = base_grid_y
    while True:
        # Most tiles don't cross the RCLK row, but a handful of tiles do!
        if grid_y - 1 in rclk_rows and tile_type not in [
                "CFRM_AMS_CFGIO",
                "PSS_ALTO",
                "CFG_CONFIG",
                "CFRM_CONFIG",
                "CFRM_B",
                "CMT_RIGHT",
        ]:
            break

        try:
            next_tile = tile_by_loc[(grid_x, grid_y - 1)]
        except KeyError:
            break

        if grid[next_tile]['type'] != 'NULL':
            break

        grid_y -= 1

    max_grid_y = grid_y

    return (max_grid_x - base_grid_x + 1), (base_grid_y - max_grid_y + 1)


def generate_tile_type_sizes(grid):
    """ Generate tile sizes for the given grid using max_size_for_tile. """
    tile_type_sizes = {}

    tile_by_loc = {}

    rclk_rows = set()

    for tile, gridinfo in grid.items():
        key = gridinfo['grid_x'], gridinfo['grid_y']
        assert key not in tile_by_loc
        tile_by_loc[key] = tile

        if gridinfo['type'] in ['RCLK_INT_R', 'RCLK_INT_L']:
            rclk_rows.add(gridinfo['grid_y'])

    for tile, gridinfo in grid.items():
        size_x, size_y = max_size_for_tile(tile, grid, tile_by_loc, rclk_rows)
        if gridinfo['type'] not in tile_type_sizes:
            tile_type_sizes[gridinfo['type']] = (size_x, size_y)
        else:
            old_size_x, old_size_y = tile_type_sizes[gridinfo['type']]
            tile_type_sizes[gridinfo['type']] = (
                min(size_x, old_size_x),
                min(size_y, old_size_y),
            )

    return tile_type_sizes


def commit_tile_type(grid, tile_type, size):
    """ First verify that expanding the specified tile type by the size
    specified works, then modify the tile grid to reflect the expanded sizes.
    """
    gridinfo_by_loc = {}
    locs = []
    for tile in grid:
        gridinfo = grid[tile]
        key = gridinfo['grid_x'], gridinfo['grid_y']
        assert key not in gridinfo_by_loc
        gridinfo_by_loc[key] = gridinfo

        if gridinfo['type'] == tile_type:
            locs.append(key)

    for loc in locs:
        for dx in range(size[0]):
            for dy in range(size[1]):
                key = loc[0] + dx, loc[1] - dy

                if dx == 0 and dy == 0:
                    assert gridinfo_by_loc[key]['type'] == tile_type
                else:
                    assert gridinfo_by_loc[key]['type'] == 'NULL', (
                        loc, key, tile_type, gridinfo_by_loc[key]['type'])

    for loc in locs:
        for dx in range(size[0]):
            for dy in range(size[1]):
                key = loc[0] + dx, loc[1] - dy
                gridinfo_by_loc[key]['type'] = 'expanded_' + tile_type


def guess_tile_type_sizes(grid):
    """ Guess tile type sizes by expanding, and then blocking by largest."""
    grid = copy.deepcopy(grid)
    tile_type_sizes = generate_tile_type_sizes(grid)
    commited_types = set()

    # Commit longest or widest tiles first
    tile_type_by_size = sorted(
        tile_type_sizes,
        key=lambda k: max(tile_type_sizes[k][0], tile_type_sizes[k][1]),
        reverse=True)

    for tile_type in tile_type_by_size:
        if tile_type_sizes[tile_type] == (1, 1):
            continue

        recompute_sizes = False
        try:
            # Attempt to commit this tile type
            commit_tile_type(grid, tile_type, tile_type_sizes[tile_type])
        except AssertionError:
            # Commit failed, try to recompute and then re-commit.
            recompute_sizes = True

        if recompute_sizes:
            new_tile_type_sizes = generate_tile_type_sizes(grid)

            for t in new_tile_type_sizes:
                if t in commited_types:
                    continue
                if t.startswith('expanded_'):
                    continue

                tile_type_sizes[t] = new_tile_type_sizes[t]

            commit_tile_type(grid, tile_type, tile_type_sizes[tile_type])

        commited_types.add(tile_type)

    return tile_type_sizes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tile_grid', required=True)

    args = parser.parse_args()

    with open(args.tile_grid) as f:
        grid = json.load(f)

    tile_type_sizes = guess_tile_type_sizes(grid)

    for tile_type in sorted(tile_type_sizes):
        size_x, size_y = tile_type_sizes[tile_type]
        print(' {} = ({}, {})'.format(tile_type, size_x, size_y))


if __name__ == "__main__":
    main()
