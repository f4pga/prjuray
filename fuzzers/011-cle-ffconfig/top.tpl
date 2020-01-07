module top(input clk);
	localparam integer DOUT_N = {{ dout }};

    wire [DOUT_N-1:0] dout;

    roi roi (
        .clk(clk),
        .dout(dout)
    );
endmodule

module roi(input clk, output [{{ dout-1 }}:0] dout);
{% for instance in instances %}
	clb_{{ instance['type'] }} #(
		.LOC("{{ instance['loc'] }}"),
		.BEL("{{ instance['bel'] }}"),
		.INIT({{ instance['init'] }})
	) clb_{{ instance['number'] }} (
		.clk(clk),
		.din(4'b1111),
		.dout(dout[{{ instance['dout'] }}])
	);
{% endfor %}
endmodule

module clb_FD ({{ ios }});
    {{ parameters }}

    {{ loc }}
	FD ff (
		.C(clk),
		.Q(dout),
		.D(din[0])
	);
endmodule

module clb_FD_1 ({{ ios }});
    {{ parameters }}

    {{ loc }}
    FD_1 ff (
	    .C(clk),
	    .Q(dout),
	    .D(din[0])
    );
endmodule

module clb_FDC ({{ ios }});
    {{ parameters }}

    {{ loc }}
    FDC ff (
	    .C(clk),
	    .Q(dout),
	    .CLR(din[0]),
	    .D(din[1])
    );
endmodule

module clb_FDC_1 ({{ ios }});
    {{ parameters }}

    {{ loc }}
    FDC_1 ff (
	    .C(clk),
	    .Q(dout),
	    .CLR(din[0]),
	    .D(din[1])
    );
endmodule

module clb_FDCE ({{ ios }});
    {{ parameters }}

	{{ loc }}
    FDCE ff (
	    .C(clk),
	    .Q(dout),
	    .CE(din[0]),
	    .CLR(din[1]),
	    .D(din[2])
    );
endmodule

module clb_FDCE_1 ({{ ios }});
    {{ parameters }}

	{{ loc }}
	FDCE_1 ff (
		.C(clk),
		.Q(dout),
		.CE(din[0]),
		.CLR(din[1]),
		.D(din[2])
	);
	endmodule

module clb_FDE ({{ ios }});
    {{ parameters }}

	{{ loc }}
	FDE ff (
		.C(clk),
		.Q(dout),
		.D(din[0]),
		.CE(din[1])
	);
	endmodule

module clb_FDE_1 ({{ ios }});
    {{ parameters }}

	{{ loc }}
	FDE_1 ff (
		.C(clk),
		.Q(dout),
		.D(din[0]),
		.CE(din[1])
	);
	endmodule

module clb_FDP ({{ ios }});
    {{ parameters }}

	{{ loc }}
	FDP ff (
		.C(clk),
		.Q(dout),
		.D(din[0]),
		.PRE(din[1])
	);
	endmodule

module clb_FDP_1 ({{ ios }});
    {{ parameters }}

	{{ loc }}
	FDP_1 ff (
		.C(clk),
		.Q(dout),
		.D(din[0]),
		.PRE(din[1])
	);
	endmodule

module clb_FDPE ({{ ios }});
    {{ parameters }}

	{{ loc }}
	FDPE ff (
		.C(clk),
		.Q(dout),
		.CE(din[0]),
		.PRE(din[1]),
		.D(din[2])
	);
	endmodule

module clb_FDPE_1 ({{ ios }});
    {{ parameters }}

	{{ loc }}
	FDPE_1 ff (
		.C(clk),
		.Q(dout),
		.CE(din[0]),
		.PRE(din[1]),
		.D(din[2])
	);
	endmodule

module clb_FDR ({{ ios }});
    {{ parameters }}

	{{ loc }}
	FDR ff (
		.C(clk),
		.Q(dout),
		.D(din[0]),
		.R(din[1])
	);
	endmodule

module clb_FDR_1 ({{ ios }});
    {{ parameters }}

	{{ loc }}
	FDR_1 ff (
		.C(clk),
		.Q(dout),
		.D(din[0]),
		.R(din[1])
	);
	endmodule

module clb_FDRE ({{ ios }});
    {{ parameters }}

	{{ loc }}
	FDRE ff (
		.C(clk),
		.Q(dout),
		.CE(din[0]),
		.R(din[1]),
		.D(din[2])
	);
	endmodule

module clb_FDRE_1 ({{ ios }});
    {{ parameters }}

	{{ loc }}
	FDRE_1 ff (
		.C(clk),
		.Q(dout),
		.CE(din[0]),
		.R(din[1]),
		.D(din[2])
	);
	endmodule

module clb_FDS ({{ ios }});
    {{ parameters }}

    {{ loc }}
	FDS ff (
		.C(clk),
		.Q(dout),
		.S(din[0]),
		.D(din[1])
	);
	endmodule

module clb_FDS_1 ({{ ios }});
    {{ parameters }}

    {{ loc }}
	FDS_1 ff (
		.C(clk),
		.Q(dout),
		.S(din[0]),
		.D(din[1])
	);
	endmodule

module clb_FDSE ({{ ios }});
    {{ parameters }}

    {{ loc }}
	FDSE ff (
		.C(clk),
		.Q(dout),
		.CE(din[0]),
		.S(din[1]),
		.D(din[2])
	);
	endmodule

module clb_FDSE_1 ({{ ios }});
    {{ parameters }}

    {{ loc }}
	FDSE_1 ff (
		.C(clk),
		.Q(dout),
		.CE(din[0]),
		.S(din[1]),
		.D(din[2])
	);
	endmodule

module clb_LDC ({{ ios }});
    {{ parameters }}

    {{ loc }}
	LDC ff (
		.G(~clk),
		.Q(dout),
		.D(din[0]),
		.CLR(din[1])
	);
	endmodule
module clb_LDC_1 ({{ ios }});
    {{ parameters }}

    {{ loc }}
	LDC_1 ff (
		.G(~clk),
		.Q(dout),
		.D(din[0]),
		.CLR(din[1])
	);
	endmodule

module clb_LDCE ({{ ios }});
    {{ parameters }}

    {{ loc }}
	LDCE ff (
		.G(~clk),
		//NOTE: diagram shows two outputs. Error?
		.Q(dout),
		.D(din[0]),
		.GE(din[1]),
		.CLR(din[2])
	);
	endmodule

module clb_LDCE_1 ({{ ios }});
    {{ parameters }}

    {{ loc }}
	LDCE_1 ff (
		.G(~clk),
		//NOTE: diagram shows two outputs. Error?
		.Q(dout),
		.D(din[0]),
		.GE(din[1]),
		.CLR(din[2])
	);
	endmodule

module clb_LDE ({{ ios }});
    {{ parameters }}

    {{ loc }}
	LDE ff (
		.G(~clk),
		.Q(dout),
		.D(din[0]),
		.GE(din[1])
	);

endmodule

module clb_LDE_1 ({{ ios }});
    {{ parameters }}

    {{ loc }}
	LDE_1 ff (
		.G(~clk),
		.Q(dout),
		.D(din[0]),
		.GE(din[1])
	);
endmodule

module clb_LDP ({{ ios }});
    {{ parameters }}

    {{ loc }}
	LDP ff (
		.G(~clk),
		.Q(dout),
		.D(din[0]),
		.PRE(din[1])
	);
endmodule

module clb_LDP_1 ({{ ios }});
    {{ parameters }}

    {{ loc }}
	LDP_1 ff (
		.G(~clk),
		.Q(dout),
		.D(din[0]),
		.PRE(din[1])
	);
endmodule

module clb_LDPE ({{ ios }});
    {{ parameters }}

    {{ loc }}
	LDPE ff (
		.G(~clk),
		.Q(dout),
		.PRE(din[0]),
		.D(din[1]),
		.GE(din[2])
	);
endmodule

module clb_LDPE_1 ({{ ios }});
    {{ parameters }}

    {{ loc }}
	LDPE_1 ff (
		.G(~clk),
		.Q(dout),
		.PRE(din[0]),
		.D(din[1]),
		.GE(din[2])
	);
endmodule
