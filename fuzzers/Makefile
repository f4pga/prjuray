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

SELF_DIR := $(dir $(lastword $(MAKEFILE_LIST)))

# Developer options for quicker runs
# Run algorithm, but only a small number of iterations
QUICK=N
# Skip metadata steps like tile and part generation
# Ex: FUZZONLY=N: 30 min, FUZZONLY=Y: 6 min
FUZZONLY=N
# 074 fuzzer isn't changed often and is slow
# Allow building without it
BITONLY=N

all:
clean: clean_fuzzers clean_fuzzers clean_logs clean_locks

clean_locks:
	rm -rf /tmp/segbits_*.db.lock

fuzzer_ok:
	mkdir -p fuzzer_ok

clean_fuzzers::
	rm -rf fuzzer_ok

clean_piplists:
	@true

define fuzzer

# $(1) - Fuzzer name/directory
# $(2) - Space seperated list of dependencies for the fuzzer.
# $(3) - Is this fuzzer setting specific? Should be either "part" or "all"

# Make the all target depend on the run.ok file for the fuzzer.
ifeq ($(3),part)
all: $(1)/run.$(URAY_PART).ok
part_only: $(1)/run.$(URAY_PART).ok
else
all: $(1)/run.ok
endif

# Make the clean target run `make clean` in the fuzzer's directory.
clean_fuzzers::
	$$(MAKE) -C $(1) clean

clean_logs::
	rm -rf $(1)/logs_*

# Describe how to create the fuzzer's run.ok file.
# This command must start with a + to tell make to pass the jobserver
# parameters downwards.

ifeq ($(3),part)
$(1)/run.$(URAY_PART).ok: $(addsuffix _$(URAY_PART).ok,$(addprefix fuzzer_ok/fuzzer_, $(2)))
else
$(1)/run.ok: $(addsuffix _$(URAY_PART).ok,$(addprefix fuzzer_ok/fuzzer_, $(2)))
endif
ifeq ($(VERBOSE),Y)
# When verbose we just call make directory
	$$(MAKE) -C $(1) run
else
# When not verbose, we use the run_fuzzer wrapper which will save the results
# to log files.
	+@$(SELF_DIR)/run_fuzzer.py $(1)
endif

ifeq ($(3),part)
fuzzer_ok/fuzzer_$(1)_$(URAY_PART).ok: $(1)/run.$(URAY_PART).ok | fuzzer_ok
else
fuzzer_ok/fuzzer_$(1)_$(URAY_PART).ok: $(1)/run.ok | fuzzer_ok
endif
	touch fuzzer_ok/fuzzer_$(1)_$(URAY_PART).ok

.PHONY: fuzzer_$(1)

fuzzer_$(1): fuzzer_ok/fuzzer_$(1)_$(URAY_PART).ok

endef

$(eval $(call fuzzer,000-init-db,,part))

ifneq ($(FUZZONLY),Y)
$(eval $(call fuzzer,001-part-yaml,000-init-db,part))
$(eval $(call fuzzer,002-tilegrid,001-part-yaml,part))
$(eval $(call fuzzer,004-tileinfo,002-tilegrid,part))
$(eval $(call fuzzer,005-pins,001-part-yaml,part))
$(eval $(call fuzzer,007-timing,001-part-yaml,all))
$(eval $(call fuzzer,014-cle-spec,002-tilegrid,all))
$(eval $(call fuzzer,020-bram,002-tilegrid,all))
$(eval $(call fuzzer,021-bram-data,002-tilegrid,all))
$(eval $(call fuzzer,031-iob-spec,002-tilegrid,all))
$(eval $(call fuzzer,050-int-seed,002-tilegrid,all))
$(eval $(call fuzzer,060-rclk-seed,002-tilegrid,all))
$(eval $(call fuzzer,070-ps8-int,002-tilegrid,all))
$(eval $(call fuzzer,071-ps8-bufg,002-tilegrid,all))
else
all:: 002-tilegrid/run.ok
	touch 002-tilegrid/run.ok
endif

quick:
	$(MAKE) QUICK=Y

# Part only targets
# -----------------

# roi_only runs the fuzzers required for supporting additional parts when building
# a roi harness.
roi_only: 000-init-db/run.${URAY_PART}.ok 001-part-yaml/run.${URAY_PART}.ok 005-pins/run.${URAY_PART}.ok
	# Copy tilegrid and tileconn
	cp ${URAY_FAMILY_DIR}/${URAY_EQUIV_PART}/tilegrid.json ${URAY_FAMILY_DIR}/${URAY_PART}/tilegrid.json
	cp ${URAY_FAMILY_DIR}/${URAY_EQUIV_PART}/tileconn.json ${URAY_FAMILY_DIR}/${URAY_PART}/tileconn.json

.PHONY: all clean clean_fuzzers clean_logs quick part_only roi_only clean_piplists
