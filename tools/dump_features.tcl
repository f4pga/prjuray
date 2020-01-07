# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

# Import:
#   site_instance_xy
#   site_index_in_tile
#   string_startswith
#   string_endswith
#   string_contains
#   convert_verilog_constant
#   now
#   get_name
source $::env(URAY_UTILS_DIR)/utils.tcl

proc get_all_pips {} {
    set all_nets [get_nets -hierarchical]
    set all_pips []

    set idx 0

    set nets_seen [dict create]
    foreach net $all_nets {
        if { $idx % 100 == 0 } {
            puts "[now]: Processing net $idx / [llength $all_nets]"
        }
        incr idx

        set first_node [lindex [lsort [get_nodes -quiet -of $net]] 0]
        if { [dict exists $nets_seen $first_node] } {
            continue
        }
        dict set nets_seen $first_node 1

        set all_pips [concat $all_pips [get_pips -of $net]]
    }

    return $all_pips
}

proc get_property_debug {propname obj} {
    if { [llength $obj] == 0 } {
        error "No object from $propname"
    }
    return [get_property $propname $obj]
}

proc remove_verilog_notation {v} {
    set base_pos [string first "'b" $v]
    if {$base_pos != -1} {
        set v [string range $v [expr $base_pos + 2] end]
    }

    return $v
}

# Create a dictionary of node -> pip uphill of node.
proc create_pip_uphill { net obj } {
    # Create node -> pip that is upstream of node map
    set pip_uphill [dict create]
    foreach pip [get_pips -of $net] {
        set node_downhill [get_nodes -of $pip -downhill]
        if { [dict exists $pip_uphill $node_downhill] == 0 } {
            dict set pip_uphill $node_downhill $pip
        }

        if { [get_property_debug IS_DIRECTIONAL $pip] == 0 } {
            set node_uphill [get_nodes -of $pip -uphill]
            if { [dict exists $pip_uphill $node_uphill] == 0 } {
                dict set pip_uphill $node_uphill $pip
            }
        }
    }

    return $pip_uphill
}

proc get_downstream_lut_pins { bel } {
    set site [get_sites -of $bel]
    set lut5 [string_endswith $bel "5LUT"]
    set lut6 [string_endswith $bel "6LUT"]
    if { !$lut5 && !$lut6 } {
        error "$bel is not a LUT?"
    }

    set letter [string index [get_name $bel] 0]

    set carry8_index [string map {
        "A" 0
        "B" 1
        "C" 2
        "D" 3
        "E" 4
        "F" 5
        "G" 6
        "H" 7
    } $letter]

    set bel_pin_strs [list]
    set site_pin [list]
    if $lut5 {
        lappend bel_pin_strs $site/OUTMUX$letter/D5
        lappend bel_pin_strs $site/FFMUX${letter}2/D5
        lappend bel_pin_strs $site/FFMUX${letter}1/D5
        lappend bel_pin_strs $site/CARRY8/DI${carry8_index}
    } else {
        lappend bel_pin_strs $site/OUTMUX$letter/D6
        lappend bel_pin_strs $site/FFMUX${letter}2/D6
        lappend bel_pin_strs $site/FFMUX${letter}1/D6
        lappend bel_pin_strs $site/CARRY8/S${carry8_index}

        set f7mux [string map {
            "A" "AB/1"
            "B" "AB/0"
            "C" "CD/1"
            "D" "CD/0"
            "E" "EF/1"
            "F" "EF/0"
            "G" "GH/1"
            "H" "GH/0"
        } $letter]
        lappend bel_pin_str $site/F7MUX_$f7mux

        set site_pin [get_site_pins -quiet $site/${letter}_O]
        if { [llength $site_pin] == 0 } {
            error "Failed to get site pin for BEL $bel"
        }
    }

    set bel_pins [list]
    foreach bel_pin_str $bel_pin_strs {
        set other_bel_str [string range $bel_pin_str 0 [string last  "/" $bel_pin_str]-1]
        set other_bel [get_bels -quiet -include_routing_bels $other_bel_str]
        if { [llength $other_bel] == 0 } {
            error "Failed to get other bel $other_bel_str for BEL $bel"
        }
        set bel_pin [get_bel_pins -quiet $bel_pin_str -of $other_bel]
        if { [llength $bel_pin] == 0 } {
            error "Failed to get input bel pin BEL $bel from $bel_pin_str"
        }

        lappend bel_pins $bel_pin
    }

    return [list $bel_pins [llength $site_pin] $site_pin]
}

proc create_physical_return {net bel} {
    if { [is_static_net $net] } {
        return [list 1 [get_property_debug TYPE $net]]
    }

    # A6LUT -> 6, H5LUT -> 5
    set width [string index [get_name $bel] 1]
    if {$width != 6 && $width != 5} {
        error "Weird lut width?"
    }

    for {set i} {$i < $width} {incr i} {
        set bel_pin_str "$bel/A[expr $i+1]"
        set bel_pin [get_bel_pins -quiet $bel_pin_str]
        if { [llength $bel_pin] == 0 } {
            error "Failed to get bel_pin $bel_pin_str"
        }

        set pin_net [get_nets -quiet -of $bel_pin]
        if { [llength $net] > 0 } {
            if { $pin_net == $net } {
                return [list 0 $bel_pin]
            }
        }
    }

    error "Failed to find physical equation for LUT from BEL $bel!?"
}

# Route-through and VCC / GND luts do not appear as cells.  Infer their
# presence by looking for uses of the O6 or O5 signal.
proc identify_physical_lut_equation { bel } {
    set cell [get_cells -quiet -of $bel]
    if { [llength $cell] > 0 } {
        error "BEL $bel has a cell?"
    }

    set pins_for_lut [get_downstream_lut_pins $bel]
    set bel_pins [lindex $pins_for_lut 0]
    set have_site_pin [lindex $pins_for_lut 1]

    if $have_site_pin {
        set site_pin [lindex $pins_for_lut 2]
        set net [get_nets -quiet -of $site_pin]
        if { [llength $net] > 0 } {
            return [create_physical_return $net $bel]
        }
    }

    foreach bel_pin $bel_pins {
        set net [get_nets -quiet -of $bel_pin]
        if { [llength $net] > 0 } {
            return [create_physical_return $net $bel]
        }

        set pin [get_pins -quiet -of $bel_pin]
        if { [llength $pin] > 0 } {
            set net [get_nets -quiet -of $pin]
            if { [llength $net] > 0 } {
                return [create_physical_return $net $bel]
            }
        }
    }

    return [list]
}

proc get_has_lut5 { bel } {
    if { [llength $bel] != 1 } {
        error "Weird input to get_has_lut5 of $bel"
    }

    # Simple case, there is a cell in the LUT5.
    if {[llength [get_cells -quiet -of $bel]] > 0 } {
        return 1
    }

    # Weird case, one of the pins of the LUT5 are in use for route through!
    if { [llength [get_pins -quiet -of [get_bel_pins -of $bel]]] > 0} {
        return 1
    }

    # Weird case, one of the pins of the LUT5 are in use for constant
    # generation!
    if { [llength [identify_physical_lut_equation $bel]] > 0 } {
        return 1
    }

    return 0
}

proc is_static_net { net } {
    set type [get_property_debug TYPE $net]
    if { $type == "GROUND" || $type == "POWER" } {
        return 1
    } else {
        return 0
    }
}

proc is_node_inverted { net cursor } {
    set pip_uphill [create_pip_uphill $net $cursor]

    set inv 0
    while { [dict exists $pip_uphill $cursor] } {
        set pip [dict get $pip_uphill $cursor]

        set start_wire_name [get_name [get_wires -of $pip -uphill]]
        set end_wire_name [get_name [get_wires -of $pip -downhill]]
        set is_bidirectional [expr [get_property_debug IS_DIRECTIONAL $pip] == 0]
        if { $is_bidirectional } {
            set div "<<->>"
        } else {
            set div "->>"
        }

        set is_fixed_inversion [get_property_debug IS_FIXED_INVERSION $pip]
        if $is_fixed_inversion {
            set inv [expr !$inv]
        }

        set uphill_node [get_nodes -of $pip -uphill]
        set downhill_node [get_nodes -of $pip -downhill]

        if { $is_bidirectional && $cursor == $uphill_node } {
            set cursor $downhill_node
        } else {
            set cursor $uphill_node
        }
    }

    return $inv
}


# Return 1 if sink is inverted because of IS_FIXED_INVERSION pip's.
proc is_sink_inverted { site_pin_inst } {
    if { [get_property_debug DIRECTION $site_pin_inst] != "IN" } {
        error "$site_pin_inst isn't a sink?"
    }

    set net [get_nets -of $site_pin_inst]
    set cursor [get_nodes -of $site_pin_inst]

    return [is_node_inverted $net $cursor]
}

# For the given LUT bel and lut_index (0-63), return the init_index into the
# INIT parameter for that underlying hardware index.
#
# This takes into account LUT bel pin to logical cell pin mapping.
proc create_lut_init_index {bel lut_index} {
    set init_index 0
    set valid_index 1

    for {set j 0} {$j < 6} {incr j} {
        if { ($lut_index & (1 << $j)) == 0 } {
            continue
        }

        set bel_pin_str "$bel/A[expr $j +1]"
        set bel_pin [get_bel_pins $bel_pin_str]
        if { [llength $bel_pin] == 0 } {
            error "Invalid BEL pin $bel_pin_str"
        }
        set pin [get_pins -quiet -of $bel_pin]
        if { [llength $pin] == 0 } {
            continue
        }

        set pin_name [get_name $pin]
        if [string_startswith $pin_name "RADR"] {
            set shift [string index $pin_name 4]
        } elseif [string_startswith $pin_name "A\["] {
            set shift [string index $pin_name 2]
        } elseif {[string_startswith $pin_name "I"] == 0 && [string_startswith $pin_name "A"] == 0} {
            set valid_index 0
            break
        } else {
            set shift [string index $pin_name 1]
        }

        set init_index [expr $init_index | (1 << $shift)]
    }

    return [list $init_index $valid_index]
}

# Return the parent net name for the specified net.
proc get_parent_net {net} {
    while 1 {
        # When a net is it's own parent, at the top.
        set parent_net_str [get_property_debug PARENT $net]
        if { $net == $parent_net_str } {
            return $net
        }

        set net [get_nets $parent_net_str]
    }
}

# Inverse pip direction string
#
# Maps "FWD" -> "REV" and "REV" -> "FWD"
proc inverse_pip_direction { pip_direction } {
    if { $pip_direction == "FWD" } {
        return "REV"
    } elseif { $pip_direction == "REV" } {
        return "FWD"
    } else {
        error "Unknown pip direction $pip_direction"
    }
}

# Determine direction of bidirectional pip based on a pip relative to the target pip.
#
# Arguments:
#  direction_from_target - Is the known_pip uphill or downhill of the target?
#  known_pip - Pip with know direction
#  node_connected_to_known_pip - Node that is connected to known pip, see
#                                diagram below.
#  known_pip_direction - What direction is the known pip?
#
#  Diagram:
#
#       direction_from_target = "uphill":
#
#                +---------------+                                           +--------------+
#                |               |                                           |              |
#     +--------->+  known_pip    +---- node_connected_to_known_pip --------->+  target pip  +------->
#                |               |                                           |              |
#                +---------------+                                           +--------------+
#
#       direction_from_target = "downhill":
#
#                +--------------+                                            +--------------+
#                |              |                                            |              |
#     +--------->+  target pip  +----- node_connected_to_known_pip --------->+  known_pip   +------->
#                |              |                                            |              |
#                +--------------+                                            +--------------+
#
proc determine_pip_direction {direction_from_target known_pip node_connected_to_known_pip known_pip_direction } {
    # The logic in this function works as follows:
    #  - Determine if known_pip is directional, if so, then return simply determined by
    #    direction_from_target and known_pip_direction, e.g.:
    #      - Return known_pip_direction if direction_from_target is uphill, otherwise inverse
    #  - If the known_pip is bidirectional, determine if known_pip_direction
    #    needs to be reversed because node_connected_to_known_pip is on
    #    opposite side of direction_from_target.

    set is_directional [get_property_debug IS_DIRECTIONAL $known_pip]
    if { $is_directional == 0 } {
        set node [get_nodes -of $known_pip -$direction_from_target]
        if { $node == $node_connected_to_known_pip } {
            set known_pip_direction [inverse_pip_direction $known_pip_direction]
        }
    }

    if { $direction_from_target == "uphill" } {
        return $known_pip_direction
    } elseif { $direction_from_target == "downhill" } {
        return [inverse_pip_direction $known_pip_direction]
    } else {
        error "Unknown direction_from_target $direction_from_target"
    }
}

# Attempt to find the direction of bidirectional pip by examining the uphill
# and downhill pips from the bipip.
#
# TODO: This algorithm assumes that there is a known pip directly uphill or
# downhill.  This assumption is not generally valid.
proc find_direction_of_bipip {bipip pip_direction node_to_uphill_pip node_to_downhill_pip} {
    set uphill_node [get_nodes -of $bipip -uphill]
    set downhill_node [get_nodes -of $bipip -downhill]

    # Try climbing uphill
    if [dict exists $node_to_uphill_pip $uphill_node] {
        set pip [dict get $node_to_uphill_pip $uphill_node]
        if [dict exists $pip_direction $pip] {
            set direction [dict get $pip_direction $pip]
            return [determine_pip_direction "uphill" $pip $uphill_node $direction]
        }
    }
    if [dict exists $node_to_uphill_pip $downhill_node] {
        set pip [dict get $node_to_uphill_pip $downhill_node]
        if [dict exists $pip_direction $pip] {
            set direction [dict get $pip_direction $pip]
            return [inverse_pip_direction [determine_pip_direction "uphill" $pip $downhill_node $direction]]
        }
    }

    # Try climbing downhill
    if [dict exists $node_to_downhill_pip $uphill_node] {
        set pip [dict get $node_to_downhill_pip $uphill_node]
        if [dict exists $pip_direction $pip] {
            set direction [dict get $pip_direction $pip]
            return [determine_pip_direction "downhill" $pip $uphill_node $direction]
        }
    }
    if [dict exists $node_to_downhill_pip $downhill_node] {
        set pip [dict get $node_to_downhill_pip $downhill_node]
        if [dict exists $pip_direction $pip] {
            set direction [dict get $pip_direction $pip]
            return [inverse_pip_direction [determine_pip_direction "downhill" $pip $downhill_node $direction]]
        }
    }

    error "Couldn't determine direction of pip $pip!"
}

