#!/bin/bash
#
# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

SPEC_DIR=$1

rm -f ${SPEC_DIR}/design.dcp
rm -f ${SPEC_DIR}/design.bit
echo "Generating bitstream for ${SPEC_DIR}"

pushd ${SPEC_DIR}
${URAY_VIVADO} -mode batch -source ../../generate.tcl > /dev/null
popd

if [[ ! -f "${SPEC_DIR}/design.dcp" || ! -f "${SPEC_DIR}/design.bit" ]]; then
    echo "Error with ${SPEC_DIR}"
    rm -f "${SPEC_DIR}/design.bit"
    rm -f "${SPEC_DIR}/design.dcp"
    exit 1
fi

echo "Bitstream for ${SPEC_DIR} complete"
