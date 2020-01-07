# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

# Return [x, y] from SLICE_X<x>Y<y>
proc site_instance_xy {site} {
    set site_name [get_property NAME $site]
    set result [regexp "_X(\\d+)Y(\\d+)$" $site_name match min_x min_y]
    if { $result == 0 } {
        error "Failed to parse site name $site_name"
    }

    return [list $min_x $min_y]
}

proc site_instance_prefix {site} {
    set idx [string last "_X" $site]
    if { $idx == -1 } {
        error "Failed to find _X from site $site"
    }
    set prefix [string range $site 0 $idx-1]

    return $prefix
}

# Return tile relative x/y coordinates for a specific site.
proc site_index_in_tile {tile site} {
    set xy [site_instance_xy $site]
    set min_x [lindex $xy 0]
    set min_y [lindex $xy 1]

    foreach site2 [get_sites -of $tile] {
        if { [site_instance_prefix $site] == [site_instance_prefix $site2] } {
            set xy2 [site_instance_xy $site2]
            set x [lindex $xy2 0]
            set y [lindex $xy2 1]

            if { $x < $min_x } {
                set min_x $x
            }
            if { $y < $min_y } {
                set min_y $y
            }
        }
    }

    set x [expr [lindex $xy 0] - $min_x]
    set y [expr [lindex $xy 1] - $min_y]

    return "[site_instance_prefix $site]_X${x}Y${y}"
}

# Convert verilog constant into [bit width, number]
proc convert_verilog_constant {s} {
    set idx [string first "'" $s]
    if { $idx == -1 } {
        error "$s is not a verilog constant?"
    }

    set width [string range $s 0 [expr $idx-1]]
    set type [string index $s [expr $idx+1]]
    set value [string range $s [expr $idx+2] end]
    if { $type == "h" } {
        if { [scan $value "%x" number] != 1 } {
            error "Failed to read $value"
        }
        return [list $width $number]
    } elseif { $type == "b" } {
        return [list $width [expr 0b$value]]
    } elseif { $type == "d" } {
        if { [scan $value "%d" number] != 1 } {
            error "Failed to read $value"
        }
        return [list $width $number]
    } else {
        error "Unsupported format type '%type'"
    }
}

# Returns 1 if str starts with prefix, 0 otherwise.
proc string_startswith {str prefix} {
    return [string equal -length [string length $prefix] $str $prefix]
}

# Returns 0 if str ends with suffix, 0 otherwise.
proc string_endswith {str suffix} {
    return [string equal [string range $str end-[expr [string length $suffix]-1] end] $suffix]
}

# Returns 1 if str contains pattern, 0 otherwise.
proc string_contains {str pattern} {
    return [expr [string first $pattern $str] != -1]
}

# Return ISO 8601 datetime string.
proc now {} {
    return [clock format [clock seconds] -format "%Y-%m-%dT%H:%M:%S"]
}

proc route_via { net nodes {assert 1} } {
    # Route a simple source to dest net via one or more intermediate nodes
    # the nodes do not have have to be directly reachable from each other
    # net: net name string
    # nodes: list of node or wires strings?
    # Returns 1 on success (previously would silently failed with antenna nets)

    set net [get_nets $net]
    # fixed_route: list of nodes in the full route
    # Begins at implicit node
    set fixed_route [get_nodes -of_objects [get_site_pins -filter {DIRECTION == OUT} -of_objects $net]]
    # Implicit end node. Route it at the end
    lappend nodes [get_nodes -of_objects [get_site_pins -filter {DIRECTION == IN} -of_objects $net]]

    puts "Routing net $net:"

    foreach to_node $nodes {
        # convert wire string to node object
        set to_node [get_nodes -of_objects [get_wires $to_node]]
        # Start at the last point
        set from_node [lindex $fixed_route end]
        # Make vivado do the hard work
        puts "  set route \[find_routing_path -quiet -from $from_node -to $to_node\]"
        set route [find_routing_path -quiet -from $from_node -to $to_node]
        # TODO: check for this
        if {$route == ""} {
            # This can also happen if you try to route to a node already in the route
            if { [ lsearch $route $to_node ] >= 0 } {
                puts "  WARNING: route_via loop. $to_node is already in the path, ignoring"
            } else {
                puts "  $from_node -> $to_node: no route found - assuming direct PIP"
                lappend fixed_route $to_node
            }
        } {
            puts "  $from_node -> $to_node: $route"
            set fixed_route [concat $fixed_route [lrange $route 1 end]]
        }
        set_property -quiet FIXED_ROUTE $fixed_route $net
    }

    # Earlier check should catch this now
    set status [get_property ROUTE_STATUS $net]
    if { $status != "ROUTED" } {
        puts "  Failed to route net $net, status $status, route: $fixed_route"
        if { $assert } {
            error "Failed to route net"
        }
        return 0
    }

    set_property -quiet FIXED_ROUTE $fixed_route $net
    puts ""
    return 1
}