proc get_clock_depth {net cursor} {
    set pip_uphill [create_pip_uphill $net $cursor]

    set distr_count 0
    while { [dict exists $pip_uphill $cursor] } {
        set pip_str [dict get $pip_uphill $cursor]
        set pip [get_pips $pip_str]
        set tile [get_tiles -of $pip]
        set tile_type [get_property_debug TYPE $tile]
        set start_wire_name [get_name [get_wires -of $pip -uphill]]
        set end_wire_name [get_name [get_wires -of $pip -downhill]]

        set is_bidirectional [expr [get_property_debug IS_DIRECTIONAL $pip] == 0]

        set start_node [get_nodes -of $pip -downhill]
        if { $is_bidirectional && $start_node == $cursor } {
            set cursor [get_nodes -of $pip -uphill]
        } else {
            set cursor [get_nodes -of $pip -downhill]
        }

        if {[string_startswith $cursor "DISTR"]} {
            incr distr_count
        }
    }

    return $distr_count
}

proc get_max_distr_depth {} {

    puts "[now] Running get_max_distr_depth"
    set all_nets [get_nets -hierarchical]
    set all_pips [::struct::set union [get_pips -of $all_nets] []]

    set nets_to_max_distr_depth [dict create]

    foreach pip_str $all_pips {
        if {[string_contains $pip_str BUFCE_ROW_FSR] && [string_contains $pip_str "CLK_IN"]} {
            set pip [get_pips $pip_str]

            set start_wire [get_wires -of $pip -downhill]
            set start_wire_name [get_name $start_wire]
            if {[string_startswith $start_wire_name "BUFCE_ROW_FSR"] && [string_endswith $start_wire_name "CLK_IN"]} {
                set net [get_nets -quiet -of $pip]
                if {[dict exists $nets_to_max_distr_depth $net] != 0} {
                    dict set nets_to_max_distr_depth $net 0
                }
                set distr_depth [get_clock_depth $net [get_nodes -of $pip downhill]]

                set max_distr_depth [dict get $nets_to_max_distr_depth $net]

                if { $distr_depth > $max_distr_depth } {
                    dict set nets_to_max_distr_depth $net $distr_depth
                }
            }
        }
    }
    puts "[now] Finished with get_max_distr_depth"

    return $max_distr_depth
}

proc prepare_pip_direction {} {
    set all_nets [get_nets -hierarchical]
    set all_pips [::struct::set union [get_pips -of $all_nets] []]

    set idx 0
    foreach pip_str $all_pips {
        set pip [get_pips $pip_str]
        if { $idx % 1000 == 0 } {
            puts "[now]: Processing pip $idx / [llength $all_pips]"
        }
        incr idx

        # Skip bi-directional pips for now, come back once all unidirectional
        # pips are handled.
        set is_directional [get_property_debug IS_DIRECTIONAL $pip]
        if { $is_directional == 0 } {
            lappend bipips $pip
            continue
        }

        # All unidirectional pips go forward
        dict set pip_direction $pip "FWD"

        set uphill_wire [get_wires -of $pip -uphill]
        set downhill_wire [get_wires -of $pip -downhill]

        set uphill_node [get_nodes -of $uphill_wire]
        set downhill_node [get_nodes -of $downhill_wire]

        # The map from node to uphill pip is backward from the pips perspective.
        # E.g. the pip downhill of a node, is uphill to the pip
        dict set node_to_uphill_pip $downhill_node $pip
        dict set node_to_downhill_pip $uphill_node $pip
    }

    return [list $pip_direction $node_to_uphill_pip $node_to_downhill_pip]
}

# Dump pip specific features from nets in the design.
#
# Returns map of "tile:tile_type" to list of features in that tile.
proc dump_pips {filter_bram filter_int} {
    set pips_by_tile [dict create]

    set all_nets [get_nets -hierarchical]
    set all_pips [filter [get_all_pips] "IS_PSEUDO == 0"]

    set bipips [list]
    set pip_direction [dict create]
    set node_to_uphill_pip [dict create]
    set node_to_downhill_pip [dict create]

    set have_max_distr_depth 0

    set idx 0
    foreach pip_str $all_pips {
        set pip [get_pips $pip_str]
        if { $idx % 1000 == 0 } {
            puts "[now]: Processing pip $idx / [llength $all_pips]"
        }
        incr idx

        set tile [get_tiles -of $pip]
        set tile_type [get_property_debug TYPE $tile]
        if { $filter_bram && $tile_type == "BRAM" } {
            continue
        }
        if { $filter_int && $tile_type == "INT" } {
            continue
        }

        if { !$filter_int && $tile_type == "INT_INTF_L_IO" } {
            set wire [get_wires -of $pip -downhill]
            if { [string_contains $wire "LOGIC_OUTS"] } {
                dict lappend pips_by_tile "$tile:$tile_type" "WIRE.LOGIC_OUTS_R.DRIVEN.V1"
            }
            continue
        }

        # Skip bi-directional pips for now, come back once all unidirectional
        # pips are handled.
        set is_directional [get_property_debug IS_DIRECTIONAL $pip]
        if { $is_directional == 0 } {
            lappend bipips $pip
            continue
        }

        set uphill_wire [get_wires -of $pip -uphill]
        set downhill_wire [get_wires -of $pip -downhill]
        set base_feature "PIP.[get_name $downhill_wire].[get_name $uphill_wire]"
        dict lappend pips_by_tile "$tile:$tile_type" $base_feature

        set uphill_node [get_nodes -of $uphill_wire]
        set downhill_node [get_nodes -of $downhill_wire]

        # All unidirectional pips go forward
        dict set pip_direction $pip "FWD"

        # The map from node to uphill pip is backward from the pips perspective.
        # E.g. the pip downhill of a node, is uphill to the pip
        dict set node_to_uphill_pip $downhill_node $pip
        dict set node_to_downhill_pip $uphill_node $pip

        set net [get_nets -quiet -of $pip]
        if {[string_contains $net "clk_dly_fuzz"] && [string_contains $downhill_wire "BUFCE_ROW_FSR"] && [string_endswith $downhill_wire "CLK_IN"]} {
            set depth [get_clock_depth $net $downhill_node]

            if { $have_max_distr_depth == 0 } {
                set max_distr_depth [get_max_distr_depth]
            }
            set tap [expr [dict get $max_distr_depth $net] - $depth]

            set site_pin [get_site_pins -of $uphill_node]
            if { [llength $site_pin] == 0 } {
                error "Failed to get site_pin from uphill of $pip"
            }

            set bufce_name [site_index_in_tile [get_tiles -of $pip] [get_sites -of $site_pin]]
            for {set i 0} {$i < 3} {incr i} {
                if { (($tap >> $i) & 0x1) == 1) } {
                    dict lappend pips_by_tile "$tile:$tile_type" "$bufce_name.COMP_DELAY_TAP\[$i\]"
                }
            }
        }
    }

    set idx 0
    puts "Number of bipips: [llength $bipips]"
    foreach bipip $bipips {
        if { $idx % 100 == 0 } {
            puts "[now]: Processing bipip $idx / [llength $bipips]"
        }
        incr idx

        set direction [find_direction_of_bipip $bipip $pip_direction $node_to_uphill_pip $node_to_downhill_pip]
        set uphill_wire [get_wires -of $bipip -uphill]
        set downhill_wire [get_wires -of $bipip -downhill]

        set tile [get_tiles -of $bipip]
        set tile_type [get_property_debug TYPE $tile]
        set base_feature "PIP.[get_name $downhill_wire].[get_name $uphill_wire]"
        dict lappend pips_by_tile "$tile:$tile_type" "$base_feature.$direction"
    }

    return $pips_by_tile
}

proc get_lut_bits {cell} {
    set bel [get_bels -of $cell]
    set bel_name [get_name $bel]
    set ret [convert_verilog_constant [get_property_debug INIT $cell]]
    set init_width [lindex $ret 0]
    set long_init [lindex $ret 1]

    set lut_bits [list]

    for {set i 0} {$i < 64} {incr i} {
        if {[string_contains $bel_name "5LUT"] && $i >= 32} {
            break
        }

        set ret [create_lut_init_index $bel $i]
        set init_index [lindex $ret 0]
        set valid_index [lindex $ret 1]

        if {!$valid_index} {
            continue
        }

        if { ($long_init & (1 << $init_index)) == 0 } {
            continue
        }

        lappend lut_bits $i
    }

    return $lut_bits
}

