#!/bin/bash
#
# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
# FIXME: fasm should be installed into the running Python environment.
export PYTHONPATH="${URAY_DIR}:${URAY_DIR}/third_party/fasm:${URAY_DIR}/third_party/prjuray-tools:$PYTHONPATH"

# Suppress the following warnings;
# - env/lib/python3.7/distutils/__init__.py:4: DeprecationWarning: the imp module is deprecated in favour of importlib; see the module's documentation for alternative uses
export PYTHONWARNINGS=ignore::DeprecationWarning:distutils
