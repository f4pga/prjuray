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
