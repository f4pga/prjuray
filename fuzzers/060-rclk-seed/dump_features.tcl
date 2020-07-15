# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

open_checkpoint design.dcp

source $::env(URAY_DIR)/tools/dump_features.tcl

dump_clock_features_to_file design.features
