// Copyright 2020 Project U-Ray Authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

module ultra_slice_memory #(
	parameter [1023:0] LOC = "",
	parameter [63:0]   ALUT_INIT = 64'h00C0FFEE,
	parameter [63:0]   BLUT_INIT = 64'h00C0FFEE,
	parameter [63:0]   CLUT_INIT = 64'h00C0FFEE,
	parameter [63:0]   DLUT_INIT = 64'h00C0FFEE,
	parameter [63:0]   ELUT_INIT = 64'h00C0FFEE,
	parameter [63:0]   FLUT_INIT = 64'h00C0FFEE,
	parameter [63:0]   GLUT_INIT = 64'h00C0FFEE,
	parameter [63:0]   HLUT_INIT = 64'h00C0FFEE,

	parameter [1023:0] A_MODE = "LOGIC",
	parameter [1023:0] B_MODE = "LOGIC",
	parameter [1023:0] C_MODE = "LOGIC",
	parameter [1023:0] D_MODE = "LOGIC",
	parameter [1023:0] E_MODE = "LOGIC",
	parameter [1023:0] F_MODE = "LOGIC",
	parameter [1023:0] G_MODE = "LOGIC",
	parameter [1023:0] H_MODE = "LOGIC",


	parameter [1023:0] AFF_TYPE = "NONE",
	parameter [1023:0] AFF2_TYPE = "NONE",
	parameter [1023:0] BFF_TYPE = "NONE",
	parameter [1023:0] BFF2_TYPE = "NONE",
	parameter [1023:0] CFF_TYPE = "NONE",
	parameter [1023:0] CFF2_TYPE = "NONE",
	parameter [1023:0] DFF_TYPE = "NONE",
	parameter [1023:0] DFF2_TYPE = "NONE",
	parameter [1023:0] EFF_TYPE = "NONE",
	parameter [1023:0] EFF2_TYPE = "NONE",
	parameter [1023:0] FFF_TYPE = "NONE",
	parameter [1023:0] FFF2_TYPE = "NONE",
	parameter [1023:0] GFF_TYPE = "NONE",
	parameter [1023:0] GFF2_TYPE = "NONE",
	parameter [1023:0] HFF_TYPE = "NONE",
	parameter [1023:0] HFF2_TYPE = "NONE",

	parameter [15:0]   FF_INIT = 16'h0000,

	parameter [1023:0] FFMUXA1 = "BYP",
	parameter [1023:0] FFMUXA2 = "BYP",
	parameter [1023:0] FFMUXB1 = "BYP",
	parameter [1023:0] FFMUXB2 = "BYP",
	parameter [1023:0] FFMUXC1 = "BYP",
	parameter [1023:0] FFMUXC2 = "BYP",
	parameter [1023:0] FFMUXD1 = "BYP",
	parameter [1023:0] FFMUXD2 = "BYP",
	parameter [1023:0] FFMUXE1 = "BYP",
	parameter [1023:0] FFMUXE2 = "BYP",
	parameter [1023:0] FFMUXF1 = "BYP",
	parameter [1023:0] FFMUXF2 = "BYP",
	parameter [1023:0] FFMUXG1 = "BYP",
	parameter [1023:0] FFMUXG2 = "BYP",
	parameter [1023:0] FFMUXH1 = "BYP",
	parameter [1023:0] FFMUXH2 = "BYP",

	parameter [1023:0] OUTMUXA = "D5",
	parameter [1023:0] OUTMUXB = "D5",
	parameter [1023:0] OUTMUXC = "D5",
	parameter [1023:0] OUTMUXD = "D5",
	parameter [1023:0] OUTMUXE = "D5",
	parameter [1023:0] OUTMUXF = "D5",
	parameter [1023:0] OUTMUXG = "D5",
	parameter [1023:0] OUTMUXH = "D5",

	parameter [1023:0] DIMUXA = "DI",
	parameter [1023:0] DIMUXB = "DI",
	parameter [1023:0] DIMUXC = "DI",
	parameter [1023:0] DIMUXD = "DI",
	parameter [1023:0] DIMUXE = "DI",
	parameter [1023:0] DIMUXF = "DI",
	parameter [1023:0] DIMUXG = "DI",

	parameter WA6USED = 0, WA7USED = 0, WA8USED = 0, WCLKINV = 0,

	parameter [1:0]    CLKINV = 2'b00, SRINV = 2'b00

) (
	input [7:0] A1, A2, A3, A4, A5, A6, I, X,
	input [1:0] CLK, SR,
	input WCLK, WE,
	input [3:0] CE,
	output [7:0] O, Q, Q2, MUX
);

	wire [8:0] wa;
	assign wa[5:0] = {A6[7], A5[7], A4[7], A3[7], A2[7], A1[7]};
	generate
		if (WA6USED) assign wa[6] = X[6];
		if (WA7USED) assign wa[7] = X[5];
		if (WA8USED) assign wa[8] = X[3];
	endgenerate

	wire [7:0] di0;
	wire [7:0] mc31;

	assign di0[7] = I[7];

	ultra_slice_logic_dimux #(.SEL(DIMUXA)) dimuxa_i (.DI(I[0]), .SIN(mc31[1]), .OUT(di0[0]));
	ultra_slice_logic_dimux #(.SEL(DIMUXB)) dimuxb_i (.DI(I[1]), .SIN(mc31[2]), .OUT(di0[1]));
	ultra_slice_logic_dimux #(.SEL(DIMUXC)) dimuxc_i (.DI(I[2]), .SIN(mc31[3]), .OUT(di0[2]));
	ultra_slice_logic_dimux #(.SEL(DIMUXD)) dimuxd_i (.DI(I[3]), .SIN(mc31[4]), .OUT(di0[3]));
	ultra_slice_logic_dimux #(.SEL(DIMUXE)) dimuxe_i (.DI(I[4]), .SIN(mc31[5]), .OUT(di0[4]));
	ultra_slice_logic_dimux #(.SEL(DIMUXF)) dimuxf_i (.DI(I[5]), .SIN(mc31[6]), .OUT(di0[5]));
	ultra_slice_logic_dimux #(.SEL(DIMUXG)) dimuxg_i (.DI(I[6]), .SIN(mc31[7]), .OUT(di0[6]));

	wire [7:0] out5;
	ultra_slice_memory_lut #(.LOC(LOC), .BEL5("H5LUT"), .BEL6("H6LUT"), .MODE(H_MODE), .INIT(HLUT_INIT), .CLKINV(WCLKINV), .WA6USED(WA6USED), .WA7USED(WA7USED), .WA8USED(WA8USED), .OUTPUT_MC31(DIMUXG=="SIN")) hlut_i (.CLK(WCLK), .CE(WE), .A({A6[7], A5[7], A4[7], A3[7], A2[7], A1[7]}), .WA(wa), .DI({X[7], di0[7]}), .DO({O[7], out5[7]}), .MC31(mc31[7]));
	ultra_slice_memory_lut #(.LOC(LOC), .BEL5("A5LUT"), .BEL6("A6LUT"), .MODE(A_MODE), .INIT(ALUT_INIT), .CLKINV(WCLKINV), .WA6USED(WA6USED), .WA7USED(WA7USED), .WA8USED(WA8USED), .OUTPUT_MC31(1)) alut_i (.CLK(WCLK), .CE(WE), .A({A6[0], A5[0], A4[0], A3[0], A2[0], A1[0]}), .WA(wa), .DI({X[0], di0[0]}), .DO({O[0], out5[0]}), .MC31(mc31[0]));
	ultra_slice_memory_lut #(.LOC(LOC), .BEL5("B5LUT"), .BEL6("B6LUT"), .MODE(B_MODE), .INIT(BLUT_INIT), .CLKINV(WCLKINV), .WA6USED(WA6USED), .WA7USED(WA7USED), .WA8USED(WA8USED), .OUTPUT_MC31(DIMUXA=="SIN")) blut_i (.CLK(WCLK), .CE(WE), .A({A6[1], A5[1], A4[1], A3[1], A2[1], A1[1]}), .WA(wa), .DI({X[1], di0[1]}), .DO({O[1], out5[1]}), .MC31(mc31[1]));
	ultra_slice_memory_lut #(.LOC(LOC), .BEL5("C5LUT"), .BEL6("C6LUT"), .MODE(C_MODE), .INIT(CLUT_INIT), .CLKINV(WCLKINV), .WA6USED(WA6USED), .WA7USED(WA7USED), .WA8USED(WA8USED), .OUTPUT_MC31(DIMUXB=="SIN")) clut_i (.CLK(WCLK), .CE(WE), .A({A6[2], A5[2], A4[2], A3[2], A2[2], A1[2]}), .WA(wa), .DI({X[2], di0[2]}), .DO({O[2], out5[2]}), .MC31(mc31[2]));
	ultra_slice_memory_lut #(.LOC(LOC), .BEL5("D5LUT"), .BEL6("D6LUT"), .MODE(D_MODE), .INIT(DLUT_INIT), .CLKINV(WCLKINV), .WA6USED(WA6USED), .WA7USED(WA7USED), .WA8USED(WA8USED), .OUTPUT_MC31(DIMUXC=="SIN")) dlut_i (.CLK(WCLK), .CE(WE), .A({A6[3], A5[3], A4[3], A3[3], A2[3], A1[3]}), .WA(wa), .DI({X[3], di0[3]}), .DO({O[3], out5[3]}), .MC31(mc31[3]));
	ultra_slice_memory_lut #(.LOC(LOC), .BEL5("E5LUT"), .BEL6("E6LUT"), .MODE(E_MODE), .INIT(ELUT_INIT), .CLKINV(WCLKINV), .WA6USED(WA6USED), .WA7USED(WA7USED), .WA8USED(WA8USED), .OUTPUT_MC31(DIMUXD=="SIN")) elut_i (.CLK(WCLK), .CE(WE), .A({A6[4], A5[4], A4[4], A3[4], A2[4], A1[4]}), .WA(wa), .DI({X[4], di0[4]}), .DO({O[4], out5[4]}), .MC31(mc31[4]));
	ultra_slice_memory_lut #(.LOC(LOC), .BEL5("F5LUT"), .BEL6("F6LUT"), .MODE(F_MODE), .INIT(FLUT_INIT), .CLKINV(WCLKINV), .WA6USED(WA6USED), .WA7USED(WA7USED), .WA8USED(WA8USED), .OUTPUT_MC31(DIMUXE=="SIN")) flut_i (.CLK(WCLK), .CE(WE), .A({A6[5], A5[5], A4[5], A3[5], A2[5], A1[5]}), .WA(wa), .DI({X[5], di0[5]}), .DO({O[5], out5[5]}), .MC31(mc31[5]));
	ultra_slice_memory_lut #(.LOC(LOC), .BEL5("G5LUT"), .BEL6("G6LUT"), .MODE(G_MODE), .INIT(GLUT_INIT), .CLKINV(WCLKINV), .WA6USED(WA6USED), .WA7USED(WA7USED), .WA8USED(WA8USED), .OUTPUT_MC31(DIMUXF=="SIN")) glut_i (.CLK(WCLK), .CE(WE), .A({A6[6], A5[6], A4[6], A3[6], A2[6], A1[6]}), .WA(wa), .DI({X[6], di0[6]}), .DO({O[6], out5[6]}), .MC31(mc31[6]));

	wire [7:0] f7f8;
	assign f7f8[0] = mc31[0] ^ 1;
