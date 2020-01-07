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

proc get_ps8_intf {filename} {
    # Return mapping between PS8 output interface wires and PS8 site pins.
    set fp [open $filename w]
    puts $fp "ps8_intf_tile,ps8_intf_wire,ps8_site_pin"

    foreach ps8_intf_tile [get_tiles -filter "TYPE == INT_INTF_LEFT_TERM_PSS"] {
        foreach wire [get_wires -of $ps8_intf_tile -filter "NAME =~ $ps8_intf_tile/LOGIC_OUTS_L*"] {
            set node [get_nodes -quiet -of $wire]
            if { [llength $node] == 0} {
                continue
            }

            set ps8_site_pin [get_site_pins -quiet -of $node]
            if { [llength $ps8_site_pin] == 0} {
                continue
            }

            puts $fp "$ps8_intf_tile,$wire,$ps8_site_pin"
        }
    }
    close $fp
}

get_ps8_intf ../ps8_intf.csv
