# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

all: build/all_sdf.ok

clean:
	rm -rf build
	rm -rf debug*.json

build/run.ok:
	bash runme.sh
	touch build/run.ok

build/fixup_timings: build/run.ok
	touch build/fixup_timings

build/bel_timings.json: build/fixup_timings tim2json.py
	PYTHONPATH=../utils python3 tim2json.py --timings=build/bel_timings.txt --json=build/bel_timings.json --cellpins=build/cell_pins.txt --debug

build/sdf.ok: build/bel_timings.json ${URAY_UTILS_DIR}/makesdf.py
	python3 ${URAY_UTILS_DIR}/makesdf.py --json=${PWD}/build/bel_timings.json --sdf=${PWD}/build
	touch build/sdf.ok

.PHONY: all clean
