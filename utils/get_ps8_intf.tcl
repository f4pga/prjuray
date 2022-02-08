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
