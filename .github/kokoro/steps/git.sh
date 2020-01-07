#!/bin/bash
#
# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

set -e


chmod 600 $KOKORO_KEYSTORE_DIR/74045_foss-fpga-tools_arch-defs_ssh_private
cat <<EOF > ssh_config
Host github.com
  IdentityFile $KOKORO_KEYSTORE_DIR/74045_foss-fpga-tools_arch-defs_ssh_private
  StrictHostKeyChecking no
EOF

export GIT_SSH_COMMAND="ssh -F $(pwd)/ssh_config"
${GIT_SSH_COMMAND} git@github.com || true

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
