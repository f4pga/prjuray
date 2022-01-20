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