# Dump features from CLEL and CLEM tiles, and BUFCE_LEAF tiles.
#
# Returns map of "tile:tile_type" to list of features in that tile.
proc dump_features {} {
    set sitefeatures_by_tile [dict create]

    puts "[now]: Getting sites in use"
    set sites_in_use [get_sites -filter {IS_USED == 1}]
    set tiles_in_use [get_tiles -of $sites_in_use]

    set idx 0
    foreach site $sites_in_use {
        if { $idx % 10 == 0 } {
            puts "[now]: Processing site $idx / [llength $sites_in_use]"
        }
        incr idx

        set site_type [get_property_debug SITE_TYPE $site]
        set tile [get_tiles -of $site]
        set tile_type [get_property_debug TYPE $tile]
        set key "$tile:$tile_type"

        if {$site_type == "SLICEL" || $site_type == "SLICEM" } {
            set clkinv [list 0 0]
            set srinv [list 0 0]
            set ffsync [list 0 0]
            set latch [list 0 0]
            set haveff [list 0 0]
            set srused [list 0 0 0 0]
            set ceused [list 0 0 0 0]
            set waused [list 0 0 0]

            foreach bel [get_bels -of $site] {
                set bel_name [get_name $bel]
                set cell [get_cells -quiet -of $bel]
                if { [llength $cell] == 0 } {
                    continue
                }

                set cell_type [get_property_debug REF_NAME $cell]

                if [string_contains $bel "LUT"] {
                    set lut_id [string map {"6" "" "5" ""} $bel_name]
                    if [string_startswith $cell_type "RAM"] {
                        dict lappend sitefeatures_by_tile $key "$lut_id.MODE.RAM"
                        if [string_contains $cell_type 32] {
                            dict lappend sitefeatures_by_tile $key "$lut_id.SIZE.SMALL"
                        } else {
                            dict lappend sitefeatures_by_tile $key "$lut_id.SIZE.LARGE"
                        }
                    } elseif [string_contains $cell_type "SRL"] {
                        dict lappend sitefeatures_by_tile $key "$lut_id.MODE.SRL"
                    } elseif { $site_type == "SLICEM" } {
                        dict lappend sitefeatures_by_tile $key "$lut_id.MODE.LUT"
                    }
                    if [string_contains $cell_type "SRL16"] {
                        dict lappend sitefeatures_by_tile $key "$lut_id.SIZE.SMALL"
                    }
                    if [string_contains $cell_type "SRLC32"] {
                        dict lappend sitefeatures_by_tile $key "$lut_id.SIZE.LARGE"
                    }
                    for {set i 6} {$i <= 8} {incr i} {
                        set pin [get_pins -quiet "$cell/WADR$i"]
                        if { [llength $pin] == 0 } {
                            continue
                        }
                        set bel_pin [get_bel_pins -quiet -of $pin]
                        if { [llength $bel_pin] != 0 } {
                            lset waused [expr $i-6] 1
                        }
                    }

                    if { [string_contains $cell_type "SRLC32"] } {
                        set pin [get_pins $cell/D]
                        set bel_pin [get_bel_pins -of $pin]
                        if { $lut_id != "HLUT" } {
                            dict lappend sitefeatures_by_tile $key "$lut_id.DI1.[get_name $bel_pin]"
                        }
                    } else {
                        set bel_pin [get_bel_pins -quiet -of $bel $bel/DI1]
                        if { [llength $bel_pin] > 0 } {
                            set pin [get_pins -quiet -of $bel_pin]
                            if { [llength $pin] > 0 && $lut_id != "HLUT" } {
                                dict lappend sitefeatures_by_tile $key "$lut_id.DI1.DI1"

                            }
                        }
                    }

                    if { [string_contains $cell_type "RAM"] || [string_contains $cell_type "SRL"] } {
                        set lclkinv [get_property_debug IS_CLK_INVERTED $cell]
                        if { [llength $lclkinv] > 0 } {
                            dict lappend sitefeatures_by_tile $key "LCLKINV.[string index $lclkinv end]"
                            dict lappend sitefeatures_by_tile $key "LCLKINV[string index $lclkinv end].[string index $lclkinv end]"
                        }
                    }
                }

                if [string_contains $bel_name "LUT"] {
                    set has_56lut 0
                    if { [string_contains $bel_name "6LUT"] } {
                        set has_56lut [get_has_lut5 [get_bels $site/[string map {"6" "5"} $bel_name]]]
                    }

                    if {!$has_56lut && [string_startswith $cell_type "LUT"]} {
                        # LUT init bits

                        set dump_lut 1
                        if {[string_contains $bel_name "6LUT"]} {
                            set bel_pin_str "$bel/A6"
                            set bel_pin [get_bel_pins $bel_pin_str]
                            if { [llength $bel_pin] == 0 } {
                                error "Invalid BEL pin $bel_pin_str"
                            }

                            set site_net [get_nets -quiet -of $bel_pin]
                            if { [llength $site_net] > 0 } {
                                set net_type [get_property_debug TYPE $site_net]
                                if { $net_type == "POWER"} {
                                    set dump_lut 0
                                }
                            }
                        }

                        if { $dump_lut == 1 } {
                            set lut_bits [get_lut_bits $cell]
                            foreach i $lut_bits {
                                dict lappend sitefeatures_by_tile $key "$lut_id.INIT\[$i\]"
                            }
                        }
                    }
                } elseif { [string_contains $bel_name "FF"] } {
                    if {$cell_type == "FDPE"} {
                        set is_latch 0
                        set is_sync 0
                        set srval 1
                        set clkpin "C"
                        set cepin "CE"
                        set srpin "PRE"
                    } elseif {$cell_type == "FDCE" } {
                        set is_latch 0
                        set is_sync 0
                        set srval 0
                        set clkpin "C"
                        set cepin "CE"
                        set srpin "CLR"
                    } elseif {$cell_type == "FDSE" } {
                        set is_latch 0
                        set is_sync 1
                        set srval 1
                        set clkpin "C"
                        set cepin "CE"
                        set srpin "S"
                    } elseif {$cell_type == "FDRE" } {
                        set is_latch 0
                        set is_sync 1
                        set srval 0
                        set clkpin "C"
                        set cepin "CE"
                        set srpin "R"
                    } elseif {$cell_type == "LDPE" } {
                        set is_latch 1
                        set is_sync 0
                        set srval 1
                        set clkpin "G"
                        set cepin "GE"
                        set srpin "PRE"
                    } elseif {$cell_type == "LDCE" } {
                        set is_latch 1
                        set is_sync 0
                        set srval 0
                        set clkpin "G"
                        set cepin "GE"
                        set srpin "CLR"
                    } else {
                        continue
                    }

                    if $is_latch {
                        set primtype "LATCH"
                    } else {
                        set primtype "FF"
                    }

                    set init_prop [get_property -quiet INIT $cell]
                    if {[llength $init_prop] > 0 } {
                        dict lappend sitefeatures_by_tile $key "$bel_name.INIT.V[string range $init_prop end end]"
                    }

                    dict lappend sitefeatures_by_tile $key "$bel_name.SRVAL.V$srval"

                    set half [string_contains "EFGH" [string index $bel_name 0]]
                    lset latch $half $is_latch
                    lset ffsync $half $is_sync
                    lset clkinv $half [string equal [get_property_debug "IS_${clkpin}_INVERTED" $cell] "1'b1"]
                    lset srinv $half [string equal [get_property_debug "IS_${srpin}_INVERTED" $cell] "1'b1"]
                    lset haveff $half 1

                    set two [string_endswith $bel_name "2"]
                    lset srused [expr $half * 2 + $two] [expr [llength [get_bel_pins -quiet -of [get_pins "$cell/$srpin"]]] > 0]
                    lset ceused [expr $half * 2 + $two] [expr [llength [get_bel_pins -quiet -of [get_pins "$cell/$cepin"]]] > 0]
                } elseif [string_contains $bel_name "CARRY8"] {
                    if { $cell_type != "CARRY8" } {
                        continue
                    }

                    set carry_type [get_property_debug CARRY_TYPE $cell]
                    if {[llength $carry_type] > 0} {
                        dict lappend sitefeatures_by_tile $key "CARRY8.CARRY_TYPE.$carry_type"
                    }

                    set pins [list CI]
                    if {$carry_type == "DUAL_CY4" } {
                        lappend pins CI_TOP
                    }
                    for {set i 0} {$i < 8} {incr i} {
                        lappend pins "DI\[$i\]"
                    }

                    set ex_di4_state [dict create]
                    foreach pin_str $pins {
                        set pin [get_pins "$cell/$pin_str"]
                        if {[llength $pin] != 1} {
                            error "Invalid pin $cell/$pin_str"
                        }

                        set phys [get_bel_pins -quiet -of $pin]
                        set net [get_nets -quiet -of $pin]
                        if {[llength $phys] > 0  && ($pin_str != "CI" || [get_name $phys] != "CIN")} {
                            if { [llength $net] > 0 } {
                                set pn [string map { "\[" "" "]" ""} $pin_str]
                                if { $pn != "DI4" || ($pn == "DI4" && $carry_type == "SINGLE_CY8") } {
                                    dict lappend sitefeatures_by_tile $key "CARRY8.$pn.[get_name $phys]"
                                }
                            }
                        } elseif {($pin_str == "CI" || $pin_str == "CI_TOP") && [llength $net] > 0} {
                            set net_type [get_property_debug TYPE $net]
                            if {$net_type == "POWER"} {
                                dict lappend sitefeatures_by_tile $key "CARRY8.$pin_str.V1"
                            } elseif {$net_type == "GROUND"} {
                                dict lappend sitefeatures_by_tile $key "CARRY8.$pin_str.V0"
                            }
                        }
                    }
                }
            }

            for {set i 0} {$i < 2} {incr i} {
                if { $i == 0 } {
                    set half "ABCD"
                } else {
                    set half "EFGH"
                }
                if {[lindex $haveff $i] == 0 } {
                    continue
                }

                if [lindex $latch $i] {
                    set primtype "LATCH"
                } else {
                    set primtype "FF"
                }
                dict lappend sitefeatures_by_tile $key "${half}FF.MODE.$primtype"

                set clkinv_set [lindex $clkinv $i]
                if { $primtype == "LATCH" } {
                    set clkinv_set [expr !$clkinv_set]
                }
                dict lappend sitefeatures_by_tile $key "${half}FF.CLKINV.V$clkinv_set"
                if { $primtype == "LATCH" } {
                    dict lappend sitefeatures_by_tile $key "${half}FF.SRINV.V[lindex $srinv $i]"
                }
                dict lappend sitefeatures_by_tile $key "${half}FF.$primtype.SRINV[lindex $srinv $i].V[lindex $srinv $i]"

                if { $primtype == "FF" } {
                    if [lindex $ffsync $i] {
                        dict lappend sitefeatures_by_tile $key "${half}FF.SYNC.SYNC"
                    } else {
                        dict lappend sitefeatures_by_tile $key "${half}FF.SYNC.ASYNC"
                    }
                }

                for {set j 0} {$j < 2} {incr j} {
                    if { $j == 1 } {
                        set two "2"
                    } else {
                        set two ""
                    }

                    if [lindex $srused [expr $i * 2 + $j]] {
                        dict lappend sitefeatures_by_tile $key "${half}FF$two.SRUSED.V1"
                    } else {
                        dict lappend sitefeatures_by_tile $key "${half}FF$two.SRUSED.V0"
                    }

                    if [lindex $ceused [expr $i * 2 + $j]] {
                        dict lappend sitefeatures_by_tile $key "${half}FF$two.CEUSED.V1"
                    } else {
                        dict lappend sitefeatures_by_tile $key "${half}FF$two.CEUSED.V0"
                    }
                }
            }

            foreach site_pip [get_site_pips -quiet -of $site -filter {IS_USED == 1}] {
                if { [string_contains $site_pip "INV"] } {
                    continue
                }

                set name [get_name $site_pip]
                set sidx [string first ":" $name]
                if { $sidx == -1 } {
                    error "Failed to parse site_pip $site_pip"
                }

                set routing_bel [string range $name 0 [expr $sidx-1]]

                set from_pin [get_property_debug FROM_PIN $site_pip]
                if { [string_startswith $name "OUTMUX"] && [string equal $from_pin "D6"] } {
                    set mux_site_pin [get_site_pins $site/[string index $routing_bel end]MUX]
                    if { [llength $mux_site_pin] == 0 } {
                        error "Failed to get MUX site pin for $site_pip"
                    }

                    set direct_site_pin [get_site_pins $site/[string index $routing_bel end]_O]
                    if { [llength $direct_site_pin] == 0 } {
                        error "Failed to get MUX site pin for $site_pip"
                    }

                    set mux_net [get_nets -quiet -of $mux_site_pin]
                    set direct_net [get_nets -quiet -of $mux_site_pin]

                    if { [llength $mux_net] == 0 || [llength $direct_net] == 0 } {
                        error "O6 through $site_pip does not go anywhere?"
                    }

                    if { $mux_net != $direct_net } {
                        error "O6 through $site_pip is strange?  Not the same net?"
                    }

                    set mux_node [get_nodes -of $mux_site_pin]
                    if { [llength $mux_node] == 0 } {
                        error "Missing mux node from $site_pip?"
                    }

                    set mux_net_from_node [get_nets -quiet -of $mux_node]
                    if { [llength $mux_net_from_node] == 0 } {
                        continue
                    }

                    if { $mux_net != $mux_net_from_node } {
                        error "Inconsistent net from $site_pip?"
                    }
                }
                dict lappend sitefeatures_by_tile $key "[string map {":" "."} $name]"
            }

            if { $site_type == "SLICEM" } {
                for {set i 0} {$i < 3} { incr i} {
                    dict lappend sitefeatures_by_tile $key "WA[expr $i+7]USED.[lindex $waused $i]"
                }
            }
        } elseif {$site_type == "BUFCE_LEAF"} {
            set name [site_index_in_tile $tile $site]
            foreach cell [get_cells -of $site] {
                set cell_type [get_property_debug REF_NAME $cell]
                if { $cell_type == "BUFCE_LEAF" } {
                    dict lappend sitefeatures_by_tile $key "$name.BUFCE_LEAF.IN_USE.V1"

                    set ce_type [get_property_debug CE_TYPE $cell]
                    if { [llength $ce_type] > 0 } {
                        dict lappend sitefeatures_by_tile $key "$name.BUFCE_LEAF.CE_TYPE.$ce_type"
                    }

                    foreach propname [list_property $cell] {
                        if {[string_startswith $propname "IS_"] && [string_endswith $propname "_INVERTED"]} {
                            set pinname [string range $propname 3 end-9]
                            set v [get_property_debug $propname $cell]
                            if { [llength $v] == 0 } {
                                continue
                            }

                            set v [remove_verilog_notation $v]
                            if { $pinname == "I" } {
                                if [is_sink_inverted [get_site_pins "$site/CLK_IN"]] {
                                    if { $v == "1" } {
                                        set v 0
                                    } else {
                                        set v 1
                                    }
                                }
                            }
                            dict lappend sitefeatures_by_tile $key "$name.BUFCE_LEAF.${pinname}INV.V$v"
                        }
                    }
                }
            }
        }
    }

    return $sitefeatures_by_tile
}

proc output_features_to_file {output_file tiles pips_by_tile sitefeatures_by_tile} {
    puts "[now] Outputing features to file $output_file"
    set fp [open $output_file "w"]

    set keys []
    foreach tile $tiles {
        set tt [get_property_debug TYPE $tile]
        set key "$tile:$tt"
        lappend keys $key
    }

    foreach key [lsort $keys] {
        set have_pips [dict exists $pips_by_tile $key]
        set have_sitefeatures [dict exists $sitefeatures_by_tile $key]

        if {!$have_pips && !$have_sitefeatures} {
            continue
        }

        puts $fp ".tile $key"
        if {$have_pips} {
            foreach feature [lsort [dict get $pips_by_tile $key]] {
                puts $fp $feature
            }
        }

        if {$have_sitefeatures} {
            foreach feature [lsort [dict get $sitefeatures_by_tile $key]] {
                puts $fp $feature
            }
        }
    }

    close $fp
}

# Dumps features to specified file
proc dump_all_features_to_file {output_file} {
    set start_time [clock seconds]
    puts "[now] Gather features"
    set filter_bram 1
    set filter_int 0
    set pips_by_tile [dump_pips $filter_bram $filter_int]
    set sitefeatures_by_tile [dump_features]

    set tiles [get_tiles -quiet -regexp -filter {TYPE =~ CLE[LM]_[LR]}]
    lappend tiles [get_tiles -quiet -regexp -filter {TYPE == CLEM}]
    lappend tiles [get_tiles -quiet -filter {TYPE == INT}]
    lappend tiles [get_tiles -quiet -filter {TYPE == INT_INTF_L_IO}]

    output_features_to_file $output_file $tiles $pips_by_tile $sitefeatures_by_tile

    set end_time [clock seconds]
    puts "[now] Done, took [expr $end_time - $start_time] seconds!"
}


proc has_delay {route} {
    foreach elem $route {
        if { [llength $elem] == 1 } {
            foreach e $elem {
                if { [string_startswith $e "NoTile/Delay_Arc_Index="] } {
                    return 1
                }
            }
        } else {
            set ret [has_delay $elem]
            if { $ret } {
                return $ret
            }
        }
    }

    return 0
}

