# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

BUILD_DIR = build
N := 72

SPECIMENS := $(addprefix $(BUILD_DIR)/specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))
SPECIMENS_bits := $(addsuffix /design_bits.ok,$(SPECIMENS))
SPECIMENS_features := $(addsuffix /design.features,$(SPECIMENS))

database: $(BUILD_DIR)/invpips.txt ${URAY_UTILS_DIR}/segmatch_all_types.py $(SPECIMENS_OK) solution_width.txt
	cd $(BUILD_DIR) && python3 ${URAY_UTILS_DIR}/segmatch_all_types.py \
		--filter_solution_width ../solution_width.txt

bits: $(SPECIMENS_bits)
	true

features: $(SPECIMENS_features)
	true

generate: $(BUILD_DIR)/invpips.txt $(SPECIMENS_OK)
	true

$(BUILD_DIR)/ps8_pin_map.csv: ${URAY_UTILS_DIR}/get_ps8_pin_map.tcl
	mkdir -p $(BUILD_DIR)/ps8_pin_map
	cd $(BUILD_DIR)/ps8_pin_map && $(URAY_VIVADO) -mode batch -source ${URAY_UTILS_DIR}/get_ps8_pin_map.tcl

$(BUILD_DIR)/permutations.csv: generate_permutations.py $(BUILD_DIR)/ps8_bufg_pin_map.csv
	cd $(BUILD_DIR) && python3 ../generate_permutations.py > permutations.csv

$(BUILD_DIR)/ps8_bufg_pin_map.csv: ${URAY_UTILS_DIR}/get_ps8_bufg_pin_map.tcl
	mkdir -p $(BUILD_DIR)/ps8_bufg_pin_map
	cd $(BUILD_DIR)/ps8_bufg_pin_map && $(URAY_VIVADO) -mode batch -source ${URAY_UTILS_DIR}/get_ps8_bufg_pin_map.tcl

$(BUILD_DIR)/extent_features_with_pips.txt: ${URAY_UTILS_DIR}/create_feature_extents.py $(BUILD_DIR)/all_pips/design.features $(SPECIMENS_features)
	python3 ${URAY_UTILS_DIR}/create_feature_extents.py \
		--root_dir $(BUILD_DIR) \
		--extent_features $(BUILD_DIR)/extent_features_with_pips.txt

$(BUILD_DIR)/all_pips/design.features: ${URAY_UTILS_DIR}/generate_all_pip_features.tcl
	mkdir -p $(BUILD_DIR)/all_pips
	cd $(BUILD_DIR)/all_pips && $(URAY_VIVADO) -mode batch -source ${URAY_UTILS_DIR}/generate_all_pip_features.tcl

$(BUILD_DIR)/invpips.txt: ${URAY_UTILS_DIR}/generate_invpips.tcl
	mkdir -p $(BUILD_DIR)/invpips
	cd $(BUILD_DIR)/invpips && $(URAY_VIVADO) -mode batch -source ${URAY_UTILS_DIR}/generate_invpips.tcl

pushdb:
	$(URAY_MERGEDB) rclk_intf_left_term_alto $(BUILD_DIR)/segbits_rclk_intf_left_term_alto.db

define generate =
$(1)/top.v: top.sh top.py ${URAY_UTILS_DIR}/spec_top.py ${URAY_UTILS_DIR}/spec/ps8_bufg.py $(BUILD_DIR)/ps8_pin_map.csv $(BUILD_DIR)/ps8_bufg_pin_map.csv $(BUILD_DIR)/permutations.csv
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

.PHONY: database pushdb run clean generate clean_generate bits features
