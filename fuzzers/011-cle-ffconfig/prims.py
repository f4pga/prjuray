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
