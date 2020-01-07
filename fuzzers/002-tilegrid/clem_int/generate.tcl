# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

source "$::env(URAY_DIR)/utils/utils.tcl"

proc run {} {
    create_project -force -part $::env(URAY_PART) design design
    read_verilog top.v
    synth_design -top top

    set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]

    set_property BEL C6LUT [get_cells lutc_* -filter "REF_NAME == LUT6"]
    set_property IS_BEL_FIXED 1 [get_cells lutc_* -filter "REF_NAME == LUT6"]

    set_property BEL D6LUT [get_cells lutd_* -filter "REF_NAME == LUT6"]
    set_property IS_BEL_FIXED 1 [get_cells lutd_* -filter "REF_NAME == LUT6"]

    place_design -directive Quick
    route_design -directive Quick

    write_checkpoint -force design.dcp
    write_bitstream -force design.bit
}

run
