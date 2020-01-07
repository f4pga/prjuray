# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

source "$::env(URAY_DIR)/utils/utils.tcl"

proc dump_lib_cells {cell_pins_fp} {
    set pins_line {}

    set lib_cells [get_lib_cells]
    lappend pins_line [llength $lib_cells]

    foreach lib_cell $lib_cells {
        set pins [get_lib_pins -of_objects $lib_cell]

        lappend pins_line $lib_cell
        lappend pins_line [llength $pins]

        foreach pin $pins {
            set pin [lindex [split $pin "/"] 1]
            lappend pins_line $pin
        }
    }

    puts $cell_pins_fp [join $pins_line]
}

proc dump_tile_timings {tile timing_fp config_fp pins_fp tile_pins_fp} {

    set IGNORED_PROPERTIES [list "CLASS" "NAME_INTERNAL" "SPEED_INDEX"]

    set timing_line {}
    set config_line {}
    set pins_line {}
    set tile_pins_line {}

    lappend timing_line [get_property TYPE $tile]
    lappend config_line [get_property TYPE $tile]
    lappend pins_line [get_property TYPE $tile]
    lappend tile_pins_line [get_property TYPE $tile]

    set sites [get_sites -of_objects [get_tiles $tile]]

    lappend tile_pins_line [llength $sites]
    lappend timing_line [llength $sites]
    lappend config_line [llength $sites]
    lappend pins_line [llength $sites]

    foreach site $sites {
        set site_type [get_property SITE_TYPE $site]

        lappend tile_pins_line $site_type
        lappend pins_line $site_type
        lappend timing_line $site_type
        lappend config_line $site_type

        # dump site pins
        set site_pins [get_site_pins -of_objects [get_sites $site]]
        lappend tile_pins_line [llength $site_pins]

        foreach pin $site_pins {
            set direction [get_property DIRECTION $pin]
            set is_part_of_bus [get_property IS_PART_OF_BUS $pin]
            regexp {\/(.*)$} $pin -> pin
            lappend tile_pins_line $pin $direction $is_part_of_bus
        }

        # dump bel pins, speed_models and configs
        set bels [get_bels -of_objects $site]

        lappend pins_line [llength $bels]
        lappend timing_line [llength $bels]
        lappend config_line [llength $bels]

        foreach bel $bels {
            set speed_models [get_speed_models -of_objects $bel]
            set bel_type [get_property TYPE $bel]
            set bel_configs [list_property $bel CONFIG*]
            set bel_pins [get_bel_pins -of_objects [get_bels $bel]]

            lappend pins_line $bel_type
            lappend pins_line [llength $bel_pins]
            foreach pin $bel_pins {
                set direction [get_property DIRECTION $pin]
                set is_clock [get_property IS_CLOCK $pin]
                set is_part_of_bus [get_property IS_PART_OF_BUS $pin]
                regexp {\/.*\/(.*)$} $pin -> pin
                lappend pins_line $pin $direction $is_clock $is_part_of_bus
            }

            lappend config_line $bel_type
            lappend config_line [llength $bel_configs]
            foreach config $bel_configs {
                set config_vals [get_property $config $bel]
                lappend config_line $config
                lappend config_line [llength $config_vals]
                foreach val $config_vals {
                    lappend config_line $val
                }
            }

            lappend timing_line "$bel_type"
            lappend timing_line [llength $speed_models]
            foreach speed_model $speed_models {
                set all_properties [list_property $speed_model]

                set properties {}
                foreach property $all_properties {
                    if {$property ni $IGNORED_PROPERTIES} {
                        lappend properties $property
                    }
                }

                lappend timing_line $speed_model
                lappend timing_line [llength $properties]
                foreach property $properties {
                    set value [get_property $property $speed_model]
                    set value_flat [join $value ""]
                    lappend timing_line "$property:$value_flat"
                }
            }
        }
    }


    puts $tile_pins_fp $tile_pins_line
    puts $pins_fp $pins_line
    puts $timing_fp [join $timing_line]
    puts $config_fp $config_line
}

proc dump {} {

    # Narrow the list of tile types to dump timings for
    set allowed_tile_types [list "CLEL_L" "CLEL_R" "CLEM" "CLEM_R" "CLE_M" "CLE_M_R" "BRAM" "URAM_URAM_FT"]

    set types [get_tile_types]
    set timing_fp [open "bel_timings.txt" w]
    set property_fp [open "bel_properties.txt" w]
    set pins_fp [open "bel_pins.txt" w]
    set tile_pins_fp [open "tile_pins.txt" w]
    foreach type $types {
        if {$type in $allowed_tile_types} {
            set tile [randsample_list 1 [get_tiles -filter "TYPE == $type"]]
            puts "Dumping timings for tile '$tile' of type '$type'"
            dump_tile_timings $tile $timing_fp $property_fp $pins_fp $tile_pins_fp
        }
    }

    # Don't do that for now
    #    set other_site_types [list ISERDESE2 OSERDESE2]
    #    foreach site_type $other_site_types {
    #        set cell [create_cell -reference $site_type test]
    #        place_design
    #        set tile [get_tiles -of [get_sites -of $cell]]
    #        dump_tile_timings $tile $timing_fp $property_fp $pins_fp $tile_pins_fp
    #        unplace_cell $cell
    #        remove_cell $cell
    #    }

    close $pins_fp
    close $timing_fp
    close $property_fp

    # Dump library cells too
    set cell_pins_fp [open "cell_pins.txt" w]
    dump_lib_cells $cell_pins_fp
    close $cell_pins_fp
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
