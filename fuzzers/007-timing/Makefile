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

SLICEL_SDFS = bel/build/SLICEL.sdf routing-bels/build/SLICEL.sdf
SLICEM_SDFS = bel/build/SLICEM.sdf routing-bels/build/SLICEM.sdf
RAMBFIFO36_SDFS = bel/build/RAMBFIFO36.sdf routing-bels/build/RAMBFIFO36.sdf
RAMB181_SDFS = bel/build/RAMB181.sdf routing-bels/build/RAMB181.sdf
URAM_SDFS = bel/build/URAM288.sdf routing-bels/build/URAM288.sdf

run: all
all: pushdb

clean:
	rm -rf sdfs
	cd bel && $(MAKE) clean
	cd routing-bels && $(MAKE) clean

bel/build/sdf.ok:
	cd bel && $(MAKE) build/sdf.ok

routing-bels/build/sdf.ok:
	cd routing-bels && $(MAKE) build/sdf.ok

database: bel/build/sdf.ok routing-bels/build/sdf.ok
	mkdir -p sdfs
	python3 ${URAY_UTILS_DIR}/sdfmerge.py --sdfs $(SLICEL_SDFS) --site SLICEL --out sdfs/SLICEL.sdf
	python3 ${URAY_UTILS_DIR}/sdfmerge.py --sdfs $(SLICEM_SDFS) --site SLICEM --out sdfs/SLICEM.sdf
	python3 ${URAY_UTILS_DIR}/sdfmerge.py --sdfs $(RAMBFIFO36_SDFS) --site RAMBFIFO36 --out sdfs/RAMBFIFO36.sdf
	python3 ${URAY_UTILS_DIR}/sdfmerge.py --sdfs $(RAMB181_SDFS) --site RAMB181 --out sdfs/RAMB181.sdf
ifeq (${URAY_PART}, xczu7ev-ffvc1156-2-i)
	python3 ${URAY_UTILS_DIR}/sdfmerge.py --sdfs $(URAM_SDFS) --site URAM288 --out sdfs/URAM288.sdf
endif

pushdb: database
	mkdir -p ${URAY_DATABASE_DIR}/${URAY_DATABASE}/timings
	cp sdfs/*.sdf ${URAY_DATABASE_DIR}/${URAY_DATABASE}/timings
	touch run.ok

cleandb:
	rm -rf ${URAY_DATABASE_DIR}/${URAY_DATABASE}/timings

.PHONY: run all clean cleandb