proc dump_clocking_wire_features {} {
    set pips_by_tile [dict create]
    set sitefeatures_by_tile [dict create]

    set all_nets [get_nets -hierarchical]
    set tiles_in_use [dict create]

    set nets_done [dict create]
    set idx 0
    foreach net $all_nets {
        if { $idx % 100 == 0 } {
            puts "[now]: Processing net $idx / [llength $all_nets]"
        }
        incr idx

        set net [get_parent_net $net]
        if { [dict exists $nets_done $net] == 1 } {
            continue
        }

        dict set nets_done $net 1

        # Some clock wires have USED features, similiar to the 7-series HROW
        # USED bits.
        set wire_done [dict create]
        foreach wire [get_wires -quiet -of $net -filter "TILE_NAME =~ RCLK_*"] {
            # Skip dups
            if { [dict exists $wire_done $wire] } {
                continue
            }
            dict set wire_done $wire 1

            set tile [get_tiles -of $wire]
            # Wire Tile Type
            set wtt [get_property_debug TYPE $tile]
            set key "$tile:$wtt"
            dict set tiles_in_use $tile 1

            set wire_name [get_name $wire]

            if {$wtt == "RCLK_BRAM_INTF_L" || $wtt == "RCLK_BRAM_INTF_TD_L" || $wtt == "RCLK_BRAM_INTF_TD_R" ||
                $wtt == "RCLK_CLEL_L_L" || $wtt == "RCLK_CLEL_L" || $wtt == "RCLK_CLEL_L_R" ||
                $wtt == "RCLK_CLEM_CLKBUF_L" || $wtt == "RCLK_CLEM_L" || $wtt == "RCLK_DSP_INTF_L" ||
                $wtt == "RCLK_DSP_INTF_R" || $wtt == "RCLK_RCLK_URAM_INTF_L_FT" ||
                $wtt == "RCLK_CLEM_R" || $wtt == "RCLK_CLEL_R" || $wtt == "GTH_QUAD_RIGHT"} {
                if {[string_startswith $wire_name "CLK_TEST_BUF_SITE_"] || [string_startswith $wire_name "CLK_HROUTE_CORE_OPT"] ||
                    [string_startswith $wire_name "CLK_VDISTR_BOT"] || [string_startswith $wire_name "CLK_VDISTR_TOP"] ||
                    [string_startswith $wire_name "CLK_VROUTE_BOT"] || [string_startswith $wire_name "CLK_VROUTE_TOP"]} {
                    dict lappend pips_by_tile $key "WIRE.$wire_name.USED.V1"
                }
            }
            if {$wtt == "RCLK_DSP_INTF_CLKBUF_L" || $wtt == "RCLK_CLEM_CLKBUF_L" ||
                $wtt == "RCLK_AMS_CFGIO" || $wtt == "RCLK_INTF_LEFT_TERM_ALTO" ||
                $wtt == "RCLK_XIPHY_OUTER_RIGHT" ||
                $wtt == "RCLK_RCLK_XIPHY_INNER_FT" || $wtt == "RCLK_HDIO"  || $wtt == "GTH_QUAD_RIGHT"} {
                if {[string_startswith $wire_name "CLK_HROUTE"] || [string_startswith $wire_name "CLK_HDISTR"]} {
                    dict lappend pips_by_tile $key "WIRE.$wire_name.USED.V1"
                }
            }
        }

        set wire_done [dict create]
        foreach wire [get_wires -quiet -of $net -filter "TILE_NAME =~ CMT_*"] {
            # Skip dups
            if { [dict exists $wire_done $wire] } {
                continue
            }
            dict set wire_done $wire 1

            set tile [get_tiles -of $wire]
            dict set tiles_in_use $tile 1

            # Wire Tile Type
            set wtt [get_property_debug TYPE $tile]

            set wire_name [get_name $wire]

            if {[string_startswith $wire_name "CLK_HROUTE_"] || [string_startswith $wire_name "CLK_HDISTR_"] || [string_startswith $wire_name "CLK_VDISTR_"] ||
                [string_startswith $wire_name "CLK_TEST_BUF_SITE_"]} {
                set key "$tile:$wtt"
                dict lappend pips_by_tile $key "WIRE.$wire_name.USED.V1";
            }
        }

        set route [get_property_debug ROUTE $net]
        set route_has_delay [has_delay $route]

        foreach pip [get_pips -quiet -of $net -regexp -filter {TILE =~ RCLK_INT_[LR].* }] {
            set tile [get_tiles -of $pip]

            # Pip Tile Type
            set ptt [get_property_debug TYPE $tile]

            if {$ptt == "RCLK_INT_L" || $ptt == "RCLK_INT_R"} {
                set wire_name [get_name [get_wires -of $pip -downhill]]
                if {[string_startswith $wire_name "CLK_LEAF_SITES_"] && [string_endswith $wire_name "_CLK_LEAF"]} {
                    set key "$tile:$ptt"
                    dict lappend pips_by_tile $key "WIRE.$wire_name.DRIVEN.V1"

                    set wire [get_wires -of $pip -uphill]
                    if {[string_endswith $wire "_CLK_IN"] && [get_property_debug IS_PSEUDO $pip]} {
                        set node [get_nodes -of $pip -uphill]
                        set site [get_sites -of [get_site_pins -of $node]]
                        set site_name [site_index_in_tile $tile $site]
                        dict lappend sitefeatures_by_tile $key "$site_name.BUFCE_LEAF.IN_USE.V1"
                        dict set tiles_in_use $tile 1

                        if { [string_contains $net "leaf_delay_"] } {
                            set count [count_clk_leafs $net]
                            if { $count == 1 } {
                                set value [lindex [split $net "_"] end]
                                dict lappend sitefeatures_by_tile $key "$site_name.BUFCE_LEAF.DELAY_TAP.V$value"
                            }
                            if {[is_node_inverted $net [get_nodes -of $pip -uphill]] } {
                                dict lappend sitefeatures_by_tile $key "$site_name.BUFCE_LEAF.IINV.V1"
                            }
                        } elseif { $route_has_delay == 0 } {
                            dict lappend sitefeatures_by_tile $key "$site_name.BUFCE_LEAF.DELAY_TAP.V0"
                        }
                    }
                }
            }
        }
    }

    foreach tile [dict keys $tiles_in_use] {
        set wtt [get_property_debug TYPE $tile]

        if {$wtt == "RCLK_BRAM_INTF_L" || $wtt == "RCLK_BRAM_INTF_TD_L" || $wtt == "RCLK_BRAM_INTF_TD_R" ||
            $wtt == "RCLK_CLEL_L_L" || $wtt == "RCLK_CLEL_L" || $wtt == "RCLK_CLEL_L_R" ||
            $wtt == "RCLK_CLEM_CLKBUF_L" || $wtt == "RCLK_CLEM_L" || $wtt == "RCLK_DSP_INTF_L" ||
            $wtt == "RCLK_DSP_INTF_R" || $wtt == "RCLK_RCLK_URAM_INTF_L_FT" ||
            $wtt == "RCLK_CLEM_R" || $wtt == "RCLK_CLEL_R" || $wtt == "GTH_QUAD_RIGHT"} {
            foreach wire [get_wires -of $tile] {
                set net [get_nets -of $wire -quiet]
                if { [llength $net] > 0 } {
                    continue
                }

                set wire_name [get_name $wire]
                if {[string_startswith $wire_name "CLK_TEST_BUF_SITE_"] || [string_startswith $wire_name "CLK_HROUTE_CORE_OPT"] ||
                    [string_startswith $wire_name "CLK_VDISTR_BOT"] || [string_startswith $wire_name "CLK_VDISTR_TOP"] ||
                    [string_startswith $wire_name "CLK_VROUTE_BOT"] || [string_startswith $wire_name "CLK_VROUTE_TOP"]} {
                    set key "$tile:$wtt"
                    dict lappend pips_by_tile $key "WIRE.$wire_name.USED.V0"
                }
            }
        }

        if {$wtt == "RCLK_DSP_INTF_CLKBUF_L" || $wtt == "RCLK_CLEM_CLKBUF_L" ||
            $wtt == "RCLK_AMS_CFGIO" || $wtt == "RCLK_INTF_LEFT_TERM_ALTO" ||
            $wtt == "RCLK_XIPHY_OUTER_RIGHT" ||
            $wtt == "RCLK_RCLK_XIPHY_INNER_FT" || $wtt == "RCLK_HDIO"  || $wtt == "GTH_QUAD_RIGHT"} {
            foreach wire [get_wires -of $tile] {
                set net [get_nets -of $wire -quiet]
                if { [llength $net] > 0 } {
                    continue
                }

                set wire_name [get_name $wire]
                if {[string_startswith $wire_name "CLK_HROUTE"] || [string_startswith $wire_name "CLK_HDISTR"]} {
                    set key "$tile:$wtt"
                    dict lappend pips_by_tile $key "WIRE.$wire_name.USED.V0"
                }
            }
        }

        if {$wtt == "CMT_L" || $wtt == "CMT_RIGHT" } {
            foreach wire [get_wires -of $tile] {
                set net [get_nets -of $wire -quiet]
                if { [llength $net] > 0 } {
                    continue
                }

                set wire_name [get_name $wire]
                if {[string_startswith $wire_name "CLK_HROUTE_"] || [string_startswith $wire_name "CLK_HDISTR_"] || [string_startswith $wire_name "CLK_VDISTR_"] ||
                    [string_startswith $wire_name "CLK_TEST_BUF_SITE_"]} {
                    set key "$tile:$wtt"
                    dict lappend pips_by_tile $key "WIRE.$wire_name.USED.V0"
                }
            }
        }
    }

    return [list $pips_by_tile $sitefeatures_by_tile $tiles_in_use]
}

proc dump_clocking_pips {} {
    set filter_bram 1
    set filter_int 1
    return [dump_pips $filter_bram $filter_int]
}

proc dump_clocking_features {tiles_in_use} {
    set sitefeatures_by_tile [dict create]

    puts "[now]: Getting sites in use"
    set sites_in_use [get_sites -filter {IS_USED == 1}]
    foreach tile [get_tiles -of $sites_in_use] {
        dict set tiles_in_use $tile 1
    }
    set tiles_in_use [dict keys $tiles_in_use]

    set idx 0
    foreach site $sites_in_use {
        if { $idx % 10 == 0 } {
            puts "[now]: Processing site $idx / [llength $sites_in_use]"
        }
        incr idx

        set site_type [get_property_debug SITE_TYPE $site]
        set tile [get_tiles -of $site]
        set tile_type [get_property_debug TYPE $tile]
        set key "$tile:$tile_type"
        set name [site_index_in_tile $tile $site]

        if {$site_type == "BUFCE_LEAF"} {
            foreach cell [get_cells -of $site] {
                set cell_type [get_property_debug REF_NAME $cell]
                if {$cell_type == "BUFCE_LEAF"} {
                    dict lappend sitefeatures_by_tile $key "$name.BUFCE_LEAF.IN_USE.V1"
                    set ce_type [get_property_debug CE_TYPE $cell]
                    if { [llength $ce_type] > 0 } {
                        dict lappend sitefeatures_by_tile $key "$name.BUFCE_LEAF.CE_TYPE.$ce_type"
                    }

                    foreach propname [list_property $cell] {
                        if {[string_startswith $propname "IS_"] && [string_endswith $propname "_INVERTED"]} {
                            set pinname [string range $propname 3 end-9]
                            set v [get_property_debug $propname $cell]
                            if { [llength $v] == 0 } {
                                continue
                            }

                            set v [remove_verilog_notation $v]

                            if { $pinname == "I" } {
                                if [is_sink_inverted [get_site_pins "$site/CLK_IN"]] {
                                    if { $v == "1" } {
                                        set v 0
                                    } else {
                                        set v 1
                                    }
                                }
                            }
                            dict lappend sitefeatures_by_tile $key "$name.BUFCE_LEAF.${pinname}INV.V$v"
                        }
                    }
                }
            }
        } elseif {[string_startswith $site_type "BUFGCE"]} {
            foreach cell [get_cells -of $site] {
                set cell_type [get_property_debug REF_NAME $cell]
                if {[string_startswith $cell_type "BUFGCE"]} {
                    dict lappend sitefeatures_by_tile $key "$name.IN_USE.V1"
                    foreach propname [list_property $cell] {
                        set v [get_property_debug $propname $cell]
                        if { [llength $v] == 0 } {
                            continue
                        }
                        set v [remove_verilog_notation $v]

                        if {[string_startswith $propname "IS_"] && [string_endswith $propname "_INVERTED"]} {
                            set pinname [string range $propname 3 end-9]

                            if { $pinname == "I" } {
                                set pin [get_pins -quiet $cell/$pinname]
                                if {[llength $pin] == 0} {
                                    continue
                                }
                                set net [get_nets -quiet -of $pin]
                                if {[llength $net] == 0} {
                                    continue
                                }
                                if [is_static_net $net] {
                                    continue
                                }

                                if [is_sink_inverted [get_site_pins "$site/CLK_IN"]] {
                                    if { $v == "1" } {
                                        set v 0
                                    } else {
                                        set v 1
                                    }
                                }
                            }
                            dict lappend sitefeatures_by_tile $key "$name.$site_type.${pinname}INV.V$v"
                        } elseif {($site_type == "BUFGCE" && $propname == "CE_TYPE") || $propname == "BUFGCE_DIVIDE"} {
                            dict lappend sitefeatures_by_tile $key "$name.$site_type.${propname}.$v"
                        }
                    }
                }
            }
        } elseif {$site_type == "BUFGCTRL"} {
            foreach cell [get_cells -of $site] {
                set cell_type [get_property_debug REF_NAME $cell]
                if {[string_startswith $cell_type "BUFGCTRL"]} {
                    dict lappend sitefeatures_by_tile $key "$name.IN_USE.V1"
                    foreach propname [list_property $cell] {
                        set v [get_property_debug $propname $cell]
                        if { [llength $v] == 0 } {
                            continue
                        }

                        set v [remove_verilog_notation $v]
                        if {[string_startswith $propname "IS_"] && [string_endswith $propname "_INVERTED"]} {
                            set pinname [string range $propname 3 end-9]
                            if { $pinname == "I0" || $pinname == "I1" } {
                                set pin [get_pins -quiet $cell/$pinname]
                                if {[llength $pin] == 0} {
                                    continue
                                }
                                set net [get_nets -quiet -of $pin]
                                if {[llength $net] == 0} {
                                    continue
                                }
                                if [is_static_net $net] {
                                    continue
                                }

                                if [is_sink_inverted [get_site_pins "$site/CLK_$pinname"]] {
                                    if { $v == "1" } {
                                        set v 0
                                    } else {
                                        set v 1
                                    }
                                }
                            }
                            dict lappend sitefeatures_by_tile $key "$name.$site_type.${pinname}INV.V$v"
                        } elseif {$propname == "INIT_OUT" || [string_startswith $propname "PRESELECT_"]} {
                            dict lappend sitefeatures_by_tile $key "$name.$site_type.${propname}.V$v"
                        }
                    }
                }
            }
        } elseif {$site_type == "MMCM"} {
            set name [site_index_in_tile $tile $site]
            set cell [get_cells -of $site]
            if { [llength $cell] == 0 } {
                continue
            }
            dict lappend sitefeatures_by_tile $key "$name.IN_USE.V1"

            set all_props [list_property $cell]
            foreach propname $all_props {
                set v [get_property_debug $propname $cell]
                if { [llength $v] == 0 } {
                    continue
                }

                set v [remove_verilog_notation $v]
                if {[string_startswith $propname "IS_"] && [string_endswith $propname "_INVERTED"]} {
                    set pinname [string range $propname 3 end-9]
                    if { $pinname == "CLKIN1" || $pinname == "CLKIN2" || $pinname == "CLKFBIN" } {
                        continue
                    }
                    set pin [get_pins $cell/$pinname]
                    set site_pin [get_site_pins -quiet -of $pin]
                    if { [llength $site_pin] == 0 } {
                        continue
                    }

                    set net [get_nets -quiet -of $site_pin]
                    if { [llength $net] == 0 } {
                        continue
                    }

                    dict lappend sitefeatures_by_tile "$name.$site_type.${pinname}INV.V$v"
                } elseif { $propname == "COMPENSATION" } {
                    dict lappend sitefeatures_by_tile "$name.$site_type.$propname.$v"
                }
            }
        } elseif {$site_type == "PLL"} {
            set name [site_index_in_tile $tile $site]
            set cell [get_cells -of $site]
            if { [llength $cell] == 0 } {
                continue
            }
            dict lappend sitefeatures_by_tile $key "$name.IN_USE.V1"

            set all_props [list_property $cell]
            foreach propname $all_props {
                set v [get_property_debug $propname $cell]
                if { [llength $v] == 0 } {
                    continue
                }

                set v [remove_verilog_notation $v]
                if {[string_startswith $propname "IS_"] && [string_endswith $propname "_INVERTED"]} {
                    set pinname [string range $propname 3 end-9]
                    if { $pinname == "CLKIN" || $pinname == "CLKFBIN" } {
                        continue
                    }

                    set pin [get_pins $cell/$pinname]
                    set site_pin [get_site_pins -quiet -of $pin]
                    if { [llength $site_pin] == 0 } {
                        continue
                    }

                    set net [get_nets -quiet -of $site_pin]
                    if { [llength $net] == 0 } {
                        continue
                    }

                    dict lappend sitefeatures_by_tile "$name.$site_type.${pinname}INV.V$v"
                } elseif { $propname == "COMPENSATION" } {
                    dict lappend sitefeatures_by_tile "$name.$site_type.$propname.$v"
                }
            }
        }
    }

    set iotiles [get_tiles -of [get_sites -of [get_ports]]]
    foreach tile $iotiles {
        set tile_type [get_property_debug TYPE $tile]
        set dci_used 0
        foreach port [get_ports -of [get_sites -of $tile]] {
            set site [get_sites -of $port]

            set cell [get_cells -of $site -filter {TYPE == "I/O"}]
            if {[llength $cell] == 0} {
                continue
            }

            if {[llength $cell] != 1} {
                error "Unexpected port setup for port $port"
            }

            set iostd [get_property_debug IOSTANDARD $cell]
            if { [string_contains $iostd "POD12_DCI"] } {
                set dci_used 1
            }
        }
        if { $dci_used } {
            set key "$tile:$tile_type"
            dict lappend sitefeatures_by_tile $key "POD12_DCI_USED"
        }
    }

    foreach tile $tiles_in_use {
        foreach site [get_sites -of $tile -filter "IS_USED == 0"] {
            # Detect sites that in use via pseudo pips, which do not mark the
            # site as in use.
            set pseudo_pip_in_use 0
            foreach pip [get_pips -of $site -filter "IS_PSEUDO == 1"] {
                set pip_net [get_nets -quiet -of $pip]
                if { [llength $pip_net] > 0 } {
                    set pseudo_pip_in_use 1
                    break
                }
            }

            if { $pseudo_pip_in_use } {
                continue
            }

            set site_type [get_property_debug SITE_TYPE $site]
            set name [site_index_in_tile $tile $site]
            set tile [get_tiles -of $site]
            set tile_type [get_property_debug TYPE $tile]
            set key "$tile:$tile_type"

            if {$site_type == "BUFCE_LEAF"} {
                dict lappend sitefeatures_by_tile $key "$name.BUFCE_LEAF.IN_USE.V0"
                set driven_wire [struct::set union [get_wires -of [get_pips -of $site] -downhill] []]
                if { [llength $driven_wire] != 1 } {
                    error "Failed to find wire from site $site"
                }

                set wire_name [get_name [get_wires $driven_wire]]
                dict lappend sitefeatures_by_tile $key "WIRE.$wire_name.DRIVEN.V0"
            } elseif {[string_startswith $site_type "BUFGCE"]} {
                dict lappend sitefeatures_by_tile $key "$name.IN_USE.V0"
            } elseif {$site_type == "BUFGCTRL"} {
                dict lappend sitefeatures_by_tile $key "$name.IN_USE.V0"
            } elseif {$site_type == "MMCM"} {
                dict lappend sitefeatures_by_tile $key "$name.IN_USE.V0"
            } elseif {$site_type == "PLL"} {
                dict lappend sitefeatures_by_tile $key "$name.IN_USE.V0"
            }
        }
    }

    return $sitefeatures_by_tile
}

