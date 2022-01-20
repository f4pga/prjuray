#!/bin/bash
#
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

set -e

cd github/$KOKORO_DIR/

source ./.github/kokoro/steps/hostsetup.sh
source ./.github/kokoro/steps/hostinfo.sh
source ./.github/kokoro/steps/git.sh

source ./.github/kokoro/steps/prjuray-env.sh

echo
echo "========================================"
echo "Running tests"
echo "----------------------------------------"
(
	make test --output-sync=target --warn-undefined-variables
)
echo "----------------------------------------"

echo
echo "========================================"
echo "Copying tests logs"
echo "----------------------------------------"
(
	cat build/*test_results.xml
	mkdir build/py
	cp build/py_test_results.xml build/py/sponge_log.xml
	mkdir build/cpp
	cp build/cpp_test_results.xml build/cpp/sponge_log.xml
)
echo "----------------------------------------"
