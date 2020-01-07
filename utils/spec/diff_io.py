#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2020 Project U-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file.
#
# SPDX-License-Identifier: ISC

import csv
import numpy as np
import sys
from utils.io_utils import choose_iobank_voltage_uniform_by_iostandard

# Use fewer IOSTANDARD's initially to reduce required sample counts.
LIMITED_STANDARDS = True


def print_top(seed, fout=sys.stdout):
    np.random.seed(seed)

    pins = []
    bank_to_pins = {}
    tile_to_pins = {}
    bank_to_iotype = {}
    site_to_pin = {}
    pin_to_bank = {}
    with open("../iopins.csv", "r") as iof:
        for row in csv.DictReader(iof):
            pin = row['pin']
            bank = int(row['bank'])
            func = row['pin_function']
            site_name = row['site_name']
            site_type = row['site_type']
            tile = row['tile']

            pins.append((pin, bank, func, site_name, site_type))
            if bank not in bank_to_pins:
                bank_to_pins[bank] = []
            bank_to_pins[bank].append(pin)

            if tile not in tile_to_pins:
                tile_to_pins[tile] = []
            tile_to_pins[tile].append(pin)

            pin_to_bank[pin] = bank
            if bank not in bank_to_iotype:
                bank_to_iotype[bank] = site_type.split("_")[0]
            site_to_pin[site_name] = pin

    used_pins = []
    io_config = []

    bank_to_vcc = {}
    bank_pod_used = set()
    bank_pod_not_used = set()
    lut_inputs = []
    lut_outputs = []
    bank_iref = {}

    def inp():
        sig = "li[%d]" % len(lut_inputs)
        lut_inputs.append(sig)
        return sig

    def outp():
        sig = "lo[%d]" % len(lut_outputs)
        lut_outputs.append(sig)
        return sig

    def maybe_inp():
        return inp() if np.random.choice([True, False]) else ""

    def maybe_outp():
        return outp() if np.random.choice([True, False]) else ""

    if LIMITED_STANDARDS:
        standards = {
            ("HPIOB", "1.8"): ["DIFF_SSTL18_I", "LVDS"],
            ("HPIOB", "1.5"): ["DIFF_SSTL15", "DIFF_SSTL15_DCI"],
            ("HPIOB", "1.35"): ["DIFF_SSTL135", "DIFF_SSTL135_DCI"],
            ("HPIOB", "1.2"): ["DIFF_SSTL12", "DIFF_POD12", "DIFF_POD12_DCI"],
            ("HPIOB", "1.0"): ["DIFF_POD10", "DIFF_POD10_DCI"],
        }
    else:
        standards = {
            ("HPIOB", "1.8"):
            ["DIFF_SSTL18_I", "DIFF_SSTL18_I_DCI", "SLVS_400_18", "LVDS"],
            ("HPIOB", "1.5"): ["DIFF_SSTL15", "DIFF_SSTL15_DCI"],
            ("HPIOB", "1.35"): ["DIFF_SSTL135", "DIFF_SSTL135_DCI"],
            ("HPIOB", "1.2"): [
                "DIFF_SSTL12", "DIFF_SSTL12_DCI", "DIFF_HSUL_12",
                "DIFF_HSUL_12_DCI", "DIFF_POD12", "DIFF_POD12_DCI"
            ],
            ("HPIOB", "1.0"): ["DIFF_POD10", "DIFF_POD10_DCI"],
        }

    prims = {
        "HPIOB": ["IBUFDS", "OBUFDS", "OBUFTDS", "IOBUFDS", "IOBUFDSE3"],
        #"HDIOB": ["IBUF","OBUF", "OBU", "IOBUF"]
    }

    drives = {}

    bank_to_vcc = choose_iobank_voltage_uniform_by_iostandard(
        bank_to_iotype, standards, drives, np.random)

    # 1 or 2 pins per tile to provide clear decoupling.
    skipped_pins = set()

    for tile in tile_to_pins:
        tile_pins = sorted(tile_to_pins[tile])
        np.random.shuffle(tile_pins)

        for _ in range(np.random.randint(1, 3)):
            skipped_pins.add(tile_pins.pop())

    for (pin, bank, func, sn, st) in pins:
        if pin in skipped_pins:
            continue

        if "VREF" in func:
            continue  # conflict

        if "VRP" in func or "VRN" in func:
            continue  # conflict

        if "HPIOB_M" not in st:
            continue

        if np.random.choice([True, False]):
            continue  # improved fuzzing

        params = {}
        iot = st.split("_")[0]
        assert (iot, bank_to_vcc[bank]) in standards, (pin, bank, iot,
                                                       bank_to_vcc[bank])
        ios = np.random.choice(standards[iot, bank_to_vcc[bank]])
        if bank in bank_pod_used and ios in (
                "DIFF_HSTL_I_12", "DIFF_HSTL_I_DCI_12", "DIFF_SSTL12",
                "DIFF_SSTL12_DCI", "DIFF_HSUL_12", "DIFF_HSUL_12_DCI"):
            continue
        if bank in bank_pod_not_used and ios in ("DIFF_POD12",
                                                 "DIFF_POD12_DCI"):
            continue
        params["IOSTANDARD"] = ios
        prim = np.random.choice(prims[iot])

        if ios == "SLVS_400_18":
            prim = "IBUFDS"

        params["prim"] = prim
        if prim in ("OBUFDS", "OBUFTDS", "IOBUFDS", "IOBUFDSE3"):
            if iot == "HPIOB":
                params["SLEW"] = np.random.choice(["SLOW", "MEDIUM", "FAST"])
            else:
                params["SLEW"] = np.random.choice(["SLOW", "FAST"])
            if iot == "HPIOB" and ("POD" in ios or "SSTL" in ios):
                params["OUTPUT_IMPEDANCE"] = np.random.choice(
                    ["RDRV_40_40", "RDRV_48_48", "RDRV_60_60"])
        if prim in ("IBUFDS", "IOBUFDS", "IOBUFDSE3", "IBUFDS_IBUFDISABLE",
                    "IBUFDS_INTERMDISABLE"):
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
            if "LVDS" in ios or "SLVS" in ios:
                params["DIFF_TERM_ADV"] = np.random.choice(
                    ["TERM_NONE", "TERM_100"])
        used_pins.append(pin)
        io_config.append(params)

        if ios in ("DIFF_POD12", "DIFF_POD12_DCI"):
            bank_pod_used.add(bank)
        if ios in ("DIFF_HSTL_I_12", "DIFF_HSTL_I_DCI_12", "DIFF_SSTL12",
                   "DIFF_SSTL12_DCI", "DIFF_HSUL_12", "DIFF_HSUL_12_DCI"):
            bank_pod_not_used.add(bank)

    print("module top(", file=fout)
    for i, params in enumerate(io_config):
        prim = params["prim"]
        bank = pin_to_bank[used_pins[i]]
        if bank in bank_iref and bank_iref[bank] is not None:
            params["int_vref"] = bank_iref[bank]
        print(
            "(* %s *)" % ", ".join('X_%s="%s"' % (k, v)
                                   for k, v in sorted(params.items())),
            file=fout)
        if prim in ("IBUFDS", "IBUFDS_IBUFDISABLE"):
            print(
                "input p%d, pn%d%s" % (i, i,
                                       "," if i < len(io_config) - 1 else ""),
                file=fout)
        elif prim in ("OBUFDS", "OBUFTDS"):
            print(
                "output p%d, pn%d%s" % (i, i,
                                        "," if i < len(io_config) - 1 else ""),
                file=fout)
        elif prim in ("IOBUFDS", "IOBUFDSE3"):
            print(
                "inout p%d, pn%d%s" % (i, i,
                                       "," if i < len(io_config) - 1 else ""),
                file=fout)
    print(");", file=fout)
    for i, params in enumerate(io_config):
        print("(* KEEP, DONT_TOUCH *)", file=fout)
        prim = params["prim"]
        if prim == "IBUFDS":
            print(
                """
                IBUFDS buf_{i} (
                    .I(p{i}), .IB(pn{i}),
                    .O({sig_o})
                );
            """.format(i=i, sig_o=maybe_inp()),
                file=fout)
        elif prim == "OBUFDS":
            print(
                """
                OBUFDS buf_{i} (
                    .O(p{i}), .OB(pn{i}),
                    .I({sig_i})
                );
            """.format(i=i, sig_i=maybe_outp()),
                file=fout)
        elif prim == "OBUFTDS":
            print(
                """
                OBUFTDS buf_{i} (
                    .O(p{i}), .OB(pn{i}),
                    .T({sig_t}),
                    .I({sig_i})
                );
            """.format(i=i, sig_t=outp(), sig_i=maybe_outp()),
                file=fout)
        elif prim == "IOBUFDS":
            print(
                """
                IOBUFDS buf_{i} (
                    .IO(p{i}), .IOB(pn{i}),
                    .T({sig_t}),
                    .I({sig_i}),
                    .O({sig_o})
                );
            """.format(
                    i=i,
                    sig_t=maybe_outp(),
                    sig_i=maybe_outp(),
                    sig_o=maybe_inp()),
                file=fout)
        elif prim == "IOBUFDSE3":
            if np.random.choice([True, False]):
                print("(* KEEP, DONT_TOUCH *)", file=fout)
            print(
                """
                IOBUFDSE3 buf_{i} (
                    .IO(p{i}), .IOB(pn{i}),
                    .T({sig_t}),
                    .I({sig_i}),
                    .O({sig_o}),
                    .DCITERMDISABLE({dci_dis}),
                    .IBUFDISABLE({ibuf_dis})
                );
            """.format(
                    i=i,
                    sig_t=maybe_outp(),
                    sig_i=maybe_outp(),
                    sig_o=maybe_inp(),
                    dci_dis=maybe_outp(),
                    ibuf_dis=maybe_outp()),
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
