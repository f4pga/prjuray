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

proc write_invpips {filename} {
    set fp [open $filename "w"]

    foreach pip [get_pips -filter {IS_FIXED_INVERSION == 1}] {
        puts $fp $pip
    }

    close $fp
}

write_invpips ../invpips.txt
