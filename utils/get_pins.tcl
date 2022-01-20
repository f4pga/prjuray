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
