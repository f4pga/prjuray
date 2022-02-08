# Copyright 2020-2022 F4PGA Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

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

    puts "Creating BUFG_PS's"
    set fp [open "params.csv"]
    gets $fp line

    set lut_o [get_pins lut/O]

    set vcc_cell [create_cell -reference VCC vcc_cell]
    set vcc_pin [get_pins -of $vcc_cell]

    set vcc_net [create_net vcc_net]
    connect_net -net $vcc_net -objects $vcc_pin

    set net [create_net net]
    connect_net -net $net -objects $lut_o

    while {[gets $fp line] >= 0} {
        set result [split [string trim $line] ","]
        set site [get_sites [lindex $result 2]]
        set site2 [get_sites [lindex $result 3]]
        set val [lindex $result 1]
        if { [llength $site] == 0 } {
            error "Failed to find site $site"
        }
        if { [llength $site2] == 0 } {
            error "Failed to find site $site2"
        }

        set cell [create_cell -reference BUFG_PS ${site}_BUFG]
        if { [llength $cell] == 0 } {
            error "Failed to find cell ${site}_BUFG"
        }

        set_property LOC $site $cell

        set cell2 [create_cell -reference BUFG_PS ${site2}_BUFG]
        if { [llength $cell2] == 0 } {
            error "Failed to find cell ${site2}_BUFG"
        }

        set_property LOC $site2 $cell2

        set site_clk_in [get_pins $cell/I]
        set site2_clk_in [get_pins $cell2/I]

        connect_net -net $net -objects $site2_clk_in

        if { $val == 1 } {
            connect_net -net $net -objects $site_clk_in
        } else {
            connect_net -net $vcc_net -objects $site_clk_in
        }
    }

    route_design -directive Quick

    write_checkpoint -force design.dcp
    write_bitstream -force design.bit
}

run
