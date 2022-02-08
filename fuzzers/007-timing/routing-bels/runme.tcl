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

proc dump_model_timings {models} {

    set IGNORED_PROPERTIES [list "CLASS" "NAME_INTERNAL" "SPEED_INDEX"]

    # Dump each model
    set timing_line {}
    foreach model $models {
        set all_properties [list_property $model]

        # Filter properties
        set properties {}
        foreach property $all_properties {
            if {$property ni $IGNORED_PROPERTIES} {
                lappend properties $property
            }
        }

        # Dump properties
        lappend timing_line $model
        lappend timing_line [llength $properties]

        foreach property $properties {
            set value [get_property $property $model]
            set value_flat [join $value ""]
            lappend timing_line "$property:$value_flat"
        }
    }

    return $timing_line
}

proc dump_tile_timings {tile timing_fp} {

    set timing_line {}
    lappend timing_line [get_property TYPE $tile]

    # List sites
    set sites [get_sites -of_objects [get_tiles $tile]]
    lappend timing_line [llength $sites]

    foreach site $sites {
        set site_type [get_property SITE_TYPE $site]

        # List all bels and all non-routing bels
        set all_bels [get_bels -include_routing_bels -of_objects $site]
        set non_routing_bels [get_bels -of_objects $site]

        # Build a list of routing bels only
        set routing_bels {}
        foreach bel $all_bels {
            if {$bel ni $non_routing_bels} {
                lappend routing_bels $bel
            }
        }

        lappend timing_line $site_type
        lappend timing_line [llength $routing_bels]

        # Look for speed models that has the name of a routing bel within
        foreach bel $routing_bels {
            set bel [lindex [split $bel "/"] 1]

            set models [get_speed_models -pattern "*$bel*"]

            lappend timing_line $bel
            lappend timing_line [llength $models]

            lappend timing_line [dump_model_timings $models]
        }
    }

    puts $timing_fp [join $timing_line]
}

proc dump {} {

    # Narrow the list of tile types to dump timings for
    set allowed_tile_types [list "CLEL_L" "CLEL_R" "CLEM" "CLEM_R" "CLE_M" "CLE_M_R" "BRAM" "URAM_URAM_FT"]

    set types [get_tile_types]
    set timing_fp [open "bel_timings.txt" w]

    foreach type $types {
        if {$type in $allowed_tile_types} {
            set tile [randsample_list 1 [get_tiles -filter "TYPE == $type"]]
            puts "Dumping timings for tile '$tile' of type '$type'"
            dump_tile_timings $tile $timing_fp
        }
    }
}

proc run {} {

    # Create an IO planning design
    create_project -force -part $::env(URAY_PART) design design
    set_property design_mode PinPlanning [current_fileset]
    open_io_design -name io_1

    # Dump timings
    dump
}

run