proc tile_wire_pairs {tile1 tile2} {
    set tile1 [get_tiles $tile1]
    set tile2 [get_tiles $tile2]

    foreach wire1 [lsort [get_wires -of_objects $tile1]] {
        set wire2 [get_wires -quiet -filter "TILE_NAME == $tile2" -of_objects [get_nodes -quiet -of_objects $wire1]]
        if {$wire2 != ""} {puts "$wire1 $wire2"}
    }
}

proc randsample_list {num lst} {
    set rlst {}
    for {set i 0} {$i<$num} {incr i} {
        set j [expr {int(rand()*[llength $lst])}]
        lappend rlst [lindex $lst $j]
        set lst [lreplace $lst $j $j]
    }
    return $rlst
}

proc randplace_pblock {num pblock} {
    set sites [randsample_list $num [get_sites -filter {SITE_TYPE == SLICEL || SITE_TYPE == SLICEM} -of_objects [get_pblocks $pblock]]]
    set cells [randsample_list $num [get_cells -hierarchical -filter "PBLOCK == [get_pblocks $pblock] && REF_NAME == LUT6"]]
    for {set i 0} {$i<$num} {incr i} {
        set site [lindex $sites $i]
        set cell [lindex $cells $i]
        set_property LOC $site $cell
    }
}

proc roi_tiles {} {
	return [get_tiles -filter "GRID_POINT_X >= $::env(URAY_ROI_GRID_X1) && \
			GRID_POINT_X < $::env(URAY_ROI_GRID_X2) && \
			GRID_POINT_Y >= $::env(URAY_ROI_GRID_Y1) && \
            GRID_POINT_Y < $::env(URAY_ROI_GRID_Y2)"]
}

proc pblock_tiles {pblock} {
    set clb_tiles [get_tiles -of_objects [get_sites -of_objects [get_pblocks $pblock]]]
    set int_tiles [get_tiles [regsub -all {CLBL[LM]} $clb_tiles INT]]
    return [get_tiles "$clb_tiles $int_tiles"]
}

# returns list of unique tile types
proc get_tile_types {} {
    set all_tiles [get_tiles]
    set types {}
    foreach tile $all_tiles {
        set type [get_property TYPE $tile]
        #ignore empty tiles
        if {$type == "NULL"} { continue }
        if {[lsearch -exact $types $type] == -1} {lappend types $type}
    }
    return $types
}

proc lintersect {lst1 lst2} {
    set rlst {}
    foreach el $lst1 {
        set idx [lsearch $lst2 $el]
        if {$idx >= 0} {lappend rlst $el}
    }
    return $rlst
}

proc putl {lst} {
    foreach line $lst {puts $line}
}

proc write_pip_txtdata {filename} {
    puts "FUZ([pwd]): Writing $filename."
    set fp [open $filename w]
    set nets [get_nets -hierarchical]
    set nnets [llength $nets]
    set neti 0
    foreach net $nets {
        incr neti
        if {($neti % 100) == 0 } {
            puts "FUZ([pwd]): Dumping pips from net $net ($neti / $nnets)"
        }
        foreach pip [get_pips -of_objects $net] {
            set tile [get_tiles -of_objects $pip]
            set src_wire [get_wires -uphill -of_objects $pip]
            set dst_wire [get_wires -downhill -of_objects $pip]
            set num_pips [llength [get_nodes -uphill -of_objects [get_nodes -of_objects $dst_wire]]]
            set dir_prop [get_property IS_DIRECTIONAL $pip]
            puts $fp "$tile $pip $src_wire $dst_wire $num_pips $dir_prop"
        }
    }
    close $fp
}

# Generic non-ROI'd generate.tcl template
proc generate_top {} {
    create_project -force -part $::env(URAY_PART) design design
    read_verilog top.v
    synth_design -top top

    set_property CFGBVS VCCO [current_design]
    set_property CONFIG_VOLTAGE 3.3 [current_design]
    set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]

    place_design
    route_design

    write_checkpoint -force design.dcp
    write_bitstream -force design.bit
}

proc dict_merge_lists args {
    set output [dict create]
    foreach d $args {
        foreach key [dict keys $d] {
            foreach value [dict get $d $key] {
                dict lappend output $key $value
            }
        }
    }

    return $output
}

