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
N := 405

SPECIMENS := $(addprefix $(BUILD_DIR)/specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))
SPECIMENS_top := $(addsuffix /top.v,$(SPECIMENS))
SPECIMENS_bits := $(addsuffix /design_bits.ok,$(SPECIMENS))
SPECIMENS_features := $(addsuffix /design.features,$(SPECIMENS))

database: $(BUILD_DIR)/invpips.txt $(SPECIMENS_OK) solution_width.txt
	cd $(BUILD_DIR) && python3 ${URAY_UTILS_DIR}/segmatch_all_types.py \
		--filter_solution_width ../solution_width.txt

bits: $(SPECIMENS_bits)
	true

top: $(SPECIMENS_top)
	true

features: $(SPECIMENS_features)
	true

$(BUILD_DIR)/extent_features_with_pips.txt: ${URAY_UTILS_DIR}/create_feature_extents.py $(BUILD_DIR)/all_pips/design.features $(SPECIMENS_features)
	python3 ${URAY_UTILS_DIR}/create_feature_extents.py \
		--root_dir $(BUILD_DIR) \
		--extent_features $(BUILD_DIR)/extent_features_with_pips.txt

generate: $(BUILD_DIR)/invpips.txt $(SPECIMENS_OK)
	true

pushdb:
	$(URAY_MERGEDB) cmt_right $(BUILD_DIR)/segbits_cmt_right.db
	$(URAY_MERGEDB) rclk_int_l $(BUILD_DIR)/segbits_rclk_int.db
	$(URAY_MERGEDB) rclk_int_r $(BUILD_DIR)/segbits_rclk_int.db
	$(URAY_MERGEDB) rclk_clel_l_l $(BUILD_DIR)/segbits_rclk_cle.db
	$(URAY_MERGEDB) rclk_clem_r $(BUILD_DIR)/segbits_rclk_cle.db
	$(URAY_MERGEDB) rclk_clem_l $(BUILD_DIR)/segbits_rclk_cle.db
	$(URAY_MERGEDB) rclk_bram_intf_l $(BUILD_DIR)/segbits_rclk_bram_intf.db
	$(URAY_MERGEDB) rclk_bram_intf_td_l $(BUILD_DIR)/segbits_rclk_bram_intf.db
	$(URAY_MERGEDB) rclk_bram_intf_td_r $(BUILD_DIR)/segbits_rclk_bram_intf.db
	$(URAY_MERGEDB) rclk_dsp_intf_l $(BUILD_DIR)/segbits_rclk_dsp_intf.db
	$(URAY_MERGEDB) rclk_dsp_intf_r $(BUILD_DIR)/segbits_rclk_dsp_intf.db
	$(URAY_MERGEDB) rclk_dsp_intf_clkbuf_l $(BUILD_DIR)/segbits_rclk_dsp_intf_clkbuf_l.db
	$(URAY_MERGEDB) rclk_hdio $(BUILD_DIR)/segbits_rclk_hdio.db
	$(URAY_MERGEDB) rclk_ams_cfgio $(BUILD_DIR)/segbits_rclk_ams_cfgio.db
	$(URAY_MERGEDB) rclk_intf_left_term_alto $(BUILD_DIR)/segbits_rclk_intf_left_term_alto.db
	$(URAY_MERGEDB) rclk_xiphy_outer_right $(BUILD_DIR)/segbits_rclk_xiphy_outer_right.db

$(BUILD_DIR)/all_pips/design.features: ${URAY_UTILS_DIR}/generate_all_pip_features.tcl
	mkdir -p $(BUILD_DIR)/all_pips
	cd $(BUILD_DIR)/all_pips && $(URAY_VIVADO) -mode batch -source ${URAY_UTILS_DIR}/generate_all_pip_features.tcl


$(BUILD_DIR)/invpips.txt: ${URAY_UTILS_DIR}/generate_invpips.tcl
	mkdir -p $(BUILD_DIR)/invpips
	cd $(BUILD_DIR)/invpips && $(URAY_VIVADO) -mode batch -source ${URAY_UTILS_DIR}/generate_invpips.tcl

