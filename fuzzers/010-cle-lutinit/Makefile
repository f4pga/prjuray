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

BUILD_DIR=build
N := 4
SPECIMENS := $(addprefix $(BUILD_DIR)/specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))
database: $(SPECIMENS_OK)
	$(URAY_SEGMATCH) -o $(BUILD_DIR)/segbits_cle.db $(shell find $(BUILD_DIR) -name "segdata_cle*.txt")

pushdb:
	$(URAY_MERGEDB) clel_l $(BUILD_DIR)/segbits_cle.db
	$(URAY_MERGEDB) clel_r $(BUILD_DIR)/segbits_cle.db
	$(URAY_MERGEDB) clem $(BUILD_DIR)/segbits_cle.db
	$(URAY_MERGEDB) clem_r $(BUILD_DIR)/segbits_cle.db

define generate =
$(1)/top.v :
	bash generate_top.sh $(1)

$(1)/design_0.bit: $(1)/top.v
	cd $(1); \
	$(URAY_VIVADO) -mode batch -source ../../generate.tcl; \
	test -z "$$$$(fgrep CRITICAL vivado.log)"

$(1)/segdata: $(1)/design_0.bit
	cd $(1); \
	bash ../../generate.sh

$(1)/OK: $(1)/segdata
	touch $$@

endef

$(foreach specimen,$(SPECIMENS),$(eval $(call generate,$(specimen))))


run:
	$(MAKE) clean
	$(MAKE) database
	$(MAKE) pushdb
	touch run.ok

clean:
	rm -rf $(BUILD_DIR) run.ok

.PHONY: database pushdb run clean
