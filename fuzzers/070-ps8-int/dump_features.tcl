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
    set filter_int 1
    set sitefeatures_by_tile [dict create]
    set pips_by_tile [dump_pips $filter_bram $filter_int]

    set outputs_used_in_tile [dict create]

    foreach tile [dict keys $pips_by_tile] {
        foreach feature [dict get $pips_by_tile $tile] {
            if { [string_contains $feature "LOGIC_OUTS"] } {
                dict set outputs_used_in_tile $tile 1
            }
        }
    }

    foreach tile [dict keys $pips_by_tile] {
        if { [dict exists $outputs_used_in_tile $tile] } {
            dict lappend sitefeatures_by_tile $tile "OUTPUTS_ENABLED.1"
        } else {
            dict lappend sitefeatures_by_tile $tile "OUTPUTS_ENABLED.0"
        }
    }

    lappend tiles [get_tiles -quiet -filter {TYPE == INT_INTF_LEFT_TERM_PSS}]

    output_features_to_file $output_file $tiles $pips_by_tile $sitefeatures_by_tile

    set end_time [clock seconds]
    puts "[now] Done, took [expr $end_time - $start_time] seconds!"
}

dump_features_to_file design.features