$(BUILD_DIR)/ccio_pins.csv: ${URAY_UTILS_DIR}/get_ccio_pins.tcl
	mkdir -p $(BUILD_DIR)/get_ccio_pins
	cd $(BUILD_DIR)/get_ccio_pins && $(URAY_VIVADO) -mode batch -source ${URAY_UTILS_DIR}/get_ccio_pins.tcl

$(BUILD_DIR)/active_bufce_row.csv: ${URAY_UTILS_DIR}/generate_active_bufce_row.tcl
	mkdir -p $(BUILD_DIR)/active_bufce_row
	cd $(BUILD_DIR)/active_bufce_row && $(URAY_VIVADO) -mode batch -source ${URAY_UTILS_DIR}/generate_active_bufce_row.tcl

$(BUILD_DIR)/bufg_outputs.csv: ${URAY_UTILS_DIR}/get_bufg_direct_outputs.tcl
	mkdir -p $(BUILD_DIR)/bufg_outputs
	cd $(BUILD_DIR)/bufg_outputs && $(URAY_VIVADO) -mode batch -source ${URAY_UTILS_DIR}/get_bufg_direct_outputs.tcl

$(BUILD_DIR)/bufce_leaf_clock_regions.csv: ${URAY_UTILS_DIR}/get_bufce_leaf_clock_regions.tcl
	mkdir -p $(BUILD_DIR)/bufce_leaf_clock_regions
	cd $(BUILD_DIR)/bufce_leaf_clock_regions && $(URAY_VIVADO) -mode batch -source ${URAY_UTILS_DIR}/get_bufce_leaf_clock_regions.tcl

define generate =
$(1)/top.v: top.sh top.py $(BUILD_DIR)/ccio_pins.csv $(BUILD_DIR)/active_bufce_row.csv $(BUILD_DIR)/bufce_leaf_clock_regions.csv $(BUILD_DIR)/bufg_outputs.csv
	bash top.sh $(1)

$(1)/design.dcp: $(1)/top.v generate.sh
	bash generate.sh $(1)

$(1)/design.features: $(1)/design.dcp $(URAY_DIR)/tools/dump_features.tcl generate_features.sh
	bash generate_features.sh $(1)

$(1)/design_bits.ok: $(1)/design.dcp
	cd $(1); ${URAY_BITREAD} -F ${URAY_ROI_FRAMES} -o design.bits -z -y design.bit
	touch $(1)/design_bits.ok

$(1)/generate.ok: $(1)/design_bits.ok $(1)/design.features ${URAY_UTILS_DIR}/create_segdata_from_features.py $(BUILD_DIR)/extent_features_with_pips.txt
	cd $(1); python3 ${URAY_UTILS_DIR}/create_segdata_from_features.py \
		--features_file design.features \
		--bits_file design.bits \
		--extent_features ../extent_features_with_pips.txt
	touch $(1)/generate.ok

$(1)/OK: $(1)/generate.ok

endef

$(foreach specimen,$(SPECIMENS),$(eval $(call generate,$(specimen))))

run:
	$(MAKE) clean
	$(MAKE) database
	$(MAKE) pushdb
	touch run.ok

clean:
	rm -rf $(BUILD_DIR) run.ok

clean_generate:
	find $(BUILD_DIR) -name "design*.features" -delete
	find $(BUILD_DIR) -name design_bits.ok -delete
	find $(BUILD_DIR) -name generate.ok -delete

check:
	cut -d ' ' -f 1 $(BUILD_DIR)/segbits_int.db | sort > $(BUILD_DIR)/int_found.txt
	cut -d ' ' -f 1 $(BUILD_DIR)/segbits_int.rdb | sort > $(BUILD_DIR)/all_int.txt

.PHONY: database pushdb run clean generate clean_generate bits features check top
