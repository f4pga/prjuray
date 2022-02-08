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

import io
import re
import yaml
import json
import unittest

from utils import xjson


def load(f):
    data = f.read()
    if isinstance(data, bytes):
        data = data.decode('utf-8')
    # Strip out of !<tags>
    data = re.sub("!<[^>]*>", "", data)
    return yaml.load(io.StringIO(data))


def tojson(f):
    d = load(f)
    o = io.StringIO()
    xjson.pprint(o, d)
    return o.getvalue()


class XYamlTest(unittest.TestCase):
    def test(self):
        s = io.StringIO("""\
!<xilinx/xc7series/part>
idcode: 0x362d093
global_clock_regions:
  top: !<xilinx/xc7series/global_clock_region>
    rows:
      0: !<xilinx/xc7series/row>
        configuration_buses:
          CLB_IO_CLK: !<xilinx/xc7series/configuration_bus>
            configuration_columns:
              0: !<xilinx/xc7series/configuration_column>
                frame_count: 42
""")
        djson = tojson(s)
        self.assertMultiLineEqual(
            djson, """\
{
    "global_clock_regions": {
        "top": {
            "rows": {
                "0": {
                    "configuration_buses": {
                        "CLB_IO_CLK": {
                            "configuration_columns": {
                                "0": {
                                    "frame_count": 42
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    "idcode": 56807571
}""")


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        unittest.main()
    else:
        assert len(sys.argv) == 2
        print(tojson(open(sys.argv[1])))
