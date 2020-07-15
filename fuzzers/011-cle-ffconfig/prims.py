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


def ones(l):
    #return l + [x + '_1' for x in l]
    #return sorted(l + [x + '_1' for x in l])
    ret = []
    for x in l:
        ret.append(x)
        ret.append(x + '_1')
    return ret


# The complete primitive sets
ffprims_fall = ones([
    'FD',
    'FDC',
    'FDCE',
    'FDE',
    'FDP',
    'FDPE',
    'FDR',
    'FDRE',
    'FDS',
    'FDSE',
])

ffprims_lall = ones([
    'LDC',
    'LDCE',
    'LDE',
    'LDPE',
    'LDP',
])

# Base primitives
ffprims_f = [
    'FDRE',
    'FDSE',
    'FDCE',
    'FDPE',
]
ffprims_l = [
    'LDCE',
    'LDPE',
]
ffprims = ffprims_fall + ffprims_lall


def isff(prim):
    return prim.startswith("FD")


def isl(prim):
    return prim.startswith("LD")


ff_bels_2 = [
    'AFF2',
    'BFF2',
    'CFF2',
    'DFF2',
    'EFF2',
    'FFF2',
    'GFF2',
    'HFF2',
]
ff_bels_ffl = [
    'AFF',
    'BFF',
    'CFF',
    'DFF',
    'EFF',
    'FFF',
    'GFF',
    'HFF',
]

ff_bels = ff_bels_ffl + ff_bels_2
