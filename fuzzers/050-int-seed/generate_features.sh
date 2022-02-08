#!/bin/bash
#
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

pushd ${SPEC_DIR}
echo "Generating features for ${SPEC_DIR}"
${URAY_VIVADO} -mode batch -source ../../dump_features.tcl > /dev/null

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
