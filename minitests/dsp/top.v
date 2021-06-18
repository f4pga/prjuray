// Copyright (C) 2020-2021  The Project U-Ray Authors.
//
// Use of this source code is governed by a ISC-style
// license that can be found in the LICENSE file or at
// https://opensource.org/licenses/ISC
//
// SPDX-License-Identifier: ISC

module top(input clk, stb, di, output do);
    localparam integer DIN_N = 160;
    localparam integer DOUT_N = 160;

    reg [DIN_N-1:0] din;
    wire [DOUT_N-1:0] dout;

    reg [DIN_N-1:0] din_shr;
    reg [DOUT_N-1:0] dout_shr;

    always @(posedge clk) begin
        din_shr <= {din_shr, di};
        dout_shr <= {dout_shr, din_shr[DIN_N-1]};
        if (stb) begin
            din <= din_shr;
            dout_shr <= dout;
        end
    end

    assign do = dout_shr[DOUT_N-1];

    roi roi (
        .clk(clk),
        .din(din),
        .dout(dout)
    );
endmodule

module roi(input clk, input [159:0] din, output [159:0] dout);
	my_DSP
	#(
		.LOC("DSP48E2_X0Y120")
	)
	inst_0 (
		.clk(clk),
		.din(din[  0 +: 11]),
		.dout(dout[ 0 +: 5])
	);
endmodule

