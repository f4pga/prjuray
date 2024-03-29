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

BUILD_DIR = build
N := 4

TILE_TYPES := clel_l clel_r clem clem_r

SPECIMENS := $(addprefix $(BUILD_DIR)/specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

DB_FILES = $(addsuffix .db,$(addprefix $(BUILD_DIR)/segbits_,$(TILE_TYPES)))

.PRECIOUS: $(SPECIMENS_OK) $(BUILD_DIR)/%.rdb

$(BUILD_DIR)/%.rdb: $(SPECIMENS_OK)
	$(URAY_SEGMATCH) -o $@ $(addsuffix /$(subst segbits,segdata,$(subst .rdb,.txt,$(notdir $@))),$(SPECIMENS))

$(BUILD_DIR)/%.db : $(BUILD_DIR)/%.rdb tag_groups.txt
	$(URAY_DBFIXUP) --seg-fn-in $< --seg-fn-out $@ -g tag_groups.txt

database: $(DB_FILES)

pushdb: $(DB_FILES)
	$(URAY_MERGEDB) $(subst segbits_,,$(basename $(notdir $<))) $<


define generate =
$(1)/top.v :
	bash top.sh $(1)

$(1)/design.bit: $(1)/top.v
	cd $(1); \
	$(URAY_VIVADO) -mode batch -source ../../generate.tcl; \
	test -z "$$$$(fgrep CRITICAL vivado.log)"

$(1)/segdata: $(1)/design.bit
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
