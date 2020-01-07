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
from utils import spec_top

SPECS = (
    (slice_memory, 10),
    (slice_logic, 10),
    (memory, 10),
    (flipflops, 10),
    (slice_carry, 10),
)


def main():
    spec_top.spec_top(SPECS)


if __name__ == "__main__":
    main()
