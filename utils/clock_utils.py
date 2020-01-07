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

from csv import DictReader

MAX_GLOBAL_CLOCKS = 24
MAX_COLUMN_CLOCKS = 12


def gen_rclk_int(grid):
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)

        if gridinfo.tile_type in ["RCLK_INT_L", "RCLK_INT_R"]:
            yield loc


def walk_tile(grid, start_loc, dy, clocks):
    key = (start_loc, dy)
    assert key not in clocks
    clocks[key] = set()

    x, y = start_loc
    while True:
        y += dy

        loc = (x, y)
        gridinfo = grid.gridinfo_at_loc(loc)

        if gridinfo.tile_type != 'INT':
            break

        left_gridinfo = grid.gridinfo_at_loc((x - 1, y))
        for site, site_type in left_gridinfo.sites.items():
            if site_type in ['SLICEL', 'SLICEM']:
                clocks[key].add(site)

        right_gridinfo = grid.gridinfo_at_loc((x + 1, y))
        for site, site_type in right_gridinfo.sites.items():
            if site_type in ['SLICEL', 'SLICEM']:
                clocks[key].add(site)


def populate_leafs(grid):
    clocks = {}
    for rclk_tile_loc in gen_rclk_int(grid):
        walk_tile(grid, rclk_tile_loc, 1, clocks)
        walk_tile(grid, rclk_tile_loc, -1, clocks)

    return clocks


class ClockColumns():
    def __init__(self, grid):
        self.sites = {}
        self.clocks_active = {}
        self.global_clocks = set()

        clock_leafs = populate_leafs(grid)

        for key, sites in clock_leafs.items():
            self.clocks_active[key] = set()
            for site in sites:
                self.sites[site] = key

    def columns(self):
        return self.clocks_active.keys()

    def remove_column(self, disabled_columns):
        for key in disabled_columns:
            del self.clocks_active[key]

        sites_to_remove = set()
        for site, key in self.sites.items():
            if key in disabled_columns:
                sites_to_remove.add(site)

        for site in sites_to_remove:
            del self.sites[site]

    def add_clock(self, site, clock):
        key = self.sites[site]
        if clock in self.clocks_active[key]:
            # Clock already in use!
            return True

        if len(self.clocks_active[key]) >= MAX_COLUMN_CLOCKS:
            # No more column clocks!
            return False

        if clock not in self.global_clocks:
            if len(self.global_clocks) >= MAX_GLOBAL_CLOCKS:
                # No more global clocks!
                return False

        self.global_clocks.add(clock)
        self.clocks_active[key].add(clock)
        return True


class GlobalClockBuffers():
    def __init__(self, bufg_outputs_file):
        self.bufgs = {}
        self.unused_bufgs = set()

        for idx in range(MAX_GLOBAL_CLOCKS):
            self.bufgs[idx] = []
            self.unused_bufgs.add(idx)

        with open(bufg_outputs_file) as f:
            for bufg in DictReader(f):
                if bufg['hroute_output'] == 'all':
                    for idx in range(MAX_GLOBAL_CLOCKS):
                        self.bufgs[idx].append(bufg['site'])
                else:
                    self.bufgs[int(bufg['hroute_output'])].append(bufg['site'])

        for idx in range(MAX_GLOBAL_CLOCKS):
            self.bufgs[idx].sort()

    def random_bufg_for_hroute(self, hroute_idx, random_choice):
        self.unused_bufgs.remove(hroute_idx)
        return random_choice(self.bufgs[hroute_idx]), hroute_idx

    def random_bufg(self, random_choice):
        hroute_idx = random_choice(sorted(self.unused_bufgs))
        return self.random_bufg_for_hroute(hroute_idx, random_choice)


