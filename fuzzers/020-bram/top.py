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
from utils.spec import bram18
from utils.spec import bram36
import random
from utils import spec_top


def spec_num():
    return int(os.getenv('SPECDIR').split('_')[1])


SPECS = (
    (bram18, 10),
    (bram36, 10),
)


def main():
    spec_top.spec_top(SPECS)


if __name__ == "__main__":
    main()
