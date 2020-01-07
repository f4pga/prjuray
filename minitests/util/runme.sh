#!/bin/bash
#
# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

set -ex
python3 $URAY_DIR/minitests/util/runme.py
${URAY_BITREAD} -F $URAY_ROI_FRAMES -o design.bits -z -y build/design.bit
test -z "$(fgrep CRITICAL build/vivado.log)"
# TODO uncomment once tilegrid generation works
#${URAY_SEGPRINT} -z -D design.bits  >design.txt

