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


if [ -f $KOKORO_KEYSTORE_DIR/74045_foss-fpga-tools_arch-defs_ssh_private ]; then

chmod 600 $KOKORO_KEYSTORE_DIR/74045_foss-fpga-tools_arch-defs_ssh_private
cat <<EOF > ssh_config
Host github.com
  IdentityFile $KOKORO_KEYSTORE_DIR/74045_foss-fpga-tools_arch-defs_ssh_private
  StrictHostKeyChecking no
EOF

export GIT_SSH_COMMAND="ssh -F $(pwd)/ssh_config"
${GIT_SSH_COMMAND} git@github.com || true

fi


echo
echo "========================================"
echo "Git log"
echo "----------------------------------------"
echo "----------------------------------------"

echo
echo "========================================"
echo "Git fetching tags"
echo "----------------------------------------"
git fetch --tags || true
echo "----------------------------------------"

echo
echo "========================================"
echo "Git version info"
echo "----------------------------------------"
git log -n1
echo "----------------------------------------"
git describe --tags || true
echo "----------------------------------------"
git describe --tags --always || true
echo "----------------------------------------"
