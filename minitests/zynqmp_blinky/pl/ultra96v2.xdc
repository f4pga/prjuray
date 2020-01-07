# LEDs
set_property PACKAGE_PIN A9 [get_ports led[0]]
set_property PACKAGE_PIN B9 [get_ports led[1]]

foreach port [get_ports] {
    set_property IOSTANDARD LVCMOS18 $port
    set_property SLEW SLOW $port
}

