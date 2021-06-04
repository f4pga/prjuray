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
        din_shr <= {din_shr, di, dout[0]};
        dout_shr <= {dout_shr, din_shr[DIN_N-1]};
        if (stb) begin
            din <= din_shr;
        end
    end
	assign do = dout_shr[0];
    roi roi (
        .clk(clk),
        .din(din),
        .dout(dout)
    );
endmodule

module roi(input clk, input [159:0] din, output [159:0] dout);

	IDELAYCTRL #(
		.SIM_DEVICE("ULTRASCALE")  // Must be set to "ULTRASCALE"
	)
	IDELAYCTRL_inst (
		.RDY(dout[159]), // 1-bit output: Ready output
		.REFCLK(clk),    // 1-bit input: Reference clock input
		.RST(din[159])   // 1-bit input: Active high reset input. Asynchronous assert, synchronous deassert to
		                 // REFCLK.
	);

	my_IDELAY
	#(
		.LOC("BITSLICE_RX_TX_X0Y305"),
        .CASCADE("NONE"),               // Cascade setting (MASTER, NONE, SLAVE_END, SLAVE_MIDDLE)
        .DELAY_FORMAT("TIME"),          // Units of the DELAY_VALUE (COUNT, TIME)
        .DELAY_SRC("DATAIN"),           // Delay input (DATAIN, IDATAIN)
        .DELAY_TYPE("FIXED"),           // Set the type of tap delay line (FIXED, VARIABLE, VAR_LOAD)
        .DELAY_VALUE(0),                // Input delay value setting
        .IS_CLK_INVERTED(1'b0),         // Optional inversion for CLK
        .IS_RST_INVERTED(1'b0),         // Optional inversion for RST
        .REFCLK_FREQUENCY(300.0),       // IDELAYCTRL clock input frequency in MHz (200.0-2667.0)
        .SIM_DEVICE("ULTRASCALE_PLUS"), // Set the device version (ULTRASCALE, ULTRASCALE_PLUS, ULTRASCALE_PLUS_ES1,
                                        // ULTRASCALE_PLUS_ES2)
        .UPDATE_MODE("ASYNC")           // Determines when updates to the delay will take effect (ASYNC, MANUAL, SYNC)
	)
	inst_0 (
		.clk(clk),
		.din(din[1:0]),
		.dout(dout[0])
	);

	my_ODELAY
	#(
		.LOC("BITSLICE_RX_TX_X0Y306"),
        .CASCADE("NONE"),               // Cascade setting (MASTER, NONE, SLAVE_END, SLAVE_MIDDLE)
        .DELAY_FORMAT("TIME"),          // Units of the DELAY_VALUE (COUNT, TIME)
        .DELAY_TYPE("FIXED"),           // Set the type of tap delay line (FIXED, VARIABLE, VAR_LOAD)
        .DELAY_VALUE(0),                // Input delay value setting
        .IS_CLK_INVERTED(1'b0),         // Optional inversion for CLK
        .IS_RST_INVERTED(1'b0),         // Optional inversion for RST
        .REFCLK_FREQUENCY(300.0),       // IDELAYCTRL clock input frequency in MHz (200.0-2667.0)
        .SIM_DEVICE("ULTRASCALE_PLUS"), // Set the device version (ULTRASCALE, ULTRASCALE_PLUS, ULTRASCALE_PLUS_ES1,
                                        // ULTRASCALE_PLUS_ES2)
        .UPDATE_MODE("ASYNC")           // Determines when updates to the delay will take effect (ASYNC, MANUAL, SYNC)
	)
	inst_1 (
		.clk(clk),
		.din(din[  2 +: 2]),
		.dout()
	);

endmodule

// ---------------------------------------------------------------------
module my_IDELAY (input clk, input [1:0] din, output dout);
   parameter LOC = "";
   parameter CASCADE = "NONE";
   parameter DELAY_FORMAT = "TIME";
   parameter DELAY_SRC = "DATAIN";
   parameter DELAY_TYPE = "FIXED";
   parameter DELAY_VALUE = 0;
   parameter IS_CLK_INVERTED = 1'b0;
   parameter IS_RST_INVERTED = 1'b0;
   parameter REFCLK_FREQUENCY = 300.0;
   parameter SIM_DEVICE = "ULTRASCALE_PLUS";
   parameter UPDATE_MODE = "ASYNC";

   (* LOC=LOC *)
   IDELAYE3 #(
      .CASCADE(CASCADE),                    // Cascade setting (MASTER, NONE, SLAVE_END, SLAVE_MIDDLE)
      .DELAY_FORMAT(DELAY_FORMAT),          // Units of the DELAY_VALUE (COUNT, TIME)
      .DELAY_SRC(DELAY_SRC),                // Delay input (DATAIN, IDATAIN)
      .DELAY_TYPE(DELAY_TYPE),              // Set the type of tap delay line (FIXED, VARIABLE, VAR_LOAD)
      .DELAY_VALUE(DELAY_VALUE),            // Input delay value setting
      .IS_CLK_INVERTED(IS_CLK_INVERTED),    // Optional inversion for CLK
      .IS_RST_INVERTED(IS_RST_INVERTED),    // Optional inversion for RST
      .REFCLK_FREQUENCY(REFCLK_FREQUENCY),  // IDELAYCTRL clock input frequency in MHz (200.0-2667.0)
      .SIM_DEVICE(SIM_DEVICE),              // Set the device version (ULTRASCALE, ULTRASCALE_PLUS, ULTRASCALE_PLUS_ES1,
                                            // ULTRASCALE_PLUS_ES2)
      .UPDATE_MODE(UPDATE_MODE)             // Determines when updates to the delay will take effect (ASYNC, MANUAL, SYNC)
   )
   IDELAYE3_inst (
      .CASC_OUT(),       // 1-bit output: Cascade delay output to ODELAY input cascade
      .CNTVALUEOUT(),    // 9-bit output: Counter value output
      .DATAOUT(dout),    // 1-bit output: Delayed data output
      .CASC_IN(),        // 1-bit input: Cascade delay input from slave ODELAY CASCADE_OUT
      .CASC_RETURN(),    // 1-bit input: Cascade delay returning from slave ODELAY DATAOUT
      .CE(1'b0),         // 1-bit input: Active high enable increment/decrement input
      .CLK(clk),         // 1-bit input: Clock input
      .CNTVALUEIN(),     // 9-bit input: Counter value input
      .DATAIN(din[0]),   // 1-bit input: Data input from the logic
      .EN_VTC(1'b1),     // 1-bit input: Keep delay constant over VT
      .IDATAIN(),        // 1-bit input: Data input from the IOBUF
      .INC(1'b0),        // 1-bit input: Increment / Decrement tap delay input
      .LOAD(1'b0),       // 1-bit input: Load DELAY_VALUE input
      .RST(din[1])       // 1-bit input: Asynchronous Reset to the DELAY_VALUE
   );
endmodule

module my_ODELAY (input clk, input [1:0] din, output dout);
   parameter LOC = "";
   parameter CASCADE = "NONE";
   parameter DELAY_FORMAT = "TIME";
   parameter DELAY_TYPE = "FIXED";
   parameter DELAY_VALUE = 0;
   parameter IS_CLK_INVERTED = 1'b0;
   parameter IS_RST_INVERTED = 1'b0;
   parameter REFCLK_FREQUENCY = 300.0;
   parameter SIM_DEVICE = "ULTRASCALE_PLUS";
   parameter UPDATE_MODE = "ASYNC";

   (* KEEP, DONT_TOUCH, LOC=LOC *)
   ODELAYE3 #(
      .CASCADE(CASCADE),                    // Cascade setting (MASTER, NONE, SLAVE_END, SLAVE_MIDDLE)
      .DELAY_FORMAT(DELAY_FORMAT),          // Units of the DELAY_VALUE (COUNT, TIME)
      .DELAY_TYPE(DELAY_TYPE),              // Set the type of tap delay line (FIXED, VARIABLE, VAR_LOAD)
      .DELAY_VALUE(DELAY_VALUE),            // Input delay value setting
      .IS_CLK_INVERTED(IS_CLK_INVERTED),    // Optional inversion for CLK
      .IS_RST_INVERTED(IS_RST_INVERTED),    // Optional inversion for RST
      .REFCLK_FREQUENCY(REFCLK_FREQUENCY),  // IDELAYCTRL clock input frequency in MHz (200.0-2667.0)
      .SIM_DEVICE(SIM_DEVICE),              // Set the device version (ULTRASCALE, ULTRASCALE_PLUS, ULTRASCALE_PLUS_ES1,
                                            // ULTRASCALE_PLUS_ES2)
      .UPDATE_MODE(UPDATE_MODE)             // Determines when updates to the delay will take effect (ASYNC, MANUAL, SYNC)
   )
   ODELAYE3_inst (
      .CASC_OUT(),       // 1-bit output: Cascade delay output to ODELAY input cascade
      .CNTVALUEOUT(),    // 9-bit output: Counter value output
      .DATAOUT(dout),    // 1-bit output: Delayed data output
      .CASC_IN(),        // 1-bit input: Cascade delay input from slave ODELAY CASCADE_OUT
      .CASC_RETURN(),    // 1-bit input: Cascade delay returning from slave ODELAY DATAOUT
      .CE(1'b0),         // 1-bit input: Active high enable increment/decrement input
      .CLK(clk),         // 1-bit input: Clock input
      .CNTVALUEIN(),     // 9-bit input: Counter value input
      .EN_VTC(1'b1),     // 1-bit input: Keep delay constant over VT
      .INC(1'b0),        // 1-bit input: Increment / Decrement tap delay input
      .LOAD(1'b0),       // 1-bit input: Load DELAY_VALUE input
	   .ODATAIN(din[0]),  // 1-bit input: Data input
      .RST(din[1])       // 1-bit input: Asynchronous Reset to the DELAY_VALUE
   );
endmodule

