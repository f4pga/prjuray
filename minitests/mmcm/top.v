
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
	my_MMCM
	#(
		.LOC("MMCM_X0Y5")
	)
	inst_0 (
		.clk(clk),
		.din(din[  0 +: 2]),
		.dout(dout[ 0 +: 14])
	);
endmodule

// ---------------------------------------------------------------------
module my_MMCM (input clk, input [1:0] din, output [13:0] dout);

   parameter LOC = "";

	(* LOC=LOC *)
   MMCME4_BASE #(
      .BANDWIDTH("OPTIMIZED"),    // Jitter programming
      .CLKFBOUT_MULT_F(8.0),      // Multiply value for all CLKOUT
      .CLKFBOUT_PHASE(0.0),       // Phase offset in degrees of CLKFB
      .CLKIN1_PERIOD(10.0),        // Input clock period in ns to ps resolution (i.e. 33.333 is 30 MHz).
      .CLKOUT0_DIVIDE_F(1.0),     // Divide amount for CLKOUT0
      .CLKOUT0_DUTY_CYCLE(0.5),   // Duty cycle for CLKOUT0
      .CLKOUT0_PHASE(0.0),        // Phase offset for CLKOUT0
      .CLKOUT1_DIVIDE(1),         // Divide amount for CLKOUT (1-128)
      .CLKOUT1_DUTY_CYCLE(0.5),   // Duty cycle for CLKOUT outputs (0.001-0.999).
      .CLKOUT1_PHASE(0.0),        // Phase offset for CLKOUT outputs (-360.000-360.000).
      .CLKOUT2_DIVIDE(1),         // Divide amount for CLKOUT (1-128)
      .CLKOUT2_DUTY_CYCLE(0.5),   // Duty cycle for CLKOUT outputs (0.001-0.999).
      .CLKOUT2_PHASE(0.0),        // Phase offset for CLKOUT outputs (-360.000-360.000).
      .CLKOUT3_DIVIDE(1),         // Divide amount for CLKOUT (1-128)
      .CLKOUT3_DUTY_CYCLE(0.5),   // Duty cycle for CLKOUT outputs (0.001-0.999).
      .CLKOUT3_PHASE(0.0),        // Phase offset for CLKOUT outputs (-360.000-360.000).
      .CLKOUT4_CASCADE("FALSE"),  // Divide amount for CLKOUT (1-128)
      .CLKOUT4_DIVIDE(1),         // Divide amount for CLKOUT (1-128)
      .CLKOUT4_DUTY_CYCLE(0.5),   // Duty cycle for CLKOUT outputs (0.001-0.999).
      .CLKOUT4_PHASE(0.0),        // Phase offset for CLKOUT outputs (-360.000-360.000).
      .CLKOUT5_DIVIDE(1),         // Divide amount for CLKOUT (1-128)
      .CLKOUT5_DUTY_CYCLE(0.5),   // Duty cycle for CLKOUT outputs (0.001-0.999).
      .CLKOUT5_PHASE(0.0),        // Phase offset for CLKOUT outputs (-360.000-360.000).
      .CLKOUT6_DIVIDE(1),         // Divide amount for CLKOUT (1-128)
      .CLKOUT6_DUTY_CYCLE(0.5),   // Duty cycle for CLKOUT outputs (0.001-0.999).
      .CLKOUT6_PHASE(0.0),        // Phase offset for CLKOUT outputs (-360.000-360.000).
      .DIVCLK_DIVIDE(1),          // Master division value
      .IS_CLKFBIN_INVERTED(1'b0), // Optional inversion for CLKFBIN
      .IS_CLKIN1_INVERTED(1'b0),  // Optional inversion for CLKIN1
      .IS_PWRDWN_INVERTED(1'b0),  // Optional inversion for PWRDWN
      .IS_RST_INVERTED(1'b0),     // Optional inversion for RST
      .REF_JITTER1(0.0),          // Reference input jitter in UI (0.000-0.999).
      .STARTUP_WAIT("FALSE")      // Delays DONE until MMCM is locked
   )
   MMCME4_BASE_inst (
      .CLKFBOUT(dout[0]),         // 1-bit output: Feedback clock pin to the MMCM
      .CLKFBOUTB(dout[1]),        // 1-bit output: Inverted CLKFBOUT
      .CLKOUT0(dout[2]),     	  // 1-bit output: CLKOUT0
      .CLKOUT0B(dout[3]),         // 1-bit output: Inverted CLKOUT0
      .CLKOUT1(dout[4]),          // 1-bit output: CLKOUT1
      .CLKOUT1B(dout[5]),         // 1-bit output: Inverted CLKOUT1
      .CLKOUT2(dout[6]),          // 1-bit output: CLKOUT2
      .CLKOUT2B(dout[7]),         // 1-bit output: Inverted CLKOUT2
      .CLKOUT3(dout[8]),          // 1-bit output: CLKOUT3
      .CLKOUT3B(dout[9]),         // 1-bit output: Inverted CLKOUT3
      .CLKOUT4(dout[10]),         // 1-bit output: CLKOUT4
      .CLKOUT5(dout[11]),         // 1-bit output: CLKOUT5
      .CLKOUT6(dout[12]),         // 1-bit output: CLKOUT6
      .LOCKED(dout[13]),          // 1-bit output: LOCK
      .CLKFBIN(),                 // 1-bit input: Feedback clock pin to the MMCM
      .CLKIN1(clk),               // 1-bit input: Primary clock
      .PWRDWN(din[0]),              // 1-bit input: Power-down
      .RST(din[1])                  // 1-bit input: Reset
   );
endmodule
