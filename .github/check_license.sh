#!/usr/bin/env bash
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

echo
echo "==========================="
echo "Check SPDX identifier"
echo "==========================="
echo

ERROR_FILES=""
FILES_TO_CHECK=`find . \
    -size +0 -type f \( -name '*.sh' -o -name '*.py' -o -name 'Makefile' -o -name '*.tcl' \) \
    \( -not -path "*/.*/*" -not -path "*/third_party/*" -not -path "*/database/*" -not -path "*/env/*" -not -path "*/build/*" \)`

for file in $FILES_TO_CHECK; do
    echo "Checking $file"
    grep -q "SPDX-License-Identifier" $file || ERROR_FILES="$ERROR_FILES $file"
done

if [ ! -z "$ERROR_FILES" ]; then
    for file in $ERROR_FILES; do
        echo "ERROR: $file does not have license information."
    done
    exit 1
fi

echo
echo "==========================="
echo "Check third party LICENSE"
echo "==========================="
echo

function check_if_submodule {
    for submodule in `git submodule --quiet foreach 'echo $sm_path'`; do
        if [ "$1" == "$submodule" ]; then
            return 1
        fi
    done
}

THIRD_PARTY_DIRS=""
if [[ -e third_party ]]; then
    #FIXME Don't ignore fasm, prjuray-tools and python-sdf-timing once ready
    THIRD_PARTY_DIRS=`ls third_party --ignore=reformat.tcl --ignore cctz --ignore gflags --ignore yosys --ignore picosoc --ignore embeddedsw --ignore prjuray-tools --ignore fasm --ignore python-sdf-timing`
fi
ERROR_NO_LICENSE=""

for dir in $THIRD_PARTY_DIRS; do
    # Checks if we are not in a submodule
    if check_if_submodule $dir; then
        echo "Checking third_party/$dir"
        [ -f third_party/$dir/LICENSE ] || ERROR_NO_LICENSE="$ERROR_NO_LICENSE $dir"
    fi
done

if [ ! -z "$ERROR_NO_LICENSE" ]; then
    for dir in $ERROR_NO_LICENSE; do
        echo "ERROR: $dir does not have the LICENSE file."
    done
    exit 1
fi
