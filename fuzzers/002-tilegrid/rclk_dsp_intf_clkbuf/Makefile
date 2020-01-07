# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

N ?= 10
SEGMATCH_ARGS?=-c 9
GENERATE_ARGS?=--oneval 1 --design params.csv --dword 0 --auto_frame
TOP_DEPS?=$(BUILD_DIR)/active_bufce_row.csv

include ../fuzzaddr/common.mk

$(BUILD_DIR)/active_bufce_row.csv: ${URAY_UTILS_DIR}/generate_active_bufce_row.tcl
	mkdir -p $(BUILD_DIR)/active_bufce_row
	cd $(BUILD_DIR)/active_bufce_row && $(URAY_VIVADO) -mode batch -source ${URAY_UTILS_DIR}/generate_active_bufce_row.tcl
