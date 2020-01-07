#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2020  The Project X-Ray Authors.
# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

import os
import random
random.seed(int(os.getenv("SEED"), 16))
from utils.spec import io_base_address

if __name__ == '__main__':
    io_base_address.run('HPIO_RIGHT')
