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
        end
    end

    assign do = dout[DOUT_N-1];

    roi roi (
        .clk(clk),
        .din(din),
        .dout(dout)
    );
endmodule

module roi(input clk, input [159:0] din, output [159:0] dout);
	my_OSERDES
	#(
		.LOC("BITSLICE_RX_TX_X0Y305"),
		.DATA_WIDTH(8),
        .INIT(1'b0),
		.IS_CLKDIV_INVERTED(1'b0),
		.IS_CLK_INVERTED(1'b0),
		.IS_RST_INVERTED(1'b0),
		.SIM_DEVICE("ULTRASCALE_PLUS")
	)
	inst_0 (
		.clk(clk),
		.din(din[  0 +: 4]),
		.dout(dout[ 0 +: 2])
	);
endmodule

// ---------------------------------------------------------------------
module my_OSERDES (input clk, input [3:0] din, output [1:0] dout);

   parameter LOC = "";
   parameter DATA_WIDTH = 1;
   parameter INIT = 1'b0;
   parameter IS_CLKDIV_INVERTED = 1'b0;
   parameter IS_CLK_INVERTED = 1'b0;
   parameter IS_RST_INVERTED = 1'b0;
   parameter SIM_DEVICE = "ULTRASCALE_PLUS";

   (* LOC=LOC *)
   OSERDESE3 #(
      .DATA_WIDTH(DATA_WIDTH),                // Parallel data width (4,8)
      .INIT(INIT),                            // Initialization value of the OSERDES flip-flops
      .IS_CLKDIV_INVERTED(IS_CLKDIV_INVERTED),// Optional inversion for CLKDIV
      .IS_CLK_INVERTED(IS_CLK_INVERTED),      // Optional inversion for CLK
      .IS_RST_INVERTED(IS_RST_INVERTED),      // Optional inversion for RST
      .SIM_DEVICE(SIM_DEVICE)                 // Set the device version (ULTRASCALE, ULTRASCALE_PLUS, ULTRASCALE_PLUS_ES1,
                                              // ULTRASCALE_PLUS_ES2)
   )
   OSERDESE3_inst (
      .OQ(oq),         // 1-bit output: Serial Output Data
      .T_OUT(t),      // 1-bit output: 3-state control output to IOB
      .CLK(clk),            // 1-bit input: High-speed clock
      .CLKDIV(din[0]),      // 1-bit input: Divided Clock
      .D(din[1]),           // 8-bit input: Parallel Data Input
      .RST(din[2]),         // 1-bit input: Asynchronous Reset
      .T(din[3])            // 1-bit input: Tristate input from fabric
   );
   OBUFT OBUFT_inst (
      .O(dout[0]), // 1-bit output: Buffer output (connect directly to top-level port)
      .I(oq), // 1-bit input: Buffer input
      .T(t)  // 1-bit input: 3-state enable input
   );
endmodule
