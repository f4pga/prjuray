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

# Minimal makefile for Sphinx documentation

MAKEDIR := $(dir $(lastword $(MAKEFILE_LIST)))

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SPHINXAUTOBUILD   = sphinx-autobuild
SPHINXPROJ    = ProjectX-Ray
SOURCEDIR     = .
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

livehtml:
	@$(SPHINXAUTOBUILD) -b html --ignore \*.swp --ignore \*~ $(SPHINXOPTS) "$(SOURCEDIR)" "$(BUILDDIR)/html"

.PHONY: help livehtml Makefile

# Update fuzzer / minitest markdown links.
fuzzers-links:
	@mkdir -p $(MAKEDIR)/db_dev_process/fuzzers
	@cd $(MAKEDIR)/db_dev_process/fuzzers && rm -f *.md
	@cd $(MAKEDIR)/db_dev_process/fuzzers && \
		for i in ../../../fuzzers/*; do \
			n=$$(basename $$i | sed -e's/^[0-9][0-9][0-9]-//'); \
			if [ ! -d $$i ]; then \
				continue; \
			fi; \
			if [ -e $$i/README.md ]; then \
				echo "Linking $$i/README.md"; \
				ln -s $$i/README.md $${n}.md; \
			else \
				echo "Missing $$i/README.md"; \
			fi; \
		done

minitests-links:
	@mkdir -p $(MAKEDIR)/db_dev_process/minitests
	@cd  $(MAKEDIR)/db_dev_process/minitests && rm -f *.md
	@cd  $(MAKEDIR)/db_dev_process/minitests && \
		for i in ../../../minitests/*; do \
			n=$$(basename $$i | sed -e's/^[0-9][0-9][0-9]-//'); \
			if [ ! -d $$i ]; then \
				continue; \
			fi; \
			if [ -e $$i/README.md ]; then \
				echo "Linking $$i/README.md"; \
				ln -s $$i/README.md $${n}.md; \
			else \
				echo "Missing $$i/README.md"; \
			fi; \
		done

links: fuzzers-links minitests-links
	@true

.PHONY: fuzzers-links minitests-links links

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile links
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