proc dump_clock_features_to_file {output_file} {
    set start_time [clock seconds]
    puts "[now] Gather clock features"
    set ret [dump_clocking_wire_features]
    set pips_by_tile [lindex $ret 0]
    set sitefeatures_by_tile [lindex $ret 1]
    set tiles_in_use [lindex $ret 2]

    set pips_by_tile [dict_merge_lists $pips_by_tile [dump_clocking_pips]]
    set sitefeatures_by_tile [dict_merge_lists $sitefeatures_by_tile [dump_clocking_features $tiles_in_use]]

    set tiles [get_tiles -quiet -regexp -filter {TYPE =~ RCLK_INT_[LR]}]
    lappend tiles [get_tiles -quiet -regexp -filter {TYPE =~ RCLK_CLEM_[LR]}]
    lappend tiles [get_tiles -quiet -regexp -filter {TYPE =~ RCLK_CLEL_[LR]}]
    lappend tiles [get_tiles -quiet -regexp -filter {TYPE =~ RCLK_CLEL_L_[LR]}]
    lappend tiles [get_tiles -quiet -regexp -filter {TYPE =~ RCLK_BRAM_[LR]}]
    lappend tiles [get_tiles -quiet -regexp -filter {TYPE =~ RCLK_BRAM_INTF_TD_[LR]}]
    lappend tiles [get_tiles -quiet -filter {TYPE == RCLK_CLEM_CLKBUF_L}]
    lappend tiles [get_tiles -quiet -regexp -filter {TYPE =~ RCLK_DSP_INTF_[LR]}]
    lappend tiles [get_tiles -quiet -filter {TYPE == RCLK_BRAM_INTF_L}]
    lappend tiles [get_tiles -quiet -filter {TYPE == RCLK_INTF_LEFT_TERM_ALTO}]
    lappend tiles [get_tiles -quiet -filter {TYPE == RCLK_DSP_INTF_CLKBUF_L}]
    lappend tiles [get_tiles -quiet -filter {TYPE == RCLK_AMS_CFGIO}]
    lappend tiles [get_tiles -quiet -filter {TYPE == RCLK_HDIO}]
    lappend tiles [get_tiles -quiet -regexp -filter {TYPE == RCLK_HPIO_[LR]}]
    lappend tiles [get_tiles -quiet -filter {TYPE == CMT_L}]
    lappend tiles [get_tiles -quiet -filter {TYPE == CMT_RIGHT}]
    lappend tiles [get_tiles -quiet -filter {TYPE == RCLK_XIPHY_OUTER_RIGHT}]
    lappend tiles [get_tiles -quiet -filter {TYPE == RCLK_RCLK_XIPHY_INNER_FT}]
    lappend tiles [get_tiles -quiet -filter {TYPE == RCLK_RCLK_INTF_XIPHY_LEFT_L_FT}]
    lappend tiles [get_tiles -quiet -filter {TYPE == RCLK_RCLK_URAM_INTF_L_FT}]
    lappend tiles [get_tiles -quiet -filter {TYPE == GTH_QUAD_RIGHT}]

    output_features_to_file $output_file $tiles $pips_by_tile $sitefeatures_by_tile

    set end_time [clock seconds]
    puts "[now] Done, took [expr $end_time - $start_time] seconds!"
}

proc dump_bram_dsp_features {} {
    set sitefeatures_by_tile [dict create]

    set sites_in_use [get_sites -filter {IS_USED == 1}]
    set idx 0
    foreach site $sites_in_use {
        if { $idx % 10 == 0 } {
            puts "[now]: Processing site $idx / [llength $sites_in_use]"
        }
        incr idx

        set site_type [get_property_debug SITE_TYPE $site]
        set tile [get_tiles -of $site]
        set tile_type [get_property_debug TYPE $tile]
        set key "$tile:$tile_type"

        if {$site_type == "RAMB181" || $site_type == "RAMBFIFO18" || $site_type == "RAMBFIFO36"} {
            foreach bel [get_bels -of $site] {
                set bel_name [get_name $bel]
                set cell [get_cells -quiet -of $bel]
                if { [llength $cell] == 0 } {
                    continue
                }

                set cell_type [get_property_debug REF_NAME $cell]
                if { [llength $cell_type] == 0 } {
                    continue
                }

                if {$site_type == "RAMBFIFO36" && $cell_type != "RAMB36E2"} {
                    continue
                }

                if {($site_type == "RAMB180" || $site_type == "RAM181") && $cell_type != "RAMB18E2" } {
                    continue
                }

                if { $site_type == "RAMBFIFO36" } {
                    set prim_width 36
                } else {
                    set prim_width 18
                }

                dict lappend sitefeatures_by_tile $key "BRAM.IN_USE.V1"
                dict lappend sitefeatures_by_tile $key "$bel_name.IN_USE.V1"

                set have_ecc 0
                set is_sdp 0

                if {[get_property_debug READ_WIDTH_A $cell] > $prim_width} {
                    set is_sdp 1
                }
                if {[get_property_debug WRITE_WIDTH_B $cell] > $prim_width} {
                    set is_sdp 1
                }
                set enum_props [list \
                        "CLOCK_DOMAINS" \
                        "DOA_REG" "DOB_REG" \
                        "READ_WIDTH_A" "READ_WIDTH_B" "WRITE_WIDTH_A" "WRITE_WIDTH_B" \
                        "WRITE_MODE_A" "WRITE_MODE_B" \
                        "ENADDRENA" "ENADDRENB" "RDADDRCHANGEA" "RDADDRCHANGEB" \
                        "RSTREG_PRIORITY_A" "RSTREG_PRIORITY_B" \
                        "SLEEP_ASYNC" "EN_ECC_PIPE" "EN_ECC_READ" "EN_ECC_WRITE" \
                        "CASCADE_ORDER_A" "CASCADE_ORDER_B"]
                foreach propname $enum_props {
                    set v [get_property_debug $propname $cell]
                    if { [llength $v] == 0 } {
                        continue
                    }
                    set v [remove_verilog_notation $v]
                    if {[string_startswith $propname "RSTREG_"] && $is_sdp} {
                        continue
                    }

                    if { $v == 0 || $v == 1 } {
                        set v "V$v"
                    }
                    dict lappend sitefeatures_by_tile $key "$bel_name.$propname.$v"
                    if {[string_contains $propname "EN_ECC"] && $v == "TRUE" } {
                        set have_ecc 1
                    }
                }

                set all_props [list_property $cell]
                foreach propname $all_props {
                    if {[string_startswith $propname "IS_"] && [string_endswith $propname "_INVERTED"]} {
                        set pinname [string range $propname 3 end-9]
                        set v [get_property_debug $propname $cell]
                        if { [llength $v] == 0 } {
                            continue
                        }

                        set v [remove_verilog_notation $v]
                        dict lappend sitefeatures_by_tile $key "$bel_name.${pinname}INV.V$v"
                    }
                }

                set bram_init_len 64
                set bram_initp_len 8
                if { $site_type == "RAMBFIFO36" } {
                    set bram_init_len 128
                    set bram_initp_len 16
                }
                set word_props ""
                for {set i 0} {$i < $bram_init_len} {incr i} {
                    lappend word_props [format "INIT_%02X" $i]
                }
                for {set i 0} {$i < $bram_initp_len} {incr i} {
                    lappend word_props [format "INITP_%02X" $i]
                }
                foreach propname $word_props {
                    set value [get_property_debug $propname $cell]
                    if {[llength $value] == 0} {
                        continue
                    }
                    for {set w 0} {$w < 8} {incr w} {
                        set word "32'h[string range $value end-[expr $w * 8 + 7] end-[expr $w * 8]]"
                        set ret [convert_verilog_constant $word]
                        set lval [lindex $ret 1]

                        for {set i 0} {$i < 32} {incr i} {
                            if {($lval & (1 << $i)) != 0} {
                                set index [expr $i + $w * 32]
                                dict lappend sitefeatures_by_tile $key "$bel_name.$propname\[$index\]"
                            }
                        }
                    }
                }

                if { $site_type != "RAMBFIFO36" } {
                    set word_props [list INIT_A INIT_B SRVAL_A SRVAL_B]
                    foreach propname $word_props {
                        set width [get_property_debug READ_WIDTH_[string index $propname end] $cell]
                        if {[llength $width] == 0 || $width != $prim_width || $have_ecc} {
                            continue
                        }

                        set value [get_property_debug $propname $cell]
                        if {[llength $value] == 0} {
                            continue
                        }

                        set ret [convert_verilog_constant $value]
                        set lval [lindex $ret 1]

                        for {set i 0} {$i < $prim_width} {incr i} {
                            if {($lval & (1 << $i)) != 0} {
                                dict lappend sitefeatures_by_tile $key "$bel_name.$propname\[$i\]"
                            }
                        }
                    }
                }

                foreach bel_pin [get_bel_pins -of $bel] {

                    set bel_pin_name [get_name $bel_pin]
                    if [string_startswith $bel_pin_name "DOUT"] {
                        foreach net [get_nets -quiet -of $bel_pin] {
                            dict lappend sitefeatures_by_tile $key "$bel_name.$bel_pin_name.USED"
                        }
                    }
                }
            }
        } elseif {$site_type == "DSP48E2"} {
            foreach cell [get_cells -of $site] {
                set sidx [string last "/" $cell]
                if {$sidx == -1} {
                    continue
                }

                # roi/INST_DSP48E2_X1Y58/DSP_ALU_INST -> roi/INST_DSP48E2_X1Y58
                set cell_str [string range $cell 0 $sidx-1]
                set cell [get_cells -quiet $cell_str]
                if {[llength $cell] == 0} {
                    continue
                }

                if {[get_property_debug REF_NAME $cell] != "DSP48E2"} {
                    continue
                }

                set name [site_index_in_tile $tile $site]
                dict lappend sitefeatures_by_tile $key "DSP.IN_USE.V1"
                dict lappend sitefeatures_by_tile $key "$name.IN_USE.V1"

                set have_patdet 0
                if {[get_property_debug USE_PATTERN_DETECT $cell] == "PATDET"} {
                    set have_patdet 1
                }

                set have_xor 0
                if {[get_property_debug USE_WIDEXOR $cell] == "TRUE"} {
                    set have_xor 1
                }

                set enum_props [list "ADREG" "ALUMODEREG" "AMULTSEL" "AREG" "AUTORESET_PATDET" "AUTORESET_PRIORITY" \
                        "BMULTSEL" "BREG" "CARRYINREG" "CARRYINSELREG" "CREG" "DREG" "INMODEREG" "MREG" "OPMODEREG" \
                        "PREADDINSEL" "PREG" "SEL_MASK" "SEL_PATTERN" "USE_PATTERN_DETECT" "USE_SIMD" "USE_WIDEXOR" "XORSIMD"]
                foreach propname $enum_props {
                    if {!$have_patdet && ($propname == "AUTORESET_PATDET" || $propname == "AUTORESET_PRIORITY" || $propname == "SEL_MASK" || $propname == "SEL_PATTERN")} {
                        continue
                    }
                    if {!$have_xor && $propname == "XORSIMD"} {
                        continue
                    }

                    set v [get_property_debug $propname $cell]
                    if {[llength $v] == 0 } {
                        continue
                    }

                    set v [remove_verilog_notation $v]
                    if { $v == 0 || $v == 1 } {
                        set v "V$v"
                    }
                    dict lappend sitefeatures_by_tile $key "$name.$propname.$v"
                }

                set all_props [list_property $cell]
                foreach propname $all_props {
                    if {[string_startswith $propname "IS_"] && [string_endswith $propname "_INVERTED"]} {
                        set pinname [string range $propname 3 end-9]
                        set width 1
                        if {$pinname == "ALUMODE"} {
                            set width 4
                        } elseif {$pinname == "INMODE"} {
                            set width 5
                        } elseif {$pinname == "OPMODE"} {
                            set width 9
                        }

                        if [string_contains $pinname "RST"] {
                            set pin [get_pins $cell/$pinname]
                            if {[llength $pin] == 0} {
                                error "Failed to get pin $cell/$pinname"
                            }
                            set net [get_nets -quiet -of $pin]
                            if {[llength $net] == 0} {
                                continue
                            }

                            set net_type [get_property_debug TYPE $net]
                            if { $net_type == "POWER"} {
                                continue
                            }
                            if { $net_type == "GROUND"} {
                                continue
                            }
                        }

                        set v [get_property_debug $propname $cell]
                        if { [llength $v] == 0 } {
                            continue
                        }

                        set ret [convert_verilog_constant $v]
                        set lval [lindex $ret 1]
                        if {$width == 1} {
                            dict lappend sitefeatures_by_tile $key "$name.${pinname}INV.V$v"
                        } else {
                            for {set i 0} {$i < $width} {incr i} {
                                if {($lval & (1 << $i)) != 0} {
                                    set value 1
                                } else {
                                    set value 0
                                }

                                dict lappend sitefeatures_by_tile $key "$name.${pinname}INV.\[$i\].$value"
                            }
                        }
                    }
                }

                set word_props [list "MASK" "PATTERN" "RND"]
                foreach propname $word_props {
                    set v [get_property_debug $propname $cell]
                    if { [llength $v] > 0 } {
                        set ret [convert_verilog_constant $v]
                        set lval [lindex $ret 1]
                        for {set i 0} {$i < 48} {incr i} {
                            if {($lval & (1 << $i)) != 0 || ($propname == "MASK" && !$have_patdet)} {
                                dict lappend sitefeatures_by_tile $key "$name.$propname\[$i\]"
                            }
                        }
                    }
                }

                foreach pin [get_pins -of $cell -filter {DIRECTION == OUT}] {
                    set net [get_nets -quiet -of $pin]
                    if {[llength $net] != 0} {
                        dict lappend sitefeatures_by_tile $key "$name.[get_name $pin].USED"
                    }
                }

                break
            }
        }
    }
    return $sitefeatures_by_tile
}

