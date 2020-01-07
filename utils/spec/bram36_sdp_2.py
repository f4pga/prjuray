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


def main():
    print(
        "module top(input clk, clkb, rst, ena, enb, cea, ceb, input [14:0] ra, wa, input [7:0] we, input [17:0] wdata, input [10:0] sel, output [35:0] rdata);"
    )
    N = 300
    print("    wire [71:0] int_d[0:%d-1];" % N)
    print("    assign rdata = int_d[sel[10:2]][18 * sel[1:0] +: 18];")
    for i in range(N):
        write_width_b = np.random.choice([0, 1, 2, 4, 9, 18, 36, 72])
        read_width_a = np.random.choice(
            [0, 1, 2, 4, 9, 18, 36, 72],
            p=[0.05, 0.1, 0.1, 0.1, 0.05, 0.05, 0.45, 0.1])
        write_width_a = 0 if (write_width_b == 72
                              or read_width_a == 72) else np.random.choice(
                                  [0, 1, 2, 4, 9, 18, 36])
        read_width_b = 0 if (write_width_b == 72
                             or read_width_a == 72) else np.random.choice(
                                 [0, 1, 2, 4, 9, 18, 36],
                                 p=[0.05, 0.1, 0.1, 0.1, 0.1, 0.1, 0.45])
        cd = np.random.choice(["INDEPENDENT", "COMMON"])

        print("    RAMB36E2 #(")
        print("        .CLOCK_DOMAINS(\"%s\")," % cd)
        print("        .READ_WIDTH_A(%d)," % read_width_a)
        print("        .READ_WIDTH_B(%d)," % read_width_b)
        print("        .WRITE_WIDTH_A(%d)," % write_width_a)
        print("        .WRITE_WIDTH_B(%d)," % write_width_b)
        print("        .WRITE_MODE_A(\"%s\")," % np.random.choice(
            ["NO_CHANGE", "READ_FIRST", "WRITE_FIRST"]))
        print("        .WRITE_MODE_B(\"%s\")," % np.random.choice(
            ["NO_CHANGE", "READ_FIRST", "WRITE_FIRST"]))
        print("        .CASCADE_ORDER_A(\"%s\")," % np.random.choice(
            ["NONE", "FIRST", "MIDDLE", "LAST"]))
        print("        .CASCADE_ORDER_B(\"%s\")," % np.random.choice(
            ["NONE", "FIRST", "MIDDLE", "LAST"]))
        print("        .DOA_REG(%d)," %
              (0 if (write_width_b == 72 or read_width_a == 72) else
               np.random.randint(2)))
        print("        .DOB_REG(%d)," %
              (0 if (write_width_b == 72 or read_width_a == 72) else
               np.random.randint(2)))
        print("        .ENADDRENA(\"%s\")," % np.random.choice(
            ["FALSE", "TRUE"]))
        print("        .ENADDRENB(\"%s\")," % np.random.choice(
            ["FALSE", "TRUE"]))
        print("        .EN_ECC_PIPE(\"%s\")," % np.random.choice(
            ["FALSE", "TRUE"], p=[0.9, 0.1]))
        print("        .EN_ECC_READ(\"%s\")," % np.random.choice(
            ["FALSE", "TRUE"], p=[0.9, 0.1]))
        print("        .EN_ECC_WRITE(\"%s\")," % np.random.choice(
            ["FALSE", "TRUE"], p=[0.9, 0.1]))
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
        for pin in ("CLKARDCLK", "CLKBWRCLK", "ENARDEN", "ENBWREN",
                    "RSTRAMARSTRAM", "RSTRAMB", "RSTREGARSTREG", "RSTREGB"):
            print("        .IS_%s_INVERTED(%d)," % (pin, np.random.randint(2)))
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
        douta_bit = np.random.randint(-1, 37)
        if douta_bit >= 0 and douta_bit < 32:
            print("        .DOUTADOUT({int_d[%d][0]%s})," %
                  (i, ", {%d{1'bx}}" % douta_bit if douta_bit > 0 else ""))
        if douta_bit >= 32:
            print("        .DOUTPADOUTP({int_d[%d][32]%s})," %
                  (i, ", {%d{1'bx}}" %
                   (douta_bit - 32) if douta_bit > 32 else ""))
        print("        .ADDRARDADDR(ra),")
        print("        .CLKARDCLK(clk),")
        print("        .ADDRENA(ena),")
        print("        .ENARDEN(ena),")
        print("        .REGCEAREGCE(cea),")
        print("        .RSTRAMARSTRAM(rst),")
        print("        .RSTREGARSTREG(rst),")
        print("        .WEA(%s)," %
              ("4'b00" if write_width_a == 0 else "we[3:0]"))
        print("        .DINBDIN({wdata[15:0], wdata[15:0]}),")
        print("        .DINPBDINP({wdata[17:16], wdata[17:16]}),")
        doutb_bit = np.random.randint(-1, 37)
        if doutb_bit >= 0 and doutb_bit < 32:
            print("        .DOUTBDOUT({int_d[%d][36]%s})," %
                  (i, ", {%d{1'bx}}" % doutb_bit if doutb_bit > 0 else ""))
        if doutb_bit >= 32:
            print("        .DOUTPBDOUTP({int_d[%d][68]%s})," %
                  (i, ", {%d{1'bx}}" %
                   (doutb_bit - 32) if doutb_bit > 32 else ""))
        print("        .ADDRBWRADDR(wa),")
        print("        .CLKBWRCLK(%s)," %
              ("clkb" if cd == "INDEPENDENT" else "clk"))
        print("        .ENBWREN(enb),")
        print("        .ADDRENB(enb),")
        print("        .REGCEB(ceb),")
        print("        .RSTRAMB(rst),")
        print("        .RSTREGB(rst),")
        print("        .WEBWE(%s)" %
              ("4'b00" if write_width_b == 0 else
               ("we[7:0]" if write_width_b == 72 else "we[7:4]")))
        print("   );")
        print()
    print("endmodule")


if __name__ == "__main__":
    main()
