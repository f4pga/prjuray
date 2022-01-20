#!/usr/bin/env python3
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

# Header
contrib = ["""\
# Contributing to Project U-Ray
"""]

# Extract the "Contributing" section from README.md
found = False
for line in open('README.md'):
    if found:
        if line.startswith('# '):
            # Found the next top level header
            break
        contrib.append(line)
    else:
        if line.startswith('# Contributing'):
            found = True

# Footer
contrib.append("""\






----

This file is generated from [README.md](README.md), please edit that file then
run the `./.github/update-contributing.py`.

""")

open("CONTRIBUTING.md", "w").write("".join(contrib))
