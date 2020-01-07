# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

vivado:
	python3 runme.py

yosys-vivado:
	mkdir -p build
	cp mem* build/
	env USE_YOSYS=1 python3 runme.py

clean:
	rm -rf build
