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
