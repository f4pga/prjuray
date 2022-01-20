#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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

get_key = """\

before_action {
  fetch_keystore {
    keystore_resource {
      keystore_config_id: 74045
      keyname: "foss-fpga-tools_arch-defs_ssh_private"
    }
  }
}
"""

db_full = """\
# Format: //devtools/kokoro/config/proto/build.proto

build_file: "symbiflow-prjuray-%(kokoro_type)s-db-%(part)s/.github/kokoro/db-full.sh"

timeout_mins: 4320

action {
  define_artifacts {
    # File types
    regex: "**/diff.html"
    regex: "**/diff.json"
    regex: "**/diff.patch"
    regex: "**/*result*.xml"
    regex: "**/*sponge_log.xml"
    regex: "**/fuzzers/*.tgz"
    # Whole directories
    # regex: "**/build/**" - Currently kokoro dies on number of artifacts.
    regex: "**/build/*.log"
    regex: "**/logs/**"
    # The database
    regex: "**/database/%(part)s/**"
    strip_prefix: "github/symbiflow-prjuray-%(kokoro_type)s-db-%(part)s/"
  }
}

env_vars {
  key: "KOKORO_TYPE"
  value: "%(kokoro_type)s"
}

env_vars {
  key: "KOKORO_DIR"
  value: "symbiflow-prjuray-%(kokoro_type)s-db-%(part)s"
}

env_vars {
  key: "URAY_SETTINGS"
  value: "%(part)s"
}

env_vars {
  key: "URAY_BUILD_TYPE"
  value: "full"
}
"""

for part in ['zynqusp', 'kintexus']:
    with open("continuous-db-%s.cfg" % part, "w") as f:
        f.write(db_full % {
            'part': part,
            'kokoro_type': 'continuous',
        })
        f.write(get_key)

    with open("presubmit-db-%s.cfg" % part, "w") as f:
        f.write(db_full % {
            'part': part,
            'kokoro_type': 'presubmit',
        })
