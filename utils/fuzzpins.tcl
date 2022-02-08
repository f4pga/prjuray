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

set gnd_pips [get_pips -of_objects [get_nets <const0>]]
set vcc_pips [get_pips -of_objects [get_nets <const1>]]

foreach site [get_sites -filter {SITE_TYPE == BITSLICE_RX_TX && IS_USED == FALSE} ] {
    if { rand() > 0.2 } {
        continue
    }
    if {[llength [get_nets -of_objects [get_nodes -of_objects [get_site_pins -of_objects $site]]]] > 0} {
        continue
    }
    set gnd_route 0
    foreach rtpip [get_pips -of_objects [get_nodes -of_objects [get_site_pins -of_objects $site]]]] {
        if {[lsearch $gnd_pips $rtpip] != -1} {
            set gnd_route 1
        }
        if {[lsearch $vcc_pips $rtpip] != -1} {
            set gnd_route 1
        }
    }
    if {$gnd_route == 1} {
        continue
    }
    set sn [get_property NAME $site]
    if { rand() > 0.5 } {
        create_cell -reference IDELAYE3 "IDELAY_$sn"
        if {[catch {place_cell  "IDELAY_$sn" "$sn/IDELAY"}]} {
            remove_cell "IDELAY_$sn"
            continue
        }
    } else {
        create_cell -reference OSERDESE3 "OSERDES_$sn"
        if {[catch {place_cell  "OSERDES_$sn" "$sn/OSERDES"}]} {
            remove_cell "OSERDES_$sn"
            continue
        }
    }
    set_property MANUAL_ROUTING TRUE $site
    set sitepips [get_property SITE_PIPS $site]
    foreach sp [get_site_pips -of_objects $site] {
        if { rand() > 0.2 } {
            continue
        }
        if {[string match "*OPTINV*" $sp]} {
            continue
        }
        regex {([A-Z0-9_]+)/([A-Z0-9_]+):([A-Z0-9_]+)} $sp match sp_site sp_bel sp_pin
        if {[string first $sp_bel $sitepips] != -1} {
            continue
        }
        puts $sp
        append sitepips " " $sp_bel ":" $sp_pin
    }
    set_property SITE_PIPS $sitepips $site
}
set_property SEVERITY {Warning} [get_drc_checks AVAL-*]
set_property SEVERITY {Warning} [get_drc_checks REQP-*]
set_property SEVERITY {Warning} [get_drc_checks BIVR-*]
set_property SEVERITY {Warning} [get_drc_checks BSCK-*]
set_property SEVERITY {Warning} [get_drc_checks PLHDIO-1]
set_property SEVERITY {Warning} [get_drc_checks PDRC-203]
set_property SEVERITY {Warning} [get_drc_checks ADEF-911]
