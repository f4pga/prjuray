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

set fp [open $::env(URAY_PART)_package_pins.csv w]
puts $fp "pin,bank,site,tile,pin_function"
foreach pin [get_package_pins] {
    set site [get_sites -quiet -of_object $pin]
    if { $site == "" } {
        continue
    }

    set tile [get_tiles -of_object $site]
    set pin_bank [get_property BANK [get_package_pins $pin]]
    set pin_function [get_property PIN_FUNC [get_package_pins $pin]]

    puts $fp "$pin,$pin_bank,$site,$tile,$pin_function"
}
