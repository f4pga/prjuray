#!/bin/bash -x
# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

source ${URAY_GENHEADER}

python3 $FUZDIR/run_fuzzer.py $2 $3 $4

cd $FUZDIR && ./generate_after_dump.sh
