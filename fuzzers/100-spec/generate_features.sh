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

pushd ${SPEC_DIR}
echo "Generating features for ${SPEC_DIR}"
${URAY_VIVADO} -mode batch -source ../../dump_features.tcl > /dev/null

if grep -q ERROR vivado.log ; then
    echo "ERROR found in log for ${SPEC_DIR}"
    exit 1
fi

popd

if [[ ! -f "${SPEC_DIR}/design_1.features" ]]; then
    echo "Missing design_1.feature file for ${SPEC_DIR}"
    exit 1
fi
if [[ ! -f "${SPEC_DIR}/design_2.features" ]]; then
    echo "Missing design_2.feature file for ${SPEC_DIR}"
    exit 1
fi
if [[ ! -f "${SPEC_DIR}/design_3.features" ]]; then
    echo "Missing design_3.feature file for ${SPEC_DIR}"
    exit 1
fi

cat \
    ${SPEC_DIR}/design_1.features \
    ${SPEC_DIR}/design_2.features \
    ${SPEC_DIR}/design_3.features \
    > ${SPEC_DIR}/design.features
echo "Successfully generated features for ${SPEC_DIR}"
