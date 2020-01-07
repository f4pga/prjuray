//move some stuff to minitests/ncy0

module top(input clk, stb, di, output do);
	localparam integer DIN_N = 256;
	localparam integer DOUT_N = 256;

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

module roi(input clk, input [255:0] din, output [255:0] dout);
    mux9_full  # (.LOC("SLICE_X22Y240"))
        c0 (.clk(clk), .din(din[  0 +: 8]), .dout(dout[0 +: 16]));
endmodule

//Minimal MUX9 placement with actual LUTs
module mux9_full (input clk, input [7:0] din, output [7:0] dout);
    parameter LOC="SLICE_X22Y240";
    wire lutho, lutgo, lutfo, luteo, lutdo, lutco, lutbo, lutao;
    wire lut7do, lut7co, lut7bo, lut7ao;
    wire lut8_bot_o, lut8_top_o;
    wire lut9o;

    assign dout[0] = lut9o;
    (* LOC=LOC, BEL="F9MUX", KEEP, DONT_TOUCH *)
    MUXF9 mux9 (.O(lut9o), .I0(lut8_top_o), .I1(lut8_bot_o), .S(din[6]));
    (* LOC=LOC, BEL="F8MUX_TOP", KEEP, DONT_TOUCH *)
    MUXF8 mux8top (.O(lut8_top_o), .I0(lut7do), .I1(lut7co), .S(din[6]));
    (* LOC=LOC, BEL="F8MUX_BOT", KEEP, DONT_TOUCH *)
    MUXF8 mux8bot (.O(lut8_bot_o), .I0(lut7bo), .I1(lut7ao), .S(din[6]));
    (* LOC=LOC, BEL="F7MUX_GH", KEEP, DONT_TOUCH *)
    MUXF7 mux7d (.O(lut7do), .I0(lutho), .I1(lutgo), .S(din[6]));
    (* LOC=LOC, BEL="F7MUX_EF", KEEP, DONT_TOUCH *)
    MUXF7 mux7c (.O(lut7co), .I0(lutfo), .I1(luteo), .S(din[6]));
    (* LOC=LOC, BEL="F7MUX_CD", KEEP, DONT_TOUCH *)
    MUXF7 mux7b (.O(lut7bo), .I0(lutdo), .I1(lutco), .S(din[6]));
    (* LOC=LOC, BEL="F7MUX_AB", KEEP, DONT_TOUCH *)
    MUXF7 mux7a (.O(lut7ao), .I0(lutbo), .I1(lutao), .S(din[6]));
    (* LOC=LOC, BEL="H6LUT", KEEP, DONT_TOUCH *)
	LUT6_2 #(
		.INIT(64'h8000_DEAD_0000_0001)
	) luth (
		.I0(din[0]),
		.I1(din[1]),
		.I2(din[2]),
		.I3(din[3]),
		.I4(din[4]),
		.I5(din[5]),
		.O5(),
		.O6(lutho));

	(* LOC=LOC, BEL="G6LUT", KEEP, DONT_TOUCH *)
	LUT6_2 #(
		.INIT(64'h8000_BEEF_0000_0001)
	) lutg (
		.I0(din[0]),
		.I1(din[1]),
		.I2(din[2]),
		.I3(din[3]),
		.I4(din[4]),
		.I5(din[5]),
		.O5(),
		.O6(lutgo));

	(* LOC=LOC, BEL="F6LUT", KEEP, DONT_TOUCH *)
	LUT6_2 #(
		.INIT(64'h8000_CAFE_0000_0001)
	) lutf (
		.I0(din[0]),
		.I1(din[1]),
		.I2(din[2]),
		.I3(din[3]),
		.I4(din[4]),
		.I5(din[5]),
		.O5(),
		.O6(lutfo));

	(* LOC=LOC, BEL="E6LUT", KEEP, DONT_TOUCH *)
	LUT6_2 #(
		.INIT(64'h8000_1CE0_0000_0001)
	) lute (
		.I0(din[0]),
		.I1(din[1]),
		.I2(din[2]),
		.I3(din[3]),
		.I4(din[4]),
		.I5(din[5]),
		.O5(),
		.O6(luteo));

	(* LOC=LOC, BEL="D6LUT", KEEP, DONT_TOUCH *)
	LUT6_2 #(
		.INIT(64'h8000_DEAD_0000_0001)
	) lutd (
		.I0(din[0]),
		.I1(din[1]),
		.I2(din[2]),
		.I3(din[3]),
		.I4(din[4]),
		.I5(din[5]),
		.O5(),
		.O6(lutdo));

	(* LOC=LOC, BEL="C6LUT", KEEP, DONT_TOUCH *)
	LUT6_2 #(
		.INIT(64'h8000_BEEF_0000_0001)
	) lutc (
		.I0(din[0]),
		.I1(din[1]),
		.I2(din[2]),
		.I3(din[3]),
		.I4(din[4]),
		.I5(din[5]),
		.O5(),
		.O6(lutco));

	(* LOC=LOC, BEL="B6LUT", KEEP, DONT_TOUCH *)
	LUT6_2 #(
		.INIT(64'h8000_CAFE_0000_0001)
	) lutb (
		.I0(din[0]),
		.I1(din[1]),
		.I2(din[2]),
		.I3(din[3]),
		.I4(din[4]),
		.I5(din[5]),
		.O5(),
		.O6(lutbo));

	(* LOC=LOC, BEL="A6LUT", KEEP, DONT_TOUCH *)
	LUT6_2 #(
		.INIT(64'h8000_1CE0_0000_0000)
	) luta (
		.I0(din[0]),
		.I1(din[1]),
		.I2(din[2]),
		.I3(din[3]),
		.I4(din[4]),
		.I5(din[5]),
		.O5(),
		.O6(lutao));
endmodule
