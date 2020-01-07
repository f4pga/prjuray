# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

all: build/sdf.ok

clean:
	rm -rf build
	rm -rf debug*.json

build/sdf.ok: build/run.ok tim2sdf.py
	PYTHONPATH=../utils python3 tim2sdf.py --timings build/bel_timings.txt --sdf build/ --debug
	touch build/sdf.ok

build/run.ok:
	bash runme.sh

.PHONY: all clean
