#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
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

import csv
import numpy as np
import sys

# LIMITED_STANDARDS is set to use fewer IOSTANDARD's initially to reduce
# required sample counts.
from utils.io_utils import bank_planner2, read_io_pins, \
        choose_iobank_voltage_uniform_by_iostandard, \
        primatives_for_bank, \
        iostandards_for_bank_and_voltage, \
        DRIVES, \
        SINGLE_ENDED_STANDARDS


def print_top(seed, fout=sys.stdout, offset=0):
    np.random.seed(0)

    pins = []
    bank_to_pins = {}
    bank_to_iotype = {}
    site_to_pin = {}
    pin_to_pin_idx = {}
    pin_to_tiles = {}

    with open("../iopins.csv", "r") as iof:
        bank_type_to_tiles, tile_to_pins, pin_to_banks, pin_to_site_offsets, pin_to_tile_types = read_io_pins(
            iof)

    with open("../iopins.csv", "r") as iof:
        for row in csv.DictReader(iof):
            pin = row['pin']
            bank = int(row['bank'])
            func = row['pin_function']
            site_name = row['site_name']
            site_type = row['site_type']
            tile = row['tile']

            if "VREF" in func:
                continue  # conflict

            if "VRP" in func or "VRN" in func:
                continue  # conflict

            pins.append((pin, bank, func, site_name, site_type))
            pin_to_pin_idx[pin] = len(pins) - 1

            if bank not in bank_to_pins:
                bank_to_pins[bank] = []
            bank_to_pins[bank].append(pin)

            if bank not in bank_to_iotype:
                bank_to_iotype[bank] = site_type.split("_")[0]
            site_to_pin[site_name] = pin

            assert pin not in pin_to_tiles
            pin_to_tiles[pin] = tile

    used_pins = []
    io_config = []

    bank_to_vcc = {}
    bank_pod_used = set()
    bank_pod_not_used = set()
    lut_inputs = []
    lut_outputs = []
    bank_iref = {}
    pin_to_bank_type = {}

    def inp():
        sig = "li[%d]" % len(lut_inputs)
        lut_inputs.append(sig)
        return sig

    def outp():
        sig = "lo[%d]" % len(lut_outputs)
        lut_outputs.append(sig)
        return sig

    def maybe_inp(pin):
        return inp() if np.random.choice([True, False]) else ""

    def maybe_outp(pin):
        if pin_to_bank_type[pin] == 'HDIOB' and (offset % 2) == 1:
            return ""
        else:
            return outp() if np.random.choice([True, False]) else ""

    bank_type_plan = {}

    bank_plan_idx = {}

    for bank_type in sorted(bank_type_to_tiles):
        pins_in_bank_type = []
        for tile in bank_type_to_tiles[bank_type]:
            for pin in tile_to_pins[tile]:
                if pin not in pin_to_pin_idx:
                    continue

                pins_in_bank_type.append(pin)

                assert pin not in pin_to_bank_type
                pin_to_bank_type[pin] = bank_type

        for idx, plan in enumerate(
                bank_planner2(
                    random_lib=np.random,
                    bank_type=bank_type,
                    single_ended=True,
                    pins=pins_in_bank_type,
                    pin_to_banks=pin_to_banks,
                    pin_to_site_offsets=pin_to_site_offsets,
                    pin_to_tile_types=pin_to_tile_types,
                    pin_to_tiles=pin_to_tiles,
                )):

            if bank_type == 'HDIOB':
                if idx == (offset // 2):
                    bank_plan_idx[bank_type] = idx
                    bank_type_plan[bank_type] = dict(plan)
            else:
                if idx == offset:
                    bank_plan_idx[bank_type] = idx
                    bank_type_plan[bank_type] = dict(plan)

    np.random.seed(seed)
    bank_to_vcc = choose_iobank_voltage_uniform_by_iostandard(
        bank_to_iotype, SINGLE_ENDED_STANDARDS, DRIVES, np.random)

    for bank_type in sorted(bank_plan_idx):
        print('// {}[{:03d}]'.format(bank_type, bank_plan_idx[bank_type]))

    for (pin, bank, func, sn, st) in pins:
        iot = st.split("_")[0]
        bank_type = iot

        if bank_type in bank_type_plan:
            assert pin in bank_type_plan[bank_type], (
                pin, bank_type_plan[bank_type].keys())
            config = bank_type_plan[bank_type][pin]
            if config is None:
                print('// {} X_OFFSET="{}"'.format(pin,
                                                   pin_to_site_offsets[pin]))
                continue
            _, ios, prim, params = config

            print('// {} X_OFFSET="{}" {} {} {}'.format(
                pin, pin_to_site_offsets[pin], ios, prim, bank))

            params["IOSTANDARD"] = ios
            params["prim"] = prim
        else:
            params = {}
            ios = np.random.choice(
                iostandards_for_bank_and_voltage(
                    iot, bank_to_vcc[bank], single_ended=True))
            if bank in bank_pod_used and ios in ("HSTL_I_12", "HSTL_I_DCI_12",
                                                 "SSTL12", "SSTL12_DCI",
                                                 "HSUL_12", "HSUL_12_DCI"):
                ios = "LVCMOS12"
            if bank in bank_pod_not_used and ios in ("POD12", "POD12_DCI"):
                ios = "LVCMOS12"
            params["IOSTANDARD"] = ios
            prim = np.random.choice(
                primatives_for_bank(bank_type, single_ended=True))
            params["prim"] = prim
            print('//', pin, ios, bank_type, prim)

            if prim in ("OBUF", "OBUFT", "IOBUF", "IOBUFE3"):
                if (iot, ios) in DRIVES:
                    params["DRIVE"] = np.random.choice(DRIVES[iot, ios])
                if iot == "HPIOB":
                    params["SLEW"] = np.random.choice(
                        ["SLOW", "MEDIUM", "FAST"])
                else:
                    params["SLEW"] = np.random.choice(["SLOW", "FAST"])

        if prim in ("IBUF", "IOBUF", "IOBUFE3", "IBUF_IBUFDISABLE",
                    "IBUF_INTERMDISABLE"):
            params["PULLTYPE"] = np.random.choice(
                ["NONE", "PULLUP", "PULLDOWN", "KEEPER"])

        if prim in ("IBUF", "IOBUF", "IOBUFE3", "IBUF_IBUFDISABLE",
                    "IBUF_INTERMDISABLE"):
            if "POD" in ios:
                odt_choices = []
                if "DCI" not in ios:
                    odt_choices.append("RTT_NONE")

                if "OUTPUT_IMPEDANCE" not in params or params[
                        "OUTPUT_IMPEDANCE"] != "RDRV_48_48":
                    odt_choices += ["RTT_40", "RTT_60"]
                else:
                    odt_choices += ["RTT_48"]

                params["ODT"] = np.random.choice(odt_choices)
                if "POD12" in ios:
                    params["EQUALIZATION"] = np.random.choice([
                        "EQ_LEVEL0", "EQ_LEVEL1", "EQ_LEVEL2", "EQ_LEVEL3",
                        "EQ_LEVEL4", "EQ_NONE"
                    ])

        used_pins.append(pin)
        io_config.append(params)
        if iot == "HDIOB":
            if ios in ("HSTL_I_18", "SSTL18_I", "SSTL18_II"):
                bank_iref[bank] = "0.90"
            elif ios in ("HSTL_I", "SSTL15", "SSTL15_II"):
                bank_iref[bank] = "0.75"
            elif ios in ("SSTL135", "SSTL135_II"):
                bank_iref[bank] = "0.675"
            elif ios == "SSTL12":
                bank_iref[bank] = "0.60"
        if ios in ("POD12", "POD12_DCI"):
            bank_pod_used.add(bank)
            bank_iref[bank] = np.random.choice([None, "0.84"])
        if ios in ("HSTL_I_12", "HSTL_I_DCI_12", "SSTL12", "SSTL12_DCI",
                   "HSUL_12", "HSUL_12_DCI"):
            bank_pod_not_used.add(bank)
            bank_iref[bank] = np.random.choice([None, "0.60"])

    print("module top(", file=fout)
    for i, params in enumerate(io_config):
        prim = params["prim"]
        bank = pin_to_banks[used_pins[i]]
        if bank in bank_iref and bank_iref[bank] is not None:
            params["internal_vref"] = bank_iref[bank]
        print(
            "(* %s, %s, %s *)" %
            ('X_PIN="{}"'.format(used_pins[i]), 'X_OFFSET="{}"'.format(
                pin_to_site_offsets[used_pins[i]]), ", ".join(
                    'X_%s="%s"' % (k, v) for k, v in sorted(params.items()))),
            file=fout)
        if prim in ("IBUF", "IBUF_IBUFDISABLE"):
            print(
                "input p%d%s" % (i, "," if i < len(io_config) - 1 else ""),
                file=fout)
        elif prim in ("OBUF", "OBUFT"):
            print(
                "output p%d%s" % (i, "," if i < len(io_config) - 1 else ""),
                file=fout)
        elif prim in ("IOBUF", "IOBUFE3"):
            print(
                "inout p%d%s" % (i, "," if i < len(io_config) - 1 else ""),
                file=fout)
    print(");", file=fout)
    for i, (pin, params) in enumerate(zip(used_pins, io_config)):
        print("(* KEEP, DONT_TOUCH *)", file=fout)
        prim = params["prim"]
        if prim == "IBUF":
            print(
                """
                IBUF buf_{i} (
                    .I(p{i}),
                    .O({sig_o})
                );
            """.format(i=i, sig_o=maybe_inp(pin)),
                file=fout)
        elif prim == "OBUF":
            print(
                """
                OBUF buf_{i} (
                    .O(p{i}),
                    .I({sig_i})
                );
            """.format(i=i, sig_i=maybe_outp(pin)),
                file=fout)
        elif prim == "OBUFT":
            print(
                """
                OBUFT buf_{i} (
                    .O(p{i}),
                    .T({sig_t}),
                    .I({sig_i})
                );
            """.format(i=i, sig_t=outp(), sig_i=maybe_outp(pin)),
                file=fout)
        elif prim == "IOBUF":
            print(
                """
                IOBUF buf_{i} (
                    .IO(p{i}),
                    .T({sig_t}),
                    .I({sig_i}),
                    .O({sig_o})
                );
            """.format(
                    i=i,
                    sig_t=maybe_outp(pin),
                    sig_i=maybe_outp(pin),
                    sig_o=maybe_inp(pin)),
                file=fout)
        elif prim == "IBUF_IBUFDISABLE":
            print(
                """
                IBUF_IBUFDISABLE buf_{i} (
                    .I(p{i}),
                    .O({sig_o}),
                    .IBUFDISABLE({ibuf_dis})
                );
            """.format(i=i, sig_o=maybe_inp(pin), ibuf_dis=maybe_outp(pin)),
                file=fout)
        elif prim == "IOBUFE3":
            if np.random.choice([True, False]):
                print("(* KEEP, DONT_TOUCH *)", file=fout)
            print(
                """
                IOBUFE3 buf_{i} (
                    .IO(p{i}),
                    .T({sig_t}),
                    .I({sig_i}),
                    .O({sig_o}),
                    .DCITERMDISABLE({dci_dis}),
                    .IBUFDISABLE({ibuf_dis})
                );
            """.format(
                    i=i,
                    sig_t=maybe_outp(pin),
                    sig_i=maybe_outp(pin),
                    sig_o=maybe_inp(pin),
                    dci_dis=maybe_outp(pin),
                    ibuf_dis=maybe_outp(pin)),
                file=fout)
        print("", file=fout)
    print("wire [%d:0] li;" % (len(lut_inputs) - 1), file=fout)
    print("wire [%d:0] lo;" % (len(lut_outputs) - 1), file=fout)

    for i in range(max(len(lut_inputs) // 6 + 1, len(lut_outputs))):
        ip = [
            "1'b0" if
            (i * 6 + j) >= len(lut_inputs) else "li[%d]" % (i * 6 + j)
            for j in range(6)
        ]
        op = "lo[%d]" % i if i < len(lut_outputs) else ""
        print(
            """
            (* KEEP, DONT_TOUCH *)
            LUT6 lut{i} (.I0({i0}), .I1({i1}), .I2({i2}), .I3({i3}), .I4({i4}), .I5({i5}), .O({o}));
            """.format(
                i=i,
                i0=ip[0],
                i1=ip[1],
                i2=ip[2],
                i3=ip[3],
                i4=ip[4],
                i5=ip[5],
                o=op,
            ),
            file=fout)
    print("endmodule", file=fout)

    with open('top.xdc', 'w') as f:
        for i, params in enumerate(io_config):
            pin = used_pins[i]
            print(
                "set_property PACKAGE_PIN %s [get_ports {p%d}]" % (pin, i),
                file=f)
            for k, v in sorted(params.items()):
                if k.isupper():
                    print(
                        "set_property %s %s [get_ports {p%d}]" % (k, v, i),
                        file=f)
        for bank, iref in sorted(bank_iref.items()):
            if iref is None:
                continue
            print(
                "set_property INTERNAL_VREF {%s} [get_iobanks %d]" % (iref,
                                                                      bank),
                file=f)

    with open('complete_top.tcl', 'w') as f:
        print(
            "set_property SEVERITY {Warning} [get_drc_checks NSTD-1]", file=f)
        print(
            "set_property SEVERITY {Warning} [get_drc_checks UCIO-1]", file=f)
        print(
            "set_property SEVERITY {Warning} [get_drc_checks AVAL-*]", file=f)
        print(
            "set_property SEVERITY {Warning} [get_drc_checks REQP-*]", file=f)
        print(
            "set_property SEVERITY {Warning} [get_drc_checks BIVR-*]", file=f)
        print(
            "set_property SEVERITY {Warning} [get_drc_checks PLHDIO-1]",
            file=f)
        print("opt_design", file=f)
        print("place_design", file=f)
        print("route_design", file=f)
