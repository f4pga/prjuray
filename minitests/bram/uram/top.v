
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
    my_URAM288_BASE
        #(
            .LOC("URAM288_X0Y64")
        )
        inst_0 (
            .clk(clk),
            .din(din[  0 +: 24]),
            .dout(dout[  0 +: 8])
        );

endmodule

// ---------------------------------------------------------------------

module my_URAM288_BASE(input clk, input [23:0] din, output [7:0] dout);
    parameter LOC = "";

    (* LOC=LOC *)
    URAM288_BASE #(
      .AUTO_SLEEP_LATENCY(8),            // Latency requirement to enter sleep mode
      .AVG_CONS_INACTIVE_CYCLES(10),     // Average concecutive inactive cycles when is SLEEP mode for power
                                         // estimation
      .BWE_MODE_A("PARITY_INTERLEAVED"), // Port A Byte write control
      .BWE_MODE_B("PARITY_INTERLEAVED"), // Port B Byte write control
      .EN_AUTO_SLEEP_MODE("FALSE"),      // Enable to automatically enter sleep mode
      .EN_ECC_RD_A("FALSE"),             // Port A ECC encoder
      .EN_ECC_RD_B("FALSE"),             // Port B ECC encoder
      .EN_ECC_WR_A("FALSE"),             // Port A ECC decoder
      .EN_ECC_WR_B("FALSE"),             // Port B ECC decoder
      .IREG_PRE_A("FALSE"),              // Optional Port A input pipeline registers
      .IREG_PRE_B("FALSE"),              // Optional Port B input pipeline registers
      .IS_CLK_INVERTED(1'b0),            // Optional inverter for CLK
      .IS_EN_A_INVERTED(1'b0),           // Optional inverter for Port A enable
      .IS_EN_B_INVERTED(1'b0),           // Optional inverter for Port B enable
      .IS_RDB_WR_A_INVERTED(1'b0),       // Optional inverter for Port A read/write select
      .IS_RDB_WR_B_INVERTED(1'b0),       // Optional inverter for Port B read/write select
      .IS_RST_A_INVERTED(1'b0),          // Optional inverter for Port A reset
      .IS_RST_B_INVERTED(1'b0),          // Optional inverter for Port B reset
      .OREG_A("FALSE"),                  // Optional Port A output pipeline registers
      .OREG_B("FALSE"),                  // Optional Port B output pipeline registers
      .OREG_ECC_A("FALSE"),              // Port A ECC decoder output
      .OREG_ECC_B("FALSE"),              // Port B output ECC decoder
      .RST_MODE_A("SYNC"),               // Port A reset mode
      .RST_MODE_B("SYNC"),               // Port B reset mode
      .USE_EXT_CE_A("FALSE"),            // Enable Port A external CE inputs for output registers
      .USE_EXT_CE_B("FALSE")             // Enable Port B external CE inputs for output registers
   )
   URAM288_BASE_inst (
      .DBITERR_A(dout[0]),                 // 1-bit output: Port A double-bit error flag status
      .DBITERR_B(dout[1]),                 // 1-bit output: Port B double-bit error flag status
      .DOUT_A(dout[2]),                    // 72-bit output: Port A read data output
      .DOUT_B(dout[3]),                    // 72-bit output: Port B read data output
      .SBITERR_A(dout[4]),                 // 1-bit output: Port A single-bit error flag status
      .SBITERR_B(dout[5]),                 // 1-bit output: Port B single-bit error flag status
      .ADDR_A(din[0]),                     // 23-bit input: Port A address
      .ADDR_B(din[1]),                     // 23-bit input: Port B address
      .BWE_A(din[2]),                       // 9-bit input: Port A Byte-write enable
      .BWE_B(din[3]),                       // 9-bit input: Port B Byte-write enable
      .CLK(clk),                           // 1-bit input: Clock source
      .DIN_A(din[4]),                       // 72-bit input: Port A write data input
      .DIN_B(din[5]),                       // 72-bit input: Port B write data input
      .EN_A(din[6]),                         // 1-bit input: Port A enable
      .EN_B(din[7]),                         // 1-bit input: Port B enable
      .INJECT_DBITERR_A(din[8]), // 1-bit input: Port A double-bit error injection
      .INJECT_DBITERR_B(din[9]), // 1-bit input: Port B double-bit error injection
      .INJECT_SBITERR_A(din[10]), // 1-bit input: Port A single-bit error injection
      .INJECT_SBITERR_B(din[11]), // 1-bit input: Port B single-bit error injection
      .OREG_CE_A(din[12]),               // 1-bit input: Port A output register clock enable
      .OREG_CE_B(din[13]),               // 1-bit input: Port B output register clock enable
      .OREG_ECC_CE_A(din[14]),       // 1-bit input: Port A ECC decoder output register clock enable
      .OREG_ECC_CE_B(din[15]),       // 1-bit input: Port B ECC decoder output register clock enable
      .RDB_WR_A(din[16]),                 // 1-bit input: Port A read/write select
      .RDB_WR_B(din[17]),                 // 1-bit input: Port B read/write select
      .RST_A(din[18]),                       // 1-bit input: Port A asynchronous or synchronous reset for output
                                           // registers
      .RST_B(din[19]),                       // 1-bit input: Port B asynchronous or synchronous reset for output
                                           // registers

      .SLEEP(din[20])                        // 1-bit input: Dynamic power gating control
   );

endmodule
