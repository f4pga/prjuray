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

import numpy as np


def print_top(seed):
    np.random.seed(seed)

    print("")
    print("module top();")
    N = 24
    bram_init = []  # ypos -> init; initp
    for y in range(N):
        bram_init.append((
            np.random.randint(0, 2, size=16384),
            np.random.randint(0, 2, size=2048),
        ))
    for y in range(N):
        print("(* KEEP, DONT_TOUCH, LOC=\"RAMB18_X1Y%d\" *)" % y)
        print("RAMB18E2 #(")
        for i in range(0, 64):
            print("    .INIT_%02X(256'b%s)," % (i, "".join([
                str(x)
                for x in reversed(bram_init[y][0][i * 256:(i + 1) * 256])
            ])))
        for i in range(0, 8):
            print("    .INITP_%02X(256'b%s)," % (i, "".join([
                str(x)
                for x in reversed(bram_init[y][1][i * 256:(i + 1) * 256])
            ])))
        print("    .DOA_REG(1'b0)")  # just here for simpler commas
        print(") bram_%d ();" % y)
    print("endmodule")
