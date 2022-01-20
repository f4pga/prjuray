#!/bin/bash
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
