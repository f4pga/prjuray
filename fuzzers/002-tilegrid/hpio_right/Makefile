# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

N ?= 5
GENERATE_ARGS?=--oneval 1 --design params.csv --dframe 02 --dword 4
TOP_DEPS?=$(BUILD_DIR)/general_purpose_io_sites.txt

include ../fuzzaddr/common.mk

$(BUILD_DIR)/general_purpose_io_sites.txt:
	mkdir -p $(BUILD_DIR)/allowed_sites; \
	cd $(BUILD_DIR)/allowed_sites; \
	$(URAY_VIVADO) -mode batch -source $(URAY_UTILS_DIR)/get_general_purpose_io.tcl
