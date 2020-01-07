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


def print_top(seed):
    with open(os.path.join(os.environ['URAY_DIR'], 'spec',
                           'picosoc_top.v')) as f:
        print(f.read())

    with open(
            os.path.join(os.environ['URAY_DIR'], 'third_party', 'picosoc',
                         'picorv32.v')) as f:
        print(f.read())