proc dump_bram_dsp_features_to_file {output_file} {
    set start_time [clock seconds]
    puts "[now] Gather features"
    set sitefeatures_by_tile [dump_bram_dsp_features]

    set filter_bram 1
    set filter_int 1
    set pips_by_tile [dump_pips $filter_bram $filter_int]


    set tiles [get_tiles -quiet -filter {TYPE == BRAM}]
    lappend tiles [get_tiles -quiet -filter {TYPE == DSP}]
    lappend tiles [get_tiles -quiet -filter {TYPE == DSP_L}]
    lappend tiles [get_tiles -quiet -filter {TYPE == DSP_R}]

    output_features_to_file $output_file $tiles $pips_by_tile $sitefeatures_by_tile

    set end_time [clock seconds]
    puts "[now] Done, took [expr $end_time - $start_time] seconds!"
}

proc is_hpio {site} {
    set site_type [get_property_debug SITE_TYPE $site]
    return [expr $site_type == "HPIOB" || $site_type == "HPIOB_S" || $site_type == "HPIOB_SNGL" || $site_type == "HPIOB_M"]
}

proc is_hdio {site} {
    set site_type [get_property_debug SITE_TYPE $site]
    return [expr $site_type == "HDIOB_M" || $site_type == "HDIOB_S"
}

proc is_hdiol {site} {
    set site_type [get_property_debug SITE_TYPE $site]
    return [expr $site_type == "HDIOLOGIC_M" || $site_type == "HDIOLOGIC_S"]
}

proc clean_value {orig} {
    return [remove_verilog_notation $orig]
}

proc process_inv {features_dict key prefix feature cell value} {
    if { ![string_endswith $feature "INVERTED"] } {
        return 0
    }

    set p0 [string first "_" $feature]
    set p1 [string last "_" $feature]

    set port [string range $feature [expr $p0+1] [expr $p1-1]]
    set pin [get_pins $cell/$port]
    if {[llength $pin] == 0} {
        error "Failed to find pin for $feature"
    }

    set net [get_nets -of $pin]
    if { [llength $net] == 0} {
        return 1
    }

    if { [is_static_net $net] } {
        return 1
    }

    set phys [get_bel_pins -of $pin]
    if {[llength $phys] == 0} {
        return 1
    }

    set site_pin [get_site_pins -of $pin]
    if { [llength $site_pin] == 0} {
        return 1
    }

    set site_node [get_nodes -of $site_pin]
    if { [llength $site_node] == 0} {
        return 1
    }

    set prop_value [clean_value $value]
    if { [is_node_inverted $net $site_node] } {
        set prop_value [expr $prop_value ^ 1]
    }
    upvar $features_dict d
    dict lappend d $key "$prefix.$feature.V$prop_value"
    return 1
}

proc add_oserdes {features_dict key prefix cell} {
    if {[get_property_debug REF_NAME $cell] == "<LOCKED>"} {
        return
    }

    upvar $features_dict d
    dict lappend d $key "$prefix.USED.V1"
    set cprefix "$prefix.[get_property_debug REF_NAME $cell]"
    dict lappend d $key "$cprefix.USED.V1"

    set basic_props [list "ODDR_MODE" "OSERDES_D_BYPASS" "OSERDES_T_BYPASS" "INIT" "IS_CLKDIV_INVERTED" "IS_CLK_INVERTED" "IS_RST_INVERTED" "DATA_WIDTH"]
    foreach prop $basic_props {
        set value [get_property_debug $prop $cell]
        if {[llength $value] == 0} {
            continue
        }
        if {[process_inv d $key $cprefix $prop $cell $value]} {
            continue
        }

        set v [clean_value $value]
        if { $v == 0 || $v == 1 } {
            set v "V$v"
        }

        dict lappend d $key "$cprefix.$prop.$v"
    }
}

proc add_iserdes {features_dict key prefix cell} {
    if {[get_property_debug REF_NAME $cell] == "<LOCKED>"} {
        return
    }

    upvar $features_dict d
    dict lappend d $key "$prefix.USED.V1"
    set cprefix "$prefix.[get_property_debug REF_NAME $cell]"
    dict lappend d $key "$cprefix.USED.V1"
    set basic_props [list "IDDR_MODE" "DDR_CLK_EDGE" "IS_CLK_B_INVERTED" "IS_CLK_INVERTED" "IS_RST_INVERTED" "DATA_WIDTH"]
    foreach prop $basic_props {
        set value [get_property_debug $prop $cell]
        if {[llength $value] == 0} {
            continue
        }
        if {[process_inv d $key $cprefix $prop $cell $value]} {
            continue
        }

        dict lappend d $key "$cprefix.$prop.[clean_value $value]"
    }
    process_inv d $key $cprefix "IS_CLKDIV_INVERTED" $cell "1'b0"
}

proc add_iddr {features_dict key prefix cell} {
    if {[get_property_debug REF_NAME $cell] == "<LOCKED>"} {
        return
    }

    upvar $features_dict d
    dict lappend d $key "$prefix.USED.V1"
    set cprefix "$prefix.[get_property_debug REF_NAME $cell]"
    dict lappend d $key "$cprefix.USED.V1"
    set basic_props [list "DDR_CLK_EDGE" "IS_C_INVERTED" "IS_CB_INVERTED" "IS_RST_INVERTED"]
    foreach prop $basic_props {
        set value [get_property_debug $prop $cell]
        if {[llength $value] == 0} {
            continue
        }
        if {[process_inv d $key $cprefix $prop $cell $value]} {
            continue
        }

        set v [clean_value $value]
        if { $v == 0 || $v == 1 } {
            set v "V$v"
        }

        dict lappend d $key "$cprefix.$prop.$v"
    }
}

proc add_delay {features_dict key prefix cell} {
    if {[get_property_debug REF_NAME $cell] == "<LOCKED>"} {
        return
    }

    upvar $features_dict d
    dict lappend d $key "$prefix.USED.V1"

    set basic_props [list "DELAY_FORMAT" "DELAY_SRC" "DELAY_TYPE" "IS_CLK_INVERTED" "IS_RST_INVERTED" "LOOPBACK" "UPDATE_MODE"]
    foreach prop $basic_props {
        set value [get_property_debug $prop $cell]
        if {[llength $value] == 0} {
            continue
        }
        if {[process_inv d $key $prefix $prop $cell $value]} {
            continue
        }

        set v [clean_value $value]
        if { $v == 0 || $v == 1 } {
            set v "V$v"
        }

        dict lappend d $key "$prefix.$prop.$v"
    }

    set value [get_property_debug DELAY_FORMAT $cell]
    if {$value == "COUNT"} {
        set counts [get_property_debug DELAY_VALUE $cell]
        if {[llength $counts] != 0} {
            for {set i 0} {$i < 9} {incr i} {
                if { (($counts >> $i) & 0x1) == 0x1} {
                    dict lappend d $key "$prefix.DELAY_VALUE\[$i\]"
                }
            }
        }
    } elseif {$value == "TIME"} {
        set del [get_property_debug DELAY_VALUE $cell]
        if {[llength $del] != 0} {
            set ps $del
            if {$ps >= 8} {
                set refdiv [expr int(floor((2000000.0/300.0) / ($ps)))];
                if { $refdiv >= 511 } {
                    set refdiv 511
                }
                for {set i 0} {$i < 9} {incr i} {
                    if {(($refdiv >> $i) & 0x1) == 0x1} {
                        dict lappend d $key "$prefix.REFCLK_MULT\[$i\]"
                    }
                }
            }
        }
    }
}

proc add_ff {features_dict key prefix cell} {
    set ct [get_property_debug REF_NAME $cell]
    if { $ct != "FDRE" && $ct != "FDPE" && $ct != "FDCE" && $ct != "FDSE" } {
        return
    }

    upvar $features_dict d
    dict lappend d $key "$prefix.USED.V1"

    if {$ct == "FDPE"} {
        set is_sync 0
        set srval 1
    } elseif {$ct == "FDCE" } {
        set is_sync 0
        set srval 0
    } elseif {$ct == "FDSE" } {
        set is_sync 1
        set srval 1
    } elseif {$ct == "FDRE" } {
        set is_sync 1
        set srval 0
    } else {
        error "unknown cell_type $ct"
    }

    if $is_sync {
        dict lappend d $key "$prefix.SYNC.SYNC"
    } else {
        dict lappend d $key "$prefix.SYNC.ASYNC"
    }

    if $srval {
        dict lappend d $key "$prefix.SR.SET"
    } else {
        dict lappend d $key "$prefix.SR.RESET"
    }

    set init [get_property_debug INIT $cell]
    if {[llength $init] != 0} {
        dict lappend d $key "$prefix.INIT.V[clean_value $init]"
    }
}

proc dump_io_pips {} {
    set filter_bram 1
    set filter_int 0
    set debug_io_dump 0
    set pips_by_tile [dump_pips $filter_bram $filter_int]

    set pips [get_all_pips]

    foreach pip $pips {
        set tile [get_tiles -of $pip]
        set ptt [get_property_debug TYPE $tile]
        set key "$tile:$ptt"

        set start_wire [get_wires -of $pip -uphill]
        set end_wire [get_wires -of $pip -downhill]

        if {$ptt == "HDIO_BOT_RIGHT" || $ptt == "HDIO_TOP_RIGHT"} {
            if { [get_property IS_PSEUDO $pip] && [get_property IS_DIRECTIONAL $pip] } {
                set base_feature "PIP.[get_name $end_wire].[get_name $start_wire]"
                dict lappend pips_by_tile "$tile:$ptt" $base_feature
            }
        }

        if {$ptt == "XIPHY_BYTE_L" || $ptt == "XIPHY_BYTE_RIGHT"} {
            if {![string_contains $end_wire "ODT"] && ([string_contains $start_wire "CLB2PHY"] || [string_contains $end_wire "CLB2PHY"])} {
                continue
            }
            if {[string_contains $end_wire "CLK_PIN"] || [string_contains $end_wire "CLKDIV_PIN"] || [string_contains $end_wire "D_PIN"]} {
                continue
            }

            set site_pin [get_site_pins -of [get_nodes -of $end_wire]]
            if {[llength $site_pin] != 0 } {
                set site [get_sites -of $site_pin]
                set site_type [get_property_debug SITE_TYPE $site]
                if {$site_type == "BITSLICE_RX_TX" && [string_contains $end_wire "Q5"]} {
                    set bypass 1
                    foreach cell [get_cells -quiet -of $site] {
                        set cell_type [get_property REF_NAME $cell]
                        if {$cell_type != "<LOCKED>"} {
                            set bypass 0
                        }
                    }
                    set sn [site_index_in_tile [get_tiles -of $site] $site]
                    dict lappend pips_by_tile $key "$sn.BYPASS.[get_name $site_pin].V$bypass"
                    if { $debug_io_dump } {
                        dict lappend pips_by_tile $key "$sn.BYPASS.[get_name $site_pin]_$bypass.V1"
                    }
                }

                if {$site_type == "BITSLICE_RX_TX" && [string_contains $end_wire "TX_Q"]} {
                    set bypass 1
                    foreach cell [get_cells -quiet -of $site] {
                        set cell_type [get_property REF_NAME $cell]
                        if {$cell_type != "<LOCKED>"} {
                            set bypass 0
                        }
                    }

                    if { $bypass == 1 } {
                        set sn [site_index_in_tile [get_tiles -of $site] $site]
                        dict lappend pips_by_tile $key "$sn.ODELAY.USED.V1"
                    }

                }
            }
        }
    }

    return $pips_by_tile
}

proc dump_io_features_to_file {output_file} {
    set start_time [clock seconds]
    puts "[now] Gather features"

    set pips_by_tile [dump_io_pips]
    set sitefeatures_by_tile [dict create]

    set debug_io_dump 0
    set all_pips [get_all_pips]

    set vrp_used_by_key [dict create]
    set sites_in_use [get_sites -filter {IS_USED == 1}]
    foreach site $sites_in_use {
        set site_type [get_property_debug SITE_TYPE $site]
        if {$site_type != "HPIOB" && $site_type != "HPIOB_M" && $site_type != "HPIOB_S" && $site_type != "HPIOB_SNGL" && $site_type != "HDIOB_M" && $site_type != "HDIOB_S"} {
            continue
        }

        set tile [get_tiles -of $site]
        set tile_type [get_property_debug TYPE $tile]
        set key "$tile:$tile_type"
        set sn [site_index_in_tile $tile $site]
        dict lappend sitefeatures_by_tile $key "SITE.${site}_$sn.1"

        if { [dict exists $vrp_used_by_key $key] == 0 } {
            dict set vrp_used_by_key $key 0
        }

        set port [get_ports -quiet -of $site]
        if { [llength $port] == 0} {
            error "Failed to find port for $site"
        }

        set pull [get_cells -quiet -of [get_bels $site/PULL]]
        set inbuf [get_cells -quiet -of [get_bels $site/INBUF]]
        set outbuf [get_cells -quiet -of [get_bels $site/OUTBUF]]

        set iostd [get_property_debug IOSTANDARD $port]

        set prefix "$sn.$iostd"

        if { $debug_io_dump } {
            dict lappend sitefeatures_by_tile $key "$sn.IOSTANDARD.$iostd"
            dict lappend sitefeatures_by_tile $key "$sn.USED.V1"
            dict lappend sitefeatures_by_tile $key "$prefix.USED.V1"
        }

        if {[llength $inbuf] != 0} {
            dict lappend sitefeatures_by_tile $key "$sn.IOSTANDARD_IN.$iostd"
            if { $debug_io_dump } {
                if { [llength $outbuf] == 0} {
                    dict lappend sitefeatures_by_tile $key "$sn.IN_ONLY.V1"
                    dict lappend sitefeatures_by_tile $key "$prefix.IN_ONLY.V1"
                } else {
                    dict lappend sitefeatures_by_tile $key "$sn.IN_ONLY.V0"
                    dict lappend sitefeatures_by_tile $key "$prefix.IN_ONLY.V0"
                }
            }

            if {[string_startswith $iostd "SSTL"] || [string_startswith $iostd "POD"] || [string_startswith $iostd "HSUL"] || [string_startswith $iostd "HSTL"]} {
                set internal_vref [get_property_debug X_internal_vref $port]
                if {[llength $internal_vref] != 0} {
                    dict lappend sitefeatures_by_tile $key "VREF.INTERNAL_[expr int(1000*$internal_vref)]_MV"
                }

                set other_internal_vref [get_property_debug X_int_vref $port]
                if {[llength $internal_vref] == 0 && [llength $other_internal_vref] == 0} {
                    dict lappend sitefeatures_by_tile $key "VREF.EXTERNAL"
                }
            }

            set tile_y [string range $tile [expr [string last "Y" $tile]+1] end]
            if {[string_endswith $iostd "DCI"] && ($tile_y % 60) == 0} {
                dict set vrp_used_by_key $key 1
            }

            set ibufdisable_bel_pins [get_bel_pins $site/IBUFCTRL/IBUFDISABLE]
            set pin [get_pins -of $ibufdisable_bel_pins]
            if {[llength $pin] == 0} {
                error "Failed to get IBUFDISABLE_USED pin for $site"
            }
            set net [get_nets -quiet -of $pin]
            if {[llength $net] != 0} {
                dict lappend sitefeatures_by_tile $key "$sn.IBUFDISABLE_USED.V1"
            } else {
                dict lappend sitefeatures_by_tile $key "$sn.IBUFDISABLE_USED.V0"
            }
        } else {
        }

        if {[llength $outbuf] != 0} {
            dict lappend sitefeatures_by_tile $key "$sn.IOSTANDARD_OUT.$iostd"

            if { $debug_io_dump } {
                dict lappend sitefeatures_by_tile $key "$sn.OUT_1.1"
                dict lappend sitefeatures_by_tile $key "$prefix.OUT_1.1"
            }

            if {[llength $inbuf] != 0} {
                dict lappend sitefeatures_by_tile $key "$sn.IOSTANDARD_IN_OUT.$iostd"
            }

            set tile_y [string range $tile [expr [string last "Y" $tile]+1] end]
            if {[string_endswith $iostd "DCI"] && ($tile_y % 60) == 0} {
                dict set vrp_used_by_key $key 1
            }

            set dcitermdisable_bel_pin [get_bel_pins -quiet $site/OUTBUF/DCITERMDISABLE]
            if {[llength $dcitermdisable_bel_pin] != 0} {
                set pin [get_pins -quiet -of $dcitermdisable_bel_pin]
                if {[llength $pin] != 0} {
                    dict lappend sitefeatures_by_tile $key "$sn.DCITERMDISABLE_USED.V1"
                    dict lappend sitefeatures_by_tile $key "$sn.IOSTANDARD_DCITERMDISABLE_USED.$iostd"
                } else {
                    dict lappend sitefeatures_by_tile $key "$sn.DCITERMDISABLE_USED.V0"
                }
            }
        }

        set pulltype [get_property_debug X_PULLTYPE $port]
        if {[llength $pulltype] != 0} {
            dict lappend sitefeatures_by_tile $key "$sn.PULLTYPE.$pulltype"
            if { $debug_io_dump } {
                dict lappend sitefeatures_by_tile $key "$prefix.PULLTYPE.$pulltype"
                dict lappend sitefeatures_by_tile $key "$sn.PULLTYPE_$pulltype.1"
                dict lappend sitefeatures_by_tile $key "$prefix.PULLTYPE_$pulltype.1"
            }
        }

        set x_drive [get_property_debug X_DRIVE $port]
        set drive [get_property_debug DRIVE $port]
        if { [llength $outbuf] != 0 } {
            if {[llength $drive] != 0 || [llength $x_drive] != 0 } {
                if { [llength $drive] == 0 } {
                    set drive $x_drive
                } elseif { [llength $x_drive] != 0 && $drive != $x_drive } {
                    error "Port $port has a weird DRIVE, $drive != $x_drive"
                }

                dict lappend sitefeatures_by_tile $key "$sn.IOSTANDARD_DRIVE.${iostd}_DRIVE_I$drive"

                if { $debug_io_dump } {
                    dict lappend sitefeatures_by_tile $key "$sn.DRIVE_I.I$drive"
                    dict lappend sitefeatures_by_tile $key "$prefix.DRIVE_I.I$drive"
                    dict lappend sitefeatures_by_tile $key "$prefix.DRIVE_I$drive.1"
                    dict lappend sitefeatures_by_tile $key "$sn.IOSTANDARD_DRIVE_${iostd}_DRIVE_I$drive.1"
                    dict lappend sitefeatures_by_tile $key "$sn.${iostd}_DRIVE_I$drive.1"
                }
            } else {
                dict lappend sitefeatures_by_tile $key "$sn.IOSTANDARD_DRIVE.${iostd}_DRIVE_I_FIXED"

                if { $debug_io_dump } {
                    dict lappend sitefeatures_by_tile $key "$sn.DRIVE_I.I_FIXED"
                    dict lappend sitefeatures_by_tile $key "$prefix.DRIVE_I.I_FIXED"
                    dict lappend sitefeatures_by_tile $key "$prefix.DRIVE_I_FIXED.1"
                    dict lappend sitefeatures_by_tile $key "$sn.IOSTANDARD_DRIVE_${iostd}_DRIVE_I_FIXED.1"
                    dict lappend sitefeatures_by_tile $key "$sn.${iostd}_DRIVE_I_FIXED.1"
                }
            }
        }

        set slew [get_property_debug X_SLEW $port]
        if {[llength $slew] != 0 && [llength $outbuf] != 0} {
            if {[llength $drive] != 0} {
                if { $debug_io_dump } {
                    dict lappend sitefeatures_by_tile $key "$prefix.DRIVE.I$drive.SLEW.$slew"
                    dict lappend sitefeatures_by_tile $key "$sn.DRIVE.I$drive.SLEW.$slew"
                    dict lappend sitefeatures_by_tile $key "$prefix.DRIVE_I${drive}_SLEW_$slew.1"
                }
            } else {
                if { $debug_io_dump } {
                    dict lappend sitefeatures_by_tile $key "$prefix.DRIVE.I_FIXED.SLEW.$slew"
                    dict lappend sitefeatures_by_tile $key "$sn.DRIVE.I_FIXED.SLEW.$slew"
                    dict lappend sitefeatures_by_tile $key "$prefix.DRIVE_I_FIXED_SLEW_$slew.1"
                }
            }
        }

        if {[llength $slew] != 0 && [llength $outbuf] != 0 && [llength $drive] != 0} {
            dict lappend sitefeatures_by_tile $key "$sn.IOSTANDARD_DRIVE_SLEW.${iostd}_DRIVE_I${drive}_SLEW_$slew"
        }

        set output_impedance [get_property_debug X_OUTPUT_IMPEDANCE $port]
        if {[llength $output_impedance] != 0 && [llength $outbuf] != 0} {
            dict lappend sitefeatures_by_tile $key "$sn.IOSTANDARD_OUTPUT_IMPEDANCE.${iostd}_$output_impedance"
        }

        set equalization [get_property_debug X_EQUALIZATION $port]
        if {[llength $equalization] != 0} {
            dict lappend sitefeatures_by_tile $key "$sn.IOSTANDARD_EQUALIZATION.${iostd}_$equalization"
        }

        set odt [get_property_debug X_ODT $port]
        if {[llength $odt] != 0} {
            dict lappend sitefeatures_by_tile $key "$sn.IOSTANDARD_ODT.${iostd}_$odt"
        }

        set used 0
        foreach site_pip [get_site_pips -quiet -of $site -filter {IS_USED == 1}] {
            set bel [get_bels -of $site -include_routing_bels [string range $site_pip 0 [string first ":" $site_pip]-1]]
            set bel_type [get_property_debug TYPE $bel]
            if {[string_contains $site_pip "INV"]} {
                continue
            }

            if { [get_name $bel] == "INPUTMUX" } {
                continue
            }

            dict lappend sitefeatures_by_tile $key "$sn.[get_name $bel].[get_property FROM_PIN $site_pip]"
            set used 1
            if { $debug_io_dump } {
                dict lappend sitefeatures_by_tile $key "$sn.[get_name $bel]_[get_property FROM_PIN $site_pip].1"
            }
        }
    }

    dict for {key val} $vrp_used_by_key {
        dict lappend sitefeatures_by_tile $key "VRP_USED.V$val"
    }

    foreach site [get_sites -filter {IS_USED == 0}] {
        set site_type [get_property_debug SITE_TYPE $site]
        if {$site_type != "HPIOB" && $site_type != "HPIOB_M" && $site_type != "HPIOB_S" && $site_type != "HPIOB_SNGL" && $site_type != "HDIOB_M" && $site_type != "HDIOB_S"} {
            continue
        }

        set port [get_ports -quiet -of $site]
        if { [llength $port] != 0 } {
            continue
        }

        set tile [get_tiles -of $site]
        set tile_type [get_property_debug TYPE $tile]
        set key "$tile:$tile_type"
        set sn [site_index_in_tile $tile $site]

        if { $debug_io_dump } {
            dict lappend sitefeatures_by_tile $key "$sn.IOSTANDARD.NONE"
        }

        dict lappend sitefeatures_by_tile $key "$sn.IOSTANDARD_DRIVE.NONE"
        dict lappend sitefeatures_by_tile $key "$sn.IOSTANDARD_DRIVE_SLEW.NONE"
        dict lappend sitefeatures_by_tile $key "$sn.IOSTANDARD_OUTPUT_IMPEDANCE.NONE"
        dict lappend sitefeatures_by_tile $key "$sn.IOSTANDARD_EQUALIZATION.NONE"
        dict lappend sitefeatures_by_tile $key "$sn.IOSTANDARD_ODT.NONE"
        dict lappend sitefeatures_by_tile $key "$sn.IOSTANDARD_IN.NONE"
        dict lappend sitefeatures_by_tile $key "$sn.IOSTANDARD_OUT.NONE"
        dict lappend sitefeatures_by_tile $key "$sn.IOSTANDARD_IN_OUT.NONE"
        dict lappend sitefeatures_by_tile $key "$sn.IOSTANDARD_DCITERMDISABLE_USED.NONE"
    }

    foreach site [get_sites] {
        set site_type [get_property_debug SITE_TYPE $site]
        if { $site_type != "HPIOBDIFFINBUF" && $site_type != "HPIOBDIFFOUTBUF" } {
            continue
        }

        puts "Dumping features from $site"

        set tile [get_tiles -of $site]
        set tile_type [get_property_debug TYPE $tile]
        set key "$tile:$tile_type"
        set sn [site_index_in_tile $tile $site]

        set used 0
        set skip 0

        foreach cell [get_cells -of $site] {
            set cell_type [get_property_debug REF_NAME $cell]
            if {$cell_type != "<LOCKED>"} {
                set used 1
            }

            if {$cell_type == "<LOCKED>"} {
                set skip 1
            }
        }

        if { $skip } {
            continue
        }

        if {$site_type == "HPIOBDIFFINBUF"} {
            set site_pin [get_site_pins $site/PAD_RES_0]
            if { [llength $site_pin] == 0 } {
                error "Failed to get PAD_RES_0 site pin from site $site"
            }

            set cursor [get_nodes -of $site_pin]
            while 1 {
                set site_pin [get_site_pins -of $cursor]
                if { [llength $site_pin] == 0} {
                    error "Failed to find master of DIFF buffer"
                }

                set site2 [get_sites -of $site_pin]
                if { [llength $site2] == 0 } {
                    error "Failed to site from site_pin $site_pin"
                }

                if { [get_property_debug SITE_TYPE $site2] == "HPIOB_M" } {
                    break
                }

                set pips [get_pips -of $cursor -uphill]
                if { [llength $pips] == 0 } {
                    error "No uphill pips for $site"
                }

                foreach pip $pips {
                    set cursor [get_nodes -of $pip -uphill]
                    break
                }
            }

            set m_site_pin [get_site_pins -of $cursor]
            if { [llength $m_site_pin] == 0 } {
                error "Failed to find master site pin for site $site"
            }

            set m [get_sites -of $m_site_pin]
            if { [llength $m] == 0 } {
                error "Failed to get master site from site $site"
            }

            set port [get_ports -of $m]
            if { [llength $port] == 0 } {
                dict lappend sitefeatures_by_tile $key "$sn.IOSTANDARD.NONE"
            } else {
                dict lappend sitefeatures_by_tile $key "$sn.IOSTANDARD.[get_property_debug IOSTANDARD $port]"
                if { $debug_io_dump } {
                    dict lappend sitefeatures_by_tile $key "$sn.[get_property_debug IOSTANDARD $port]_DIFF_IN.V1"
                }

                set diff_term_adv [get_property_debug X_DIFF_TERM_ADV $port]
                if { [llength $diff_term_adv] != 0 } {
                    dict lappend sitefeatures_by_tile $key "$sn.IOSTANDARD_DIFF_TERM_ADV.[get_property_debug IOSTANDARD $port]_$diff_term_adv"
                    if { $debug_io_dump } {
                        dict lappend sitefeatures_by_tile $key "$sn.[get_property_debug IOSTANDARD $port].DIFF_TERM_ADV_$diff_term_advi.1"
                    }
                }
            }
        } elseif {$site_type == "HPIOBDIFFOUTBUF"} {
            set site_pin [get_site_pins $site/AOUT]
            if { [llength $site_pin] == 0 } {
                error "Failed to get AOUT site pin from site $site"
            }

            set cursor [get_nodes -of $site_pin]
            while 1 {
                set site_pin [get_site_pins -of $cursor]
                if { [llength $site_pin] == 0} {
                    error "Failed to find master of DIFF buffer"
                }

                set site2 [get_sites -of $site_pin]
                if { [llength $site2] == 0 } {
                    error "Failed to site from site_pin $site_pin"
                }

                if { [get_property_debug SITE_TYPE $site2] == "HPIOB_M" } {
                    break
                }

                set pips [get_pips -of $cursor -downhill]
                if { [llength $pips] == 0 } {
                    error "No downhill pips for $site"
                }

                foreach pip $pips {
                    set cursor [get_nodes -of $pip -downhill]
                    break
                }
            }

            set m_site_pin [get_site_pins -of $cursor]
            if { [llength $m_site_pin] == 0 } {
                error "Failed to find master site pin for site $site"
            }

            set m [get_sites -of $m_site_pin]
            if { [llength $m] == 0 } {
                error "Failed to get master site from site $site"
            }

            set port [get_port -of $m]
            if { [llength $port] == 0 } {
                dict lappend sitefeatures_by_tile $key "$sn.IOSTANDARD.NONE"
            } else {
                dict lappend sitefeatures_by_tile $key "$sn.IOSTANDARD.[get_property_debug IOSTANDARD $port]"
                if { $debug_io_dump } {
                    dict lappend sitefeatures_by_tile $key "$sn.[get_property_debug IOSTANDARD $port]_DIFF_OUT.1"
                }
            }
        }
    }

    foreach site [get_sites] {
        if {![string_startswith $site "BITSLICE_RX_TX_"] } {
            continue
        }

        set site_type [get_property_debug SITE_TYPE $site]
        set tile [get_tiles -of $site]
        set tile_type [get_property_debug TYPE $tile]
        set key "$tile:$tile_type"
        set sn [site_index_in_tile $tile $site]

        if { [get_property IS_USED $site] } {
            dict lappend sitefeatures_by_tile $key "$sn.USED.V1"
        } else {
            set site_pseudo_used 0
            set pips_for_site [get_pips -of $site -filter {IS_PSEUDO == 1}]
            if { [llength [::struct::set intersect $pips_for_site $all_pips]] != 0 } {
                set site_pseudo_used 1
            }

            if { $debug_io_dump } {
                dict lappend sitefeatures_by_tile $key "$sn.TX_Q_PSEUDO.$site_pseudo_used"
                dict lappend sitefeatures_by_tile $key "$sn.TX_Q_PSEUDO_$site_pseudo_used.1"
            }
            dict lappend sitefeatures_by_tile $key "$sn.USED.V$site_pseudo_used"
            if { $site_pseudo_used == 0 } {
                dict lappend sitefeatures_by_tile $key "$sn.ODELAY.USED.V0"
            }
        }
    }

    foreach site $sites_in_use {
        set site_type [get_property_debug SITE_TYPE $site]
        set tile [get_tiles -of $site]
        set tile_type [get_property_debug TYPE $tile]
        set key "$tile:$tile_type"
        set sn [site_index_in_tile $tile $site]

        set bels [get_bels -of $site]
        set is_component_rx_tx [string equal [get_name [lindex [lsort [get_bels -of $site]] 0]] "EN_DQ"]
        if $is_component_rx_tx {
            puts "Dumping features from $site, $key, $sn"

            set only_locked 1
            foreach cell [get_cells -of $site] {
                if {[get_property_debug REF_NAME $cell] != "<LOCKED>"} {
                    set only_locked 0
                }
            }

            if {!$only_locked} {
                dict lappend sitefeatures_by_tile $key "$sn.COMPONENT_MODE.V1"
            } else {
                dict lappend sitefeatures_by_tile $key "$sn.COMPONENT_MODE.V0"
                continue
            }

            set idelay ""
            set odelay ""
            set oserdes ""
            set off ""

            set oserdes_used 0
            set iserdes_used 0
            set idelay_used 0
            set odelay_used 0
            set in_ff_used 0
            set out_ff_used 0

            foreach cell [get_cells -quiet -of $site] {
                set bel [get_name [get_bels -of $cell]]
                if { $bel == "IDELAY" } {
                    set idelay $cell
                    set idelay_used 1
                    add_delay sitefeatures_by_tile $key "$sn.IDELAY" $cell
                } elseif { $bel == "ODELAY" } {
                    set odelay $cell
                    set odelay_used 1
                    add_delay sitefeatures_by_tile $key "$sn.ODELAY" $cell
                } elseif { $bel == "ISERDES" } {
                    set subgroup [get_property PRIMITIVE_SUBGROUP $cell]
                    set iserdes_used 1
                    set in_ff_used 1
                    if { $subgroup == "SERDES" } {
                        add_iserdes sitefeatures_by_tile $key "$sn.ISERDES" $cell
                    }
                } elseif { $bel == "OSERDES" } {
                    set oserdes_used 1
                    set out_ff_used 1
                    set oserdes $cell
                    set subgroup [get_property PRIMITIVE_SUBGROUP $cell]
                    if { $subgroup == "SERDES" } {
                        set pin [get_pins $cell/OQ]
                        if { [llength $pin] == 0 } {
                            error "Failed to get pin from cell $cell"
                        }

                        set net [get_nets -of $pin -quiet]
                        if { [llength $net] != 0 } {
                            puts "add_oserdes $key $cell $sn"
                            add_oserdes sitefeatures_by_tile $key "$sn.OSERDES" $cell
                        }
                    }
                } elseif { $bel == "IN_FF" } {
                    set in_ff_used 1
                    set iserdes_used 1
                    add_ff sitefeatures_by_tile $key "$sn.IN_FF" $cell
                } elseif { $bel == "OUT_FF" } {
                    set off $cell
                    set out_ff_used 1
                    set oserdes_used 1
                    add_ff sitefeatures_by_tile $key "$sn.OUT_FF" $cell
                }
            }

            if { !$idelay_used } {
                dict lappend sitefeatures_by_tile $key "$sn.IDELAY.USED.V0"
            }
            if { !$iserdes_used } {
                dict lappend sitefeatures_by_tile $key "$sn.ISERDES.USED.V0"
            }
            if { !$oserdes_used } {
                dict lappend sitefeatures_by_tile $key "$sn.OSERDES.USED.V0"
            }
            if { !$in_ff_used } {
                dict lappend sitefeatures_by_tile $key "$sn.IN_FF.USED.V0"
            }
            if { !$out_ff_used } {
                dict lappend sitefeatures_by_tile $key "$sn.OUT_FF.USED.V0"
            }

            set routing_bels [dict create]

            foreach site_pip [get_site_pips -quiet -of $site -filter {IS_USED == 1}] {
                set bel [get_bels -of $site -include_routing_bels [string range $site_pip 0 [string first ":" $site_pip]-1]]
                set bel_type [get_property_debug TYPE $bel]
                if {[string_contains $bel_type "INV"]} {
                    continue
                }

                dict lappend sitefeatures_by_tile $key "$sn.[get_name $bel].[get_property FROM_PIN $site_pip]"
                if { $debug_io_dump } {
                    dict lappend sitefeatures_by_tile $key "$sn.[get_name $bel]_[get_property FROM_PIN $site_pip].1"
                }
                dict set routing_bels [get_name $bel] [get_property FROM_PIN $site_pip]
            }

            if {[llength $odelay] != 0 && [llength $oserdes] == 0 && [llength $off] == 0 && [dict exists $routing_bels XIPHY_ROUTE_THROUGH_ODELAY_BYPASS]} {
                if { [dict get $routing_bels XIPHY_ROUTE_THROUGH_ODELAY_BYPASS] == "D0" } {
                    if { $debug_io_dump } {
                        dict lappend sitefeatures_by_tile $key "$sn.OSERDES.BYPASSED.1"
                        dict lappend sitefeatures_by_tile $key "$sn.OSERDES.BYPASSED_1.1"
                    }
                }
            }

            if {[llength $odelay] != 0 && [llength $oserdes] != 0 && [dict exists $routing_bels XIPHY_ROUTE_THROUGH_ODELAY_BYPASS]} {
                if { $debug_io_dump } {
                    dict lappend sitefeatures_by_tile $key "$sn.OSERDES.BYPASSED.0"
                }
            }

            if {[llength $idelay] == 0 && [dict exists $routing_bels XIPHY_ROUTE_THROUGH_ODELAY_BYPASS]} {
                if { [dict get $routing_bels XIPHY_ROUTE_THROUGH_ODELAY_BYPASS] == "D0" } {
                    if { $debug_io_dump } {
                        dict lappend sitefeatures_by_tile $key "$sn.IDELAY.BYPASSED.1"
                    }
                }
            }

            if {[llength $idelay] != 0 && [dict exists $routing_bels XIPHY_ROUTE_THROUGH_ODELAY_BYPASS]} {
                if { [dict get $routing_bels XIPHY_ROUTE_THROUGH_ODELAY_BYPASS] == "D0" } {
                    if { $debug_io_dump } {
                        dict lappend sitefeatures_by_tile $key "$sn.IDELAY.BYPASSED.0"
                    }
                }
            }

            set tx_q_site_pin [get_site_pins $site/TX_Q]
            set tx_q_net [get_nets -quiet -of [get_nodes -of $tx_q_site_pin]]
            set tx_q_used 0
            set rx_d_used 0
            if { [llength $tx_q_net] != 0 } {
                set tx_q_used 1
            }

            if { [dict exists $routing_bels XIPHY_ROUTE_MUX2TO1_Q] } {
                if { [dict exists $routing_bels XIPHY_FEEDTHRU_MUX] } {
                    if { [dict get $routing_bels XIPHY_FEEDTHRU_MUX] == "D1" } {
                        set tx_q_used 1
                    }
                    if { [dict get $routing_bels XIPHY_FEEDTHRU_MUX] == "D0" } {
                        set rx_d_used 1
                    }
                }

                if { [dict exists $routing_bels XIPHY_INT_MUX] } {
                    if { [dict get $routing_bels XIPHY_INT_MUX] == "D1" } {
                        set tx_q_used 1
                    }
                    if { [dict get $routing_bels XIPHY_INT_MUX] == "D0" } {
                        set rx_d_used 1
                    }
                }
            } else {
                dict lappend sitefeatures_by_tile $key "$sn.TX_Q.USED.V0"
            }

            if { $tx_q_used } {
                dict lappend sitefeatures_by_tile $key "$sn.TX_Q.USED.V1"
            }

            dict lappend sitefeatures_by_tile $key "$sn.RX_D.USED.V$rx_d_used"

            if { [dict exists $routing_bels XIPHY_ROUTE_THROUGH_ODELAY_BYPASS] } {
                if {[dict get $routing_bels XIPHY_ROUTE_THROUGH_ODELAY_BYPASS] == "D1"} {
                    set bel_pin [get_bel_pins $site/OSERDES/OQ]
                    if { [llength $bel_pin] == 0 } {
                        error "Failed to get OSERDES/OQ bel pin"
                    }

                    set pin [get_pins -of $bel_pin]
                    if { [llength $pin] != 0 } {
                        if { [llength $net] != 0 } {
                            dict lappend sitefeatures_by_tile $key "$sn.OSERDES_OQ.USED.V1"
                        }
                    }
                }
            } else {
                dict lappend sitefeatures_by_tile $key "$sn.OSERDES_OQ.USED.V0"
            }
        } elseif {$site_type == "BITSLICE_CONTROL"} {
            puts "Dumping features from $site"

            foreach cell [get_cells -of $site] {
                if {[get_property_debug REF_NAME $cell] == "IDELAYCTRL"} {
                    dict lappend sitefeatures_by_tile $key "$sn.IDELAYCTRL.USED.V1"
                }
            }
        } elseif { $site_type == "HDIOLOGIC_M" || $site_type == "HDIOLOGIC_S" } {
            puts "Dumping features from $site"

            set only_locked 1
            foreach cell [get_cells -of $site] {
                if {[get_property_debug REF_NAME $cell] == "<LOCKED>"} {
                    set only_locked 0
                }
            }
            if {!$only_locked} {
                dict lappend sitefeatures_by_tile $key "$sn.USED.V1"
            } else {
                dict lappend sitefeatures_by_tile $key "$sn.USED.V0"
            }

            set iff_used 0
            set opff_used 0
            set tff_used 0
            set iddr_used 0
            set optff_used 0

            if { $site_type == "HDIOLOGIC_M" } {
                set pin [get_site_pins $site/OPFFM_Q]
            } elseif { $site_type == "HDIOLOGIC_S" } {
                set pin [get_site_pins $site/OPFFS_Q]
            }

            if { [llength $pin] == 0 } {
                error "Failed to find OQ pin for site $site"
            }

            set oq_net [get_nets -of $pin -quiet]

            foreach cell [get_cells -quiet -of $site] {
                set bel [get_name [get_bels -of $cell]]
                if { $bel == "IFF" } {
                    set iff_used 1
                    add_ff sitefeatures_by_tile $key "$sn.IFF" $cell
                } elseif { $bel == "OPFF" } {
                    set opff_used 1
                    add_ff sitefeatures_by_tile $key "$sn.OPFF" $cell
                } elseif { $bel == "TFF" } {
                    set tff_used 1
                    add_ff sitefeatures_by_tile $key "$sn.TFF" $cell
                } elseif { $bel == "IDDR" } {
                    set iddr_used 1
                    add_iddr sitefeatures_by_tile $key "$sn.IDDR" $cell
                } elseif { $bel == "OPTFF" } {
                    set optff_used 1
                    add_oserdes sitefeatures_by_tile $key "$sn.OPTFF" $cell
                }
            }

            if { [llength $oq_net] > 0 } {
                if { $optff_used } {
                    dict lappend sitefeatures_by_tile $key "$sn.OQ_MUX.OPTFF"
                } else {
                    dict lappend sitefeatures_by_tile $key "$sn.OQ_MUX.NOT_OPTFF"
                }
            }

            if { $iff_used == 0 } {
                dict lappend sitefeatures_by_tile $key "$sn.IFF.USED.V0"
            }
            if { $opff_used == 0 } {
                dict lappend sitefeatures_by_tile $key "$sn.OPFF.OSERDESE3.USED.V0"
                dict lappend sitefeatures_by_tile $key "$sn.OPFF.USED.V0"
            }
            if { $tff_used == 0 } {
                dict lappend sitefeatures_by_tile $key "$sn.TFF.USED.V0"
            }
            if { $iddr_used == 0 } {
                dict lappend sitefeatures_by_tile $key "$sn.IDDR.USED.V0"
            }
            if { $optff_used == 0 } {
            }
        }
    }

    set iobank_voltages [dict create]

    foreach port [get_ports] {
        set iostd [get_property IOSTANDARD $port]
        set iostd_obj [get_io_standard $iostd]
        set vcc [get_property VCCO_IN $iostd_obj]
        set bank [get_iobanks -of $port]

        dict lappend iobank_voltages $bank $vcc
    }

    dict for { bank voltages } $iobank_voltages {
        set voltages [struct::set union $voltages []]
        if { [llength $voltages] != 1 } {
            error "Bank $bank has weird voltages $voltages"
        }

        foreach tile [get_tiles -of [get_sites -of [get_iobanks $bank]]] {
            set tile_type [get_property_debug TYPE $tile]
            set key "$tile:$tile_type"

            if { $voltages < 2.5 } {
                dict lappend sitefeatures_by_tile $key "BANK_VOLTAGE.LOW_VOLTAGE"
            } else {
                dict lappend sitefeatures_by_tile $key "BANK_VOLTAGE.HIGH_VOLTAGE"
            }
        }
    }

    set tiles [get_tiles -quiet -filter {TYPE == HPIO_L}]
    lappend tiles [get_tiles -quiet -filter {TYPE == HPIO_RIGHT}]
    lappend tiles [get_tiles -quiet -filter {TYPE == HDIO_TOP_RIGHT}]
    lappend tiles [get_tiles -quiet -filter {TYPE == HDIO_BOT_RIGHT}]
    lappend tiles [get_tiles -quiet -filter {TYPE == XIPHY_BYTE_L}]
    lappend tiles [get_tiles -quiet -filter {TYPE == XIPHY_BYTE_RIGHT}]

    output_features_to_file $output_file $tiles $pips_by_tile $sitefeatures_by_tile

    set end_time [clock seconds]
    puts "[now] Done, took [expr $end_time - $start_time] seconds!"
}
