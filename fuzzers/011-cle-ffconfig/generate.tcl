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

create_project -force -part $::env(URAY_PART) design design
read_verilog top.v
synth_design -top top

set_property -dict "PACKAGE_PIN $::env(URAY_PIN_00) IOSTANDARD LVCMOS33" [get_ports clk]

create_pblock roi

set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]
set_param tcl.collectionResultDisplayLimit 0

set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets clk_IBUF]
set_property IS_ENABLED 0 [get_drc_checks {NDRV-1}]
set_property IS_ENABLED 0 [get_drc_checks {UCIO-1}]
set_property IS_ENABLED 0 [get_drc_checks {NSTD-1}]
set_property IS_ENABLED 0 [get_drc_checks {RTSTAT-4}]
set_property IS_ENABLED 0 [get_drc_checks {RTSTAT-6}]
set_property IS_ENABLED 0 [get_drc_checks {RTSTAT-10}]

place_design -directive Quick
route_design -directive Quick

write_checkpoint -force design.dcp
write_bitstream -force design.bit

# Get all FF's in pblock
set ffs [get_bels -filter {TYPE =~ *} */*FF]

set fp [open "design.txt" w]
# set ff [lindex $ffs 0]
# set ff [get_bels SLICE_X23Y100/AFF]
# proc putl {lst} { foreach line $lst {puts $line} }
foreach ff $ffs {
    # Tile information
    set tile [get_tile -of_objects $ff]
    set type [get_property TYPE $tile]

    # Location information
    set grid_x [get_property GRID_POINT_X $tile]
    set grid_y [get_property GRID_POINT_Y $tile]

    # FF BEL information
    set bel_type [get_property TYPE $ff]
    set used [get_property IS_USED $ff]
    set usedstr ""

    if $used {
        set ffc [get_cells -of_objects $ff]
        set cell_bel [get_property BEL $ffc]

        # ex: FDRE
        set ref_name [get_property REF_NAME $ffc]

        # Flip-Flops : have CLOCK pin
        # Latches    : have GATE pin
        set cpin [get_pins -of_objects $ffc -filter {REF_PIN_NAME == C || REF_PIN_NAME == G}]
        set cinv [get_property IS_INVERTED $cpin]

        set init [get_property INIT $ffc]

        set usedstr "$cell_bel $ref_name $cinv $init"
    }
    puts $fp "$type $tile $grid_x $grid_y $ff $bel_type $used $usedstr"
}
close $fp
