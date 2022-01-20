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
