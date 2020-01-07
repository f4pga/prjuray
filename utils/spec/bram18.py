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
from utils.verilog import top_harness_clk


def print_top(seed):
    np.random.seed(seed)
    DCLK_N = 2
    DIN_N = 66
    DOUT_N = 36
    top_harness_clk(DCLK_N, DIN_N, DOUT_N)

    print("")
    print("""
        module roi(input [{DCLK_N}-1:0] clk, input [{DIN_N}-1:0] din, output [35:0] dout);

        wire clk1;
        wire clk1b;
        wire rst;
        wire ena;
        wire enb;
        wire cea;
        wire ceb;
        wire [13:0] ra;
        wire [13:0] wa;
        wire [3:0] we;
        wire [17:0] wdata;
        wire [10:0] sel;
        wire [35:0] rdata;

        assign clk1 = clk[0];
        assign clk1b = clk[1];

        assign rst = din[0];
        assign ena = din[1];
        assign enb = din[2];
        assign cea = din[3];
        assign ceb = din[4];
        assign ra = din[5+:14];
        assign wa = din[19+:14];
        assign we = din[33+:4];
        assign wdata = din[37+:18];
        assign sel = din[55+:11];

        assign dout = rdata;
        """.format(DCLK_N=DCLK_N, DIN_N=DIN_N))

    N = 200
    print("    wire [35:0] int_d[0:%d-1];" % N)
    print(
        "    assign rdata = sel[0] ? int_d[sel[10:1]][35:18] : int_d[sel[10:1]][17:0];"
    )
    for i in range(N):
        write_width_b = np.random.choice([0, 1, 2, 4, 9, 18, 36])
        read_width_a = np.random.choice(
            [0, 1, 2, 4, 9, 18, 36], p=[0.05, 0.1, 0.1, 0.1, 0.1, 0.45, 0.1])
        write_width_a = 0 if (write_width_b == 36
                              or read_width_a == 36) else np.random.choice(
                                  [0, 1, 2, 4, 9, 18])
        read_width_b = 0 if (
            read_width_a == 36 or write_width_b == 36) else np.random.choice(
                [0, 1, 2, 4, 9, 18], p=[0.05, 0.1, 0.1, 0.1, 0.1, 0.55])

        cd = np.random.choice(["INDEPENDENT", "COMMON"])

        if cd == "INDEPENDENT":
            RDADDRCHANGE_choices = ["FALSE"]
        else:
            RDADDRCHANGE_choices = ["TRUE", "FALSE"]

        WRITE_MODE_A = np.random.choice(
            ["NO_CHANGE", "READ_FIRST", "WRITE_FIRST"])
        CASCADE_ORDER_A = np.random.choice(["NONE", "FIRST", "MIDDLE", "LAST"])

        if read_width_a == 36 or write_width_b == 36:
            WRITE_MODE_B = WRITE_MODE_A
            CASCADE_ORDER_B = CASCADE_ORDER_A
        else:
            WRITE_MODE_B = np.random.choice(
                ["NO_CHANGE", "READ_FIRST", "WRITE_FIRST"])
            CASCADE_ORDER_B = np.random.choice(
                ["NONE", "FIRST", "MIDDLE", "LAST"])

        print("    RAMB18E2 #(")
        print("        .CLOCK_DOMAINS(\"%s\")," % cd)
        print("        .READ_WIDTH_A(%d)," % read_width_a)
        print("        .READ_WIDTH_B(%d)," % read_width_b)
        print("        .WRITE_WIDTH_A(%d)," % write_width_a)
        print("        .WRITE_WIDTH_B(%d)," % write_width_b)
        print("        .WRITE_MODE_A(\"%s\")," % WRITE_MODE_A)
        print("        .WRITE_MODE_B(\"%s\")," % WRITE_MODE_B)
        print("        .CASCADE_ORDER_A(\"%s\")," % CASCADE_ORDER_A)
        print("        .CASCADE_ORDER_B(\"%s\")," % CASCADE_ORDER_B)
        print("        .DOA_REG(%d)," %
              (0 if (write_width_b == 36 or read_width_a == 36) else
               np.random.randint(2)))
        print("        .DOB_REG(%d)," %
              (0 if (write_width_b == 36 or read_width_a == 36) else
               np.random.randint(2)))
        print("        .ENADDRENA(\"%s\")," % np.random.choice(
            ["FALSE", "TRUE"]))
        print("        .ENADDRENB(\"%s\")," % np.random.choice(
            ["FALSE", "TRUE"]))
        print("        .RDADDRCHANGEA(\"%s\")," %
              np.random.choice(RDADDRCHANGE_choices))
        print("        .RDADDRCHANGEB(\"%s\")," %
              np.random.choice(RDADDRCHANGE_choices))
        print("        .RSTREG_PRIORITY_A(\"%s\")," % np.random.choice(
            ["RSTREG", "REGCE"]))
        print("        .RSTREG_PRIORITY_B(\"%s\")," % np.random.choice(
            ["RSTREG", "REGCE"]))
        print("        .SLEEP_ASYNC(\"%s\")," % np.random.choice(
            ["FALSE", "TRUE"]))
        for pin in ("CLKARDCLK", "CLKBWRCLK", "ENARDEN", "ENBWREN",
                    "RSTRAMARSTRAM", "RSTRAMB", "RSTREGARSTREG", "RSTREGB"):
            print("        .IS_%s_INVERTED(%d)," % (pin, np.random.randint(2)))
        print("        .INIT_A(18'd%d)," % np.random.randint(2**18))
        print("        .INIT_B(18'd%d)," % np.random.randint(2**18))
        print("        .SRVAL_A(18'd%d)," % np.random.randint(2**18))
        print("        .SRVAL_B(18'd%d)" % np.random.randint(2**18))
        print("   ) ram%d (" % i)
        print("        .DINADIN(wdata[15:0]),")
        print("        .DINPADINP(wdata[17:16]),")
        print("        .DOUTADOUT(int_d[%d][15:0])," % i)
        print("        .DOUTPADOUTP(int_d[%d][17:16])," % i)
        print("        .ADDRARDADDR(ra),")
        print("        .CLKARDCLK(clk1),")
        print("        .ADDRENA(ena),")
        print("        .ENARDEN(ena),")
        print("        .REGCEAREGCE(cea),")
        print("        .RSTRAMARSTRAM(rst),")
        print("        .RSTREGARSTREG(rst),")
        print("        .WEA(%s)," %
              ("2'b00" if write_width_a == 0 else "we[1:0]"))
        print("        .DINBDIN(wdata[15:0]),")
        print("        .DINPBDINP(wdata[17:16]),")
        print("        .DOUTBDOUT(int_d[%d][33:18])," % i)
        print("        .DOUTPBDOUTP(int_d[%d][35:34])," % i)
        print("        .ADDRBWRADDR(wa),")
        print("        .CLKBWRCLK(%s)," %
              ("clk1b" if cd == "INDEPENDENT" else "clk1"))
        print("        .ENBWREN(enb),")
        print("        .ADDRENB(enb),")
        print("        .REGCEB(ceb),")
        print("        .RSTRAMB(rst),")
        print("        .RSTREGB(rst),")
        print("        .WEBWE(%s)" %
              ("2'b00" if write_width_b == 0 else
               ("we[3:0]" if write_width_b == 36 else "we[3:2]")))
        print("   );")
        print()
    print("endmodule")
