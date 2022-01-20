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

N ?= 5
GENERATE_ARGS?=--oneval 1 --design params.csv --dframe 00 --dword 06
TOP_DEPS?=$(BUILD_DIR)/general_purpose_io_sites.txt

include ../fuzzaddr/common.mk

$(BUILD_DIR)/general_purpose_io_sites.txt:
	mkdir -p $(BUILD_DIR)/allowed_sites; \
	cd $(BUILD_DIR)/allowed_sites; \
	$(URAY_VIVADO) -mode batch -source $(URAY_UTILS_DIR)/get_general_purpose_io.tcl
