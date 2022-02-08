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

open_checkpoint design.dcp

source $::env(URAY_DIR)/tools/dump_features.tcl

proc dump_features_to_file {output_file} {
    set start_time [clock seconds]
    puts "[now] Gather features"
    set filter_bram 1
    set filter_int 0
    set sitefeatures_by_tile [dict create]
    set pips_by_tile [dump_pips $filter_bram $filter_int]

    lappend tiles [get_tiles -quiet -filter {TYPE == INT}]

    output_features_to_file $output_file $tiles $pips_by_tile $sitefeatures_by_tile

    set end_time [clock seconds]
    puts "[now] Done, took [expr $end_time - $start_time] seconds!"
}

dump_features_to_file design.features
