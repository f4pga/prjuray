set_property -dict { PACKAGE_PIN F23    IOSTANDARD LVDS } [get_ports { IO_CLK_P }];
set_property -dict { PACKAGE_PIN E23    IOSTANDARD LVDS } [get_ports { IO_CLK_N }];
create_clock -add -name sys_clk_pin -period 8.000 -waveform {0 4.000}  [get_ports { IO_CLK_P }];

create_generated_clock -name clk_50_unbuf -source [get_pin clkgen/pll/CLKIN] [get_pin clkgen/pll/CLKOUT0]
create_generated_clock -name clk_48_unbuf -source [get_pin clkgen/pll/CLKIN] [get_pin clkgen/pll/CLKOUT1]
set_clock_groups -group clk_50_unbuf -group clk_48_unbuf -asynchronous

set_property -dict { PACKAGE_PIN C19   IOSTANDARD LVCMOS18 } [get_ports { IO_UTX }];
set_property -dict { PACKAGE_PIN A20   IOSTANDARD LVCMOS18 } [get_ports { IO_URX }];
