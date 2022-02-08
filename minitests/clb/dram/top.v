// Copyright 2020-2022 F4PGA Authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//
// SPDX-License-Identifier: Apache-2.0

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
    DRAM32X1S
        #(
            .LOC("SLICE_X1Y240")
        )
        inst_0 (
            .clk(clk),
            .din(din[  0 +: 10]),
            .dout(dout[  0 +: 1])
        );

    DRAM64X1S
        #(
            .LOC("SLICE_X1Y241")
        )
        inst_1 (
            .clk(clk),
            .din(din[  10 +: 10]),
            .dout(dout[  1 +: 1])
        );
endmodule

// ---------------------------------------------------------------------

module DRAM32X1S(input clk, input [5:0] din, output dout);
	parameter LOC = "";

    (* LOC=LOC *)
    RAM32X1S #(
        .INIT(32'h00000000),    // Initial contents of RAM
        .IS_WCLK_INVERTED(1'b0) // Specifies active high/low WCLK
     ) RAM32X1S_inst (
        .O(dout),       // RAM output
        .A0(din[0]),     // RAM address[0] input
        .A1(din[1]),     // RAM address[1] input
        .A2(din[2]),     // RAM address[2] input
        .A3(din[3]),     // RAM address[3] input
        .A4(din[4]),     // RAM address[4] input
        .D(din[5]),       // RAM data input
        .WCLK(clk), // Write clock input
        .WE(1'b1)      // Write enable input
     );
endmodule

module DRAM64X1S(input clk, input [6:0] din, output dout);
	parameter LOC = "";

    (* LOC=LOC *)
    RAM64X1S #(
        .INIT(64'h00000000),    // Initial contents of RAM
        .IS_WCLK_INVERTED(1'b0) // Specifies active high/low WCLK
     ) RAM64X1S_inst (
        .O(dout),       // RAM output
        .A0(din[0]),     // RAM address[0] input
        .A1(din[1]),     // RAM address[1] input
        .A2(din[2]),     // RAM address[2] input
        .A3(din[3]),     // RAM address[3] input
        .A4(din[4]),     // RAM address[4] input
        .A5(din[5]),     // RAM address[5] input
        .D(din[6]),       // RAM data input
        .WCLK(clk), // Write clock input
        .WE(1'b1)      // Write enable input
     );
endmodule
