# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

create_project -force -part $::env(URAY_PART) design design
set_property design_mode PinPlanning [current_fileset]
open_io_design -name io_1

proc get_ps8_pin_map {filename} {
    # Return mapping between PS8 cell pin, bel pin, site pin and node.
    set fp [open $filename w]
    puts $fp "pin,bel_pin,site_pin,node"

    set tile [get_tiles -filter "TYPE == PSS_ALTO"]
    set site [get_sites -of $tile]
    set bel [get_bels $site/PS8]

    set cell [create_cell -ref PS8 ps8_cell]
    set_property LOC $site $cell

    if { [llength $bel] != 1 } {
        error "Failed to find PS8 bel?"
    }

    foreach pin [get_pins -of $cell] {
        set bel_pin [get_bel_pins -quiet -of $pin]
        if { [llength $bel_pin] == 0 } {
            continue
        }

        set site_pin [get_site_pins -quiet -of $bel_pin]
        if { [llength $site_pin] == 0 } {
            continue
        }

        set node [get_nodes -quiet -of $site_pin]
        if { [llength $node] == 0 } {
            continue
        }

        puts $fp "$pin,$bel_pin,$site_pin,$node"
    }

    close $fp
}

get_ps8_pin_map ../ps8_pin_map.csv
