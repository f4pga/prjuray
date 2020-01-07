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

proc get_bufce_leaf_clock_regions {filename} {
    set fp [open $filename "w"]

    puts $fp "site,tile,clock_region"
    foreach site [get_sites -filter "SITE_TYPE == BUFCE_LEAF"] {
        set tile [get_tiles -of $site]
        set clock_region [get_property CLOCK_REGION $site]
        puts $fp "$site,$tile,$clock_region"
    }

    close $fp
}

get_bufce_leaf_clock_regions ../bufce_leaf_clock_regions.csv
