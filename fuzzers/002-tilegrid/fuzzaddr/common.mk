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

N ?= 10
BUILD_DIR=build_$(URAY_PART)
SEGMATCH_ARGS ?=
GENERATE_ARGS ?=
TOP_DEPS ?=
SPECIMENS := $(addprefix $(BUILD_DIR)/specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))
export FUZDIR=$(PWD)

database: $(BUILD_DIR)/segbits_tilegrid.tdb

$(BUILD_DIR)/segbits_tilegrid.tdb: $(SPECIMENS_OK)
	$(URAY_SEGMATCH) $(SEGMATCH_ARGS) -o $(BUILD_DIR)/segbits_tilegrid.tdb $$(find $(BUILD_DIR) -name "segdata_tilegrid.txt")

define generate =
$(1)/top.v $(1)/params.csv: $(TOP_DEPS)
	GENERATE_ARGS="$(GENERATE_ARGS)" bash ../fuzzaddr/generate.sh $(1)

$(1)/design.bit $(1)/design.dcp: $(1)/top.v
	cd $(1); \
	$(URAY_VIVADO) -mode batch -source $(FUZDIR)/generate.tcl; \
	test -z "$$$$(fgrep CRITICAL vivado.log)"

$(1)/design.bits: $(1)/design.bit
	$(URAY_BITREAD) -F $(URAY_ROI_FRAMES) -o $$@ -z -y $$<

$(1)/segdata_tilegrid.txt: $(1)/design.bits
	cd $(1); \
	python3 $(FUZDIR)/../fuzzaddr/generate.py $(GENERATE_ARGS) > segdata_tilegrid.txt

$(1)/OK: $(1)/segdata_tilegrid.txt
	touch $$@

endef

$(foreach specimen,$(SPECIMENS),$(eval $(call generate,$(specimen))))

run:
	$(MAKE) clean
	$(MAKE) database
	$(MAKE) pushdb
	touch run.ok

clean:
	rm -rf $(BUILD_DIR)

.PHONY: database pushdb run clean

