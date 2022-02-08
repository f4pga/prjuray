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
