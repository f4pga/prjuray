#!/bin/bash
#
# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

# dirs
URAY_ENV_PATH="${BASH_SOURCE[0]}"
while [ -h "$URAY_ENV_PATH" ]; do # resolve $URAY_ENV_PATH until the file is no longer a symlink
  URAY_UTILS_DIR="$( cd -P "$( dirname "$URAY_ENV_PATH" )" && pwd )"
  URAY_ENV_PATH="$(readlink "$URAY_ENV_PATH")"
  [[ $URAY_ENV_PATH != /* ]] && URAY_ENV_PATH="$URAY_UTILS_DIR/$URAY_ENV_PATH" # if $URAY_ENV_PATH was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
export URAY_UTILS_DIR="$( cd -P "$( dirname "$URAY_ENV_PATH" )" && pwd )"
export URAY_DIR="$( dirname "$URAY_UTILS_DIR" )"
export URAY_DATABASE_DIR="${URAY_DIR}/database"
export URAY_TOOLS_DIR="${URAY_DIR}/third_party/prjuray-tools/build/tools"
export URAY_FUZZERS_DIR="${URAY_DIR}/fuzzers"
export URAY_FAMILY_DIR="${URAY_DATABASE_DIR}/${URAY_DATABASE}"

if [ -e "${URAY_DIR}/env/bin/activate" ]; then
  source "${URAY_DIR}/env/bin/activate"
fi

# misc
export URAY_PART_YAML="${URAY_DATABASE_DIR}/${URAY_DATABASE}/${URAY_PART}/part.yaml"
export PYTHONPATH="${URAY_DIR}:${URAY_DIR}/third_party/fasm:${URAY_DIR}/third_party/prjuray-tools:$PYTHONPATH"

# tools
export URAY_GENHEADER="${URAY_UTILS_DIR}/genheader.sh"
export URAY_BITREAD="${URAY_TOOLS_DIR}/bitread -E --part_file ${URAY_PART_YAML} --architecture ${URAY_ARCH}"
export URAY_MERGEDB="bash ${URAY_UTILS_DIR}/mergedb.sh"
export URAY_DBFIXUP="python3 ${URAY_UTILS_DIR}/dbfixup.py"
export URAY_MASKMERGE="bash ${URAY_UTILS_DIR}/maskmerge.sh"
export URAY_SEGMATCH="${URAY_TOOLS_DIR}/segmatch"
export URAY_SEGPRINT="python3 ${URAY_UTILS_DIR}/segprint.py"
export URAY_BIT2FASM="python3 ${URAY_UTILS_DIR}/bit2fasm.py"
export URAY_FASM2FRAMES="python3 ${URAY_UTILS_DIR}/fasm2frames.py"
export URAY_FASM2BIT="python3 ${URAY_UTILS_DIR}/fasm2bit.py"
export URAY_BITTOOL="${URAY_TOOLS_DIR}/bittool"
export URAY_BLOCKWIDTH="python3 ${URAY_UTILS_DIR}/blockwidth.py"
export URAY_PARSEDB="python3 ${URAY_UTILS_DIR}/parsedb.py"
export URAY_TCL_REFORMAT="${URAY_UTILS_DIR}/tcl-reformat.sh"
export URAY_VIVADO="${URAY_UTILS_DIR}/vivado.sh"
export URAY_CORRELATE="${URAY_TOOLS_DIR}/correlate_segdata"

# Verify an approved version is in use
export URAY_VIVADO_SETTINGS="${URAY_VIVADO_SETTINGS:-/opt/Xilinx/Vivado/2019.2/settings64.sh}"
# Vivado v2019.2 (64-bit)
if [ $(${URAY_VIVADO} -h |grep Vivado |cut -d\  -f 2) != "v2019.2" ] ; then
    echo "Requires Vivado 2019.2 to have Zynq US+ support."
    # Can't exit since sourced script
    # Trash a key environment variable to preclude use
    export URAY_DIR="/bad/vivado/version"
    return
fi
