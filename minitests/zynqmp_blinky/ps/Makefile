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

ifndef URAY_DIR
$(error "Env variable URAY_DIR is not set. \
	Source the selected settings script from the project's main directory, \
	for example: settings/zynqus.sh")
endif
EMBEDDEDSW_DIR = $(URAY_DIR)/third_party/embeddedsw
ZYNQMP_FSBL_DIR = $(EMBEDDEDSW_DIR)/lib/sw_apps/zynqmp_fsbl
ZYNQMP_FSBL_SRC = $(ZYNQMP_FSBL_DIR)/src
BOARD_DIR = $(ZYNQMP_FSBL_DIR)/misc/zcu104
PWD = $(shell pwd)

all: fsbl.elf

fsbl.elf:
	if [ ! -d $(BOARD_DIR) ]; then \
		cd $(EMBEDDEDSW_DIR); \
		git am < $(PWD)/0001-Add-zcu104.patch; \
	fi
	$(MAKE) -C $(ZYNQMP_FSBL_SRC) BOARD=zcu104 PROC=a53
	cp $(ZYNQMP_FSBL_SRC)/fsbl.elf .

clean:
	rm -rf fsbl.elf
	$(MAKE) -C $(ZYNQMP_FSBL_SRC) clean
	rm -rf $(ZYNQMP_FSBL_DIR)/misc/zynqmp_fsbl_bsp
