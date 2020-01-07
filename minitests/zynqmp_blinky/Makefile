# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

.PHONY: clean all

all: top.bit fsbl.elf

fsbl.elf:
	$(MAKE) -C ps
	mkdir -p build
	cp ps/fsbl.elf build/

top.bit:
	$(MAKE) -C pl
	mkdir -p build
	cp pl/top.bit build/

program: build/fsbl.elf build/top.bit
	bash program.sh
clean:
	$(MAKE) -C ps clean
	$(MAKE) -C pl clean
	rm -rf build
