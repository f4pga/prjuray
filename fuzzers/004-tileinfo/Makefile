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

N := 1
BUILD_DIR = build_${URAY_PART}
SPECIMENS := $(addprefix $(BUILD_DIR)/specimen_,$(shell seq -f '%03.0f' $(N)))
SPECIMENS_OK := $(addsuffix /OK,$(SPECIMENS))
MAX_VIVADO_PROCESS ?= 4
MAX_TILES_INSTANCE ?= 1000
MAX_NODES_INSTANCE ?= 100000

database: $(SPECIMENS_OK)
	true

pushdb:
	# Copy tile types
	mkdir -p ${URAY_FAMILY_DIR}/tile_types
	cp $(BUILD_DIR)/output/tile_types/* ${URAY_FAMILY_DIR}/tile_types
	# Copy site types
	mkdir -p ${URAY_FAMILY_DIR}/site_types
	cp $(BUILD_DIR)/output/site_types/* ${URAY_FAMILY_DIR}/site_types
	# Copy tileconn
	cp $(BUILD_DIR)/output/tileconn.json ${URAY_FAMILY_DIR}/$(URAY_PART)/

$(SPECIMENS_OK):
	bash generate.sh $(subst /OK,,$@) -p=$(MAX_VIVADO_PROCESS) -t=$(MAX_TILES_INSTANCE) -n=$(MAX_NODES_INSTANCE)
	touch $@

run:
	rm -rf $(BUILD_DIR) run.${URAY_PART}.ok
	$(MAKE) database
	$(MAKE) pushdb
	# Clean up intermediate files after successful pushdb.
	find $(BUILD_DIR) -name "*.tmp.json" -delete
	touch run.${URAY_PART}.ok

clean:
	rm -rf build_* run.*.ok

update_ignored_wires:
	mkdir -p ignored_wires/${URAY_DATABASE}
	python3 analyze_errors.py \
		--error_nodes ${BUILD_DIR}/output/error_nodes.json \
		--output_ignore_list | sort \
		> ignored_wires/${URAY_DATABASE}/${URAY_PART}_ignored_wires.txt

.PHONY: database pushdb run clean

