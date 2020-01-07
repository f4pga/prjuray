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
from utils.spec import bram_init
from utils import spec_top


def spec_num():
    return int(os.getenv('SPECDIR').split('_')[1])


SPECS = ((bram_init, 10), )


def main():
    spec_top.spec_top(SPECS)


if __name__ == "__main__":
    main()
