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

from utils.spec import io
from utils.spec import iologic
from utils.spec import empty
from utils import spec_top

SPECS = (
    (io, 125),
    (iologic, 100),
    (empty, 1),
)


def main():
    spec_top.spec_top(SPECS)


if __name__ == "__main__":
    main()
