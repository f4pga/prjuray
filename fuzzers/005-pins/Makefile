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
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))

database: $(SPECIMENS_OK)

pushdb:
	mkdir -p ${URAY_FAMILY_DIR}/${URAY_PART}/
	cp $(BUILD_DIR)/specimen_001/*_package_pins.csv ${URAY_FAMILY_DIR}/${URAY_PART}/package_pins.csv

$(SPECIMENS_OK):
	bash generate.sh $(subst /OK,,$@)
	touch $@

run:
	rm -rf $(BUILD_DIR) run.${URAY_PART}.ok
	$(MAKE) database
	$(MAKE) pushdb
	touch run.$(URAY_PART).ok

clean:
	rm -rf build_* run.*.ok

.PHONY: database pushdb run clean
