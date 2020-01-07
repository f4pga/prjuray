BUFG\_PS input mux fuzzer
-------------------------

Each `RCLK_INTF_LEFT_TERM_ALTO` tile has 24 `BUFG_PS` sites, one for each US\+
global clock resource.  Each `RCLK_INTF_LEFT_TERM_ALTO` has 18 dedicated clock
inputs from the PS8 tile, along with an interconnect connection.  Each of the
18 dedicated can reach all 24 of the `BUFG_PS` sites, mean that there are
18 * 24 possible connections.
