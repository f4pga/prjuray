# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

SEGBITS=\
      clel_l \
      clel_r \
      clem \
      clem_r \
      int \

DB_SIMPLE=\
    $(addprefix segbits_, $(SEGBITS)) \

DB_FILES=$(sort $(addsuffix .origin_info.db,$(DB_SIMPLE)) $(addsuffix .db,$(DB_SIMPLE)))
DB_FILES_PATH=$(addprefix $(URAY_DATABASE_DIR)/$(URAY_DATABASE)/,$(DB_FILES))

check:
	@mkdir -p build
	@rm -f build/existing.txt
	@for DB_FILE in $(sort $(notdir $(wildcard $(URAY_DATABASE_DIR)/$(URAY_DATABASE)/*.db))); do \
		echo $$DB_FILE >> build/existing.txt; \
	done
	@rm -f build/tocreate.txt
	@for DB_FILE in $(sort $(DB_FILES)); do \
		echo $$DB_FILE >> build/tocreate.txt; \
	done
	diff -u build/existing.txt build/tocreate.txt

status:
	@echo $(DB_FILES_PATH)
	@for DB_FILE in $(DB_FILES_PATH); do \
		echo -n "$$(basename $$DB_FILE) "; \
		if [ -e "$$DB_FILE" ]; then \
			echo -n "Exists! - "; \
		else \
			echo -n "Missing! - "; \
		fi; \
		echo "$$DB_FILE"; \
	done

$(URAY_FAMILY_DIR)/$(URAY_PART):
	mkdir -p ${URAY_FAMILY_DIR}/${URAY_PART}

$(URAY_FAMILY_DIR)/tile_types: $(URAY_FAMILY_DIR)/$(URAY_PART)
	mkdir -p ${URAY_FAMILY_DIR}/tile_types

$(URAY_FAMILY_DIR)/site_types: $(URAY_FAMILY_DIR)/$(URAY_PART)
	mkdir -p ${URAY_FAMILY_DIR}/site_types

$(DB_FILES_PATH): ${URAY_FAMILY_DIR}/tile_types ${URAY_FAMILY_DIR}/site_types
	touch $@

pushdb: $(DB_FILES_PATH)
	@true

run:
	rm -rf $(BUILD_DIR) run.${URAY_PART}.ok
	$(MAKE) pushdb
	touch run.${URAY_PART}.ok

clean:
	rm -rf build_* run.*.ok logs

.PHONY: pushdb clean run
