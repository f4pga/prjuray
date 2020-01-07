# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

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
