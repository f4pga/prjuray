# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

FUZDIR=$(shell pwd)
BUILD_FOLDER=build_${URAY_PART}
BUILD_DIR=$(FUZDIR)/$(BUILD_FOLDER)
TILEGRID_TDB_DEPENDENCIES=
TILEGRID_TDB_DEPENDENCIES += cle/$(BUILD_FOLDER)/segbits_tilegrid.tdb \
                             clem_r/$(BUILD_FOLDER)/segbits_tilegrid.tdb \
                             clel_int/$(BUILD_FOLDER)/segbits_tilegrid.tdb \
                             clem_int/$(BUILD_FOLDER)/segbits_tilegrid.tdb \
                             rclk_int/$(BUILD_FOLDER)/segbits_tilegrid.tdb \
                             bram/$(BUILD_FOLDER)/segbits_tilegrid.tdb \
                             bram_block/$(BUILD_FOLDER)/segbits_tilegrid.tdb

ifeq (${URAY_ARCH}, UltraScalePlus)
TILEGRID_TDB_DEPENDENCIES += rclk_other/$(BUILD_FOLDER)/segbits_tilegrid.tdb \
                             rclk_hdio/$(BUILD_FOLDER)/segbits_tilegrid.tdb \
                             rclk_pss_alto/$(BUILD_FOLDER)/segbits_tilegrid.tdb \
                             cmt_right/$(BUILD_FOLDER)/segbits_tilegrid.tdb \
                             intf_r_pcie4_hdio/$(BUILD_FOLDER)/segbits_tilegrid.tdb \
                             pss_alto/$(BUILD_FOLDER)/segbits_tilegrid.tdb \
                             hdio_top_right/$(BUILD_FOLDER)/segbits_tilegrid.tdb \
                             hdio_bot_right/$(BUILD_FOLDER)/segbits_tilegrid.tdb \
                             hpio_right/$(BUILD_FOLDER)/segbits_tilegrid.tdb \
                             rclk_dsp_intf_clkbuf/$(BUILD_FOLDER)/segbits_tilegrid.tdb \
                             ps8_intf/$(BUILD_FOLDER)/segbits_tilegrid.tdb \
                             bitslice_tiles/$(BUILD_FOLDER)/segbits_tilegrid.tdb
endif

GENERATE_FULL_ARGS=

database: $(BUILD_FOLDER)/tilegrid.json

pushdb: $(BUILD_FOLDER)/tilegrid.json
	cp $(BUILD_FOLDER)/tilegrid.json ${URAY_FAMILY_DIR}/${URAY_PART}/tilegrid.json

$(BUILD_FOLDER)/tiles/tiles.txt:
	bash generate.sh $(BUILD_FOLDER)/tiles tiles

$(BUILD_FOLDER)/basicdb/${URAY_PART}/tilegrid.json: generate.py $(BUILD_FOLDER)/tiles/tiles.txt
	mkdir -p $(BUILD_FOLDER)/basicdb/${URAY_PART}
	mkdir -p $(BUILD_FOLDER)/basicdb/tile_types
	mkdir -p $(BUILD_FOLDER)/basicdb/site_types
	cd $(BUILD_FOLDER) && python3 ${FUZDIR}/generate.py \
		--tiles $(FUZDIR)/$(BUILD_FOLDER)/tiles/tiles.txt \
		--pin_func $(FUZDIR)/$(BUILD_FOLDER)/tiles/pin_func.txt \
		--out ${BUILD_DIR}/basicdb/${URAY_PART}/tilegrid.json

define segbits_tilegrid_tdb =
$(1): $(BUILD_FOLDER)/basicdb/${URAY_PART}/tilegrid.json
	cd $(2) && $$(MAKE)
endef

$(foreach tdb,$(TILEGRID_TDB_DEPENDENCIES),$(eval $(call segbits_tilegrid_tdb,$(tdb),$(firstword $(subst /, ,$(tdb))))))

$(BUILD_FOLDER)/tilegrid_tdb.json: add_tdb.py $(TILEGRID_TDB_DEPENDENCIES)
	python3 add_tdb.py \
		--fn-in $(BUILD_FOLDER)/basicdb/${URAY_PART}/tilegrid.json \
		--fn-out $(BUILD_FOLDER)/tilegrid_tdb.json

$(BUILD_FOLDER)/tilegrid.json: generate_full.py $(BUILD_FOLDER)/tilegrid_tdb.json
	cd $(BUILD_FOLDER) && python3 ${FUZDIR}/generate_full.py \
		--json-in tilegrid_tdb.json \
		--json-out tilegrid.json

run:
	$(MAKE) clean
	$(MAKE) database
	$(MAKE) pushdb
	touch run.ok

define clean_tdb =
clean_$(1):
	cd $(2) && $$(MAKE) clean
endef

$(foreach tdb,$(TILEGRID_TDB_DEPENDENCIES),$(eval $(call clean_tdb,$(tdb),$(firstword $(subst /, ,$(tdb))))))

clean: $(foreach tdb,$(TILEGRID_TDB_DEPENDENCIES),clean_$(tdb))
	rm -rf $(BUILD_FOLDER) run.ok

.PHONY: database pushdb clean run