def make_bufg(site, site_type, idx, ce_inputs, randlib):
    if site_type in ['BUFGCE', 'BUFGCE_HDIO']:
        s = """
wire bufg_o_{idx};
(* LOC="{loc}", KEEP, DONT_TOUCH *) BUFGCE #(
    .IS_CE_INVERTED({invert_ce}),
    .CE_TYPE("{ce_type}")
    ) bufg_{idx} (
        .CE({ce}),
        .O(bufg_o_{idx})
    );""".format(
            loc=site,
            idx=idx,
            invert_ce=randlib.randint(2),
            ce_type=randlib.choice(["SYNC", "ASYNC"]),
            ce=randlib.choice(ce_inputs))
    elif site_type == 'BUFGCE_DIV':
        s = """
wire bufg_o_{idx};
(* LOC="{loc}", KEEP, DONT_TOUCH *) BUFGCE_DIV #(
    .IS_CE_INVERTED({invert_ce}),
    .CE_TYPE("{ce_type}"),
    .BUFGCE_DIVIDE({bufce_divide})
    ) bufg_{idx} (
        .CE({ce}),
        .CLR({clr}),
        .O(bufg_o_{idx})
    );""".format(
            loc=site,
            idx=idx,
            invert_ce=randlib.randint(2),
            ce_type=randlib.choice(["SYNC", "ASYNC"]),
            ce=randlib.choice(ce_inputs),
            clr=randlib.choice(ce_inputs),
            bufce_divide=randlib.choice(range(1, 9)))
    elif site_type == 'BUFG_PS':
        s = """
wire bufg_o_{idx};
(* LOC="{loc}", KEEP, DONT_TOUCH *) BUFG_PS #(
    ) bufg_{idx} (
        .O(bufg_o_{idx})
    );""".format(
            loc=site, idx=idx)
    elif site_type == 'BUFGCTRL':
        preselect_i0 = randlib.randint(2)
        if not preselect_i0:
            preselect_i1 = randlib.randint(2)
        else:
            preselect_i1 = 0

        s0 = randlib.choice(ce_inputs)
        s1 = randlib.choice(ce_inputs)
        if s0 == '0':
            while s1 == '0':
                s1 = randlib.choice(ce_inputs)

        if s0 == '0' and s1 == '1':
            invert_s0 = randlib.randint(2)
            invert_s1 = 0
        elif s0 == '1' and s1 == '0':
            invert_s1 = randlib.randint(2)
            invert_s0 = 0
        elif s0 == '1' and s1 == '1':
            invert_s0 = randlib.randint(2)
            if invert_s0:
                invert_s1 = 0
            else:
                invert_s1 = randlib.randint(2)
        else:
            invert_s0 = randlib.randint(2)
            invert_s1 = randlib.randint(2)

        s = """
wire bufg_o_{idx};
(* LOC="{loc}", KEEP, DONT_TOUCH *) BUFGCTRL #(
    .INIT_OUT({init_out}),
    .IS_CE0_INVERTED({invert_ce0}),
    .IS_CE1_INVERTED({invert_ce1}),
    .IS_S0_INVERTED({invert_s0}),
    .IS_S1_INVERTED({invert_s1}),
    .IS_IGNORE0_INVERTED({invert_ignore0}),
    .IS_IGNORE1_INVERTED({invert_ignore1}),
    .PRESELECT_I0({preselect_i0}),
    .PRESELECT_I1({preselect_i1})
    ) bufg_{idx} (
        .IGNORE0({ignore0}),
        .IGNORE1({ignore1}),
        .S0({s0}),
        .S1({s1}),
        .CE0({ce0}),
        .CE1({ce1}),
        .O(bufg_o_{idx})
    );""".format(
            loc=site,
            idx=idx,
            init_out=randlib.randint(2),
            s0=s0,
            s1=s1,
            ce0=randlib.choice(ce_inputs),
            ce1=randlib.choice(ce_inputs),
            ignore0=randlib.choice(ce_inputs),
            ignore1=randlib.choice(ce_inputs),
            invert_ce0=randlib.randint(2),
            invert_ce1=randlib.randint(2),
            invert_s0=invert_s0,
            invert_s1=invert_s1,
            invert_ignore0=randlib.randint(2),
            invert_ignore1=randlib.randint(2),
            preselect_i0=preselect_i0,
            preselect_i1=preselect_i1,
        )
    else:
        assert False, site_type

    return s, 'bufg_o_{idx}'.format(idx=idx)
