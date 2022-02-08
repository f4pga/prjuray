#!/bin/bash -xe
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

# By default use ~50 GiB for generate_grid.py, but allow override.
export DEFAULT_MAX_GRID_CPU=10

export BUILD_DIR=build_${URAY_PART}
rm -rf ${BUILD_DIR}/output
mkdir -p ${BUILD_DIR}/output
python3 reduce_tile_types.py \
  --root_dir ${BUILD_DIR}/specimen_001/ \
  --output_dir ${BUILD_DIR}/output
python3 reduce_site_types.py --output_dir ${BUILD_DIR}/output
python3 generate_grid.py \
  --root_dir ${BUILD_DIR}/specimen_001/ \
  --output_dir ${BUILD_DIR}/output \
  --ignored_wires ignored_wires/${URAY_DATABASE}/${URAY_PART}_ignored_wires.txt \
  --max_cpu=${MAX_GRID_CPU:-${DEFAULT_MAX_GRID_CPU}}
