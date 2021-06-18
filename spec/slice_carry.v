// Copyright (C) 2020-2021  The Project U-Ray Authors.
//
// Use of this source code is governed by a ISC-style
// license that can be found in the LICENSE file or at
// https://opensource.org/licenses/ISC
//
// SPDX-License-Identifier: ISC

module ultra_slice_carry #(
	parameter [1023:0] LOC = "",
	parameter [1023:0] LOC2 = "",
	parameter [63:0]   ALUT_INIT = 64'h00C0FFEE,
	parameter [63:0]   BLUT_INIT = 64'h00C0FFEE,
	parameter [63:0]   CLUT_INIT = 64'h00C0FFEE,
	parameter [63:0]   DLUT_INIT = 64'h00C0FFEE,
	parameter [63:0]   ELUT_INIT = 64'h00C0FFEE,
	parameter [63:0]   FLUT_INIT = 64'h00C0FFEE,
	parameter [63:0]   GLUT_INIT = 64'h00C0FFEE,
	parameter [63:0]   HLUT_INIT = 64'h00C0FFEE,

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

	parameter [1023:0] DI0MUX  = "DI",
	parameter [1023:0] DI1MUX  = "DI",
	parameter [1023:0] DI2MUX  = "DI",
	parameter [1023:0] DI3MUX  = "DI",
	parameter [1023:0] DI4MUX  = "DI",
	parameter [1023:0] DI5MUX  = "DI",
	parameter [1023:0] DI6MUX  = "DI",
	parameter [1023:0] DI7MUX  = "DI",

	parameter [1023:0] CARRY_TYPE  = "NONE",

	parameter [1023:0] CIMUX  = "CI",
	parameter [1023:0] CITOPMUX  = "CI",

	parameter [1:0]    CLKINV = 2'b00, SRINV = 2'b00,
	parameter          CARRY_USED = 0

) (
	input [7:0] A1, A2, A3, A4, A5, A6, I, X,
	input [1:0] CLK, SR,
	input [3:0] CE,
	output [7:0] O, Q, Q2, MUX
);
	wire [7:0] out5;
	generate
	if (DI0MUX == "DI") (* BEL="A5LUT", LOC=LOC *) LUT4 #(.INIT(ALUT_INIT[15:0])) a5lut (.I0(A1[0]), .I1(A2[0]), .I2(A3[0]), .I3(A4[0]), .O(out5[0]));
	(* BEL="A6LUT", LOC=LOC, keep, dont_touch *) LUT4 #(.INIT(ALUT_INIT[47:32])) a6lut (.I0(A1[0]), .I1(A2[0]), .I2(A3[0]), .I3(A4[0]), .O(O[0]));
	if (DI1MUX == "DI") (* BEL="B5LUT", LOC=LOC *) LUT4 #(.INIT(BLUT_INIT[15:0])) b5lut (.I0(A1[1]), .I1(A2[1]), .I2(A3[1]), .I3(A4[1]), .O(out5[1]));
	(* BEL="B6LUT", LOC=LOC, keep, dont_touch *) LUT4 #(.INIT(BLUT_INIT[47:32])) b6lut (.I0(A1[1]), .I1(A2[1]), .I2(A3[1]), .I3(A4[1]), .O(O[1]));
	if (DI2MUX == "DI") (* BEL="C5LUT", LOC=LOC *) LUT4 #(.INIT(CLUT_INIT[15:0])) c5lut (.I0(A1[2]), .I1(A2[2]), .I2(A3[2]), .I3(A4[2]),.O(out5[2]));
	(* BEL="C6LUT", LOC=LOC, keep, dont_touch *) LUT4 #(.INIT(CLUT_INIT[47:32])) c6lut (.I0(A1[2]), .I1(A2[2]), .I2(A3[2]), .I3(A4[2]), .O(O[2]));
	if (DI3MUX == "DI") (* BEL="D5LUT", LOC=LOC *) LUT4 #(.INIT(DLUT_INIT[15:0])) d5lut (.I0(A1[3]), .I1(A2[3]), .I2(A3[3]), .I3(A4[3]),  .O(out5[3]));
	(* BEL="D6LUT", LOC=LOC, keep, dont_touch *) LUT4 #(.INIT(DLUT_INIT[47:32])) d6lut (.I0(A1[3]), .I1(A2[3]), .I2(A3[3]), .I3(A4[3]), .O(O[3]));

	if (DI4MUX == "DI") (* BEL="E5LUT", LOC=LOC *) LUT4 #(.INIT(ELUT_INIT[15:0])) e5lut (.I0(A1[4]), .I1(A2[4]), .I2(A3[4]), .I3(A4[4]), .O(out5[4]));
	(* BEL="E6LUT", LOC=LOC, keep, dont_touch *) LUT4 #(.INIT(ELUT_INIT[47:32])) e6lut (.I0(A1[4]), .I1(A2[4]), .I2(A3[4]), .I3(A4[4]), .O(O[4]));
	if (DI5MUX == "DI") (* BEL="F5LUT", LOC=LOC *) LUT4 #(.INIT(FLUT_INIT[15:0])) f5lut (.I0(A1[5]), .I1(A2[5]), .I2(A3[5]), .I3(A4[5]),  .O(out5[5]));
	(* BEL="F6LUT", LOC=LOC, keep, dont_touch *) LUT4 #(.INIT(FLUT_INIT[47:32])) f6lut (.I0(A1[5]), .I1(A2[5]), .I2(A3[5]), .I3(A4[5]), .O(O[5]));
	if (DI6MUX == "DI") (* BEL="G5LUT", LOC=LOC *) LUT4 #(.INIT(GLUT_INIT[15:0])) g5lut (.I0(A1[6]), .I1(A2[6]), .I2(A3[6]), .I3(A4[6]), .O(out5[6]));
	(* BEL="G6LUT", LOC=LOC, keep, dont_touch *) LUT4 #(.INIT(GLUT_INIT[47:32])) g6lut (.I0(A1[6]), .I1(A2[6]), .I2(A3[6]), .I3(A4[6]), .O(O[6]));
	if (DI7MUX == "DI") (* BEL="H5LUT", LOC=LOC *) LUT4 #(.INIT(HLUT_INIT[15:0])) h5lut (.I0(A1[7]), .I1(A2[7]), .I2(A3[7]), .I3(A4[7]), .O(out5[7]));
	(* BEL="H6LUT", LOC=LOC, keep, dont_touch *) LUT4 #(.INIT(HLUT_INIT[47:32])) h6lut (.I0(A1[7]), .I1(A2[7]), .I2(A3[7]), .I3(A4[7]), .O(O[7]));
	endgenerate

	wire [7:0] f7f8;
	assign f7f8 = 8'h55;
