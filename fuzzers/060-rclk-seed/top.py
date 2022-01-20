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
