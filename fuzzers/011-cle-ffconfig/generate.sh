#!/bin/bash
#
# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
${URAY_BITREAD} -F $URAY_ROI_FRAMES -o design.bits -z -y design.bit

touch segdata_clel_l.txt
touch segdata_clel_r.txt
touch segdata_clem.txt
touch segdata_clem_r.txt

python3 ../../generate.py
