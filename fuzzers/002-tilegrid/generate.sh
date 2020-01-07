#!/bin/bash -x
# Copyright (C) 2017-2020  The Project X-Ray Authors.
# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

PRJ=$2

export FUZDIR=$PWD
source ${URAY_GENHEADER}

${URAY_VIVADO} -mode batch -source $FUZDIR/generate_$PRJ.tcl
test -z "$(fgrep CRITICAL vivado.log)"

if [ $PRJ != "tiles" ] ; then
    for x in design*.bit; do
	    ${URAY_BITREAD} -F $URAY_ROI_FRAMES -o ${x}s -z -y $x
    done

    for x in design_*.bits; do
	    diff -u design.bits $x | grep '^[-+]bit' > ${x%.bits}.delta
    done
    touch deltas
fi

