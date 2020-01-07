################################################################################
# IO constraints
################################################################################
# serial:0.cts
set_property LOC A19 [get_ports serial_cts]
set_property IOSTANDARD LVCMOS18 [get_ports serial_cts]

# serial:0.rts
set_property LOC C18 [get_ports serial_rts]
set_property IOSTANDARD LVCMOS18 [get_ports serial_rts]

# serial:0.tx
set_property LOC C19 [get_ports serial_tx]
set_property IOSTANDARD LVCMOS18 [get_ports serial_tx]

# serial:0.rx
set_property LOC A20 [get_ports serial_rx]
set_property IOSTANDARD LVCMOS18 [get_ports serial_rx]

# clk125:0.p
set_property LOC F23 [get_ports clk125_p]
set_property IOSTANDARD LVDS [get_ports clk125_p]

# clk125:0.n
set_property LOC E23 [get_ports clk125_n]
set_property IOSTANDARD LVDS [get_ports clk125_n]

################################################################################
# Design constraints
################################################################################

set_property INTERNAL_VREF {0.84} [get_iobanks 65]

set_property INTERNAL_VREF {0.84} [get_iobanks 66]

################################################################################
# Clock constraints
################################################################################


create_clock -name clk125_p -period 8.0 [get_nets clk125_p]

################################################################################
# False path constraints
################################################################################


set_false_path -quiet -to [get_nets -quiet -filter {mr_ff == TRUE}]

set_false_path -quiet -to [get_pins -quiet -filter {REF_PIN_NAME == PRE} -of [get_cells -quiet FDPE* ]]

set_max_delay 2 -quiet -from [get_pins -quiet -filter {REF_PIN_NAME == Q} -of [get_cells -quiet FDPE ]] -to [get_pins -quiet -filter {REF_PIN_NAME == D} -of [get_cells -quiet FDPE_1 ]]

set_max_delay 2 -quiet -from [get_pins -quiet -filter {REF_PIN_NAME == Q} -of [get_cells -quiet FDPE_2 ]] -to [get_pins -quiet -filter {REF_PIN_NAME == D} -of [get_cells -quiet FDPE_3 ]]
