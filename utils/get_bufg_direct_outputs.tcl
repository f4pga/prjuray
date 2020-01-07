# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

# Import:
#   get_name
source $::env(URAY_UTILS_DIR)/utils.tcl

create_project -force -part $::env(URAY_PART) design design
set_property design_mode PinPlanning [current_fileset]
open_io_design -name io_1

proc get_hroute_value_from_node {node} {
    # RCLK_INTF_LEFT_TERM_ALTO_X0Y149/CLK_HROUTE0 -> 0
    # RCLK_DSP_INTF_CLKBUF_L_X18Y149/CLK_HROUTE_R0 -> 0
    set name [get_name $node]

    if { [regexp "HROUTE(?:_R)?(\[0-9\]+)" $name m s] == 0 } {
        error "Failed to get hroute number from node $node"
    }

    if { ($s+0) < 0 && ($s+0) >= 24 } {
        error "Failed to get hroute number from node $node"
    }

    return $s
}

proc check_all_hroute {nodes} {
    set values []
    foreach node $nodes {
        lappend values [get_hroute_value_from_node $node]
    }

    if { [llength $values] != 24 } {
        error "Have [llength $values] instead of expected values"
    }

    set values [lsort -integer $values]
    for {set i 0} {$i < 24} {incr i} {
        if { $i != [lindex $values $i] } {
            error "Missing HROUTE $i from $nodes, $values"
        }
    }
}

proc write_bufg_direct_outputs {filename} {
    set bufg_direct_outputs [dict create]

    foreach site [get_sites -filter "SITE_TYPE =~ BUFG*"] {
        set src_node [get_nodes -of [get_site_pins $site/CLK_OUT]]
        set direct_node [get_nodes -quiet -of [get_pips -of $src_node] -downhill -filter "NAME =~ *HROUTE*"]

        if { [llength $direct_node] > 0 } {
            dict set bufg_direct_outputs $site $direct_node
        }

        set clock_region [get_property BASE_CLOCK_REGION $src_node]

        set tiles [get_tiles -of [get_sites -filter "CLOCK_REGION == $clock_region && SITE_TYPE == BUFCE_ROW_FSR"] -filter "TYPE =~ RCLK_CLE*"]
        if { [llength $tiles] == 0 } {
            error "No RCLK_CLE* tiles in clock region $clock_region for site $site"
        }

        set tile [lindex $tiles 0]

        for {set i 0} {$i < 24} {incr i} {
            set dest_node [get_nodes -of [get_wires $tile/CLK_HROUTE_FT0_$i]]
            if { [llength $dest_node] == 0 } {
                error "Failed to get HROUTE$i node for site $site?"
            }

            set path [find_routing_path -from $src_node -to $dest_node  -allow_overlap -quiet -max_nodes 6]
            if { [llength $path] > 0 } {
                dict lappend bufg_direct_outputs $site $dest_node
            }
        }
    }

    set fp [open $filename w]

    puts $fp "site,hroute_output,clock_region"

    foreach site [get_sites -filter "SITE_TYPE =~ BUFG*"] {
        set nodes [dict get $bufg_direct_outputs $site]
        if {[llength $nodes] == 1 } {
            puts $fp "$site,[get_hroute_value_from_node $nodes],[get_property CLOCK_REGION $site]"
        } elseif {[llength $nodes] == 24} {
            check_all_hroute $nodes
            puts $fp "$site,all,[get_property CLOCK_REGION $site]"
        } else {
            error "Weird site $site, nodes $nodes"
        }
    }

}

write_bufg_direct_outputs ../bufg_outputs.csv