# Return portion of obj name after last "/"
#
# E.g. SLICE_X0Y0/A6LUT returns A6LUT.
proc get_name {obj} {
    set name [get_property NAME $obj]
    set idx [string last "/" $name]

    return [string range $obj [expr $idx+1] end]
}

proc optionally_route_ps8_interface {src_bel int_node_str xiphy_node_str input_node_str isone} {
    set src_pin [get_pins -quiet $src_bel/O]
    if { [llength $src_pin] != 1 } {
        error "Failed to get src_pin for cell $src_bel"
    }

    set net [get_nets -of $src_pin]
    if { [llength $net] != 1 } {
        error "Failed to get net for cell $src_bel"
    }

    set int_node [get_nodes -quiet $int_node_str]
    if { [llength $int_node] != 1 } {
        error "Failed to get int_node from $int_node_str"
    }

    set xiphy_node [get_nodes -quiet $xiphy_node_str]
    if { [llength $xiphy_node] != 1 } {
        error "Failed to get xiphy_node from $xiphy_node_str"
    }

    set input_node [get_nodes -quiet $input_node_str]
    if { [llength $input_node] != 1 } {
        error "Failed to get input_node from $input_node_str"
    }

    set src_site_pin [get_site_pins -of $net -filter "DIRECTION == OUT"]
    if { [llength $src_site_pin] == 0 } {
        error "Failed to get src_site_pin for net $net"
    }

    set src_node [get_nodes -of [lindex $src_site_pin 0]]

    set path [find_routing_path -from $src_node -to $int_node]
    if $isone {
        lappend path $xiphy_node
    }
    lappend path $input_node

    set_property FIXED_ROUTE $path $net
}

# Create a leaf delay net from the given BUFGCE site to a given CLE slice,
# via a specified BUFCE_LEAF with a specified delay.
proc create_leaf_delay { idx delay bufgce_site bufce_leaf_site slice_site } {
    set bufg [create_cell -ref BUFGCE bufg_$bufgce_site]
    set_property LOC $bufgce_site $bufg

    set sink [create_cell -ref FDRE sink_ff_$slice_site]
    set_property BEL AFF $sink
    set_property LOC $slice_site $sink

    set net [create_net leaf_delay_${idx}_$delay]

    connect_net -net $net -objects [list [get_pins $sink/C] [get_pins $bufg/O]]

    set_property ROUTE "" $net
    set src_node [get_nodes -of [get_site_pin [get_sites -of $bufg]/CLK_OUT]]
    set dst_node1 [get_nodes -of [get_site_pin $bufce_leaf_site/CLK_LEAF]]
    set dst_node2 [get_nodes -of [get_site_pin $slice_site/CLK1]]
    set path [find_routing_path -from $src_node -to $dst_node1]
    set path2 [find_routing_path -from $dst_node1 -to $dst_node2]
    puts "path: $path"
    puts "path2: $path2"
    set_property FIXED_ROUTE [concat $path NoTile/Delay_Arc_Index=$delay [lrange $path2 1 end]] $net
}

proc count_clk_leafs {net} {
    set count 0
    foreach pip2 [get_pips -of $net] {
        set end_wire_name [get_name [get_wires -of $pip2 -downhill]]
        set start_wire_name [get_name [get_wires -of $pip2 -uphill]]
        puts "[get_tiles -of $pip2] $end_wire_name $start_wire_name"
        if { [string_startswith $end_wire_name "CLK_LEAF_SITES_"] && [string_endswith $end_wire_name "_CLK_LEAF"] && [string_startswith $start_wire_name "CLK_LEAF_SITES_"] } {
            incr count
        }
    }
    return $count
}

proc route_bufg_to_bufce_leaf { bufg_site_str bufce_leaf_str hdistr } {
    set bufg_site [get_sites $bufg_site_str]
    if { [llength $bufg_site] != 1 } {
        error "Failed to find site $bufg_site_str?"
    }

    set bufce_leaf [get_sites $bufce_leaf_str]
    if { [llength $bufce_leaf] != 1} {
        error "Failed to find site $bufce_leaf_str?"
    }
    set src_site_pin [get_site_pins $bufg_site/CLK_OUT]
    if { [llength $src_site_pin] != 1 } {
        error "Failed to find CLK_OUT site pin from site $bufg_site!"
    }

    set src_node [get_nodes -of $src_site_pin]

    set dest_tile [get_tiles -of $bufce_leaf]
    set dest_wire [get_wires $dest_tile/CLK_HDISTR_FT0_$hdistr]
    if { [llength $dest_wire] != 1 } {
        error "Failed to find HDISTR $hdistr wire from tile $dest_tile!"
    }

    set dest_node [get_nodes -of $dest_wire]

    set src_cell [get_cells -of $bufg_site]
    if { [llength $src_cell] != 1 } {
        error "Failed to find source cell from $bufg_site!"
    }

    set src_pin [get_pins $src_cell/O]
    if { [llength $src_pin] != 1 } {
        error "Failed to find source pin from $bufg_site!"
    }

    set net [get_nets -of $src_pin]
    if { [llength $net] != 1 } {
        error "Failed to find net from $bufg_site!"
    }

    set dest_site_pin [get_site_pins $bufce_leaf/CLK_IN]
    if { [llength $dest_site_pin] != 1 } {
        error "Failed to find CLK_IN site pin from site $bufce_leaf!"
    }

    # $dest_node -> $final_node is just 1 hop!
    set final_node [get_nodes -of $dest_site_pin]

    set start_path [find_routing_path -from $src_node -to $dest_node]
    if { [llength $start_path] == 0 } {
        error "Failed to route from BUFG ($src_node) to HDISTR ($dest_node)!"
    }

    set_property FIXED_ROUTE [concat $start_path $final_node] $net
}

