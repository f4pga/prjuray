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