/*
	(* BEL="F7MUX_AB",  LOC=LOC, keep, dont_touch *) MUXF7 f7muxab_i (.I0(O[1]), .I1(O[0]), .S(X[0]), .O(f7f8[1]));
	(* BEL="F7MUX_CD",  LOC=LOC, keep, dont_touch *) MUXF7 f7muxcd_i (.I0(O[3]), .I1(O[2]), .S(X[2]), .O(f7f8[3]));
	(* BEL="F7MUX_EF",  LOC=LOC, keep, dont_touch *) MUXF7 f7muxef_i (.I0(O[5]), .I1(O[4]), .S(X[4]), .O(f7f8[5]));
	(* BEL="F7MUX_GH",  LOC=LOC, keep, dont_touch *) MUXF7 f7muxgh_i (.I0(O[7]), .I1(O[6]), .S(X[6]), .O(f7f8[7]));

	(* BEL="F8MUX_BOT", LOC=LOC, keep, dont_touch *) MUXF8 f8muxabcd_i (.I0(f7f8[3]), .I1(f7f8[1]), .S(X[1]), .O(f7f8[2]));
	(* BEL="F8MUX_TOP", LOC=LOC, keep, dont_touch *) MUXF8 f8muxefgh_i (.I0(f7f8[7]), .I1(f7f8[5]), .S(X[5]), .O(f7f8[6]));

	(* BEL="F9MUX",     LOC=LOC, keep, dont_touch *) MUXF9 f9_i (.I0(f7f8[6]), .I1(f7f8[2]), .S(X[3]), .O(f7f8[4]));
*/
	assign f7f8[7:1] = O[7:1];
	wire [15:0] ffin;
	ultra_slice_logic_ffmux #(.SEL(FFMUXA1)) ffmuxa1_i (.XORIN(), .F7F8(f7f8[0]), .D6(O[0]), .D5(out5[0]), .CY(), .BYP(X[0]), .OUT(ffin[0]));
	ultra_slice_logic_ffmux #(.SEL(FFMUXA2)) ffmuxa2_i (.XORIN(), .F7F8(f7f8[0]), .D6(O[0]), .D5(out5[0]), .CY(), .BYP(I[0]), .OUT(ffin[1]));
	ultra_slice_logic_ffmux #(.SEL(FFMUXB1)) ffmuxb1_i (.XORIN(), .F7F8(f7f8[1]), .D6(O[1]), .D5(out5[1]), .CY(), .BYP(X[1]), .OUT(ffin[2]));
	ultra_slice_logic_ffmux #(.SEL(FFMUXB2)) ffmuxb2_i (.XORIN(), .F7F8(f7f8[1]), .D6(O[1]), .D5(out5[1]), .CY(), .BYP(I[1]), .OUT(ffin[3]));
	ultra_slice_logic_ffmux #(.SEL(FFMUXC1)) ffmuxc1_i (.XORIN(), .F7F8(f7f8[2]), .D6(O[2]), .D5(out5[2]), .CY(), .BYP(X[2]), .OUT(ffin[4]));
	ultra_slice_logic_ffmux #(.SEL(FFMUXC2)) ffmuxc2_i (.XORIN(), .F7F8(f7f8[2]), .D6(O[2]), .D5(out5[2]), .CY(), .BYP(I[2]), .OUT(ffin[5]));
	ultra_slice_logic_ffmux #(.SEL(FFMUXD1)) ffmuxd1_i (.XORIN(), .F7F8(f7f8[3]), .D6(O[3]), .D5(out5[3]), .CY(), .BYP(X[3]), .OUT(ffin[6]));
	ultra_slice_logic_ffmux #(.SEL(FFMUXD2)) ffmuxd2_i (.XORIN(), .F7F8(f7f8[3]), .D6(O[3]), .D5(out5[3]), .CY(), .BYP(I[3]), .OUT(ffin[7]));

	ultra_slice_logic_ffmux #(.SEL(FFMUXE1)) ffmuxe1_i (.XORIN(), .F7F8(f7f8[4]), .D6(O[4]), .D5(out5[4]), .CY(), .BYP(X[4]), .OUT(ffin[8]));
	ultra_slice_logic_ffmux #(.SEL(FFMUXE2)) ffmuxe2_i (.XORIN(), .F7F8(f7f8[4]), .D6(O[4]), .D5(out5[4]), .CY(), .BYP(I[4]), .OUT(ffin[9]));
	ultra_slice_logic_ffmux #(.SEL(FFMUXF1)) ffmuxf1_i (.XORIN(), .F7F8(f7f8[5]), .D6(O[5]), .D5(out5[5]), .CY(), .BYP(X[5]), .OUT(ffin[10]));
	ultra_slice_logic_ffmux #(.SEL(FFMUXF2)) ffmuxf2_i (.XORIN(), .F7F8(f7f8[5]), .D6(O[5]), .D5(out5[5]), .CY(), .BYP(I[5]), .OUT(ffin[11]));
	ultra_slice_logic_ffmux #(.SEL(FFMUXG1)) ffmuxg1_i (.XORIN(), .F7F8(f7f8[6]), .D6(O[6]), .D5(out5[6]), .CY(), .BYP(X[6]), .OUT(ffin[12]));
	ultra_slice_logic_ffmux #(.SEL(FFMUXG2)) ffmuxg2_i (.XORIN(), .F7F8(f7f8[6]), .D6(O[6]), .D5(out5[6]), .CY(), .BYP(I[6]), .OUT(ffin[13]));
	ultra_slice_logic_ffmux #(.SEL(FFMUXH1)) ffmuxh1_i (.XORIN(), .F7F8(f7f8[7]), .D6(O[7]), .D5(out5[7]), .CY(), .BYP(X[7]), .OUT(ffin[14]));
	ultra_slice_logic_ffmux #(.SEL(FFMUXH2)) ffmuxh2_i (.XORIN(), .F7F8(f7f8[7]), .D6(O[7]), .D5(out5[7]), .CY(), .BYP(I[7]), .OUT(ffin[15]));

	ultra_slice_logic_ffx #(.LOC(LOC), .BEL("AFF"),  .TYPE(AFF_TYPE),  .CLKINV(CLKINV[0]), .SRINV(SRINV[0]), .INIT(FF_INIT[0])) aff_i  (.C(CLK[0]), .SR(SR[0]), .CE(CE[0]), .D(ffin[0]), .Q(Q[0]));
	ultra_slice_logic_ffx #(.LOC(LOC), .BEL("AFF2"), .TYPE(AFF2_TYPE), .CLKINV(CLKINV[0]), .SRINV(SRINV[0]), .INIT(FF_INIT[1])) aff2_i (.C(CLK[0]), .SR(SR[0]), .CE(CE[1]), .D(ffin[1]), .Q(Q2[0]));
	ultra_slice_logic_ffx #(.LOC(LOC), .BEL("BFF"),  .TYPE(BFF_TYPE),  .CLKINV(CLKINV[0]), .SRINV(SRINV[0]), .INIT(FF_INIT[2])) bff_i  (.C(CLK[0]), .SR(SR[0]), .CE(CE[0]), .D(ffin[2]), .Q(Q[1]));
	ultra_slice_logic_ffx #(.LOC(LOC), .BEL("BFF2"), .TYPE(BFF2_TYPE), .CLKINV(CLKINV[0]), .SRINV(SRINV[0]), .INIT(FF_INIT[3])) bff2_i (.C(CLK[0]), .SR(SR[0]), .CE(CE[1]), .D(ffin[3]), .Q(Q2[1]));
	ultra_slice_logic_ffx #(.LOC(LOC), .BEL("CFF"),  .TYPE(CFF_TYPE),  .CLKINV(CLKINV[0]), .SRINV(SRINV[0]), .INIT(FF_INIT[4])) cff_i  (.C(CLK[0]), .SR(SR[0]), .CE(CE[0]), .D(ffin[4]), .Q(Q[2]));
	ultra_slice_logic_ffx #(.LOC(LOC), .BEL("CFF2"), .TYPE(CFF2_TYPE), .CLKINV(CLKINV[0]), .SRINV(SRINV[0]), .INIT(FF_INIT[5])) cff2_i (.C(CLK[0]), .SR(SR[0]), .CE(CE[1]), .D(ffin[5]), .Q(Q2[2]));
	ultra_slice_logic_ffx #(.LOC(LOC), .BEL("DFF"),  .TYPE(DFF_TYPE),  .CLKINV(CLKINV[0]), .SRINV(SRINV[0]), .INIT(FF_INIT[6])) dff_i  (.C(CLK[0]), .SR(SR[0]), .CE(CE[0]), .D(ffin[6]), .Q(Q[3]));
	ultra_slice_logic_ffx #(.LOC(LOC), .BEL("DFF2"), .TYPE(DFF2_TYPE), .CLKINV(CLKINV[0]), .SRINV(SRINV[0]), .INIT(FF_INIT[7])) dff2_i (.C(CLK[0]), .SR(SR[0]), .CE(CE[1]), .D(ffin[7]), .Q(Q2[3]));

	ultra_slice_logic_ffx #(.LOC(LOC), .BEL("EFF"),  .TYPE(EFF_TYPE),  .CLKINV(CLKINV[1]), .SRINV(SRINV[1]), .INIT(FF_INIT[8])) eff_i  (.C(CLK[1]), .SR(SR[1]), .CE(CE[2]), .D(ffin[8]), .Q(Q[4]));
	ultra_slice_logic_ffx #(.LOC(LOC), .BEL("EFF2"), .TYPE(EFF2_TYPE), .CLKINV(CLKINV[1]), .SRINV(SRINV[1]), .INIT(FF_INIT[9])) eff2_i (.C(CLK[1]), .SR(SR[1]), .CE(CE[3]), .D(ffin[9]), .Q(Q2[4]));
	ultra_slice_logic_ffx #(.LOC(LOC), .BEL("FFF"),  .TYPE(FFF_TYPE),  .CLKINV(CLKINV[1]), .SRINV(SRINV[1]), .INIT(FF_INIT[10])) fff_i  (.C(CLK[1]), .SR(SR[1]), .CE(CE[2]), .D(ffin[10]), .Q(Q[5]));
	ultra_slice_logic_ffx #(.LOC(LOC), .BEL("FFF2"), .TYPE(FFF2_TYPE), .CLKINV(CLKINV[1]), .SRINV(SRINV[1]), .INIT(FF_INIT[11])) fff2_i (.C(CLK[1]), .SR(SR[1]), .CE(CE[3]), .D(ffin[11]), .Q(Q2[5]));
	ultra_slice_logic_ffx #(.LOC(LOC), .BEL("GFF"),  .TYPE(GFF_TYPE),  .CLKINV(CLKINV[1]), .SRINV(SRINV[1]), .INIT(FF_INIT[12])) gff_i  (.C(CLK[1]), .SR(SR[1]), .CE(CE[2]), .D(ffin[12]), .Q(Q[6]));
	ultra_slice_logic_ffx #(.LOC(LOC), .BEL("GFF2"), .TYPE(GFF2_TYPE), .CLKINV(CLKINV[1]), .SRINV(SRINV[1]), .INIT(FF_INIT[13])) gff2_i (.C(CLK[1]), .SR(SR[1]), .CE(CE[3]), .D(ffin[13]), .Q(Q2[6]));
	ultra_slice_logic_ffx #(.LOC(LOC), .BEL("HFF"),  .TYPE(HFF_TYPE),  .CLKINV(CLKINV[1]), .SRINV(SRINV[1]), .INIT(FF_INIT[14])) hff_i  (.C(CLK[1]), .SR(SR[1]), .CE(CE[2]), .D(ffin[14]), .Q(Q[7]));
	ultra_slice_logic_ffx #(.LOC(LOC), .BEL("HFF2"), .TYPE(HFF2_TYPE), .CLKINV(CLKINV[1]), .SRINV(SRINV[1]), .INIT(FF_INIT[15])) hff2_i (.C(CLK[1]), .SR(SR[1]), .CE(CE[3]), .D(ffin[15]), .Q(Q2[7]));

	ultra_slice_logic_outmux #(.SEL(OUTMUXA)) outmuxa_i (.XORIN(), .F7F8(f7f8[0]), .D6(O[0]), .D5(out5[0]), .CY(), .OUT(MUX[0]));
	ultra_slice_logic_outmux #(.SEL(OUTMUXB)) outmuxb_i (.XORIN(), .F7F8(f7f8[1]), .D6(O[1]), .D5(out5[1]), .CY(), .OUT(MUX[1]));
	ultra_slice_logic_outmux #(.SEL(OUTMUXC)) outmuxc_i (.XORIN(), .F7F8(f7f8[2]), .D6(O[2]), .D5(out5[2]), .CY(), .OUT(MUX[2]));
	ultra_slice_logic_outmux #(.SEL(OUTMUXD)) outmuxd_i (.XORIN(), .F7F8(f7f8[3]), .D6(O[3]), .D5(out5[3]), .CY(), .OUT(MUX[3]));

	ultra_slice_logic_outmux #(.SEL(OUTMUXE)) outmuxe_i (.XORIN(), .F7F8(f7f8[4]), .D6(O[4]), .D5(out5[4]), .CY(), .OUT(MUX[4]));
	ultra_slice_logic_outmux #(.SEL(OUTMUXF)) outmuxf_i (.XORIN(), .F7F8(f7f8[5]), .D6(O[5]), .D5(out5[5]), .CY(), .OUT(MUX[5]));
	ultra_slice_logic_outmux #(.SEL(OUTMUXG)) outmuxg_i (.XORIN(), .F7F8(f7f8[6]), .D6(O[6]), .D5(out5[6]), .CY(), .OUT(MUX[6]));
	ultra_slice_logic_outmux #(.SEL(OUTMUXH)) outmuxh_i (.XORIN(), .F7F8(f7f8[7]), .D6(O[7]), .D5(out5[7]), .CY(), .OUT(MUX[7]));


