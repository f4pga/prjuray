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
