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

#export FUZDIR=$PWD
source ${URAY_GENHEADER}

# Some projects have hard coded top.v, others are generated
if [ -f $FUZDIR/top.py ] ; then
    set +e
    URAY_DATABASE_ROOT=$FUZDIR/../build_${URAY_PART}/basicdb python3 $FUZDIR/top.py >top.v
    RET=$?
    set -e
    if [ $RET -ne 0 ]; then
        rm top.v
        exit $RET
    fi
fi