endmodule

module ultra_slice_logic_ffmux #(
	parameter [1023:0] SEL = "BYP"
) (
	input XORIN, F7F8, D6, D5, CY, BYP,
	output OUT
);
	generate
		case(SEL)
			"XORIN": assign OUT = XORIN;
			"F7F8":  assign OUT = F7F8;
			"D6":    assign OUT = D6;
			"D5":    assign OUT = D5;
			"CY":    assign OUT = CY;
			"BYP":   assign OUT = BYP;
		endcase
	endgenerate
endmodule

module ultra_slice_logic_ffx #(
	parameter [1023:0] LOC = "",
	parameter [1023:0] BEL = "",
	parameter [1023:0] TYPE = "",
	parameter CLKINV = 1'b0,
	parameter SRINV = 1'b0,
	parameter INIT = 1'b0
) (
	input C, CE, SR, D,
	output Q
);
	generate
		case (TYPE)
			"FDPE": (* LOC=LOC, BEL=BEL, keep, dont_touch *) FDPE #(.IS_C_INVERTED(CLKINV), .IS_PRE_INVERTED(SRINV), .INIT(INIT)) ff_i (.C(C), .CE(CE), .PRE(SR), .D(D), .Q(Q));
			"FDCE": (* LOC=LOC, BEL=BEL, keep, dont_touch *) FDCE #(.IS_C_INVERTED(CLKINV), .IS_CLR_INVERTED(SRINV), .INIT(INIT)) ff_i (.C(C), .CE(CE), .CLR(SR), .D(D), .Q(Q));
			"FDSE": (* LOC=LOC, BEL=BEL, keep, dont_touch *) FDSE #(.IS_C_INVERTED(CLKINV), .IS_S_INVERTED(SRINV), .INIT(INIT)) ff_i (.C(C), .CE(CE), .S(SR), .D(D), .Q(Q));
			"FDRE": (* LOC=LOC, BEL=BEL, keep, dont_touch *) FDRE #(.IS_C_INVERTED(CLKINV), .IS_R_INVERTED(SRINV), .INIT(INIT)) ff_i (.C(C), .CE(CE), .R(SR), .D(D), .Q(Q));

			"LDPE": (* LOC=LOC, BEL=BEL, keep, dont_touch *) LDPE #(.IS_G_INVERTED(CLKINV), .IS_PRE_INVERTED(SRINV), .INIT(INIT)) ff_i (.G(C), .GE(CE), .PRE(SR), .D(D), .Q(Q));
			"LDCE": (* LOC=LOC, BEL=BEL, keep, dont_touch *) LDCE #(.IS_G_INVERTED(CLKINV), .IS_CLR_INVERTED(SRINV), .INIT(INIT)) ff_i (.G(C), .GE(CE), .CLR(SR), .D(D), .Q(Q));
			"NONE": assign Q = INIT;
		endcase
	endgenerate
