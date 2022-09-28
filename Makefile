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

SHELL = bash
ALL_EXCLUDE = third_party .git env build docs/env

ifneq ($(CI_RUN),1)
# Check if root
ifeq ($(shell id -u),0)
        $(error ERROR: Running as ID 0)
endif
endif

# Tools + Environment
IN_ENV = if [ -e env/bin/activate ]; then . env/bin/activate; fi; source utils/environment.python.sh;
env:
	git submodule update --init --recursive
	virtualenv --python=python3 env
	# Install utils
	ln -sf $(PWD)/utils env/lib/python3.*/site-packages/
	# Install project dependencies
	$(IN_ENV) pip install -r requirements.txt
	# Install project's documentation dependencies
	$(IN_ENV) pip install -r docs/requirements.txt
	# Check prjuray-tools installation
	$(IN_ENV) python -c "import prjuray"
	$(IN_ENV) python -c "import prjuray.db"
	# Check fasm library was installed
	$(IN_ENV) python -c "import fasm"
	$(IN_ENV) python -c "import fasm.output"
	# Check sdfparse lib was installed
	$(IN_ENV) python -c "import sdf_timing"
	$(IN_ENV) python -c "import sdf_timing.sdfparse"
	# Check edalize lib was installed
	$(IN_ENV) python -c "import edalize"
	# Check YAML is installed
	$(IN_ENV) python -c "import yaml" || (echo "Unable to find python-yaml" && exit 1)

.PHONY: env tools

tools:
	git submodule update --init --recursive
	mkdir -p third_party/prjuray-tools/build
	cd third_party/prjuray-tools/build; cmake ..; $(MAKE)

# Run tests of code.
# ------------------------
TEST_EXCLUDE = $(foreach x,$(ALL_EXCLUDE) docs fuzzers minitests experiments,--ignore $(x))

test: test-py test-cpp
	@true

test-py:
	$(IN_ENV) which py.test; py.test $(TEST_EXCLUDE) --doctest-modules --junitxml=build/py_test_results.xml

test-cpp:
	mkdir -p build
	mkdir -p third_party/prjuray-tools/build
	cd third_party/prjuray-tools/build && cmake -DPRJURAY_BUILD_TESTING=ON ..
	cd third_party/prjuray-tools/build && $(MAKE) -s
	cd third_party/prjuray-tools/build && ctest --no-compress-output -T Test -C RelWithDebInfo --output-on-failure
	xsltproc .github/kokoro/ctest2junit.xsl third_party/prjuray-tools/build/Testing/*/Test.xml > build/cpp_test_results.xml

.PHONY: test test-py test-cpp

# Auto formatting of code.
# ------------------------
FORMAT_EXCLUDE = $(foreach x,$(ALL_EXCLUDE),-and -not -path './$(x)/*') -and -not -name *.bit

CLANG_FORMAT ?= clang-format-5.0
format-cpp:
	find . -name \*.cc $(FORMAT_EXCLUDE) -print0 | xargs -0 -P $$(nproc) ${CLANG_FORMAT} -style=file -i
	find . -name \*.h $(FORMAT_EXCLUDE) -print0 | xargs -0 -P $$(nproc) ${CLANG_FORMAT} -style=file -i

format-docs:
	./.github/update-contributing.py

PYTHON_FORMAT ?= yapf
format-py:
	$(IN_ENV) find . -name \*.py $(FORMAT_EXCLUDE) -print0 | xargs -0 -P $$(nproc) yapf -p -i

TCL_FORMAT ?= utils//tcl-reformat.sh
format-tcl:
	find . -name \*.tcl $(FORMAT_EXCLUDE) -print0 | xargs -0 -P $$(nproc) -n 1 $(TCL_FORMAT)

# Command to find and replace trailing whitespace in-place using `sed` (This is
# placed inside quotes later so need to escape the "'")
WS_CMD = sed -i '\''s@\s\+$$@@g'\''

# File filter for files to fix trailing whitespace in, this is just a couple of
# chained bash conditionals ensuring that the file (indicated by {}, provided by
# xargs later) is a file, and not a directory or link.  Also filters out .bit
# files as these are the only binary files currently tracked by Git and we don't
# want to inadvertently change these at all.
WS_FILTER = [ -f {} -a ! -L {} ] && [[ {} != *.bit ]] && [[ {} != *.patch ]]

# For every file piped to $(WS_FORMAT) apply the filter and perform the command,
# if a file does not match the filter, just returns true.
WS_FORMAT = xargs -P $$(nproc) -n 1 -I{} bash -c '$(WS_FILTER) && $(WS_CMD) {} || true'

format-trailing-ws:
	# Use `git ls-files` to give us a complete list of tracked files to fix
	# whitespace in; there is no point spending time processing anything that is
	# not known to Git.
	git ls-files | $(WS_FORMAT)

format: format-cpp format-docs format-py format-tcl format-trailing-ws
	@true

.PHONY: format format-cpp format-py format-tcl format-trailing-ws

check-license:
	@./.github/check_license.sh
	@./.github/check_python_scripts.sh

.PHONY: check-license

# Targets related to Project X-Ray databases
# ------------------------

DATABASES=zynqusp kintexus

define database

# $(1) - Database name

db-$(1):
	+source settings/$(1).sh && $$(MAKE) -C fuzzers

db-check-$(1):
	@echo
	@echo "Checking $(1) database"
	@echo "============================"
	@$(IN_ENV) python3 utils/checkdb.py

db-format-$(1):
	@echo
	@echo "Formatting $(1) database"
	@echo "============================"
	@$(IN_ENV) cd database/$(1); python3 ../../utils/sort_db.py
	@if [ -e database/Info.md ]; then $(IN_ENV) ./utils/info_md.py --keep; fi

.PHONY: db-$(1) db-check-$(1) db-format-$(1) db-extras-$(1) db-extras-$(1)-parts db-extras-$(1)-harness

db-extras-$(1): db-extras-$(1)-parts db-extras-$(1)-harness

db-$(1)-all: db-$(1) db-extras-$(1)-parts
	# Build harnesses after database is complete
	$$(MAKE) db-extras-$(1)-harness

db-check: db-check-$(1)
db-format: db-format-$(1)

endef

$(foreach DB,$(DATABASES),$(eval $(call database,$(DB))))

# Targets related to Project X-Ray parts
# --------------------------------------

ZYNQ_PARTS=zynq_usp_7ev

URAY_PARTS=${ZYNQ_PARTS}

define multiple-parts

# $(1): PART to be used

db-part-only-$(1):
	+source settings/$(1).sh && $$(MAKE) -C fuzzers part_only

endef

$(foreach PART,$(URAY_PARTS),$(eval $(call multiple-parts,$(PART))))

db-extras-zynqusp-parts: $(addprefix db-part-only-,$(ZYNQ_PARTS))

db-extras-zynqusp-harness:
	+URAY_PIN_00=E8 URAY_PIN_01=B6 URAY_PIN_02=A9 URAY_PIN_03=B9 \
		URAY_PART=xczu3eg-sbva484-1-e URAY_EQUIV_PART=xczu3eg-sfvc784-1-e $(MAKE) -C fuzzers roi_only

db-check:
	@true

db-format:
	@true

db-info:
	$(IN_ENV) ./utils/info_md.py

.PHONY: db-check db-format

clean:
	$(MAKE) -C database clean
	$(MAKE) -C fuzzers clean
	rm -rf build

.PHONY: clean
