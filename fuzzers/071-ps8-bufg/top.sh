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

source $URAY_GENHEADER
echo '`define SEED 32'"'h$(echo $1 | md5sum | cut -c1-8)" > setseed.vh

# Some projects have hard coded top.v, others are generated
if [ -f $FUZDIR/top.py ] ; then
    set +e
    python3 $FUZDIR/top.py >top.v
    RET=$?
    set -e
    if [ $RET -ne 0 ]; then
        rm top.v
    fi
    exit $RET
fi