// ---------------------------------------------------------------------
module my_DSP (input clk, input [10:0] din, output [4:0] dout);

   parameter LOC = "";

   (* LOC=LOC *)
   DSP48E2 #(
      // Feature Control Attributes: Data Path Selection
      .AMULTSEL("A"),                    // Selects A input to multiplier (A, AD)
      .A_INPUT("DIRECT"),                // Selects A input source, "DIRECT" (A port) or "CASCADE" (ACIN port)
      .BMULTSEL("B"),                    // Selects B input to multiplier (AD, B)
      .B_INPUT("DIRECT"),                // Selects B input source, "DIRECT" (B port) or "CASCADE" (BCIN port)
      .PREADDINSEL("A"),                 // Selects input to pre-adder (A, B)
      .RND(48'h000000000000),            // Rounding Constant
      .USE_MULT("MULTIPLY"),             // Select multiplier usage (DYNAMIC, MULTIPLY, NONE)
      .USE_SIMD("ONE48"),                // SIMD selection (FOUR12, ONE48, TWO24)
      .USE_WIDEXOR("FALSE"),             // Use the Wide XOR function (FALSE, TRUE)
      .XORSIMD("XOR24_48_96"),           // Mode of operation for the Wide XOR (XOR12, XOR24_48_96)
      // Pattern Detector Attributes: Pattern Detection Configuration
      .AUTORESET_PATDET("NO_RESET"),     // NO_RESET, RESET_MATCH, RESET_NOT_MATCH
      .AUTORESET_PRIORITY("RESET"),      // Priority of AUTORESET vs. CEP (CEP, RESET).
      .MASK(48'h3fffffffffff),           // 48-bit mask value for pattern detect (1=ignore)
      .PATTERN(48'h000000000000),        // 48-bit pattern match for pattern detect
      .SEL_MASK("MASK"),                 // C, MASK, ROUNDING_MODE1, ROUNDING_MODE2
      .SEL_PATTERN("PATTERN"),           // Select pattern value (C, PATTERN)
      .USE_PATTERN_DETECT("NO_PATDET"),  // Enable pattern detect (NO_PATDET, PATDET)
      // Programmable Inversion Attributes: Specifies built-in programmable inversion on specific pins
      .IS_ALUMODE_INVERTED(4'b0000),     // Optional inversion for ALUMODE
      .IS_CARRYIN_INVERTED(1'b0),        // Optional inversion for CARRYIN
      .IS_CLK_INVERTED(1'b0),            // Optional inversion for CLK
      .IS_INMODE_INVERTED(5'b00000),     // Optional inversion for INMODE
      .IS_OPMODE_INVERTED(9'b000000000), // Optional inversion for OPMODE
      .IS_RSTALLCARRYIN_INVERTED(1'b0),  // Optional inversion for RSTALLCARRYIN
      .IS_RSTALUMODE_INVERTED(1'b0),     // Optional inversion for RSTALUMODE
      .IS_RSTA_INVERTED(1'b0),           // Optional inversion for RSTA
      .IS_RSTB_INVERTED(1'b0),           // Optional inversion for RSTB
      .IS_RSTCTRL_INVERTED(1'b0),        // Optional inversion for RSTCTRL
      .IS_RSTC_INVERTED(1'b0),           // Optional inversion for RSTC
      .IS_RSTD_INVERTED(1'b0),           // Optional inversion for RSTD
      .IS_RSTINMODE_INVERTED(1'b0),      // Optional inversion for RSTINMODE
      .IS_RSTM_INVERTED(1'b0),           // Optional inversion for RSTM
      .IS_RSTP_INVERTED(1'b0),           // Optional inversion for RSTP
      // Register Control Attributes: Pipeline Register Configuration
      .ACASCREG(1),                      // Number of pipeline stages between A/ACIN and ACOUT (0-2)
      .ADREG(1),                         // Pipeline stages for pre-adder (0-1)
      .ALUMODEREG(1),                    // Pipeline stages for ALUMODE (0-1)
      .AREG(1),                          // Pipeline stages for A (0-2)
      .BCASCREG(1),                      // Number of pipeline stages between B/BCIN and BCOUT (0-2)
      .BREG(1),                          // Pipeline stages for B (0-2)
      .CARRYINREG(1),                    // Pipeline stages for CARRYIN (0-1)
      .CARRYINSELREG(1),                 // Pipeline stages for CARRYINSEL (0-1)
      .CREG(1),                          // Pipeline stages for C (0-1)
      .DREG(1),                          // Pipeline stages for D (0-1)
      .INMODEREG(1),                     // Pipeline stages for INMODE (0-1)
      .MREG(1),                          // Multiplier pipeline stages (0-1)
      .OPMODEREG(1),                     // Pipeline stages for OPMODE (0-1)
      .PREG(1)                           // Number of pipeline stages for P (0-1)
   )
   DSP48E2_inst (
      // Cascade outputs: Cascade Ports
      .ACOUT(),                          // 30-bit output: A port cascade
      .BCOUT(),                          // 18-bit output: B cascade
      .CARRYCASCOUT(),                   // 1-bit output: Cascade carry
      .MULTSIGNOUT(),                    // 1-bit output: Multiplier sign cascade
      .PCOUT(),                          // 48-bit output: Cascade output
      // Control outputs: Control Inputs/Status Bits
      .OVERFLOW(),                       // 1-bit output: Overflow in add/acc
      .PATTERNBDETECT(dout[0]),          // 1-bit output: Pattern bar detect
      .PATTERNDETECT(dout[1]),           // 1-bit output: Pattern detect
      .UNDERFLOW(),                      // 1-bit output: Underflow in add/acc
      // Data outputs: Data Ports
      .CARRYOUT(dout[2]),                // 4-bit output: Carry
      .P(dout[3]),                       // 48-bit output: Primary data
      .XOROUT(dout[4]),                  // 8-bit output: XOR data
      // Cascade inputs: Cascade Ports
      .ACIN(),                    		  // 30-bit input: A cascade data
      .BCIN(),                    		  // 18-bit input: B cascade
      .CARRYCASCIN(),             		  // 1-bit input: Cascade carry
      .MULTSIGNIN(),              		  // 1-bit input: Multiplier sign cascade
      .PCIN(),                    		  // 48-bit input: P cascade
      // Control inputs: Control Inputs/Status Bits
      .ALUMODE(din[0]),                  // 4-bit input: ALU control
      .CARRYINSEL(din[1]),               // 3-bit input: Carry select
      .CLK(clk),                         // 1-bit input: Clock
      .INMODE(din[2]),                   // 5-bit input: INMODE control
      .OPMODE(din[3]),                   // 9-bit input: Operation mode
      // Data inputs: Data Ports
      .A(din[4]),                        // 30-bit input: A data
      .B(din[5]),                       // 18-bit input: B data
      .C(din[6]),                       // 48-bit input: C data
      .CARRYIN(din[7]),                 // 1-bit input: Carry-in
      .D(din[8]),                       // 27-bit input: D data
      // Reset/Clock Enable inputs: Reset/Clock Enable Inputs
      .CEA1(1'b1),                       // 1-bit input: Clock enable for 1st stage AREG
      .CEA2(1'b1),                       // 1-bit input: Clock enable for 2nd stage AREG
      .CEAD(1'b1),                       // 1-bit input: Clock enable for ADREG
      .CEALUMODE(din[9]),               // 1-bit input: Clock enable for ALUMODE
      .CEB1(1'b1),                       // 1-bit input: Clock enable for 1st stage BREG
      .CEB2(1'b1),                       // 1-bit input: Clock enable for 2nd stage BREG
      .CEC(1'b1),                        // 1-bit input: Clock enable for CREG
      .CECARRYIN(1'b1),                  // 1-bit input: Clock enable for CARRYINREG
      .CECTRL(1'b1),                     // 1-bit input: Clock enable for OPMODEREG and CARRYINSELREG
      .CED(1'b1),                        // 1-bit input: Clock enable for DREG
      .CEINMODE(din[10]),                // 1-bit input: Clock enable for INMODEREG
      .CEM(1'b1),                        // 1-bit input: Clock enable for MREG
      .CEP(1'b1),                        // 1-bit input: Clock enable for PREG
      .RSTA(1'b0),                       // 1-bit input: Reset for AREG
      .RSTALLCARRYIN(1'b0),              // 1-bit input: Reset for CARRYINREG
      .RSTALUMODE(1'b0),                 // 1-bit input: Reset for ALUMODEREG
      .RSTB(1'b0),                       // 1-bit input: Reset for BREG
      .RSTC(1'b0),                       // 1-bit input: Reset for CREG
      .RSTCTRL(1'b0),                    // 1-bit input: Reset for OPMODEREG and CARRYINSELREG
      .RSTD(1'b0),                       // 1-bit input: Reset for DREG and ADREG
      .RSTINMODE(1'b0),                  // 1-bit input: Reset for INMODEREG
      .RSTM(1'b0),                       // 1-bit input: Reset for MREG
      .RSTP(1'b0)                        // 1-bit input: Reset for PREG
   );
endmodule
