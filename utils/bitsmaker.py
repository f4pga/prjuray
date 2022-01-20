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

from utils import bitstream


def write(bits_fn, fnout, tags, bitfilter=None):
    '''
    seg 00020000_046
    bit 18_20
    bit 39_63
    tag LIOB33.IOB_Y1.REFBIT 0
    '''
    fout = open(fnout, "w")

    def line(s):
        fout.write(s + "\n")

    # Everything relative to start of bitstream
    line("seg 00000000_000")

    bitdata = bitstream.load_bitdata2(open(bits_fn, "r"))

    for frame, words in bitdata.items():
        for word, wbits in words.items():
            if bitfilter is not None:
                if not bitfilter(frame, word):
                    continue

            for bitidx in sorted(list(wbits)):
                # Are the names arbitrary? Lets just re-create
                line("bit %08X_%03u_%02u" % (frame, word, bitidx))

    for k, v in tags.items():
        line("tag %s %u" % (k, v))
