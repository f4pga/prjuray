module top(input clk, stb, di, output do);
	roi roi(
		.clk(clk),
		.stb(stb),
		.di(di),
		.do(do)
	);
endmodule

module roi(input clk, stb, di, output do);
	reg do_reg = 0;
	always @(posedge clk) begin
		if (stb) begin
			do_reg <= di;
		end
	end
	assign do = do_reg;
endmodule
