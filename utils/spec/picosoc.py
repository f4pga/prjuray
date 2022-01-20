#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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

import os


def print_top(seed):
    with open(os.path.join(os.environ['URAY_DIR'], 'spec',
                           'picosoc_top.v')) as f:
        print(f.read())

    with open(
            os.path.join(os.environ['URAY_DIR'], 'third_party', 'picosoc',
                         'picorv32.v')) as f:
        print(f.read())
