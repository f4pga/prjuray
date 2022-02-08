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

proc write_ccio_pins {filename} {
    set fp [open $filename "w"]

    foreach pin [get_package_pins -filter {IS_GLOBAL_CLK == 1 && IS_MASTER == 1}] {
        puts $fp "$pin,[get_sites -of $pin]"
    }

    close $fp
}

write_ccio_pins ../ccio_pins.csv