endmodule

module ultra_slice_logic_outmux #(
	parameter SEL = "D5"
) (
	input XORIN, F7F8, D6, D5, CY,
	output OUT
);
	generate
		case(SEL)
			"XORIN": assign OUT = XORIN;
			"F7F8":  assign OUT = F7F8;
			"D6":    assign OUT = D6;
			"D5":    assign OUT = D5;
			"CY":    assign OUT = CY;
		endcase
	endgenerate
endmodule

module ultra_slice_logic_dimux #(
	parameter [1023:0] SEL = "DI"
) (
	input DI, SIN,
	output OUT
);
	generate
		case(SEL)
			"DI": assign OUT = DI;
			"SIN":  assign OUT = SIN;
		endcase
	endgenerate
endmodule

module ultra_slice_memory_lut #(
	parameter [1023:0] LOC = "",
	parameter [1023:0] BEL5 = "",
	parameter [1023:0] BEL6 = "",
	parameter [1023:0] MODE = "LOGIC",
	parameter [63:0] INIT = 64'h0,
	parameter CLKINV = 0, WA6USED = 0, WA7USED = 0, WA8USED = 0, OUTPUT_MC31 = 0
) (
	input CLK, CE,
	input [5:0] A,
	input [8:0] WA,
	input [1:0] DI,
	output [1:0] DO,
	output MC31
);
	generate
		if (MODE == "LOGIC") begin
			(* keep, dont_touch *) LUT5 #(.INIT(INIT[63:32])) lut6 (.I0(A[0]), .I1(A[1]), .I2(A[2]), .I3(A[3]), .I4(A[4]), .O(DO[1]));
			(* keep, dont_touch *) LUT5 #(.INIT(INIT[31:0])) lut5 (.I0(A[0]), .I1(A[1]), .I2(A[2]), .I3(A[3]), .I4(A[4]), .O(DO[0]));
			assign MC31 = DO[1];
		end else if (MODE == "SRL16") begin
			(* keep, dont_touch *) SRL16E #(.INIT(INIT[63:32]), .IS_CLK_INVERTED(CLKINV)) srl6 (.A0(1'b1), .A1(1'b1), .A2(1'b1), .A3(1'b1), .D(DI[1]), .CLK(CLK), .CE(CE), .Q(DO[1]));
			(* keep, dont_touch *) SRL16E #(.INIT(INIT[31:0]), .IS_CLK_INVERTED(CLKINV)) srl5 (.A0(1'b1), .A1(1'b1), .A2(1'b1), .A3(1'b1), .D(DI[0]), .CLK(CLK), .CE(CE), .Q(DO[0]));
			assign MC31 = DO[1];
		end else if (MODE == "SRL32") begin
			if (OUTPUT_MC31) begin
				(* keep, dont_touch *) SRLC32E #(.INIT(INIT[31:0]), .IS_CLK_INVERTED(CLKINV)) srl6(.A(5'b11111), .D(DI[0]), .CLK(CLK), .CE(CE), .Q(DO[1]), .Q31(MC31));
			end else begin
				(* keep, dont_touch *) SRLC32E #(.INIT(INIT[31:0]), .IS_CLK_INVERTED(CLKINV)) srl6(.A(5'b11111), .D(DI[0]), .CLK(CLK), .CE(CE), .Q(DO[1]));
			end
			assign DO[0] = DO[1];
		end else if (MODE == "RAMD64") begin
			if (WA6USED && WA7USED) begin
				(* keep, dont_touch *) RAMD64E #(.INIT(INIT), .IS_CLK_INVERTED(CLKINV)) ram_i (
					.RADR0(A[0]), .RADR1(A[1]), .RADR2(A[2]), .RADR3(A[3]), .RADR4(A[4]), .RADR5(A[5]),
					.WADR0(WA[0]), .WADR1(WA[1]), .WADR2(WA[2]), .WADR3(WA[3]), .WADR4(WA[4]), .WADR5(WA[5]), .WADR6(WA[6]), .WADR7(WA[7]),
					.CLK(CLK), .WE(CE),
					.I(DI[0]), .O(DO[1])
				);

			end else if (WA6USED) begin
				(* keep, dont_touch *) RAMD64E #(.INIT(INIT), .IS_CLK_INVERTED(CLKINV)) ram_i (
					.RADR0(A[0]), .RADR1(A[1]), .RADR2(A[2]), .RADR3(A[3]), .RADR4(A[4]), .RADR5(A[5]),
					.WADR0(WA[0]), .WADR1(WA[1]), .WADR2(WA[2]), .WADR3(WA[3]), .WADR4(WA[4]), .WADR5(WA[5]), .WADR6(WA[6]),
					.CLK(CLK), .WE(CE),
					.I(DI[0]), .O(DO[1])
				);
			end else begin
				(* keep, dont_touch *) RAMD64E #(.INIT(INIT), .IS_CLK_INVERTED(CLKINV)) ram_i (
					.RADR0(A[0]), .RADR1(A[1]), .RADR2(A[2]), .RADR3(A[3]), .RADR4(A[4]), .RADR5(A[5]),
					.WADR0(WA[0]), .WADR1(WA[1]), .WADR2(WA[2]), .WADR3(WA[3]), .WADR4(WA[4]), .WADR5(WA[5]),
					.CLK(CLK), .WE(CE),
					.I(DI[0]), .O(DO[1])
				);
			end
			assign DO[0] = DO[1];
			assign MC31 = DO[1];
		end else if (MODE == "RAMS64") begin
			if (WA6USED && WA7USED && WA8USED) begin
				(* keep, dont_touch *) RAMS64E1 #(.INIT(INIT), .IS_CLK_INVERTED(CLKINV)) ram_i (
					.ADR0(WA[0]), .ADR1(WA[1]), .ADR2(WA[2]), .ADR3(WA[3]), .ADR4(WA[4]), .ADR5(WA[5]),
					.WADR6(WA[6]), .WADR7(WA[7]), .WADR8(WA[8]),
					.CLK(CLK), .WE(CE),
					.I(DI[0]), .O(DO[1])
				);
			end else if (WA6USED && WA7USED) begin
				(* keep, dont_touch *) RAMS64E1 #(.INIT(INIT), .IS_CLK_INVERTED(CLKINV)) ram_i (
					.ADR0(WA[0]), .ADR1(WA[1]), .ADR2(WA[2]), .ADR3(WA[3]), .ADR4(WA[4]), .ADR5(WA[5]),
					.WADR6(WA[6]), .WADR7(WA[7]),
					.CLK(CLK), .WE(CE),
					.I(DI[0]), .O(DO[1])
				);
			end else if (WA6USED) begin
				(* keep, dont_touch *) RAMS64E1 #(.INIT(INIT), .IS_CLK_INVERTED(CLKINV)) ram_i (
					.ADR0(WA[0]), .ADR1(WA[1]), .ADR2(WA[2]), .ADR3(WA[3]), .ADR4(WA[4]), .ADR5(WA[5]),
					.WADR6(WA[6]),
					.CLK(CLK), .WE(CE),
					.I(DI[0]), .O(DO[1])
				);
			end else begin
				(* keep, dont_touch *) RAMS64E1 #(.INIT(INIT), .IS_CLK_INVERTED(CLKINV)) ram_i (
					.ADR0(WA[0]), .ADR1(WA[1]), .ADR2(WA[2]), .ADR3(WA[3]), .ADR4(WA[4]), .ADR5(WA[5]),
					.CLK(CLK), .WE(CE),
					.I(DI[0]), .O(DO[1])
				);
			end
			assign DO[0] = DO[1];
			assign MC31 = DO[1];
		end else if (MODE == "RAMS32") begin
			(* keep, dont_touch *) RAMS32 #(.INIT(INIT[63:32]), .IS_CLK_INVERTED(CLKINV)) ram1_i (
				.ADR0(WA[0]), .ADR1(WA[1]), .ADR2(WA[2]), .ADR3(WA[3]), .ADR4(WA[4]),
				.CLK(CLK), .WE(CE),
				.I(DI[1]), .O(DO[1])
			);
			(* keep, dont_touch *) RAMS32 #(.INIT(INIT[31:0]), .IS_CLK_INVERTED(CLKINV)) ram0_i (
				.ADR0(WA[0]), .ADR1(WA[1]), .ADR2(WA[2]), .ADR3(WA[3]), .ADR4(WA[4]),
				.CLK(CLK), .WE(CE),
				.I(DI[0]), .O(DO[0])
			);
			assign MC31 = DO[1];
		end else if (MODE == "RAMD32") begin
			(* keep, dont_touch *) RAMD32 #(.INIT(INIT[63:32]), .IS_CLK_INVERTED(CLKINV)) ram1_i (
				.WADR0(WA[0]), .WADR1(WA[1]), .WADR2(WA[2]), .WADR3(WA[3]), .WADR4(WA[4]),
				.RADR0(A[0]), .RADR1(A[1]), .RADR2(A[2]), .RADR3(A[3]), .RADR4(A[4]),
				.CLK(CLK), .WE(CE),
				.I(DI[1]), .O(DO[1])
			);
			(* keep, dont_touch *) RAMD32 #(.INIT(INIT[31:0]), .IS_CLK_INVERTED(CLKINV)) ram0_i (
				.WADR0(WA[0]), .WADR1(WA[1]), .WADR2(WA[2]), .WADR3(WA[3]), .WADR4(WA[4]),
				.RADR0(A[0]), .RADR1(A[1]), .RADR2(A[2]), .RADR3(A[3]), .RADR4(A[4]),
				.CLK(CLK), .WE(CE),
				.I(DI[0]), .O(DO[0])
			);
			assign MC31 = DO[1];
		end else begin
			$error("unsupported mode");
		end
	endgenerate
endmodule
