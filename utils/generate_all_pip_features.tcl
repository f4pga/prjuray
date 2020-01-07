# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

source $::env(URAY_UTILS_DIR)/utils.tcl
create_project -force -part $::env(URAY_PART) design design
set_property design_mode PinPlanning [current_fileset]
open_io_design -name io_1

proc write_all_pip_features {filename} {
    set fp [open $filename "w"]

    set tiles [get_tiles]
    set tile_types [lsort [::struct::set union [get_property TYPE $tiles] []]]

    set tile_per_type []
    foreach type $tile_types {
        lappend tile_per_type [lindex [get_tiles -filter "TYPE == $type"] 0]
    }
    set pips [get_pips -of $tile_per_type -quiet -filter "IS_PSEUDO == 0"]
    set pips_by_tile [dict create]

    set idx 0
    foreach pip $pips {
        if { ($idx % 1000) == 0 } {
            puts "Pips ($idx / [llength $pips])"
        }
        incr idx

        set tile [get_tiles -of $pip]
        set ptt [get_property TYPE $tile]

        set key "$tile:$ptt"
        set is_directional [get_property IS_DIRECTIONAL $pip]
        set downhill_wire [get_wires -of $pip -downhill]
        set uphill_wire [get_wires -of $pip -uphill]
        set basename "PIP.[get_name $downhill_wire].[get_name $uphill_wire]"

        if { $is_directional } {
            dict lappend pips_by_tile $key $basename
        } else {
            dict lappend pips_by_tile $key "$basename.REV"
            dict lappend pips_by_tile $key "$basename.REV"
        }
    }

    foreach tile [lsort $tile_per_type] {
        set ptt [get_property TYPE $tile]
        set key "$tile:$ptt"

        if { [dict exists $pips_by_tile $key] } {
            puts $fp ".tile $key"
            foreach f [lsort [dict get $pips_by_tile $key]] {
                puts $fp $f
            }
        }
    }

    close $fp
}

write_all_pip_features design.features
