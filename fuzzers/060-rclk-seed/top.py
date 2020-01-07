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

from utils.spec import rclk_int_3
from utils.spec import rclk_int_4
from utils.spec import rclk_int_5
from utils.spec import rclk_int_7
from utils.spec import rclk_int_8
from utils.spec import rclk_int_9
from utils.spec import rclk_int_10
from utils.spec import rclk_int_11
from utils.spec import rclk_int_12
from utils.spec import gclk_3
from utils.spec import gclk_4
from utils.spec import picosoc
from utils import spec_top

SPECS = (
    (rclk_int_12, 20),
    (rclk_int_11, 50),
    (rclk_int_10, 50),
    (rclk_int_9, 40),
    (rclk_int_5, 25),
    (gclk_3, 35),
    (gclk_4, 35),
    (rclk_int_8, 50),
    (rclk_int_7, 25),
    (rclk_int_4, 25),
    (rclk_int_3, 25),
    (picosoc, 25),
)


def main():
    spec_top.spec_top(SPECS)


if __name__ == "__main__":
    main()
