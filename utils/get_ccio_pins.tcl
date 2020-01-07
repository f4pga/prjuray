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

proc write_ccio_pins {filename} {
    set fp [open $filename "w"]

    foreach pin [get_package_pins -filter {IS_GLOBAL_CLK == 1 && IS_MASTER == 1}] {
        puts $fp "$pin,[get_sites -of $pin]"
    }

    close $fp
}

write_ccio_pins ../ccio_pins.csv
