# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

set blocknb [lindex $argv 0]
set start [expr int([lindex $argv 1])]
set stop [expr int([lindex $argv 2])]

create_project -force -part $::env(URAY_PART) $blocknb $blocknb
set_property design_mode PinPlanning [current_fileset]
open_io_design -name io_1

#set_param tcl.collectionResultDisplayLimit 0
set_param messaging.disableStorage 1

set fname "node_${blocknb}.tmp.json"
set root_fp [open "root_node_${blocknb}.csv" w]
puts $root_fp "node,,$fname"
close $root_fp

set nodes [get_nodes]

set fp [open "${fname}" w]

puts $fp "\["
for {set j $start } { $j < $stop } { incr j } {
    set node [lindex $nodes $j]

    # Skip nodes that don't appear to be connected to anything.
    set num_pips [llength [get_pips -quiet -of $node]]
    set num_site_pins [llength [get_site_pins -quiet -of $node]]
    if { $num_pips == 0 && $num_site_pins == 0 } {
        continue
    }

    # node properties:
    # BASE_CLOCK_REGION CLASS COST_CODE COST_CODE_NAME IS_BAD IS_COMPLETE
    # IS_GND IS_INPUT_PIN IS_OUTPUT_PIN IS_PIN IS_VCC NAME NUM_WIRES PIN_WIRE
    # SPEED_CLASS
    puts $fp "\t\{"
    puts $fp "\t\t\"node\": \"$node\","
    puts $fp "\t\t\"wires\": \["
    foreach wire [get_wires -of_objects $node] {
        # wire properties:
        # CLASS COST_CODE ID_IN_TILE_TYPE IS_CONNECTED IS_INPUT_PIN IS_OUTPUT_PIN
        # IS_PART_OF_BUS NAME NUM_DOWNHILL_PIPS NUM_INTERSECTS NUM_PIPS
        # NUM_TILE_PORTS NUM_UPHILL_PIPS SPEED_INDEX TILE_NAME TILE_PATTERN_OFFSET
        puts $fp "\t\t\t\{"
        puts $fp "\t\t\t\t\"wire\":\"$wire\""
        puts $fp "\t\t\t\},"
    }
    puts $fp "\t\t\t\{\}"
    puts $fp "\t\t\]"
    puts $fp "\t\},"
}

puts $fp "\t\{\}"
puts $fp "\]"
close $fp
