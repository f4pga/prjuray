# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

set filename [lindex $argv 0]

create_project -force -part $::env(URAY_PART) -name $filename
set_property design_mode PinPlanning [current_fileset]
open_io_design -name io_1

set_param messaging.disableStorage 1
set fp [open $filename r]
set file_data [read $fp]
close $fp

set fp [open $filename w]

set indices [split $file_data "\n"]

# Convert DRIVE from ??? units to 10^(-3 to -6) Ohms
set MAGIC 0.6875

puts $fp "\{"


foreach index $indices {
    if {$index == ""} {
        continue
    }

    set split_index [split $index ","]
    set resource [lindex $split_index 0]
    set resource_index [lindex $split_index 1]

    puts $fp "\t\"$resource_index\":"
    puts $fp "\t\t\{"

    if {$resource == "site_pin"} {
    } elseif {$resource == "pip"} {
        # Getting all site_pin information
        set speed_model [get_speed_models -filter "SPEED_INDEX == $resource_index"]

        puts $fp "\t\t\t\"resource_name\": \"$resource\","

        set model_type [get_speed_model_name [get_property TYPE $speed_model]]
        puts $fp "\t\t\t\"delay\":\["
        puts $fp "\t\t\t\t\"[get_property FAST_MIN $forward_speed_model]\","
        puts $fp "\t\t\t\t\"[get_property FAST_MAX $forward_speed_model]\","
        puts $fp "\t\t\t\t\"[get_property SLOW_MIN $forward_speed_model]\","
        puts $fp "\t\t\t\t\"[get_property SLOW_MAX $forward_speed_model]\","
        puts $fp "\t\t\t\],"
    } elseif {$resource == "wire"} {
        # Getting all wire information
        set speed_model [get_speed_models -filter "SPEED_INDEX == $resource_index"]

        puts $fp "\t\t\t\"resource_name\": \"$resource\","
        puts $fp "\t\t\t\"res\":\"[get_property WIRE_RES $speed_model]\","
        puts $fp "\t\t\t\"cap\":\"[get_property WIRE_CAP $speed_model]\","
    } else {
        puts "STUFF TO READ $index $resource"
        exit 2
    }

    puts $fp "\t\t\},"
}

puts $fp "\}"

close $fp
