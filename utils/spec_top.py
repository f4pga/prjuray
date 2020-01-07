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

import os
import random
import inspect


def spec_num():
    return int(os.getenv('SPECDIR').split('_')[1])


def spec_top(specs):
    N = spec_num()
    seed = int(os.getenv("SEED"), 16)
    with open('top.tcl', 'w') as f:
        f.write('\n')

    with open('top.xdc', 'w') as f:
        pass

    with open('complete_top.tcl', 'w') as f:
        print('place_design -directive Quick', file=f)
        print('route_design -directive Quick', file=f)

    all_funcs = []

    for func, num_instances in specs:
        all_funcs.append(func)

    max_count = 0
    for func, num_instances in specs:
        prev_count = max_count
        max_count += num_instances
        if N <= max_count:
            print('// ', func)
            func_sig = inspect.signature(func.print_top)
            if 'offset' in func_sig.parameters:
                func.print_top(seed, offset=N - prev_count)
            else:
                func.print_top(seed)
            return

    random.seed(seed)
    fun = random.choice(all_funcs)
    print('// ', fun)
    fun.print_top(seed)
