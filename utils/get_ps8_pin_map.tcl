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
