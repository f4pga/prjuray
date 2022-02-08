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

import numpy as np
import sys

X = 8
N = 200

root = sys.argv[2]


def random_vector(size):
    return "{%s}" % ", ".join(
        ["d[%d]" % np.random.randint(12) for k in range(size)])


def main():
    for x in range(X):

        with open(root + "/dsp2/dsp_b%d.v" % x, "w") as f:
            print(
                "module top(input [7:0] clk, cen, rst, input [11:0] d, input [7:0] sel, output [63:0] q);",
                file=f)
            print("    wire [8:0] r = {1'b0, rst}, e = {1'b1, cen};", file=f)
            print("    wire [63:0] int_q[0:%d];" % (N - 1), file=f)
            print("    assign q = int_q[sel];", file=f)
            for i in range(N):
                use_preadd = np.random.choice([False, True])
                bmultsel = (np.random.choice(["AD", "B"])
                            if use_preadd else "B")
                amultsel = (np.random.choice(["AD", "A"])
                            if use_preadd and bmultsel == "AD" else
                            ("AD" if use_preadd else "A"))
                use_patdet = np.random.choice([False, True])
                print("    (* keep, dont_touch *) DSP48E2 #(", file=f)
                print(
                    "        .ADREG(%d)," %
                    (np.random.randint(2) if use_preadd else 0),
                    file=f)
                print(
                    "        .ALUMODEREG(%d)," % np.random.randint(2), file=f)
                print("        .AMULTSEL(\"%s\")," % amultsel, file=f)
                print("        .AREG(%d)," % np.random.randint(3), file=f)
                print(
                    "        .AUTORESET_PATDET(\"%s\")," % np.random.choice(
                        ["NO_RESET", "RESET_MATCH", "RESET_NOT_MATCH"]),
                    file=f)
                print(
                    "        .AUTORESET_PRIORITY(\"%s\")," % np.random.choice(
                        ["RESET", "CEP"]),
                    file=f)
                print("        .A_INPUT(\"DIRECT\"),", file=f)
                print("        .BMULTSEL(\"%s\")," % bmultsel, file=f)
                print("        .BREG(%d)," % np.random.randint(3), file=f)
                print("        .B_INPUT(\"DIRECT\"),", file=f)
                print(
                    "        .CARRYINREG(%d)," % np.random.randint(2), file=f)
                print(
                    "        .CARRYINSELREG(%d)," % np.random.randint(2),
                    file=f)
                print("        .CREG(%d)," % np.random.randint(2), file=f)
                print("        .DREG(%d)," % np.random.randint(2), file=f)
                print("        .INMODEREG(%d)," % np.random.randint(2), file=f)
                print(
                    "        .IS_ALUMODE_INVERTED(%d)," %
                    np.random.randint(16),
                    file=f)
                print(
                    "        .IS_CARRYIN_INVERTED(%d)," % np.random.randint(2),
                    file=f)
                print(
                    "        .IS_CLK_INVERTED(%d)," % np.random.randint(2),
                    file=f)
                print(
                    "        .IS_INMODE_INVERTED(%d)," % np.random.randint(32),
                    file=f)
                print(
                    "        .IS_OPMODE_INVERTED(%d)," %
                    np.random.randint(512),
                    file=f)
                print(
                    "        .IS_RSTALLCARRYIN_INVERTED(%d)," %
                    np.random.randint(2),
                    file=f)
                print(
                    "        .IS_RSTALUMODE_INVERTED(%d)," %
                    np.random.randint(2),
                    file=f)
                print(
                    "        .IS_RSTA_INVERTED(%d)," % np.random.randint(2),
                    file=f)
                print(
                    "        .IS_RSTB_INVERTED(%d)," % np.random.randint(2),
                    file=f)
                print(
                    "        .IS_RSTCTRL_INVERTED(%d)," % np.random.randint(2),
                    file=f)
                print(
                    "        .IS_RSTC_INVERTED(%d)," % np.random.randint(2),
                    file=f)
                print(
                    "        .IS_RSTD_INVERTED(%d)," % np.random.randint(2),
                    file=f)
                print(
                    "        .IS_RSTINMODE_INVERTED(%d)," %
                    np.random.randint(2),
                    file=f)
                print(
                    "        .IS_RSTM_INVERTED(%d)," % np.random.randint(2),
                    file=f)
                print(
                    "        .IS_RSTP_INVERTED(%d)," % np.random.randint(2),
                    file=f)
                print(
                    "        .MASK({24'd%d, 24'd%d})," % (np.random.randint(
                        2**24), np.random.randint(2**24)),
                    file=f)
                print("        .MREG(%d)," % np.random.randint(2), file=f)
                print("        .OPMODEREG(%d)," % np.random.randint(2), file=f)
                print(
                    "        .PATTERN({24'd%d, 24'd%d})," % (np.random.randint(
                        2**24), np.random.randint(2**24)),
                    file=f)
                print(
                    "        .PREADDINSEL(\"%s\")," % np.random.choice(
                        ["A", "B"]),
                    file=f)
                print("        .PREG(%d)," % np.random.randint(2), file=f)
                print(
                    "        .RND({24'd%d, 24'd%d})," % (np.random.randint(
                        2**24), np.random.randint(2**24)),
                    file=f)
                print(
                    "        .SEL_MASK(\"%s\")," % np.random.choice(
                        ["MASK", "C", "ROUNDING_MODE1", "ROUNDING_MODE2"]),
                    file=f)
                print(
                    "        .SEL_PATTERN(\"%s\")," % np.random.choice(
                        ["PATTERN", "C"]),
                    file=f)
                print(
                    "        .USE_PATTERN_DETECT(\"%s\")," %
                    ("PATDET" if use_patdet else "NO_PATDET"),
                    file=f)
                print(
                    "        .USE_SIMD(\"%s\")," % np.random.choice(
                        ["ONE48", "TWO24", "FOUR12"]),
                    file=f)
                print(
                    "        .USE_WIDEXOR(\"%s\")," % np.random.choice(
                        ["TRUE", "FALSE"]),
                    file=f)
                print(
                    "        .XORSIMD(\"%s\")" % np.random.choice(
                        ["XOR12", "XOR24_48_96"]),
                    file=f)
                print("    ) dsp_%d (" % i, file=f)
                print("        .A(%s)," % random_vector(30), file=f)
                print("        .ALUMODE(%s)," % random_vector(4), file=f)
                print("        .B(%s)," % random_vector(18), file=f)
                #print("        .C(%s)," % random_vector(48), file=f)
                print("        .CARRYIN(%s)," % random_vector(1), file=f)
                print("        .CEA1(e[%d])," % np.random.randint(9), file=f)
                print("        .CEA2(e[%d])," % np.random.randint(9), file=f)
                print("        .CEAD(e[%d])," % np.random.randint(9), file=f)
                print(
                    "        .CEALUMODE(e[%d])," % np.random.randint(9),
                    file=f)
                print("        .CEC(e[%d])," % np.random.randint(9), file=f)
                print(
                    "        .CECARRYIN(e[%d])," % np.random.randint(9),
                    file=f)
                print("        .CECTRL(e[%d])," % np.random.randint(9), file=f)
                print("        .CED(e[%d])," % np.random.randint(9), file=f)
                print(
                    "        .CEINMODE(e[%d])," % np.random.randint(9), file=f)
                print("        .CEM(e[%d])," % np.random.randint(9), file=f)
                print("        .CEP(e[%d])," % np.random.randint(9), file=f)
                #print("        .D(%s)," % random_vector(27), file=f)
                print("        .INMODE(%s)," % random_vector(5), file=f)
                print("        .OPMODE(%s)," % random_vector(9), file=f)
                print("        .RSTA(r[%d])," % np.random.randint(9), file=f)
                print(
                    "        .RSTALLCARRYIN(r[%d])," % np.random.randint(9),
                    file=f)
                print(
                    "        .RSTALUMODE(r[%d])," % np.random.randint(9),
                    file=f)
                print("        .RSTB(r[%d])," % np.random.randint(9), file=f)
                print("        .RSTC(r[%d])," % np.random.randint(9), file=f)
                print(
                    "        .RSTCTRL(r[%d])," % np.random.randint(9), file=f)
                print("        .RSTD(r[%d])," % np.random.randint(9), file=f)
                print(
                    "        .RSTINMODE(r[%d])," % np.random.randint(9),
                    file=f)
                print("        .RSTM(r[%d])," % np.random.randint(9), file=f)
                print("        .RSTP(r[%d])," % np.random.randint(9), file=f)
                o_bit = np.random.randint(-1, 64)
                if o_bit >= 0 and o_bit < 48:
                    print(
                        "        .P({int_q[%d][0]%s})," %
                        (i, ", {%d{1'bx}}" % o_bit if o_bit > 0 else ""),
                        file=f)
                if o_bit >= 48 and o_bit < 52:
                    print(
                        "        .CARRYOUT({int_q[%d][48]%s})," %
                        (i, ", {%d{1'bx}}" %
                         (o_bit - 48) if o_bit > 48 else ""),
                        file=f)
                if o_bit >= 52 and o_bit < 60:
                    print(
                        "        .XOROUT({int_q[%d][52]%s})," %
                        (i, ", {%d{1'bx}}" %
                         (o_bit - 52) if o_bit > 52 else ""),
                        file=f)
                if o_bit == 60:
                    print("        .PATTERNDETECT(int_q[%d][60])," % i, file=f)
                if o_bit == 61:
                    print(
                        "        .PATTERNBDETECT(int_q[%d][61])," % i, file=f)
                if o_bit == 62:
                    print("        .OVERFLOW(int_q[%d][62])," % i, file=f)
                if o_bit == 63:
                    print("        .UNDERFLOW(int_q[%d][63])," % i, file=f)
                print("        .CLK(clk[%d])" % np.random.randint(8), file=f)
                print("    );", file=f)
                print("", file=f)
            print("endmodule", file=f)
        with open(root + "/dsp2/dsp_b%d.tcl" % x, "w") as f:
            print("add_files %s" % (root + ("/dsp2/dsp_b%d.v" % x)), file=f)
            print("synth_design -top top -part xczu7ev-ffvc1156-2-e", file=f)
            print("opt_design", file=f)
            print("place_design", file=f)
            print("route_design", file=f)
            print(
                "set_property SEVERITY {Warning} [get_drc_checks NSTD-1]",
                file=f)
            print(
                "set_property SEVERITY {Warning} [get_drc_checks UCIO-1]",
                file=f)
            print(
                "set_property SEVERITY {Warning} [get_drc_checks AVAL-*]",
                file=f)
            print(
                "set_property SEVERITY {Warning} [get_drc_checks REQP-*]",
                file=f)
            print(
                "set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]",
                file=f)
            print(
                "write_checkpoint -force %s/specimen_bram/dsp_b%d.dcp" % (root,
                                                                          x),
                file=f)
            print(
                "write_edif -force %s/specimen_bram/dsp_b%d.edf" % (root, x),
                file=f)
            print(
                "write_bitstream -force %s/specimen_bram/dsp_b%d.bit" % (root,
                                                                         x),
                file=f)
    with open(root + "/dsp2/run.sh", "w") as f:
        print("#/usr/bin/env bash", file=f)
        #print("set -ex", file=f)
        for x in range(X):
            print(
                "vivado -mode batch -nolog -nojournal -source dsp_b%d.tcl" % x,
                file=f)
            print("if [ $? -eq 0 ]; then", file=f)
            print(
                "    ../../ultra/tools/dump_bitstream %s/specimen_bram/dsp_b%d.bit %s/frames.txt > %s/specimen_bram/dsp_b%d.dump"
                % (root, x, root, root, x),
                file=f)
            print(
                "    python3 ../../ultra/tools/bits_to_tiles.py %s/tile.json %s/specimen_bram/dsp_b%d.dump > %s/specimen_bram/dsp_b%d.tbits"
                % (root, root, x, root, x),
                file=f)
            print("else", file=f)
            print("   rm %s/specimen_bram/dsp_b%d.dump" % (root, x), file=f)
            print("   rm %s/specimen_bram/dsp_b%d.tbits" % (root, x), file=f)
            print("   rm %s/specimen_bram/dsp_b%d.dcp" % (root, x), file=f)
            print("   rm %s/specimen_bram/dsp_b%d.bit" % (root, x), file=f)
            print(
                "   rm %s/specimen_bram/dsp_b%d.features" % (root, x), file=f)
            print("fi", file=f)


if __name__ == "__main__":
    main()
