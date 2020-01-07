# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

source "$::env(URAY_DIR)/utils/utils.tcl"

proc run {} {
    create_project -force -part $::env(URAY_PART) design design
    read_verilog top.v
    synth_design -top top

    set_property BEL A6LUT [get_cells -filter "REF_NAME == LUT6"]
    set_property IS_BEL_FIXED 1 [get_cells -filter "REF_NAME == LUT6"]

    set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]
    set_property IS_ENABLED 0 [get_drc_checks {LUTLP-1}]

    place_design -directive Quick

    set fp [open "params.csv"]
    gets $fp line

    # The placer will not accept BUFCE_LEAF or BUFCE_ROW instances, so create
    # and connect those cells after placement.
    while {[gets $fp line] >= 0} {
        set result [split [string trim $line] ","]
        set left_row_driver [get_sites [lindex $result 2]]
        set right_row_driver [get_sites [lindex $result 3]]
        set left_column_driver [get_sites [lindex $result 4]]
        set right_column_driver [get_sites [lindex $result 5]]

        set isone [lindex $result 1]

        set left_row_cell [create_cell -reference BUFCE_ROW ${left_row_driver}_BUFCE_ROW]
        set_property LOC $left_row_driver $left_row_cell

        set right_row_cell [create_cell -reference BUFCE_ROW ${right_row_driver}_BUFCE_ROW]
        set_property LOC $right_row_driver $right_row_cell

        set left_column_cell [create_cell -reference BUFCE_LEAF ${left_column_driver}_BUFCE_LEAF]
        set_property LOC $left_column_driver $left_column_cell

        set right_column_cell [create_cell -reference BUFCE_LEAF ${right_column_driver}_BUFCE_LEAF]
        set_property LOC $right_column_driver $right_column_cell

        set left_net [create_net ${left_row_driver}_net]
        connect_net -net $left_net -objects [list [get_pins $left_row_cell/O] [get_pins $left_column_cell/I]]

        set right_net [create_net ${right_row_driver}_net]
        connect_net -net $right_net -objects [get_pins $right_row_cell/O]

        # When isone = 1, connect the left BUFCE_ROW driver from the clock
        # region left of the current RCLK_DSP_INTF tile to the clock region
        # right of the current RCLK_DSP_INTF tile.
        if { $isone } {
            connect_net -net $left_net -objects [get_pins $right_column_cell/I]
        } else {
            connect_net -net $right_net -objects [get_pins $right_column_cell/I]
        }
    }

    route_design -directive Quick

    write_checkpoint -force design.dcp
    write_bitstream -force design.bit
}

run
