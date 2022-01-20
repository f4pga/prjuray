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

proc write_active_bufce_row {filename} {
    set fp [open $filename "w"]
    puts $fp "site,site_clock_region,hdistr_number"

    # Find a clock sink to check if the row buffer is connected, and to
    # determine which HDISTR is being used.
    set site [lindex [get_sites -filter "SITE_TYPE == SLICEL"] 0]
    set clk_sink_site_pin [get_site_pin $site/CLK1]
    set sink_node [get_nodes -of $clk_sink_site_pin]

    if { [llength $sink_node] == 0} {
        error "Failed to find a clock sink node."
    }

    # Find all sites that contain a BUFCE_ROW
    set sites [get_sites -of [get_bels -filter "TYPE == BUFCE_BUFCE_ROW"]]

    foreach site $sites {
        set site_type [get_property SITE_TYPE $site]
        set site_clock_region [get_property CLOCK_REGION $site]

        set src_site_pin [get_site_pin $site/CLK_OUT]
        if { [llength $src_site_pin] == 0 } {
            error "Failed to find CLK_OUT site pin $src_site_pin."
        }

        set src_node [get_nodes -quiet -of $src_site_pin]
        if { [llength $src_node] == 0 } {
            continue
        }

        set path [find_routing_path -quiet -allow_overlap -from $src_node -to $sink_node]
        if { [llength $path] == 0 } {
            continue
        }

        set first_hdistr_wire []
        foreach node $path {
            set hdistr_wires [get_wires -of $node -quiet -filter "NAME =~ *HDISTR*"]
            if { [llength $hdistr_wires] == 0 } {
                continue
            }

            set node_clock_region [get_property BASE_CLOCK_REGION $node]
            if { $site_clock_region != $node_clock_region } {
                error "Site $site is from clock region $site_clock_region, but detected first HDISTR node in clock region $node_clock_region?"
            }

            set hdistr_wires [get_wires -of $node -regexp -filter {NAME =~ RCLK_INT_._X[0-9]+Y[0-9]+/CLK_HDISTR.*}]
            if { [llength $hdistr_wires] == 0 } {
                error "Failed to find first HDISTR wire for site $site?"
            }

            set first_hdistr_wire [lindex $hdistr_wires 0]
            break
        }

        if { [llength $first_hdistr_wire] == 0 } {
            error "Failed to find first HDISTR wire for site $site?"
        }

        if { [regexp "RCLK_INT_._X[0-9]+Y[0-9]+/CLK_HDISTR_FT0_([0-9]+)" $first_hdistr_wire m hdistr_number] == 0 } {
            error "Failed to get HDISTR number from from site $site"
        }

        puts $fp "$site,$site_clock_region,$hdistr_number"
    }

    close $fp
}

write_active_bufce_row ../active_bufce_row.csv