/*
	(* BEL="F7MUX_AB",  LOC=LOC, keep, dont_touch *) MUXF7 f7muxab_i (.I0(O[1]), .I1(O[0]), .S(X[0]), .O(f7f8[1]));
	(* BEL="F7MUX_CD",  LOC=LOC, keep, dont_touch *) MUXF7 f7muxcd_i (.I0(O[3]), .I1(O[2]), .S(X[2]), .O(f7f8[3]));
	(* BEL="F7MUX_EF",  LOC=LOC, keep, dont_touch *) MUXF7 f7muxef_i (.I0(O[5]), .I1(O[4]), .S(X[4]), .O(f7f8[5]));
	(* BEL="F7MUX_GH",  LOC=LOC, keep, dont_touch *) MUXF7 f7muxgh_i (.I0(O[7]), .I1(O[6]), .S(X[6]), .O(f7f8[7]));

	(* BEL="F8MUX_BOT", LOC=LOC, keep, dont_touch *) MUXF8 f8muxabcd_i (.I0(f7f8[3]), .I1(f7f8[1]), .S(X[1]), .O(f7f8[2]));
	(* BEL="F8MUX_TOP", LOC=LOC, keep, dont_touch *) MUXF8 f8muxefgh_i (.I0(f7f8[7]), .I1(f7f8[5]), .S(X[5]), .O(f7f8[6]));

	(* BEL="F9MUX",     LOC=LOC, keep, dont_touch *) MUXF9 f9_i (.I0(f7f8[6]), .I1(f7f8[2]), .S(X[3]), .O(f7f8[4]));
*/
	wire [7:0] di;
	wire ci, ci_top;
	ultra_slice_carry_dimux #(.SEL(DI0MUX)) di0mux_i (.DI(out5[0]), .X(X[0]), .OUT(di[0]));
	ultra_slice_carry_dimux #(.SEL(DI1MUX)) di1mux_i (.DI(out5[1]), .X(X[1]), .OUT(di[1]));
	ultra_slice_carry_dimux #(.SEL(DI2MUX)) di2mux_i (.DI(out5[2]), .X(X[2]), .OUT(di[2]));
	ultra_slice_carry_dimux #(.SEL(DI3MUX)) di3mux_i (.DI(out5[3]), .X(X[3]), .OUT(di[3]));
	ultra_slice_carry_dimux #(.SEL(DI4MUX)) di4mux_i (.DI(out5[4]), .X(X[4]), .OUT(di[4]));
	ultra_slice_carry_dimux #(.SEL(DI5MUX)) di5mux_i (.DI(out5[5]), .X(X[5]), .OUT(di[5]));
	ultra_slice_carry_dimux #(.SEL(DI6MUX)) di6mux_i (.DI(out5[6]), .X(X[6]), .OUT(di[6]));
	ultra_slice_carry_dimux #(.SEL(DI7MUX)) di7mux_i (.DI(out5[7]), .X(X[7]), .OUT(di[7]));

	ultra_slice_carry_cimux #(.SEL(CIMUX)) cimux_i (.CI(), .X(X[0]), .OUT(ci));
	ultra_slice_carry_cimux #(.SEL(CITOPMUX)) citopmux_i (.CI(), .X(X[4]), .OUT(ci_top));

	wire [7:0] xoro, cout;

	generate
		if (CARRY_TYPE != "NONE") begin
			(* BEL="CARRY8", LOC=LOC, keep, dont_touch *) CARRY8 #(.CARRY_TYPE(CARRY_TYPE)) c8_i(.CI(ci), .CI_TOP(ci_top), .DI(di), .S(O), .O(xoro), .CO(cout));
			if (CARRY_USED) begin
				(* BEL="CARRY8", LOC=LOC2, keep, dont_touch *) CARRY8 #(
					.CARRY_TYPE("SINGLE_CY8")
				) c8_i2 (.CI(cout[7]), .CI_TOP(), .DI(), .S(), .O(), .CO());
			end
		end
	endgenerate

	wire [15:0] ffin;
	ultra_slice_logic_ffmux #(.SEL(FFMUXA1)) ffmuxa1_i (.XORIN(xoro[0]), .F7F8(f7f8[0]), .D6(O[0]), .D5(out5[0]), .CY(cout[0]), .BYP(), .OUT(ffin[0]));
	ultra_slice_logic_ffmux #(.SEL(FFMUXA2)) ffmuxa2_i (.XORIN(xoro[0]), .F7F8(f7f8[0]), .D6(O[0]), .D5(out5[0]), .CY(cout[0]), .BYP(I[0]), .OUT(ffin[1]));
	ultra_slice_logic_ffmux #(.SEL(FFMUXB1)) ffmuxb1_i (.XORIN(xoro[1]), .F7F8(f7f8[1]), .D6(O[1]), .D5(out5[1]), .CY(cout[1]), .BYP(), .OUT(ffin[2]));
	ultra_slice_logic_ffmux #(.SEL(FFMUXB2)) ffmuxb2_i (.XORIN(xoro[1]), .F7F8(f7f8[1]), .D6(O[1]), .D5(out5[1]), .CY(cout[1]), .BYP(I[1]), .OUT(ffin[3]));
	ultra_slice_logic_ffmux #(.SEL(FFMUXC1)) ffmuxc1_i (.XORIN(xoro[2]), .F7F8(f7f8[2]), .D6(O[2]), .D5(out5[2]), .CY(cout[2]), .BYP(), .OUT(ffin[4]));
	ultra_slice_logic_ffmux #(.SEL(FFMUXC2)) ffmuxc2_i (.XORIN(xoro[2]), .F7F8(f7f8[2]), .D6(O[2]), .D5(out5[2]), .CY(cout[2]), .BYP(I[2]), .OUT(ffin[5]));
	ultra_slice_logic_ffmux #(.SEL(FFMUXD1)) ffmuxd1_i (.XORIN(xoro[3]), .F7F8(f7f8[3]), .D6(O[3]), .D5(out5[3]), .CY(cout[3]), .BYP(), .OUT(ffin[6]));
	ultra_slice_logic_ffmux #(.SEL(FFMUXD2)) ffmuxd2_i (.XORIN(xoro[3]), .F7F8(f7f8[3]), .D6(O[3]), .D5(out5[3]), .CY(cout[3]), .BYP(I[3]), .OUT(ffin[7]));

	ultra_slice_logic_ffmux #(.SEL(FFMUXE1)) ffmuxe1_i (.XORIN(xoro[4]), .F7F8(f7f8[4]), .D6(O[4]), .D5(out5[4]), .CY(cout[4]), .BYP(), .OUT(ffin[8]));
	ultra_slice_logic_ffmux #(.SEL(FFMUXE2)) ffmuxe2_i (.XORIN(xoro[4]), .F7F8(f7f8[4]), .D6(O[4]), .D5(out5[4]), .CY(cout[4]), .BYP(I[4]), .OUT(ffin[9]));
	ultra_slice_logic_ffmux #(.SEL(FFMUXF1)) ffmuxf1_i (.XORIN(xoro[5]), .F7F8(f7f8[5]), .D6(O[5]), .D5(out5[5]), .CY(cout[5]), .BYP(), .OUT(ffin[10]));
	ultra_slice_logic_ffmux #(.SEL(FFMUXF2)) ffmuxf2_i (.XORIN(xoro[5]), .F7F8(f7f8[5]), .D6(O[5]), .D5(out5[5]), .CY(cout[5]), .BYP(I[5]), .OUT(ffin[11]));
	ultra_slice_logic_ffmux #(.SEL(FFMUXG1)) ffmuxg1_i (.XORIN(xoro[6]), .F7F8(f7f8[6]), .D6(O[6]), .D5(out5[6]), .CY(cout[6]), .BYP(), .OUT(ffin[12]));
	ultra_slice_logic_ffmux #(.SEL(FFMUXG2)) ffmuxg2_i (.XORIN(xoro[6]), .F7F8(f7f8[6]), .D6(O[6]), .D5(out5[6]), .CY(cout[6]), .BYP(I[6]), .OUT(ffin[13]));
	ultra_slice_logic_ffmux #(.SEL(FFMUXH1)) ffmuxh1_i (.XORIN(xoro[7]), .F7F8(f7f8[7]), .D6(O[7]), .D5(out5[7]), .CY(cout[7]), .BYP(), .OUT(ffin[14]));
	ultra_slice_logic_ffmux #(.SEL(FFMUXH2)) ffmuxh2_i (.XORIN(xoro[7]), .F7F8(f7f8[7]), .D6(O[7]), .D5(out5[7]), .CY(cout[7]), .BYP(I[7]), .OUT(ffin[15]));

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

	ultra_slice_logic_outmux #(.SEL(OUTMUXA)) outmuxa_i (.XORIN(xoro[0]), .F7F8(f7f8[0]), .D6(O[0]), .D5(out5[0]), .CY(cout[0]), .OUT(MUX[0]));
	ultra_slice_logic_outmux #(.SEL(OUTMUXB)) outmuxb_i (.XORIN(xoro[1]), .F7F8(f7f8[1]), .D6(O[1]), .D5(out5[1]), .CY(cout[1]), .OUT(MUX[1]));
	ultra_slice_logic_outmux #(.SEL(OUTMUXC)) outmuxc_i (.XORIN(xoro[2]), .F7F8(f7f8[2]), .D6(O[2]), .D5(out5[2]), .CY(cout[2]), .OUT(MUX[2]));
	ultra_slice_logic_outmux #(.SEL(OUTMUXD)) outmuxd_i (.XORIN(xoro[3]), .F7F8(f7f8[3]), .D6(O[3]), .D5(out5[3]), .CY(cout[3]), .OUT(MUX[3]));

	ultra_slice_logic_outmux #(.SEL(OUTMUXE)) outmuxe_i (.XORIN(xoro[4]), .F7F8(f7f8[4]), .D6(O[4]), .D5(out5[4]), .CY(cout[4]), .OUT(MUX[4]));
	ultra_slice_logic_outmux #(.SEL(OUTMUXF)) outmuxf_i (.XORIN(xoro[5]), .F7F8(f7f8[5]), .D6(O[5]), .D5(out5[5]), .CY(cout[5]), .OUT(MUX[5]));
	ultra_slice_logic_outmux #(.SEL(OUTMUXG)) outmuxg_i (.XORIN(xoro[6]), .F7F8(f7f8[6]), .D6(O[6]), .D5(out5[6]), .CY(cout[6]), .OUT(MUX[6]));
	ultra_slice_logic_outmux #(.SEL(OUTMUXH)) outmuxh_i (.XORIN(xoro[7]), .F7F8(f7f8[7]), .D6(O[7]), .D5(out5[7]), .CY(cout[7]), .OUT(MUX[7]));


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

module ultra_slice_carry_dimux #(
	parameter SEL = "DI"
) (
	input DI, X,
	output OUT
);
	generate
		case(SEL)
			"DI": assign OUT = DI;
			"X":  assign OUT = X;
		endcase
	endgenerate
endmodule

module ultra_slice_carry_cimux #(
	parameter SEL = "CI"
) (
	input CI, X,
	output OUT
);
	generate
		case(SEL)
			"CI": assign OUT = CI;
			"0":  assign OUT = 1'b0;
			"1":  assign OUT = 1'b1;
			"X":  assign OUT = X;
		endcase
	endgenerate
endmodule
