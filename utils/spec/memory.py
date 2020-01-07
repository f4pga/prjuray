#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

import numpy as np
import math

from utils.verilog import top_harness_clk


def print_top(seed):
    np.random.seed(seed)
    DCLK_N = 10
    DIN_N = (16 + 9 + 8 + 8 + 12)
    DOUT_N = 4
    top_harness_clk(DCLK_N, DIN_N, DOUT_N)

    print("""
        module roi(input [{DCLK_N}-1:0] clk, input [{DIN_N}-1:0] din, output [{DOUT_N}:0] dout);

        wire [15:0] cen;
        wire [8:0] wa;
        wire [7:0] ra;
        wire [7:0] d;
        wire [11:0] sel;
        wire [3:0] q;

        assign cen = din[0+:16];
        assign wa = din[16+:9];
        assign ra = din[25+:8];
        assign d = din[33+:8];
        assign sel = din[41+:12];
        assign dout = q;

        """.format(DCLK_N=DCLK_N, DIN_N=DIN_N, DOUT_N=DOUT_N))

    N = 512
    print("    wire [3:0] int_d[0:%d-1];" % N)
    print("    assign q = int_d[sel];")

    def connect(sig, dst, len):
        if sig is None:
            return []
        bit = 0
        conns = []
        for x in sig:
            if type(x) is tuple:
                name, width = x
                conns.append(".%s(%s[%d +: %d])" % (name, dst, bit, width))
                bit += width
            else:
                conns.append(".%s(%s[%d])" % (x, dst, bit))
                bit += 1
        return conns

    for i in range(N):
        ctype = np.random.choice([
            "SRL16E", "SRLC32E", "RAM32X1D", "RAM32X1S", "RAM64X1D",
            "RAM64X1S", "RAM128X1S", "RAM128X1D", "RAM256X1D", "RAM256X1S",
            "RAM512X1S"
        ])
        clockport = None
        ceport = None
        wraddr = None
        rdaddr = None
        wdata = None
        rdata = None
        init_len = None
        if ctype in ("SRL16E", "SRLC32E"):
            clockport = "CLK"
            ceport = "CE"
            wdata = ["D"]
            rdata = ["Q"]
            if ctype == "SRLC32E":
                rdata.append("Q31")
                rdaddr = [("A", 5)]
                init_len = 32
            else:
                rdaddr = ["A0", "A1", "A2", "A3"]
                init_len = 16
        elif ctype in ("RAM32X1D", "RAM32X1S"):
            clockport = "WCLK"
            ceport = "WE"
            wdata = ["D"]
            wraddr = ["A0", "A1", "A2", "A3", "A4"]
            init_len = 32
            if ctype == "RAM32X1D":
                rdaddr = ["DPRA0", "DPRA1", "DPRA2", "DPRA3", "DPRA4"]
                rdata = ["SPO", "DPO"]
            else:
                rdata = ["O"]
        elif ctype in ("RAM64X1D", "RAM64X1S"):
            clockport = "WCLK"
            ceport = "WE"
            wdata = ["D"]
            wraddr = ["A0", "A1", "A2", "A3", "A4", "A5"]
            init_len = 64
            if ctype == "RAM64X1D":
                rdaddr = ["DPRA0", "DPRA1", "DPRA2", "DPRA3", "DPRA4", "DPRA5"]
                rdata = ["SPO", "DPO"]
            else:
                rdata = ["O"]
        elif ctype in ("RAM128X1S", "RAM128X1D", "RAM256X1D", "RAM256X1S",
                       "RAM512X1S"):
            init_len = int(ctype[3:6])
            abits = math.log2(init_len)
            clockport = "WCLK"
            ceport = "WE"
            wdata = ["D"]
            if ctype == "RAM128X1S":
                wraddr = ["A0", "A1", "A2", "A3", "A4", "A5", "A6"]
            else:
                wraddr = [("A", abits)]
            if ctype[-1] == "D":
                rdaddr = [("DPRA", abits)]
                rdata = ["SPO", "DPO"]
            else:
                rdata = ["O"]
        else:
            assert False, ctype
        conns = []
        if clockport is not None:
            conns.append(
                ".%s(clk[%d])" % (clockport, np.random.randint(0, 16)))
        if ceport is not None:
            conns.append(".%s(cen[%d])" % (ceport, np.random.randint(0, 16)))
        conns += connect(wraddr, "wa", 9)
        conns += connect(rdaddr, "ra", 8)
        conns += connect(wdata, "d", 8)
        conns += connect(rdata, "int_d[%d]" % i, 4)
        print("    %s #(" % ctype)
        if init_len is not None:
            initdata = np.random.randint(2, size=init_len)
            print("        .INIT(%d'b%s)" % (init_len, "".join(
                [str(_) for _ in initdata])))
        print("    ) %s_%d (" % (ctype, i))
        print("    %s" % ",\n    ".join(conns))
        print("    );")
    print("endmodule")
