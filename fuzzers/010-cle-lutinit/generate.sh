#!/bin/bash
#
# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

for i in 0 1; do
	${URAY_BITREAD} -F $URAY_ROI_FRAMES -o design_$i.bits -z -y design_$i.bit
done

for i in 0 1; do
	python3 ../../generate.py $i
done

