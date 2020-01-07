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

from utils.segmaker import Segmaker

segmk = Segmaker("design.bits", bits_per_word=16)

print("Loading tags")
'''
site,bel,rs_inv
SLICE_X12Y100,AFF,0
SLICE_X13Y100,EFF,1
'''
f = open('params.csv', 'r')
f.readline()
for l in f:
    site, bel, rs_inv = l.split(',')
    rs_inv = int(rs_inv)

    segmk.add_site_tag(site, "RST_ABCDINV" if bel == "AFF" else "RST_EFGHINV",
                       rs_inv)
segmk.compile()
segmk.write()
