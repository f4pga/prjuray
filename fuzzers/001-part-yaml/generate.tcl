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

proc extract_iobanks {filename} {
    set fp [open $filename "w"]
    foreach iobank [get_iobanks] {
        set sample_site [lindex [get_sites -of $iobank] 0]
        if {[llength $sample_site] == 0} continue
        set clock_region [get_property CLOCK_REGION $sample_site]
        foreach tile [get_tiles -filter {TYPE=~HCLK_IOI3}] {
            set tile_sites [get_sites -of_object $tile]
            if {[llength $tile_sites] == 0} continue
            set hclk_tile_clock_region [get_property CLOCK_REGION [lindex [get_sites -of_object $tile] 0]]
            if {$clock_region == $hclk_tile_clock_region} {
                set coord [lindex [split $tile "_"] 2]
                puts $fp "$iobank,$coord"
            }
        }
    }
    close $fp
}

create_project -force -part $::env(URAY_PART) design design

read_verilog ../../top.v
synth_design -top top

set_property -dict "PACKAGE_PIN $::env(URAY_PIN_00) IOSTANDARD LVCMOS33" [get_ports clk]
set_property -dict "PACKAGE_PIN $::env(URAY_PIN_01) IOSTANDARD LVCMOS33" [get_ports di]
set_property -dict "PACKAGE_PIN $::env(URAY_PIN_02) IOSTANDARD LVCMOS33" [get_ports do]
set_property -dict "PACKAGE_PIN $::env(URAY_PIN_03) IOSTANDARD LVCMOS33" [get_ports stb]

set_param tcl.collectionResultDisplayLimit 0

place_design
route_design

extract_iobanks iobanks.txt
write_checkpoint -force design.dcp

# Write a normal bitstream that will do a singe FDRI write of all the frames.
write_bitstream -force design.bit

# Write a perframecrc bitstream which writes each frame individually followed by
# the frame address.  This shows where there are gaps in the frame address
# space.
set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]
write_bitstream -force design.perframecrc.bit
set_property BITSTREAM.GENERAL.PERFRAMECRC NO [current_design]
