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
'''
FDCE Primitive: D Flip-Flop with Clock Enable and Asynchronous Clear
FDPE Primitive: D Flip-Flop with Clock Enable and Asynchronous Preset
FDRE Primitive: D Flip-Flop with Clock Enable and Synchronous Reset
FDSE Primitive: D Flip-Flop with Clock Enable and Synchronous Set
LDCE Primitive: Transparent Data Latch with Asynchronous Clear and Gate Enable
LDPE Primitive: Transparent Data Latch with Asynchronous Preset and Gate Enable
'''

from prims import isff, isl

from utils.segmaker import Segmaker

segmk = Segmaker("design.bits", bits_per_word=16)


def loadtop():
    '''
    i,prim,loc,bel
    0,FDPE,SLICE_X12Y100,C5FF
    1,FDPE,SLICE_X15Y100,A5FF
    2,FDPE_1,SLICE_X16Y100,B5FF
    3,LDCE_1,SLICE_X17Y100,BFF
    '''
    f = open('top.txt', 'r')
    f.readline()
    ret = {}
    for l in f:
        i, prim, loc, bel, init = l.split(",")
        i = int(i)
        init = int(init)
        ret[loc] = (i, prim, loc, bel, init)
    return ret


top = loadtop()


def vs2i(s):
    return {"1'b0": 0, "1'b1": 1}[s]


print("Loading tags from design.txt")
with open("design.txt", "r") as f:
    for line in f:
        '''
        puts $fp "$type $tile $grid_x $grid_y $ff $bel_type $used $usedstr"

        CLEM CLEM_X10Y137 30 13 SLICE_X13Y137/AFF REG_INIT 1 FDRE
        CLEM CLEM_X10Y137 30 13 SLICE_X12Y137/D2FF FF_INIT 0
        '''
        line = line.split()
        tile_type = line[0]
        tile_name = line[1]
        grid_x = line[2]
        grid_y = line[3]
        # Other code uses BEL name
        # SLICE_X12Y137/D2FF
        site_ff_name = line[4]
        site, ff_name = site_ff_name.split('/')
        ff_type = line[5]
        used = int(line[6])
        cel_prim = None
        cel_name = None
        if used:
            cel_name = line[7]
            cel_prim = line[8]
            cinv = int(line[9])
            init = vs2i(line[10])

        # A B C D E F G H
        which = ff_name[0]
        # LUT6 vs LUT5 FF
        is2 = '2' in ff_name

        if used:
            segmk.add_site_tag(site, "%s.ZINI" % ff_name, 1 ^ init)
            '''
            On name:
            The primitives you listed have a control input to set the FF value to zero (clear/reset),
            the other three primitives have a control input that sets the FF value to one.
            Z => inversion
            '''
            segmk.add_site_tag(site, "%s.ZRST" % ff_name,
                               cel_prim in ('FDRE', 'FDCE', 'LDCE'))

segmk.compile()
segmk.write()
