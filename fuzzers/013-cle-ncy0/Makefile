# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

BUILD_DIR = build
N := 3

SPECIMENS := $(addprefix $(BUILD_DIR)/specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: $(SPECIMENS_OK)
	$(URAY_SEGMATCH) -o $(BUILD_DIR)/segbits_cle.db $(shell find build -name "segdata_cle*.txt")

pushdb:
	$(URAY_MERGEDB) clel_l $(BUILD_DIR)/segbits_cle.db
	$(URAY_MERGEDB) clel_r $(BUILD_DIR)/segbits_cle.db
	$(URAY_MERGEDB) clem $(BUILD_DIR)/segbits_cle.db
	$(URAY_MERGEDB) clem_r $(BUILD_DIR)/segbits_cle.db

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
