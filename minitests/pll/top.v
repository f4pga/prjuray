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
	my_PLL
	#(
		.LOC("PLL_X0Y10")
	)
	inst_0 (
		.clk(clk),
		.din(din[  0 +: 2]),
		.dout(dout[ 0 +: 7])
	);
endmodule

// ---------------------------------------------------------------------
module my_PLL (input clk, input [1:0] din, output [6:0] dout);

   parameter LOC = "";

   (* LOC=LOC *)
   PLLE4_BASE #(
      .CLKFBOUT_MULT(8),          // Multiply value for all CLKOUT
      .CLKFBOUT_PHASE(0.0),       // Phase offset in degrees of CLKFB
      .CLKIN_PERIOD(10.0),         // Input clock period in ns to ps resolution (i.e. 33.333 is 30 MHz).
      .CLKOUT0_DIVIDE(1),         // Divide amount for CLKOUT0
      .CLKOUT0_DUTY_CYCLE(0.5),   // Duty cycle for CLKOUT0
      .CLKOUT0_PHASE(0.0),        // Phase offset for CLKOUT0
      .CLKOUT1_DIVIDE(1),         // Divide amount for CLKOUT1
      .CLKOUT1_DUTY_CYCLE(0.5),   // Duty cycle for CLKOUT1
      .CLKOUT1_PHASE(0.0),        // Phase offset for CLKOUT1
      .CLKOUTPHY_MODE("VCO_2X"),  // Frequency of the CLKOUTPHY
      .DIVCLK_DIVIDE(1),          // Master division value
      .IS_CLKFBIN_INVERTED(1'b0), // Optional inversion for CLKFBIN
      .IS_CLKIN_INVERTED(1'b0),   // Optional inversion for CLKIN
      .IS_PWRDWN_INVERTED(1'b0),  // Optional inversion for PWRDWN
      .IS_RST_INVERTED(1'b0),     // Optional inversion for RST
      .REF_JITTER(0.0),           // Reference input jitter in UI
      .STARTUP_WAIT("FALSE")      // Delays DONE until PLL is locked
   )
   PLLE4_BASE_inst (
      .CLKFBOUT(dout[0]),       // 1-bit output: Feedback clock
      .CLKOUT0(dout[1]),         // 1-bit output: General Clock output
      .CLKOUT0B(dout[2]),       // 1-bit output: Inverted CLKOUT0
      .CLKOUT1(dout[3]),         // 1-bit output: General Clock output
      .CLKOUT1B(dout[4]),       // 1-bit output: Inverted CLKOUT1
      .CLKOUTPHY(),     // 1-bit output: Bitslice clock
      .LOCKED(dout[6]),           // 1-bit output: LOCK
      .CLKFBIN(),         // 1-bit input: Feedback clock
      .CLKIN(clk),             // 1-bit input: Input clock
      .CLKOUTPHYEN(1'b1), // 1-bit input: CLKOUTPHY enable
      .PWRDWN(din[0]),           // 1-bit input: Power-down
      .RST(din[1])                  // 1-bit input: Reset
   );
endmodule
