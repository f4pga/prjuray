# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

N := 1
BUILD_DIR = build_${URAY_PART}
SPECIMENS := $(addprefix $(BUILD_DIR)/specimen_,$(shell seq -f '%03.0f' $(N)))

database: $(SPECIMENS)
	mkdir -p $(BUILD_DIR)
	cp $(BUILD_DIR)/specimen_001/part.yaml $(BUILD_DIR)/part.yaml
	python3 -m utils.xyaml $(BUILD_DIR)/part.yaml > $(BUILD_DIR)/part_no_iobanks.json
	python3 add_iobanks.py --part_json $(BUILD_DIR)/part_no_iobanks.json --iobanks_info $(BUILD_DIR)/specimen_001/iobanks.txt > $(BUILD_DIR)/part.json
	cp ${URAY_PART}_required_features.fasm $(BUILD_DIR)/ 2>/dev/null || true

$(SPECIMENS): Makefile.specimen
	mkdir -p $@
	$(MAKE) -C $@ -f ../../Makefile.specimen

pushdb:
	mkdir -p ${URAY_FAMILY_DIR}/${URAY_PART}
	cp $(BUILD_DIR)/part.json $(URAY_FAMILY_DIR)/${URAY_PART}/part.json
	cp $(BUILD_DIR)/part.yaml $(URAY_FAMILY_DIR)/${URAY_PART}/part.yaml
	cp $(BUILD_DIR)/${URAY_PART}_required_features.fasm ${URAY_FAMILY_DIR}/${URAY_PART}/required_features.fasm 2>/dev/null || true

run:
	rm -rf $(BUILD_DIR) run.${URAY_PART}.ok
	$(MAKE) database
	$(MAKE) pushdb
	touch run.${URAY_PART}.ok

clean:
	rm -rf build_* run.*.ok

.PHONY: database pushdb clean run $(SPECIMENS)
