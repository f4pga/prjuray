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

    puts "Creating BUFCE_ROW's"
    set fp [open "params.csv"]
    gets $fp line

    set lut_pin [get_pins lut/O]

    set net [create_net lut_net]
    connect_net -net $net -objects $lut_pin

    while {[gets $fp line] >= 0} {
        set result [split [string trim $line] ","]
        set site [get_sites [lindex $result 2]]
        set val [lindex $result 1]
        if { [llength $site] == 0 } {
            error "Failed to find site $site"
        }

        set cell [create_cell -reference BUFCE_ROW ${site}_BUFCE_ROW]
        if { [llength $cell] == 0 } {
            error "Failed to find cell ${site}_BUFCE_ROW"
        }

        set pin [get_pins $cell/CE]
        set_property LOC $site $cell
        set_property IS_CE_INVERTED $val $cell
        connect_net -net $net -objects $pin
    }

    route_design -directive Quick

    write_checkpoint -force design.dcp
    write_bitstream -force design.bit
}

run
