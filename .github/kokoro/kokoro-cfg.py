#!/usr/bin/env python3

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
