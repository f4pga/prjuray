module top(input clk, input[{{ params.ni }}:0] di, output [{{ params.no }}:0] do);

    {% for mod in params.mods %}
    {{ mod.type }} # (
        .LOC_CI         ("{{ mod.loc_ci }}"),
        .LOC_CO         ("{{ mod.loc_co }}"),
        .CARRY_TYPE     ("{{ mod.carry_type }}"),
        .PRECYINIT_TOP  ("{{ mod.precyinit_top }}"),
        .PRECYINIT_BOT  ("{{ mod.precyinit_bot }}")
    ) {{ mod.name }} (
        .clk            (clk),
        .inp            ({{ mod.inp }}),
        .out            ({{ mod.out }})
    );
    {% endfor %}

endmodule


module PRECYINIT (
    input  wire        clk,
    input  wire [15:0] inp,
    output wire [15:0] out
);
    parameter LOC_CO     = "SLICE_FIXME";
    parameter LOC_CI     = "SLICE_FIXME";
    parameter CARRY_TYPE = "CARRY_TYPE_FIXME";

    parameter PRECYINIT_TOP = "FIXME";
    parameter PRECYINIT_BOT = "FIXME";

    wire precyinit_top;
    wire precyinit_bot;

    generate if(PRECYINIT_TOP == "C0") begin
        assign precyinit_top = 1'b0;
    end else if(PRECYINIT_TOP == "C1") begin
        assign precyinit_top = 1'b1;
    end else if(PRECYINIT_TOP == "EX") begin
        assign precyinit_top = inp[4];
    end else if(PRECYINIT_TOP == "CO3") begin
        assign precyinit_top = out[3];
    end endgenerate

    generate if(PRECYINIT_BOT == "C0") begin
        assign precyinit_bot = 1'b0;
    end else if(PRECYINIT_BOT == "C1") begin
        assign precyinit_bot = 1'b1;
    end else if(PRECYINIT_BOT == "AX") begin
        assign precyinit_bot = inp[0];
    end endgenerate

    (* LOC=LOC_CI, KEEP, DONT_TOUCH *)
    CARRY8 #(.CARRY_TYPE(CARRY_TYPE)) carry8_ci
        (
        .CI     (precyinit_bot),
        .CI_TOP (precyinit_top),
        .DI     (inp[ 7:0]),
        .S      (inp[15:8]),
        .CO     (out[ 7:0]),
        .O      (out[15:8])
        );

endmodule

module PRECYINIT_CIN (
    input  wire        clk,
    input  wire [31:0] inp,
    output wire [31:0] out
);
    parameter LOC_CO     = "SLICE_FIXME";
    parameter LOC_CI     = "SLICE_FIXME";
    parameter CARRY_TYPE = "CARRY_TYPE_FIXME";

    parameter PRECYINIT_TOP = "FIXME";
    parameter PRECYINIT_BOT = "FIXME";

    wire precyinit_top;
    wire precyinit_bot;

    wire cin = out[23];

    generate if(PRECYINIT_TOP == "C0") begin
        assign precyinit_top = 1'b0;
    end else if(PRECYINIT_TOP == "C1") begin
        assign precyinit_top = 1'b1;
    end else if(PRECYINIT_TOP == "EX") begin
        assign precyinit_top = inp[4];
    end else if(PRECYINIT_TOP == "CO3") begin
        assign precyinit_top = out[3];
    end endgenerate

    generate if(PRECYINIT_BOT == "C0") begin
        assign precyinit_bot = 1'b0;
    end else if(PRECYINIT_BOT == "C1") begin
        assign precyinit_bot = 1'b1;
    end else if(PRECYINIT_BOT == "AX") begin
        assign precyinit_bot = inp[0];
    end else if(PRECYINIT_BOT == "CIN") begin
        assign precyinit_bot = cin;
    end endgenerate

    (* LOC=LOC_CI, KEEP, DONT_TOUCH *)
    CARRY8 #(.CARRY_TYPE(CARRY_TYPE)) carry8_ci
        (
        .CI     (precyinit_bot),
        .CI_TOP (precyinit_top),
        .DI     (inp[ 7:0]),
        .S      (inp[15:8]),
        .CO     (out[ 7:0]),
        .O      (out[15:8])
        );

    (* LOC=LOC_CO, KEEP, DONT_TOUCH *)
    CARRY8 #(.CARRY_TYPE("SINGLE_CY8")) carry8_co
        (
        .CI     (1'b0),
        .CI_TOP (1'b0),
        .DI     (inp[23:16]),
        .S      (inp[31:24]),
        .CO     (out[23:16]),
        .O      (out[31:24])
        );

endmodule

