module top(input clk, stb, di, output do);
    localparam integer DIN_N = 8;
    localparam integer DOUT_N = 8;

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

    roi (
                .clk(clk),
                .din(din),
                .dout(dout)
        );

endmodule

(* KEEP_HIERARCHY *)
module roi(input clk, input [9:0] din, output [9:0] dout);
{% for param in parameters %}
    wire o6_{{ param['site_name'] }};
    (* KEEP, DONT_TOUCH, LOC = "{{ param['site_name'] }}", BEL = "{{ param['bel_lut6'] }}"*)
        LUT6 lut_{{ param['site_name'] }} (
                                .I0(),
                                .I1(),
                                .I2(),
                                .I3(),
                                .I4(),
                                .I5(),
                                .O(o6_{{ param['site_name'] }})
                        );
    (* KEEP, DONT_TOUCH, LOC = "{{ param['site_name'] }}", BEL = "{{ param['bel_ff'] }}"*)
        FDPE ff_{{ param['site_name'] }} (
                .C(clk),
                .CE(1'b1),
                .D(o6_{{ param['site_name'] }}),
                .PRE(1'b0),
                .Q()
                );
{% endfor %}
endmodule

