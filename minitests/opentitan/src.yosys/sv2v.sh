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
PRIM_ASSERT_PATH=$(find .. -name prim_assert.sv)
PRIM_ASSERT_DIR=$(dirname ${PRIM_ASSERT_PATH})
PKG_FILES=$(find .. -name "*_pkg.sv")
if [ "$1" = "prim_generic_pad_wrapper.v" ]; then
	sv2v --define=VERILATOR --define=SYNTHESIS --incdir=$PRIM_ASSERT_DIR $2 > $1
elif [ "$1" = "prim_generic_rom.v" ] || [ "$1" = "prim_xilinx_rom.v" ]; then
	sv2v --define=SYNTHESIS --define=ROM_INIT_FILE=../boot_rom_fpga_nexysvideo.vmem --incdir=$PRIM_ASSERT_DIR $2 > $1
else
	sv2v --define=SYNTHESIS --incdir=$PRIM_ASSERT_DIR $PRIM_ASSERT_PATH $PKG_FILES $2 > $1
fi


if [ "$1" = "prim_lfsr.v" ]; then
	sed -i 's/sv2v_cast_64\((["A-Za-z0-9_]*)\)/\1/g' $1
fi
sed -i 's/parameter unsigned/parameter/g' $1
sed -i 's/localparam unsigned/localparam/g' $1
sed -i 's/if (.*) ;//g' $1
