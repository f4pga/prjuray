# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

create_project -force -part $::env(URAY_PART) design design

read_verilog top.v
synth_design -top top

write_checkpoint -force design_presource.dcp
source top.tcl

set_property IS_ENABLED 0 [get_drc_checks {UCIO-1}]
set_property IS_ENABLED 0 [get_drc_checks {NSTD-1}]
set_property IS_ENABLED 0 [get_drc_checks {PDCY-1}]
set_property IS_ENABLED 0 [get_drc_checks {PDCN-1567}]
set_property IS_ENABLED 0 [get_drc_checks {UCIO-1}]


set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]
set_param tcl.collectionResultDisplayLimit 0

write_checkpoint -force design_preplace.dcp

source complete_top.tcl

write_checkpoint -force design.dcp
write_edif -force design.edif
write_bitstream  -force design.bit
