
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
    my_RAMB36E2
        #(
            .LOC("RAMB36_X2Y60"),
            .DOA_REG(1'b1),
            .DOB_REG(1'b0),
            .INIT_A(18'b001000001000010101),
            .INIT_B(18'b001111100001101011),
            .IS_CLKARDCLK_INVERTED(1'b0),
            .IS_CLKBWRCLK_INVERTED(1'b0),
            .IS_ENARDEN_INVERTED(1'b0),
            .IS_ENBWREN_INVERTED(1'b0),
            .IS_RSTRAMARSTRAM_INVERTED(1'b1),
            .IS_RSTRAMB_INVERTED(1'b1),
            .IS_RSTREGARSTREG_INVERTED(1'b0),
            .IS_RSTREGB_INVERTED(1'b1),
			.RDADDRCHANGEA("FALSE"),
			.RDADDRCHANGEB("FALSE"),
            .READ_WIDTH_A(4),
            .READ_WIDTH_B(4),
            .WRITE_WIDTH_A(18),
            .WRITE_WIDTH_B(1),
            .RSTREG_PRIORITY_A("RSTREG"),
            .RSTREG_PRIORITY_B("RSTREG"),
            .SRVAL_A(18'b110111110110100101),
            .SRVAL_B(18'b000001011100001111),
            .WRITE_MODE_A("WRITE_FIRST"),
            .WRITE_MODE_B("WRITE_FIRST")
        )
        inst_0 (
            .clk(clk),
            .din(din[  0 +: 24]),
            .dout(dout[  0 +: 8])
        );

endmodule

// ---------------------------------------------------------------------

module my_RAMB36E2 (input clk, input [23:0] din, output [7:0] dout);
    parameter LOC = "";
    parameter DOA_REG = 1'b0;
    parameter DOB_REG = 1'b0;
    parameter INIT_A = 18'b0;
    parameter INIT_B = 18'b0;
    parameter IS_CLKARDCLK_INVERTED = 1'b0;
    parameter IS_CLKBWRCLK_INVERTED = 1'b0;
    parameter IS_ENARDEN_INVERTED = 1'b0;
    parameter IS_ENBWREN_INVERTED = 1'b0;
    parameter IS_RSTRAMARSTRAM_INVERTED = 1'b0;
    parameter IS_RSTRAMB_INVERTED = 1'b0;
    parameter IS_RSTREGARSTREG_INVERTED = 1'b0;
    parameter IS_RSTREGB_INVERTED = 1'b0;
    parameter RDADDRCHANGEA = "FALSE";
    parameter RDADDRCHANGEB = "FALSE";
    parameter READ_WIDTH_A = 0;
    parameter READ_WIDTH_B = 0;
    parameter WRITE_WIDTH_A = 0;
    parameter WRITE_WIDTH_B = 0;
    parameter RSTREG_PRIORITY_A = "RSTREG";
    parameter RSTREG_PRIORITY_B = "RSTREG";
    parameter SRVAL_A = 18'b0;
    parameter SRVAL_B = 18'b0;
    parameter WRITE_MODE_A = "WRITE_FIRST";
    parameter WRITE_MODE_B = "WRITE_FIRST";

    (* LOC=LOC *)
    RAMB36E2 #(
	    .INITP_00(256'b0),
	    .INITP_01(256'b0),
	    .INITP_02(256'b0),
	    .INITP_03(256'b0),
	    .INITP_04(256'b0),
	    .INITP_05(256'b0),
	    .INITP_06(256'b0),
	    .INITP_07(256'b0),
	    .INITP_08(256'b0),
	    .INITP_09(256'b0),
	    .INITP_0A(256'b0),
	    .INITP_0B(256'b0),
	    .INITP_0C(256'b0),
	    .INITP_0D(256'b0),
	    .INITP_0E(256'b0),
	    .INITP_0F(256'b0),

	    .INIT_00(256'b0),
	    .INIT_01(256'b0),
	    .INIT_02(256'b0),
	    .INIT_03(256'b0),
	    .INIT_04(256'b0),
	    .INIT_05(256'b0),
	    .INIT_06(256'b0),
	    .INIT_07(256'b0),
	    .INIT_08(256'b0),
	    .INIT_09(256'b0),
	    .INIT_0A(256'b0),
	    .INIT_0B(256'b0),
	    .INIT_0C(256'b0),
	    .INIT_0D(256'b0),
	    .INIT_0E(256'b0),
	    .INIT_0F(256'b0),
	    .INIT_10(256'b0),
	    .INIT_11(256'b0),
	    .INIT_12(256'b0),
	    .INIT_13(256'b0),
	    .INIT_14(256'b0),
	    .INIT_15(256'b0),
	    .INIT_16(256'b0),
	    .INIT_17(256'b0),
	    .INIT_18(256'b0),
	    .INIT_19(256'b0),
	    .INIT_1A(256'b0),
	    .INIT_1B(256'b0),
	    .INIT_1C(256'b0),
	    .INIT_1D(256'b0),
	    .INIT_1E(256'b0),
	    .INIT_1F(256'b0),
	    .INIT_20(256'b0),
	    .INIT_21(256'b0),
	    .INIT_22(256'b0),
	    .INIT_23(256'b0),
	    .INIT_24(256'b0),
	    .INIT_25(256'b0),
	    .INIT_26(256'b0),
	    .INIT_27(256'b0),
	    .INIT_28(256'b0),
	    .INIT_29(256'b0),
	    .INIT_2A(256'b0),
	    .INIT_2B(256'b0),
	    .INIT_2C(256'b0),
	    .INIT_2D(256'b0),
	    .INIT_2E(256'b0),
	    .INIT_2F(256'b0),
	    .INIT_30(256'b0),
	    .INIT_31(256'b0),
	    .INIT_32(256'b0),
	    .INIT_33(256'b0),
	    .INIT_34(256'b0),
	    .INIT_35(256'b0),
	    .INIT_36(256'b0),
	    .INIT_37(256'b0),
	    .INIT_38(256'b0),
	    .INIT_39(256'b0),
	    .INIT_3A(256'b0),
	    .INIT_3B(256'b0),
	    .INIT_3C(256'b0),
	    .INIT_3D(256'b0),
	    .INIT_3E(256'b0),
	    .INIT_3F(256'b0),
	    .INIT_40(256'b0),
	    .INIT_41(256'b0),
	    .INIT_42(256'b0),
	    .INIT_43(256'b0),
	    .INIT_44(256'b0),
	    .INIT_45(256'b0),
	    .INIT_46(256'b0),
	    .INIT_47(256'b0),
	    .INIT_48(256'b0),
	    .INIT_49(256'b0),
	    .INIT_4A(256'b0),
	    .INIT_4B(256'b0),
	    .INIT_4C(256'b0),
	    .INIT_4D(256'b0),
	    .INIT_4E(256'b0),
	    .INIT_4F(256'b0),
	    .INIT_50(256'b0),
	    .INIT_51(256'b0),
	    .INIT_52(256'b0),
	    .INIT_53(256'b0),
	    .INIT_54(256'b0),
	    .INIT_55(256'b0),
	    .INIT_56(256'b0),
	    .INIT_57(256'b0),
	    .INIT_58(256'b0),
	    .INIT_59(256'b0),
	    .INIT_5A(256'b0),
	    .INIT_5B(256'b0),
	    .INIT_5C(256'b0),
	    .INIT_5D(256'b0),
	    .INIT_5E(256'b0),
	    .INIT_5F(256'b0),
	    .INIT_60(256'b0),
	    .INIT_61(256'b0),
	    .INIT_62(256'b0),
	    .INIT_63(256'b0),
	    .INIT_64(256'b0),
	    .INIT_65(256'b0),
	    .INIT_66(256'b0),
	    .INIT_67(256'b0),
	    .INIT_68(256'b0),
	    .INIT_69(256'b0),
	    .INIT_6A(256'b0),
	    .INIT_6B(256'b0),
	    .INIT_6C(256'b0),
	    .INIT_6D(256'b0),
	    .INIT_6E(256'b0),
	    .INIT_6F(256'b0),
	    .INIT_70(256'b0),
	    .INIT_71(256'b0),
	    .INIT_72(256'b0),
	    .INIT_73(256'b0),
	    .INIT_74(256'b0),
	    .INIT_75(256'b0),
	    .INIT_76(256'b0),
	    .INIT_77(256'b0),
	    .INIT_78(256'b0),
	    .INIT_79(256'b0),
	    .INIT_7A(256'b0),
	    .INIT_7B(256'b0),
	    .INIT_7C(256'b0),
	    .INIT_7D(256'b0),
	    .INIT_7E(256'b0),
	    .INIT_7F(256'b0),
	    .DOA_REG(DOA_REG),
	    .DOB_REG(DOB_REG),
	    .INIT_A(INIT_A),
	    .INIT_B(INIT_B),
	    .IS_CLKARDCLK_INVERTED(IS_CLKARDCLK_INVERTED),
	    .IS_CLKBWRCLK_INVERTED(IS_CLKBWRCLK_INVERTED),
	    .IS_ENARDEN_INVERTED(IS_ENARDEN_INVERTED),
	    .IS_ENBWREN_INVERTED(IS_ENBWREN_INVERTED),
	    .IS_RSTRAMARSTRAM_INVERTED(IS_RSTRAMARSTRAM_INVERTED),
	    .IS_RSTRAMB_INVERTED(IS_RSTRAMB_INVERTED),
	    .IS_RSTREGARSTREG_INVERTED(IS_RSTREGARSTREG_INVERTED),
	    .IS_RSTREGB_INVERTED(IS_RSTREGB_INVERTED),
	    .RDADDRCHANGEA(RDADDRCHANGEA),
	    .RDADDRCHANGEB(RDADDRCHANGEB),
	    .READ_WIDTH_A(READ_WIDTH_A),
	    .READ_WIDTH_B(READ_WIDTH_B),
	    .WRITE_WIDTH_A(WRITE_WIDTH_A),
	    .WRITE_WIDTH_B(WRITE_WIDTH_B),
	    .RSTREG_PRIORITY_A(RSTREG_PRIORITY_A),
	    .RSTREG_PRIORITY_B(RSTREG_PRIORITY_B),
	    .SRVAL_A(SRVAL_A),
	    .SRVAL_B(SRVAL_B),
	    .WRITE_MODE_A(WRITE_MODE_A),
	    .WRITE_MODE_B(WRITE_MODE_B)
    ) ram (
     // Port A Address/Control Signals inputs: Port A address and control signals
      .ADDRARDADDR(din[0]),         // 14-bit input: A/Read port address
      .ADDRENA(din[1]),                 // 1-bit input: Active-High A/Read port address enable
      .CLKARDCLK(din[2]),             // 1-bit input: A/Read port clock
      .ENARDEN(din[3]),                 // 1-bit input: Port A enable/Read enable
      .REGCEAREGCE(din[4]),         // 1-bit input: Port A register enable/Register enable
      .RSTRAMARSTRAM(din[5]),     // 1-bit input: Port A set/reset
      .RSTREGARSTREG(din[6]),     // 1-bit input: Port A register set/reset
      .WEA(1'b0),                         // 2-bit input: Port A write enable
      // Port A Data inputs: Port A data
      .DINADIN(din[7]),                 // 16-bit input: Port A data/LSB data
      .DINPADINP(din[8]),             // 2-bit input: Port A parity/LSB parity
      // Port B Address/Control Signals inputs: Port B address and control signals
      .ADDRBWRADDR(din[9]),         // 14-bit input: B/Write port address
      .ADDRENB(din[10]),                 // 1-bit input: Active-High B/Write port address enable
      .CLKBWRCLK(din[11]),             // 1-bit input: B/Write port clock
      .ENBWREN(din[12]),                 // 1-bit input: Port B enable/Write enable
      .REGCEB(din[13]),                   // 1-bit input: Port B register enable
      .RSTRAMB(din[14]),                 // 1-bit input: Port B set/reset
      .RSTREGB(din[15]),                 // 1-bit input: Port B register set/reset
      .SLEEP(din[16]),                     // 1-bit input: Sleep Mode
      .WEBWE(din[17]),                     // 4-bit input: Port B write enable/Write enable
      // Port B Data inputs: Port B data
      .DINBDIN(din[18]),                 // 16-bit input: Port B data/MSB data
      .DINPBDINP(din[19]),              // 2-bit input: Port B parity/MSB parity
      // Port A Data outputs: Port A data
      .DOUTADOUT(dout[0]),             // 16-bit output: Port A data/LSB data
      .DOUTPADOUTP(dout[1]),         // 2-bit output: Port A parity/LSB parity
      // Port B Data outputs: Port B data
      .DOUTBDOUT(dout[2]),             // 16-bit output: Port B data/MSB data
      .DOUTPBDOUTP(dout[3]));         // 2-bit output: Port B parity/MSB parity

endmodule
