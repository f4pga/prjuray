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
	my_ISERDES
	#(
		.LOC("BITSLICE_RX_TX_X0Y305"),
		.DATA_WIDTH(8),
		.FIFO_ENABLE("FALSE"),
		.FIFO_SYNC_MODE("FALSE"),
		.IS_CLK_B_INVERTED(1'b0),
		.IS_CLK_INVERTED(1'b0),
		.IS_RST_INVERTED(1'b0),
		.SIM_DEVICE("ULTRASCALE_PLUS")
	)
	inst_0 (
		.clk(clk),
		.din(din[  0 +: 3]),
		.dout(dout[ 0 +: 2])
	);
endmodule

// ---------------------------------------------------------------------
module my_ISERDES (input clk, input [2:0] din, output [1:0] dout);

   parameter LOC = "";
   parameter DATA_WIDTH = 8;
   parameter FIFO_ENABLE = "FALSE";
   parameter FIFO_SYNC_MODE = "FALSE";
   parameter IS_CLK_B_INVERTED = 1'b0;
   parameter IS_CLK_INVERTED = 1'b0;
   parameter IS_RST_INVERTED = 1'b0;
   parameter SIM_DEVICE = "ULTRASCALE";

	(* LOC=LOC *)
   ISERDESE3 #(
      .DATA_WIDTH(DATA_WIDTH),                // Parallel data width (4,8)
      .FIFO_ENABLE(FIFO_ENABLE),              // Enables the use of the FIFO
      .FIFO_SYNC_MODE(FIFO_SYNC_MODE),        // Always set to FALSE. TRUE is reserved for later use.
      .IS_CLK_B_INVERTED(IS_CLK_B_INVERTED),  // Optional inversion for CLK_B
      .IS_CLK_INVERTED(IS_CLK_INVERTED),      // Optional inversion for CLK
      .IS_RST_INVERTED(IS_RST_INVERTED),      // Optional inversion for RST
      .SIM_DEVICE(SIM_DEVICE)                 // Set the device version (ULTRASCALE, ULTRASCALE_PLUS, ULTRASCALE_PLUS_ES1,
                                              // ULTRASCALE_PLUS_ES2)
   )
   ISERDESE3_inst (
      .FIFO_EMPTY(dout[1]),           // 1-bit output: FIFO empty flag
      .INTERNAL_DIVCLK(), // 1-bit output: Internally divided down clock used when FIFO is
                                         // disabled (do not connect)

      .Q(dout[0]),                             // 8-bit registered output
      .CLK(clk),                         // 1-bit input: High-speed clock
      .CLKDIV(din[0]),                   // 1-bit input: Divided Clock
      .CLK_B(~clk),                     // 1-bit input: Inversion of High-speed clock CLK
      .D(din[1]),                             // 1-bit input: Serial Data Input
      .FIFO_RD_CLK(1'b0),         // 1-bit input: FIFO read clock
      .FIFO_RD_EN(1'b0),           // 1-bit input: Enables reading the FIFO when asserted
      .RST(din[2])                          // 1-bit input: Asynchronous Reset
   );
endmodule
