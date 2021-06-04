// Copyright (C) 2020-2021  The Project U-Ray Authors.
//
// Use of this source code is governed by a ISC-style
// license that can be found in the LICENSE file or at
// https://opensource.org/licenses/ISC
//
// SPDX-License-Identifier: ISC
module top(input clk, stb, di, output do);
	reg do_reg = 0;
	always @(posedge clk) begin
		if (stb) begin
			do_reg = di;
		end
	end
	assign do = do_reg;
endmodule
