# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

N ?= 30
GENERATE_ARGS?=--oneval 1 --design params.csv --dword 1 --auto_frame
TOP_DEPS?=$(BUILD_DIR)/ps8_intf.csv $(BUILD_DIR)/ps8_pin_map.csv

include ../fuzzaddr/common.mk

$(BUILD_DIR)/ps8_intf.csv: ${URAY_UTILS_DIR}/get_ps8_intf.tcl
	mkdir -p $(BUILD_DIR)/ps8_intf
	cd $(BUILD_DIR)/ps8_intf && $(URAY_VIVADO) -mode batch -source ${URAY_UTILS_DIR}/get_ps8_intf.tcl

$(BUILD_DIR)/ps8_pin_map.csv: ${URAY_UTILS_DIR}/get_ps8_pin_map.tcl
	mkdir -p $(BUILD_DIR)/ps8_pin_map
	cd $(BUILD_DIR)/ps8_pin_map && $(URAY_VIVADO) -mode batch -source ${URAY_UTILS_DIR}/get_ps8_pin_map.tcl