# Some BUFG outputs can go left or right onto the HROUTE wire.
# Instead of routing directly to the BUFCE_ROW, first go the opposite
# direction, then route to the BUFCE_ROW.
#
# This adds diversity to the pip usage and causes diversity in
# HROUTE.USED features.
proc route_bufg_to_bufce_row_via_opposite_wire { bufg_site_str bufce_row_str hroute } {
    set bufg_site [get_sites $bufg_site_str]
    if { [llength $bufg_site] != 1 } {
        error "Failed to find site $bufg_site_str?"
    }

    set bufce_row [get_sites $bufce_row_str]
    if { [llength $bufce_row] != 1 } {
        error "Failed to find site $bufce_row_str?"
    }

    set src_site_pin [get_site_pins $bufg_site/CLK_OUT]
    if { [llength $src_site_pin] != 1 } {
        error "Failed to find CLK_OUT site pin from site $bufg_site!"
    }

    set src_node [get_nodes -of $src_site_pin]

    set src_cell [get_cells -of $bufg_site]
    if { [llength $src_cell] != 1 } {
        error "Failed to find source cell from $bufg_site!"
    }

    set src_pin [get_pins $src_cell/O]
    if { [llength $src_pin] != 1 } {
        error "Failed to find source pin from $bufg_site!"
    }

    set net [get_nets -of $src_pin]
    if { [llength $net] != 1 } {
        error "Failed to find net from $bufg_site!"
    }

    set dest_site_pin [get_site_pins $bufce_row/CLK_IN]
    if { [llength $dest_site_pin] != 1 } {
        error "Failed to find CLK_IN site pin from site $bufce_row!"
    }

    set dest_node [get_nodes -of $dest_site_pin]

    set tile [get_tiles -of $bufg_site]
    set tile_type [get_property TYPE $tile]
    if { $tile_type == "RCLK_HDIO" } {
        set left_wire [get_wires $tile/CLK_HROUTE_L$hroute]
        if { [llength $left_wire] != 1 } {
            error "Failed to get left wire from source tile $tile"
        }

        set left_node [get_nodes -of $left_wire]
        if { [llength $left_node] != 1 } {
            error "Failed to get left node from source tile $tile"
        }

        set right_wire [get_wires $tile/CLK_HROUTE_R$hroute]
        if { [llength $right_wire] != 1 } {
            error "Failed to get right wire from source tile $tile"
        }

        set right_node [get_nodes -of $right_wire]
        if { [llength $right_node] != 1 } {
            error "Failed to get right node from source tile $tile"
        }

        set direct_path [find_routing_path -from $src_node -to $dest_node -allow_overlap]
        set is_left 0
        set is_right 0
        foreach node $direct_path {
            if { $node == $right_node } {
                set is_right 1
            }

            if { $node == $left_node } {
                set is_left 1
            }
        }

        if { $is_left && $is_right } {
            return
        }

        if { $is_left } {
            set inter_node $right_node
        }

        if { $is_right } {
            set inter_node $left_node
        }

        set path_to_inter [find_routing_path -from $src_node -to $inter_node]
        if { [llength $path_to_inter] == 0 } {
            error "Failed to find path from $src_node to $inter_node"
        }

        set path_inter_to_dest [find_routing_path -from $inter_node -to $dest_node]
        if { [llength $path_inter_to_dest] == 0 } {
            error "Failed to find path from $inter_node to $dest_node"
        }

        set_property FIXED_ROUTE [concat $path_to_inter [lrange $path_inter_to_dest 1 end]] $net
    } else {
        error "Unsupported BUFG source tile type $tile_type"
    }
}
