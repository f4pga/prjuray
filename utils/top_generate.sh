#!/bin/bash
#
# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
# Generic generate.sh for scripts that use top.py to generate top.v
# and then use generate.py for segment generation

set -ex

export FUZDIR=$PWD
source ${URAY_GENHEADER}

echo '`define SEED 32'"'h$(echo $1 | md5sum | cut -c1-8)" > setseed.vh

make -f $URAY_DIR/utils/top_generate.mk

