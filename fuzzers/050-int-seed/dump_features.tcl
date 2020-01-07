# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

open_checkpoint design.dcp

source $::env(URAY_DIR)/tools/dump_features.tcl

proc dump_features_to_file {output_file} {
    set start_time [clock seconds]
    puts "[now] Gather features"
    set filter_bram 1
    set filter_int 0
    set sitefeatures_by_tile [dict create]
    set pips_by_tile [dump_pips $filter_bram $filter_int]

    lappend tiles [get_tiles -quiet -filter {TYPE == INT}]

    output_features_to_file $output_file $tiles $pips_by_tile $sitefeatures_by_tile

    set end_time [clock seconds]
    puts "[now] Done, took [expr $end_time - $start_time] seconds!"
}

dump_features_to_file design.features
