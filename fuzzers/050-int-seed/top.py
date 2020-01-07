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

from utils.spec import slice_logic
from utils.spec import slice_carry
from utils.spec import slice_memory
from utils.spec import flipflops
from utils.spec import memory
from utils.spec import rclk_int
from utils.spec import rclk_int_3
from utils.spec import gclk
from utils.spec import gclk_2
from utils.spec import gclk_3
from utils.spec import gclk_4
from utils.spec import picosoc
from utils import spec_top

SAMPLES = 3
SPECS = (
    (picosoc, 4 * SAMPLES),
    (slice_memory, SAMPLES),
    (slice_logic, SAMPLES),
    (memory, SAMPLES),
    (flipflops, SAMPLES),
    (slice_carry, SAMPLES),
    (rclk_int, SAMPLES),
    (rclk_int_3, SAMPLES),
    (gclk, SAMPLES),
    (gclk_2, SAMPLES),
    (gclk_3, SAMPLES),
    (gclk_4, SAMPLES),
)


def main():
    spec_top.spec_top(SPECS)


if __name__ == "__main__":
    main()
