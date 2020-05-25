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
    DIN_N = 78
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
        wire [15:0] we;
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
        assign we = din[33+:16];
        assign wdata = din[49+:18];
        assign sel = din[67+:11];

        assign dout = rdata;
        """.format(DCLK_N=DCLK_N, DIN_N=DIN_N))

    N = 200
    print("    wire [71:0] int_d[0:%d-1];" % N)
    print("    assign rdata = int_d[sel[10:2]][18 * sel[1:0] +: 18];")
    for i in range(N):
        read_width_a = np.random.choice(
            [0, 1, 2, 4, 9, 18, 36, 72],
            p=[0.05, 0.1, 0.1, 0.1, 0.1, 0.1, 0.40, 0.05])
        write_width_a = np.random.choice([0, 1, 2, 4, 9, 18, 36])
        read_width_b = np.random.choice(
            [0, 1, 2, 4, 9, 18, 36], p=[0.05, 0.1, 0.1, 0.1, 0.1, 0.1, 0.45])
        write_width_b = np.random.choice([0, 1, 2, 4, 9, 18, 36, 72])
        cd = np.random.choice(["INDEPENDENT", "COMMON"])
        en_ecc_read = np.random.choice(["FALSE", "TRUE"], p=[0.9, 0.1])
        en_ecc_write = np.random.choice(["FALSE", "TRUE"], p=[0.9, 0.1])
        if en_ecc_read == "TRUE" or en_ecc_write == "TRUE":
            read_width_a = 72
            write_width_b = 72
        write_mode_a = np.random.choice(
            ["NO_CHANGE", "READ_FIRST", "WRITE_FIRST"])
        write_mode_b = np.random.choice(
            ["NO_CHANGE", "READ_FIRST", "WRITE_FIRST"])
        cascade_order_a = np.random.choice(["NONE", "FIRST", "MIDDLE", "LAST"])
        cascade_order_b = np.random.choice(["NONE", "FIRST", "MIDDLE", "LAST"])
        # DRC AVAL-165
        if read_width_a == 72 or write_width_b == 72:
            cascade_order_b = cascade_order_a
            write_mode_b = write_mode_a

        print("    RAMB36E2 #(")
        print("        .CLOCK_DOMAINS(\"%s\")," % cd)
        print("        .READ_WIDTH_A(%d)," % read_width_a)
        print("        .READ_WIDTH_B(%d)," % read_width_b)
        print("        .WRITE_WIDTH_A(%d)," % write_width_a)
        print("        .WRITE_WIDTH_B(%d)," % write_width_b)
        print("        .WRITE_MODE_A(\"%s\")," % write_mode_a)
        print("        .WRITE_MODE_B(\"%s\")," % write_mode_b)
        print("        .CASCADE_ORDER_A(\"%s\")," % cascade_order_a)
        print("        .CASCADE_ORDER_B(\"%s\")," % cascade_order_b)
        print("        .DOA_REG(%d)," % np.random.randint(2))
        print("        .DOB_REG(%d)," % np.random.randint(2))
        print("        .ENADDRENA(\"%s\")," % np.random.choice(
            ["FALSE", "TRUE"]))
        print("        .ENADDRENB(\"%s\")," % np.random.choice(
            ["FALSE", "TRUE"]))
        print("        .EN_ECC_PIPE(\"%s\")," % en_ecc_read)
        print("        .EN_ECC_READ(\"%s\")," % en_ecc_read)
        print("        .EN_ECC_WRITE(\"%s\")," % en_ecc_write)
        print("        .RDADDRCHANGEA(\"%s\")," % np.random.choice(
            ["FALSE", "TRUE"]))
        print("        .RDADDRCHANGEB(\"%s\")," % np.random.choice(
            ["FALSE", "TRUE"]))
        print("        .SLEEP_ASYNC(\"%s\")," % np.random.choice(
            ["FALSE", "TRUE"]))
        print("        .RSTREG_PRIORITY_A(\"%s\")," % np.random.choice(
            ["RSTREG", "REGCE"]))
        print("        .RSTREG_PRIORITY_B(\"%s\")," % np.random.choice(
            ["RSTREG", "REGCE"]))
        clk_inv = np.random.randint(2)
        print("        .IS_CLKARDCLK_INVERTED(%d)," % clk_inv)
        print("        .IS_CLKBWRCLK_INVERTED(%d)," % clk_inv)
        for pin in ("ENARDEN", "ENBWREN", "RSTRAMARSTRAM", "RSTRAMB",
                    "RSTREGARSTREG", "RSTREGB"):
            print("        .IS_%s_INVERTED(%d)," % (pin, clk_inv))
        print("        .INIT_A({18'd%d, 18'd%d})," % (np.random.randint(
            2**18), np.random.randint(2**18)))
        print("        .INIT_B({18'd%d, 18'd%d})," % (np.random.randint(
            2**18), np.random.randint(2**18)))
        print("        .SRVAL_A({18'd%d, 18'd%d})," % (np.random.randint(
            2**18), np.random.randint(2**18)))
        print("        .SRVAL_B({18'd%d, 18'd%d})" % (np.random.randint(
            2**18), np.random.randint(2**18)))
        print("   ) ram%d (" % i)
        print("        .DINADIN({wdata[15:0], wdata[15:0]}),")
        print("        .DINPADINP({wdata[17:16], wdata[17:16]}),")
        print("        .DOUTADOUT({int_d[%d][31:0]})," % i)
        print("        .DOUTPADOUTP({int_d[%d][35:32]})," % i)
        print("        .ADDRARDADDR(ra),")
        print("        .CLKARDCLK(clk),")
        print("        .ADDRENA(ena),")
        print("        .ENARDEN(ena),")
        print("        .REGCEAREGCE(cea),")
        print("        .RSTRAMARSTRAM(rst),")
        print("        .RSTREGARSTREG(rst),")
        print("        .WEA(%s)," % ("8'b00" if write_width_a == 0
                                     or write_width_b == 72 else "we[7:0]"))
        print("        .DINBDIN({wdata[15:0], wdata[15:0]}),")
        print("        .DINPBDINP({wdata[17:16], wdata[17:16]}),")
        print("        .DOUTBDOUT(int_d[%d][67:36])," % i)
        print("        .DOUTPBDOUTP(int_d[%d][71:68])," % i)
        print("        .ADDRBWRADDR(wa),")
        print("        .CLKBWRCLK(%s)," %
              ("clkb" if cd == "INDEPENDENT" else "clk"))
        print("        .ENBWREN(enb),")
        print("        .ADDRENB(enb),")
        print("        .REGCEB(ceb),")
        print("        .RSTRAMB(rst),")
        print("        .RSTREGB(rst),")
        print(
            "        .WEBWE(%s)" % ("8'b00" if write_width_b == 0 else "8'hFF"
                                    if en_ecc_write == "TRUE" else "we[15:8]"))
        print("   );")
        print()
    print("endmodule")


if __name__ == "__main__":
    main()
