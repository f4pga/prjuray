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

for i in 0 ; do
	python3 ../../generate.py $i
done

