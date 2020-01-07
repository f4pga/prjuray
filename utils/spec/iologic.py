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


def make_ioff(name, sig_c, sig_d, sig_r, sig_e, sig_q, f):
    sr_sig = {
        "FDRE": "R",
        "FDSE": "S",
        "FDPE": "PRE",
        "FDCE": "CLR",
    }

    fftype = np.random.choice(["FDRE", "FDSE", "FDPE", "FDCE"])
    print(
        """
        {t} #(.INIT({init})) {n} (
            .C({c}), .{sr}({r}), .CE({e}), .D({d}), .Q({q})
        );
        """.format(
            t=fftype,
            init=np.random.randint(0, 2),
            n=name,
            sr=sr_sig[fftype],
            c=sig_c,
            r=sig_r,
            e=sig_e,
            d=sig_d,
            q=sig_q),
        file=f)


def make_iddr(name, allow_inv, sig_c, sig_cb, sig_r, sig_d, sig_q1, sig_q2, f):
    print(
        """
        IDDRE1 #(.DDR_CLK_EDGE("{e}"), .IS_C_INVERTED({ci}), .IS_CB_INVERTED({cbi})) {n} (
            .C({c}), .CB({cb}), .R({r}), .D({d}), .Q1({q1}), .Q2({q2})
        );
        """.format(
            e=np.random.choice(
                ["OPPOSITE_EDGE", "SAME_EDGE", "SAME_EDGE_PIPELINED"]),
            ci=np.random.randint(0, 2) if allow_inv else 0,
            cbi=np.random.randint(0, 2) if allow_inv else 1,
            n=name,
            c=sig_c,
            cb=sig_cb,
            r=sig_r,
            d=sig_d,
            q1=sig_q1,
            q2=sig_q2),
        file=f)


def make_oddr(name, srval, sig_c, c_inv, sig_d1, sig_d2, sig_sr, sig_q, f):
    print(
        """
        ODDRE1 #(.IS_C_INVERTED({ci}), .SRVAL({srv})) {n} (
            .C({c}), .D1({d1}), .D2({d2}), .SR({sr}), .Q({q})
        );
        """.format(
            ci=1 if c_inv else 0,
            srv=srval,
            n=name,
            c=sig_c,
            d1=sig_d1,
            d2=sig_d2,
            sr=sig_sr,
            q=sig_q),
        file=f)


def make_iserdes(name, sig_clk, sig_clkdiv, sig_clk_b, sig_d, sig_rst, sig_q,
                 f):
    print(
        """
        ISERDESE3 #(
            .DATA_WIDTH({dw}),
            .IS_CLK_B_INVERTED({cbi}),
            .IS_CLK_INVERTED({ci}),
            .IS_RST_INVERTED({ri})
        ) {n} (
            .Q({q}),
            .CLK({clk}), .CLKDIV({clkdiv}), .CLK_B({clk_b}), .D({d}), .RST({rst})
        );
    """.format(
            dw=np.random.choice([4, 8]),
            cbi=np.random.randint(0, 2),
            ci=np.random.randint(0, 2),
            ri=np.random.randint(0, 2),
            n=name,
            q=sig_q,
            clk=sig_clk,
            clkdiv=sig_clkdiv,
            clk_b=sig_clk_b,
            rst=sig_rst,
            d=sig_d),
        file=f)


