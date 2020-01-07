module top(input clk, input [{{ din_index }}:0] di, output [{{ dout_index }}:0] do);
{% for params in parameters %}
    {{ params['name'] }}
    #(.LOC("{{ params['site'] }}"), .BEL("{{ params['bel'] }}"), .FORCE_R(1'b{{ params['rs_inv'] }}))
    {% set inst_index = loop.index - 1 %}
    {% set din_index = inst_index * 4 %}
    clb_{{ inst_index }} (.clk(clk), .din(di[{{ din_index }} +: 4]), .dout(do[{{ inst_index }}]));
{% endfor %}
endmodule

module clb_FDRE (input clk, input [3:0] din, output dout);
    parameter LOC="SLICE_X16Y114";
    parameter BEL="AFF";
    parameter FORCE_R=1;
    (* LOC=LOC, BEL=BEL, KEEP, DONT_TOUCH *)
    FDRE ff (
        .C(clk),
        .Q(dout),
        .CE(din[0]),
        .R(~FORCE_R),
        .D(din[2])
    );
endmodule
