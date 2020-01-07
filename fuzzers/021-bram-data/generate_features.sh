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
${URAY_VIVADO} -mode batch -source ../../dump_features.tcl  > /dev/null

if grep -q ERROR vivado.log ; then
    echo "ERROR found in log for ${SPEC_DIR}"
    exit 1
fi

popd

if [[ ! -f "${SPEC_DIR}/design.features" ]]; then
    echo "Missing design.feature file for ${SPEC_DIR}"
    exit 1
fi

echo "Successfully generated features for ${SPEC_DIR}"
