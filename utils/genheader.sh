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

# header for fuzzer generate.sh scripts
if [ -z "$URAY_DATABASE" ]; then
	echo "No URAY environment found. Make sure to source the settings file first!"
	exit 1
fi

set -ex

export FUZDIR=$PWD

# for some reason on sourced script set -e doesn't work
# Scripts may have additional arguments, but first is reserved for build directory
test $# -ge 1 || exit 1
test ! -e "$SPECDIR"
export SPECDIR=$1

mkdir -p "$SPECDIR"
cd "$SPECDIR"

export SEED="$(echo $SPECDIR | md5sum | cut -c1-8)"
export SEEDN="$(basename $(pwd) |sed s/specimen_0*//)"

function seed_vh () {
    echo '`define SEED 32'"'h${SEED}" > setseed.vh
}

