# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

source "$::env(FUZDIR)/util.tcl"

proc write_tiles_txt {} {
    # Get all tiles, ie not just the selected LUTs
    set tiles [get_tiles]
    set skip_tile 0

    # Write tiles.txt with site metadata
    set fp [open "tiles.txt" w]
    set fp_pin [open "pin_func.txt" w]
    foreach tile $tiles {
        set sites [get_sites -quiet -of_objects $tile]

        set type [get_property TYPE $tile]
        set grid_x [get_property GRID_POINT_X $tile]
        set grid_y [get_property GRID_POINT_Y $tile]
        set typed_sites {}

        set clock_region "NA"

        if { [llength $sites] != 0 && $skip_tile == 0 } {
            set site_types [get_property SITE_TYPE $sites]
            foreach t $site_types s $sites {
                lappend typed_sites $t $s

                set package_pin [get_package_pins -of $s -quiet]
                foreach pin $package_pin {
                    puts $fp_pin "$s $pin [get_property PIN_FUNC $pin]"
                }
                set clock_region [get_property CLOCK_REGION $s]
            }
        }
        if {[llength $clock_region] == 0} {
            set clock_region "NA"
        }


        puts $fp "$type $tile $grid_x $grid_y $skip_tile $clock_region $typed_sites"
    }
    close $fp_pin
    close $fp
}

proc run {} {
    # Generate grid of entire part
    create_project -force -part $::env(URAY_PART) design design
    set_property design_mode PinPlanning [current_fileset]
    open_io_design -name io_1
    set_param messaging.disableStorage 1

    write_tiles_txt
}

run
