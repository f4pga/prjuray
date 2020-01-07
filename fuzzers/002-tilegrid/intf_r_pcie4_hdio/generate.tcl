# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

source "$::env(URAY_DIR)/utils/utils.tcl"

proc create_intf_r_pcie4 {site val} {
    set lut_cell [create_cell -reference LUT1 lut_$site]
    set lut_o_pin [get_pins lut_$site/O]

    set ddr_cell [create_cell -reference ODDRE1 oddre_$site]
    set_property LOC $site $ddr_cell
    set ddr_pin [get_pins "$ddr_cell/D\[0\]"]

    set end_node [get_nodes -of [get_site_pins -of [get_bel_pins -of $ddr_pin]]]
    set pip_node $end_node
    set pips [get_pips -of $pip_node -filter {IS_PSEUDO == 0}]
    if {[llength $pips] == 1} {
        # Walk up again if only 1 pip!
        set pip_node [get_nodes -of $pips -uphill]
        set pips [get_pips -of $pip_node -filter {IS_PSEUDO == 0} -uphill]
    }

    if { [llength $pips] != 2 } {
        error "Expected two pips going to site $site, from node $pip_node"
    }

    set target_tile [get_tiles -of $pips]
    if {[llength $target_tile] != 1 } {
        error "Unexpected number of tiles from site $site"
    }

    set mid_node1 [get_nodes -of [lindex $pips 0] -uphill]
    set mid_node2 [get_nodes -of [lindex $pips 1] -uphill]

    if { [string_contains $mid_node1 "DELAYWIRE"] } {
        set delay_node $mid_node1
        set mid_node $mid_node2
    } else {
        set delay_node $mid_node2
        set mid_node $mid_node1
    }

    if { [string_contains $delay_node "DELAYWIRE"] == 0 } {
        error "Unexpected structure from site $site!"
    }

    set mid_node2 [get_nodes -of [get_pips -uphill -of $delay_node] -uphill]
    if { $mid_node != $mid_node2 } {
        error "Not the same mid node? $mid_node, $mid_node2"
    }

    set source_tile [get_tiles -filter "GRID_POINT_X == [expr [get_property GRID_POINT_X $target_tile]-2]  && GRID_POINT_Y == [get_property GRID_POINT_Y $target_tile]"]
    if { [llength $source_tile] != 1 } {
        error "Error getting source tile for site $site"
    }

    set source_site [get_sites -of $source_tile]
    if { [llength $source_site] != 1 } {
        error "Error getting source site for site $site"
    }

    set_property LOC $source_site $lut_cell
    set_property BEL A6LUT $lut_cell

    set lut_o_site_pin [lindex [get_site_pins -of [get_bel_pins -of $lut_o_pin]] 0]
    set source_node [get_nodes -of $lut_o_site_pin]

    set net [create_net net_$site]
    connect_net -net $net -objects "$lut_o_pin $ddr_pin"

    set path1 [find_routing_path -from $source_node -to $mid_node]
    if { $pip_node == $end_node } {
        set path2 $end_node
    } else {
        set path2 [list $pip_node $end_node]
    }

    if { $val == 1 } {
        # Use delay pip
        set_property FIXED_ROUTE [concat $path1 $delay_node $path2] $net
    } else {
        # Direct path
        set_property FIXED_ROUTE [concat $path1 $path2] $net
    }

    return $target_tile
}

proc run {} {
    create_project -force -part $::env(URAY_PART) design design
    read_verilog top.v
    synth_design -top top

    set_property BEL A6LUT [get_cells -filter "REF_NAME == LUT6"]
    set_property IS_BEL_FIXED 1 [get_cells -filter "REF_NAME == LUT6"]

    set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]
    set_property IS_ENABLED 0 [get_drc_checks {LUTLP-1}]

    place_design -directive Quick

    set in_fp [open "gen_params.csv"]
    set fp [open "params.csv" "w"]

    while {[gets $in_fp line] >= 0} {
        set result [split [string trim $line] ","]
        set site [get_sites [lindex $result 0]]
        set val [lindex $result 1]
        set tile [create_intf_r_pcie4 $site $val]
        puts $fp "$tile,$val"
    }

    close $fp
    close $in_fp

    route_design -directive Quick

    write_checkpoint -force design.dcp
    write_bitstream -force design.bit
}

run
