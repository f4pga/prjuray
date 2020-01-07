#!/bin/bash
#
# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
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
