# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

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