def make_oserdes(name, sig_clk, sig_clkdiv, sig_d, sig_rst, sig_t, sig_oq,
                 sig_t_out, f):
    print(
        """
        OSERDESE3 #(
            .DATA_WIDTH({dw}),
            .INIT({init}),
            .IS_CLKDIV_INVERTED({cdi}),
            .IS_CLK_INVERTED({ci}),
            .IS_RST_INVERTED({ri}),
            .OSERDES_D_BYPASS("{db}"),
            .OSERDES_T_BYPASS("{dt}"),
            .ODDR_MODE("{oddr_mode}")
        ) {n} (
            .OQ({oq}), .T_OUT({t_out}),
            .CLK({clk}), .CLKDIV({clkdiv}), .D({d}), .RST({rst}), .T({t})
        );
    """.format(
            dw=np.random.choice([4, 8]),
            init=np.random.randint(0, 2),
            cdi=np.random.randint(0, 2),
            ci=np.random.randint(0, 2),
            ri=np.random.randint(0, 2),
            db=np.random.choice(["TRUE", "FALSE"]),
            dt=np.random.choice(["TRUE", "FALSE"]),
            oddr_mode=np.random.choice(["TRUE", "FALSE"]),
            n=name,
            oq=sig_oq,
            t_out=sig_t_out,
            clk=sig_clk,
            clkdiv=sig_clkdiv,
            d=sig_d,
            rst=sig_rst,
            t=sig_t,
        ),
        file=f)


def make_idelay(name, del_fmt, time_dly, sig_clk, sig_ce, sig_inc, sig_load,
                sig_rst, sig_en_vtc, sig_datain, sig_idatain, sig_dataout, f):
    print(
        """
        IDELAYE3 #(
            .DELAY_SRC("{ds}"),
            .DELAY_TYPE("{dt}"),
            .DELAY_VALUE({dv}),
            .DELAY_FORMAT("{df}"),
            .UPDATE_MODE("{um}"),
            .IS_CLK_INVERTED({ci}),
            .IS_RST_INVERTED({ri}),
            .LOOPBACK("{lb}"),
            .REFCLK_FREQUENCY(300.0)
        ) {n} (
            .CLK({clk}), .CE({ce}), .INC({inc}), .LOAD({load}), .RST({rst}), .EN_VTC({en_vtc}),
            .DATAIN({datain}), .IDATAIN({idatain}), .DATAOUT({dataout})
        );
    """.format(
            ds=np.random.choice(["DATAIN", "IDATAIN"]),
            dt=np.random.choice(["FIXED", "VAR_LOAD", "VARIABLE"]),
            dv=np.random.randint(0, 512) if del_fmt == "COUNT" else time_dly,
            df=del_fmt,
            um=np.random.choice(["ASYNC", "SYNC", "MANUAL"]),
            ci=np.random.randint(0, 2),
            ri=np.random.randint(0, 2),
            lb=np.random.choice(["FALSE", "TRUE"]),
            n=name,
            clk=sig_clk,
            ce=sig_ce,
            inc=sig_inc,
            load=sig_load,
            rst=sig_rst,
            en_vtc=sig_en_vtc,
            datain=sig_datain,
            idatain=sig_idatain,
            dataout=sig_dataout),
        file=f)


def make_odelay(name, del_fmt, time_dly, sig_clk, sig_ce, sig_inc, sig_load,
                sig_rst, sig_en_vtc, sig_odatain, sig_dataout, f):
    print(
        """
        ODELAYE3 #(
            .DELAY_TYPE("{dt}"),
            .DELAY_VALUE({dv}),
            .DELAY_FORMAT("{df}"),
            .UPDATE_MODE("{um}"),
            .IS_CLK_INVERTED({ci}),
            .IS_RST_INVERTED({ri}),
            .REFCLK_FREQUENCY(300.0)
        ) {n} (
            .CLK({clk}), .CE({ce}), .INC({inc}), .LOAD({load}), .RST({rst}), .EN_VTC({en_vtc}),
            .ODATAIN({odatain}), .DATAOUT({dataout})
        );
    """.format(
            dt=np.random.choice(["FIXED", "VAR_LOAD", "VARIABLE"]),
            dv=np.random.randint(0, 512) if del_fmt == "COUNT" else time_dly,
            df=del_fmt,
            um=np.random.choice(["ASYNC", "SYNC", "MANUAL"]),
            ci=np.random.randint(0, 2),
            ri=np.random.randint(0, 2),
            n=name,
            clk=sig_clk,
            ce=sig_ce,
            inc=sig_inc,
            load=sig_load,
            rst=sig_rst,
            en_vtc=sig_en_vtc,
            odatain=sig_odatain,
            dataout=sig_dataout),
        file=f)


