# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

create_project -force -part $::env(URAY_PART) design design
set_property design_mode PinPlanning [current_fileset]
open_io_design -name io_1

proc get_pins {filename} {
    set fp [open $filename "w"]

    puts $fp "pin,bank,pin_function,site_name,site_type,iol_site,tile,tile_type"
    foreach pin [get_package_pins -filter "IS_GENERAL_PURPOSE == 1"] {
        set bank [get_iobanks -of $pin]
        set pin_function [get_property PIN_FUNC $pin]
        set site_name [get_sites -of $pin]
        set tile [get_tiles -of $site_name]
        set tile_type [get_property TYPE $tile]
        set site_type [get_property SITE_TYPE $site_name]

        set site_pin [get_site_pins $site_name/OP]
        set node [get_nodes -of $site_pin]
        set iol_site [get_sites -of [get_site_pins -of [get_nodes -of [get_pips -of $node -uphill] -uphill]]]
        puts $fp "$pin,$bank,$pin_function,$site_name,$site_type,$iol_site,$tile,$tile_type"
    }

    close $fp
}

get_pins ../iopins.csv
