#!/bin/bash -x
# Copyright 2020-2022 F4PGA Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

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

