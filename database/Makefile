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

DATABASE_FILES = *.csv *.db *.json *.yaml
TIMINGS_FILES = *.sdf
PART_DIRECTORIES = xczu*/

clean-zynqusp-db:
	rm -f $(addprefix zynqusp/,$(DATABASE_FILES))
	rm -f $(addprefix zynqusp/timings/,$(TIMINGS_FILES))
	rm -rf $(addprefix zynqusp/,$(PART_DIRECTORIES))

clean-db: clean-zynqusp-db
	@true

clean: clean-db
	@true

.PHONY: clean-zynqusp-db clean-db clean

reset:
	git reset --hard

.PHONY: reset

update:
	git stash
	git fetch origin
	git merge origin/master
	git stash pop

.PHONY: update