def print_top(seed, fout=sys.stdout):
    np.random.seed(seed)

    pins = []
    bank_to_pins = {}
    bank_to_iotype = {}
    site_to_pin = {}

    with open("../iopins.csv", "r") as iof:
        for row in csv.DictReader(iof):
            pin = row['pin']
            bank = row['bank']
            func = row['pin_function']
            site_name = row['site_name']
            site_type = row['site_type']
            iol_site = row['iol_site']

            pins.append((pin, bank, func, site_name, site_type, iol_site))
            if bank not in bank_to_pins:
                bank_to_pins[bank] = []
            bank_to_pins[bank].append(pin)
            if bank not in bank_to_iotype:
                bank_to_iotype[bank] = site_type.split("_")[0]
            site_to_pin[site_name] = pin

    used_pins = []
    io_config = []

    lut_inputs = []
    lut_outputs = []

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

    def clock():
        return ("gclk[%d]" % np.random.randint(0, 6))

    def maybe_outp_z():
        return outp() if np.random.choice([True, False]) else "null"

    def maybe(x):
        return x if np.random.choice([True, False]) else ""

    io_config = []
    used_pins = []
    for i in range(len(pins)):
        if "XIPHY" in pins[i][5]:
            prim = np.random.choice([
                None, None, None, None, None, "IBUF", "OBUF", "OBUFT", "IOBUF"
            ])
        else:
            prim = np.random.choice([
                None, None, None, None, None, "IBUF", "OBUF", "OBUFT", "IOBUF",
                "IOBUFE3"
            ])
        if prim is not None:
            io_config.append(prim)
            used_pins.append(pins[i])

    print("module top(", file=fout)
    for i, prim in enumerate(io_config):
        if prim == "IBUF":
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
    print("wire null;", file=fout)
    print("wire [5:0] gclk;", file=fout)
    print(
        "BUFG bufg_i[5:0] (.I({%s, %s, %s, %s, %s, %s}), .O(gclk));" % tuple(
            outp() for i in range(6)),
        file=fout)
    del_groups = set()
    for i, prim in enumerate(io_config):
        print(
            "wire p{i}i, p{i}i_d, p{i}o, p{i}o_d, p{i}t;".format(i=i),
            file=fout)
        print("(* KEEP, DONT_TOUCH *)", file=fout)
        if prim == "IBUF":
            print(
                """
                IBUF buf_{i} (
                    .I(p{i}),
                    .O(p{i}o)
                );
            """.format(i=i),
                file=fout)
        elif prim == "OBUF":
            print(
                """
                OBUF buf_{i} (
                    .O(p{i}),
                    .I(p{i}i_d)
                );
            """.format(i=i),
                file=fout)
        elif prim == "OBUFT":
            print(
                """
                OBUFT buf_{i} (
                    .O(p{i}),
                    .T(p{i}t),
                    .I(p{i}i_d)
                );
            """.format(i=i),
                file=fout)
        elif prim == "IOBUF":
            print(
                """
                IOBUF buf_{i} (
                    .IO(p{i}),
                    .T(p{i}t),
                    .I(p{i}i_d),
                    .O(p{i}o)
                );
            """.format(i=i),
                file=fout)
        elif prim == "IOBUFE3":
            print(
                """
                IOBUFE3 buf_{i} (
                    .IO(p{i}),
                    .T(p{i}t),
                    .I(p{i}i_d),
                    .O(p{i}o),
                    .DCITERMDISABLE({dci_dis})
                );
            """.format(i=i, dci_dis=maybe_outp()),
                file=fout)
        iol_site = used_pins[i][5]
        idelay_used = False
        odelay_used = False
        if "BITSLICE" in iol_site:
            idelay_used = np.random.choice([False, True])
            odelay_used = np.random.choice([False, True])
            del_fmt = np.random.choice(["TIME", "COUNT"])
            time_dly = int(6666.667 / np.random.uniform(7, 666))
            slow_clk = clock()
            group = "B" + str(used_pins[i][1])
            if idelay_used:
                print(
                    "(* KEEP, DONT_TOUCH, LOC=\"%s\", BEL=\"IDELAY\", IODELAY_GROUP=\"%s\" *)"
                    % (iol_site, group),
                    file=fout)
                make_idelay(
                    name="idelay%d" % i,
                    del_fmt=del_fmt,
                    time_dly=time_dly,
                    sig_clk=maybe(slow_clk),
                    sig_ce=maybe_outp(),
                    sig_inc=maybe_outp(),
                    sig_load=maybe_outp(),
                    sig_rst=maybe_outp(),
                    sig_en_vtc=maybe_outp(),
                    sig_datain=maybe_outp(),
                    sig_idatain="p%do" % i,
                    sig_dataout="p%do_d" % i,
                    f=fout)
                del_groups.add(group)
            if odelay_used:
                print(
                    "(* KEEP, DONT_TOUCH, LOC=\"%s\", BEL=\"ODELAY\", IODELAY_GROUP=\"%s\" *)"
                    % (iol_site, group),
                    file=fout)
                make_odelay(
                    name="odelay%d" % i,
                    del_fmt=del_fmt,
                    time_dly=time_dly,
                    sig_clk=maybe(slow_clk),
                    sig_ce=maybe_outp(),
                    sig_inc=maybe_outp(),
                    sig_load=maybe_outp(),
                    sig_rst=maybe_outp(),
                    sig_en_vtc=maybe_outp(),
                    sig_odatain="p%di" % i,
                    sig_dataout="p%di_d" % i,
                    f=fout)
                del_groups.add(group)
            input_mode = np.random.choice(
                ["NONE", "BYP", "FF", "DDR", "SERDES"])
            if input_mode == "BYP":
                print(
                    "assign %s = p%do%s;" % (inp(), i,
                                             "_d" if idelay_used else ""),
                    file=fout)
            elif input_mode == "FF" and prim in ("IBUF", "IOBUF", "IOBUFE3"):
                print(
                    "(* KEEP, DONT_TOUCH, LOC=\"%s\", BEL=\"IN_FF\" *)" %
                    iol_site,
                    file=fout)
                make_ioff(
                    name="iff%d" % i,
                    sig_c=slow_clk,
                    sig_d="p%do_d" % i if idelay_used else ("p%do" % i),
                    sig_r=maybe_outp(),
                    sig_e=maybe_outp(),
                    sig_q=maybe_inp(),
                    f=fout)
            elif input_mode == "DDR" and prim in ("IBUF", "IOBUF", "IOBUFE3"):
                print(
                    "(* KEEP, DONT_TOUCH, LOC=\"%s\", BEL=\"ISERDES\" *)" %
                    iol_site,
                    file=fout)
                make_iddr(
                    name="iddr%d" % i,
                    allow_inv=True,
                    sig_c=slow_clk,
                    sig_cb=clock(),
                    sig_r=maybe_outp(),
                    sig_d="p%do_d" % i if idelay_used else "p%do" % i,
                    sig_q1=maybe_inp(),
                    sig_q2=maybe_inp(),
                    f=fout)
            elif input_mode == "SERDES":
                print(
                    "(* KEEP, DONT_TOUCH, LOC=\"%s\", BEL=\"ISERDES\" *)" %
                    iol_site,
                    file=fout)
                make_iserdes(
                    name="iserdes%d" % i,
                    sig_clk=clock(),
                    sig_clkdiv=slow_clk,
                    sig_clk_b=clock(),
                    sig_d="p%do_d" % i if idelay_used else "p%do" % i,
                    sig_rst=maybe_outp(),
                    sig_q="{%s}" % (", ".join([inp() for i in range(8)])),
                    f=fout)
            output_mode = np.random.choice(
                ["NONE", "BYP", "FF", "DDR", "SERDES"])
            if output_mode == "SERDES":
                print(
                    "(* KEEP, DONT_TOUCH, LOC=\"%s\", BEL=\"OSERDES\" *)" %
                    iol_site,
                    file=fout)
                make_oserdes(
                    name="oserdes%d" % i,
                    sig_clk=clock(),
                    sig_clkdiv=slow_clk,
                    sig_d="{%s}" % (", ".join(
                        [maybe_outp_z() for i in range(8)])),
                    sig_rst=maybe_outp(),
                    sig_t=maybe_outp(),
                    sig_oq="p%di" % i,
                    sig_t_out="p%dt" % i,
                    f=fout)
            else:
                if output_mode == "BYP" or odelay_used:
                    print("assign p%di = %s;" % (i, outp()), file=fout)
                    print("assign p%dt = %s;" % (i, outp()), file=fout)
                elif output_mode == "FF" and prim in ("OBUF", "OBUFT", "IOBUF",
                                                      "IOBUFE3"):
                    print(
                        "(* KEEP, DONT_TOUCH, LOC=\"%s\", BEL=\"OUT_FF\" *)" %
                        iol_site,
                        file=fout)
                    make_ioff(
                        name="off%d" % i,
                        sig_c=slow_clk,
                        sig_d=maybe_inp(),
                        sig_r=maybe_outp(),
                        sig_e=maybe_outp(),
                        sig_q="p%di" % i,
                        f=fout)
                elif output_mode == "DDR":
                    print(
                        "(* KEEP, DONT_TOUCH, LOC=\"%s\", BEL=\"OSERDES\" *)" %
                        iol_site,
                        file=fout)
                    make_oddr(
                        name="oddr%d" % i,
                        srval=np.random.randint(0, 2),
                        sig_c=slow_clk,
                        c_inv=np.random.choice([True, False]),
                        sig_d1=outp(),
                        sig_d2=outp(),
                        sig_sr=maybe_outp(),
                        sig_q="p%di" % i,
                        f=fout)
        elif "HDIO" in iol_site:
            slow_clk = clock()
            reset = maybe_outp()
            enable = maybe_outp()
            input_mode = np.random.choice(["NONE", "BYP", "FF", "DDR"])
            if input_mode == "BYP":
                print("assign %s = p%do;" % (inp(), i), file=fout)
            elif input_mode == "FF" and prim in ("IBUF", "IOBUF"):
                print(
                    "(* KEEP, DONT_TOUCH, LOC=\"%s\", BEL=\"IPFF\" *)" %
                    iol_site,
                    file=fout)
                make_ioff(
                    name="iff%d" % i,
                    sig_c=slow_clk,
                    sig_d="p%do" % i,
                    sig_r=reset,
                    sig_e=maybe_outp(),
                    sig_q=maybe_inp(),
                    f=fout)
            elif input_mode == "DDR":
                print(
                    "(* KEEP, DONT_TOUCH, LOC=\"%s\", BEL=\"IDDR\" *)" %
                    iol_site,
                    file=fout)
                make_iddr(
                    name="iddr%d" % i,
                    allow_inv=False,
                    sig_c=slow_clk,
                    sig_cb=clock(),
                    sig_r=reset,
                    sig_d="p%do" % i,
                    sig_q1=maybe_inp(),
                    sig_q2=maybe_inp(),
                    f=fout)
            output_mode = np.random.choice(["NONE", "BYP", "FF", "DDR"])
            tristate_mode = np.random.choice(["NONE", "BYP", "FF", "DDR"])
            srval = np.random.randint(0, 2)
            if output_mode == "BYP":
                print("assign p%di = %s;" % (i, outp()), file=fout)
            elif output_mode == "FF" and prim in ("OBUF", "OBUFT", "IOBUF"):
                print(
                    "(* KEEP, DONT_TOUCH, LOC=\"%s\", BEL=\"OPFF\" *)" %
                    iol_site,
                    file=fout)
                make_ioff(
                    name="off%d" % i,
                    sig_c=slow_clk,
                    sig_d=maybe_inp(),
                    sig_r=reset,
                    sig_e=enable,
                    sig_q="p%di" % i,
                    f=fout)
            elif output_mode == "DDR" and prim in ("OBUF", "OBUFT", "IOBUF"):
                #print("(* KEEP, DONT_TOUCH, LOC=\"%s\" *)" % iol_site, file=fout)
                make_oddr(
                    name="oddr%d" % i,
                    srval=srval,
                    sig_c=slow_clk,
                    c_inv=False,
                    sig_d1=maybe_outp(),
                    sig_d2=maybe_outp(),
                    sig_sr=reset,
                    sig_q="p%di" % i,
                    f=fout)
                tristate_mode = "DDR"

            if tristate_mode == "BYP":
                print("assign p%dt = %s;" % (i, outp()), file=fout)
            elif tristate_mode == "FF" and prim in ("OBUFT", "IOBUF"):
                print(
                    "(* KEEP, DONT_TOUCH, LOC=\"%s\", BEL=\"TFF\" *)" %
                    iol_site,
                    file=fout)
                make_ioff(
                    name="tff%d" % i,
                    sig_c=slow_clk,
                    sig_d=maybe_inp(),
                    sig_r=reset,
                    sig_e=enable,
                    sig_q="p%dt" % i,
                    f=fout)
            elif tristate_mode == "DDR" and prim in (
                    "OBUFT", "IOBUF") and output_mode == "DDR":
                #print("(* KEEP, DONT_TOUCH, LOC=\"%s\", BEL=\"OPTFF\" *)" % iol_site, file=fout)
                make_oddr(
                    name="tddr%d" % i,
                    srval=srval,
                    sig_c=slow_clk,
                    c_inv=False,
                    sig_d1=maybe_outp(),
                    sig_d2=maybe_outp(),
                    sig_sr=reset,
                    sig_q="p%dt" % i,
                    f=fout)
        if not odelay_used:
            print("assign p%di_d = p%di;" % (i, i), file=fout)

        print("", file=fout)

    for group in sorted(del_groups):
        print(
            "(* KEEP, DONT_TOUCH, IODELAY_GROUP=\"%s\" *)" % group, file=fout)
        print(
            " IDELAYCTRL ctrl_{n} (.REFCLK({c}), .RST({r}), .RDY({rd}));".
            format(
                n=group,
                c=clock(),
                r=maybe_outp(),
                rd=maybe_inp(),
            ),
            file=fout)

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
        for i, prim in enumerate(io_config):
            pin = used_pins[i][0]
            print(
                "set_property PACKAGE_PIN %s [get_ports {p%d}]" % (pin, i),
                file=f)
            print(
                "set_property IOSTANDARD LVCMOS18 [get_ports {p%d}]" % (i),
                file=f)

    with open("complete_top.tcl", "w") as f:
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
            "set_property SEVERITY {Warning} [get_drc_checks BSCK-*]", file=f)
        print(
            "set_property SEVERITY {Warning} [get_drc_checks PLHDIO-1]",
            file=f)
        print(
            "set_property SEVERITY {Warning} [get_drc_checks PDRC-203]",
            file=f)
        print(
            "set_property SEVERITY {Warning} [get_drc_checks PDRC-213]",
            file=f)
        print(
            "set_property SEVERITY {Warning} [get_drc_checks ADEF-911]",
            file=f)

        print("set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets]", file=f)
        print("opt_design", file=f)
        print("place_design", file=f)
        print("route_design", file=f)
        print("source $::env(URAY_UTILS_DIR)/fuzzpins.tcl", file=f)
