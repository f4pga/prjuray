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
