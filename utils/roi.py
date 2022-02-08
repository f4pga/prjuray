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


class Roi(object):
    """ Object that represents a Project X-ray ROI.

    Can be used to iterate over tiles and sites within an ROI.

    """

    def __init__(self, db, x1, x2, y1, y2):
        self.grid = db.grid()
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2

    def tile_in_roi(self, grid_loc):
        """ Returns true if grid_loc (GridLoc tuple) is within the ROI. """
        x = grid_loc.grid_x
        y = grid_loc.grid_y
        return self.x1 <= x and x <= self.x2 and self.y1 <= y and y <= self.y2

    def gen_tiles(self, tile_types=None):
        ''' Yield tile names within ROI.

        tile_types: list of tile types to keep, or None for all
        '''

        for tile_name in self.grid.tiles():
            loc = self.grid.loc_of_tilename(tile_name)

            if not self.tile_in_roi(loc):
                continue

            gridinfo = self.grid.gridinfo_at_loc(loc)

            if tile_types is not None and gridinfo.tile_type not in tile_types:
                continue

            yield tile_name

    def gen_sites(self, site_types=None):
        ''' Yield (tile_name, site_name, site_type) within ROI.

        site_types: list of site types to keep, or None for all

        '''

        for tile_name in self.grid.tiles():
            loc = self.grid.loc_of_tilename(tile_name)

            if not self.tile_in_roi(loc):
                continue

            gridinfo = self.grid.gridinfo_at_loc(loc)

            for site_name, site_type in gridinfo.sites.items():
                if site_types is not None and site_type not in site_types:
                    continue

                yield (tile_name, site_name, site_type)
