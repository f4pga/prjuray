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

# ddram:0.a
set_property LOC AH16 [get_ports ddram_a[0]]
set_property SLEW FAST [get_ports ddram_a[0]]
set_property IOSTANDARD SSTL12_DCI [get_ports ddram_a[0]]

# ddram:0.a
set_property LOC AG14 [get_ports ddram_a[1]]
set_property SLEW FAST [get_ports ddram_a[1]]
set_property IOSTANDARD SSTL12_DCI [get_ports ddram_a[1]]

# ddram:0.a
set_property LOC AG15 [get_ports ddram_a[2]]
set_property SLEW FAST [get_ports ddram_a[2]]
set_property IOSTANDARD SSTL12_DCI [get_ports ddram_a[2]]

# ddram:0.a
set_property LOC AF15 [get_ports ddram_a[3]]
set_property SLEW FAST [get_ports ddram_a[3]]
set_property IOSTANDARD SSTL12_DCI [get_ports ddram_a[3]]

# ddram:0.a
set_property LOC AF16 [get_ports ddram_a[4]]
set_property SLEW FAST [get_ports ddram_a[4]]
set_property IOSTANDARD SSTL12_DCI [get_ports ddram_a[4]]

# ddram:0.a
set_property LOC AJ14 [get_ports ddram_a[5]]
set_property SLEW FAST [get_ports ddram_a[5]]
set_property IOSTANDARD SSTL12_DCI [get_ports ddram_a[5]]

# ddram:0.a
set_property LOC AH14 [get_ports ddram_a[6]]
set_property SLEW FAST [get_ports ddram_a[6]]
set_property IOSTANDARD SSTL12_DCI [get_ports ddram_a[6]]

# ddram:0.a
set_property LOC AF17 [get_ports ddram_a[7]]
set_property SLEW FAST [get_ports ddram_a[7]]
set_property IOSTANDARD SSTL12_DCI [get_ports ddram_a[7]]

# ddram:0.a
set_property LOC AK17 [get_ports ddram_a[8]]
set_property SLEW FAST [get_ports ddram_a[8]]
set_property IOSTANDARD SSTL12_DCI [get_ports ddram_a[8]]

# ddram:0.a
set_property LOC AJ17 [get_ports ddram_a[9]]
set_property SLEW FAST [get_ports ddram_a[9]]
set_property IOSTANDARD SSTL12_DCI [get_ports ddram_a[9]]

# ddram:0.a
set_property LOC AK14 [get_ports ddram_a[10]]
set_property SLEW FAST [get_ports ddram_a[10]]
set_property IOSTANDARD SSTL12_DCI [get_ports ddram_a[10]]

# ddram:0.a
set_property LOC AK15 [get_ports ddram_a[11]]
set_property SLEW FAST [get_ports ddram_a[11]]
set_property IOSTANDARD SSTL12_DCI [get_ports ddram_a[11]]

# ddram:0.a
set_property LOC AL18 [get_ports ddram_a[12]]
set_property SLEW FAST [get_ports ddram_a[12]]
set_property IOSTANDARD SSTL12_DCI [get_ports ddram_a[12]]

# ddram:0.a
set_property LOC AK18 [get_ports ddram_a[13]]
set_property SLEW FAST [get_ports ddram_a[13]]
set_property IOSTANDARD SSTL12_DCI [get_ports ddram_a[13]]

# ddram:0.ba
set_property LOC AL15 [get_ports ddram_ba[0]]
set_property SLEW FAST [get_ports ddram_ba[0]]
set_property IOSTANDARD SSTL12_DCI [get_ports ddram_ba[0]]

# ddram:0.ba
set_property LOC AL16 [get_ports ddram_ba[1]]
set_property SLEW FAST [get_ports ddram_ba[1]]
set_property IOSTANDARD SSTL12_DCI [get_ports ddram_ba[1]]

# ddram:0.bg
set_property LOC AC16 [get_ports ddram_bg[0]]
set_property SLEW FAST [get_ports ddram_bg[0]]
set_property IOSTANDARD SSTL12_DCI [get_ports ddram_bg[0]]

# ddram:0.bg
set_property LOC AB16 [get_ports ddram_bg[1]]
set_property SLEW FAST [get_ports ddram_bg[1]]
set_property IOSTANDARD SSTL12_DCI [get_ports ddram_bg[1]]

# ddram:0.ras_n
set_property LOC AD15 [get_ports ddram_ras_n]
set_property SLEW FAST [get_ports ddram_ras_n]
set_property IOSTANDARD SSTL12_DCI [get_ports ddram_ras_n]

# ddram:0.cas_n
set_property LOC AA14 [get_ports ddram_cas_n]
set_property SLEW FAST [get_ports ddram_cas_n]
set_property IOSTANDARD SSTL12_DCI [get_ports ddram_cas_n]

# ddram:0.we_n
set_property LOC AA16 [get_ports ddram_we_n]
set_property SLEW FAST [get_ports ddram_we_n]
set_property IOSTANDARD SSTL12_DCI [get_ports ddram_we_n]

# ddram:0.cs_n
set_property LOC AA15 [get_ports ddram_cs_n]
set_property SLEW FAST [get_ports ddram_cs_n]
set_property IOSTANDARD SSTL12_DCI [get_ports ddram_cs_n]

# ddram:0.act_n
set_property LOC AC17 [get_ports ddram_act_n]
set_property SLEW FAST [get_ports ddram_act_n]
set_property IOSTANDARD SSTL12_DCI [get_ports ddram_act_n]

# ddram:0.dm
set_property LOC AF11 [get_ports ddram_dm[0]]
set_property SLEW FAST [get_ports ddram_dm[0]]
set_property IOSTANDARD POD12_DCI [get_ports ddram_dm[0]]

# ddram:0.dm
set_property LOC AH12 [get_ports ddram_dm[1]]
set_property SLEW FAST [get_ports ddram_dm[1]]
set_property IOSTANDARD POD12_DCI [get_ports ddram_dm[1]]

# ddram:0.dm
set_property LOC AK13 [get_ports ddram_dm[2]]
set_property SLEW FAST [get_ports ddram_dm[2]]
set_property IOSTANDARD POD12_DCI [get_ports ddram_dm[2]]

# ddram:0.dm
set_property LOC AN12 [get_ports ddram_dm[3]]
set_property SLEW FAST [get_ports ddram_dm[3]]
set_property IOSTANDARD POD12_DCI [get_ports ddram_dm[3]]

# ddram:0.dq
set_property LOC AC13 [get_ports ddram_dq[0]]
set_property SLEW FAST [get_ports ddram_dq[0]]
set_property IOSTANDARD POD12_DCI [get_ports ddram_dq[0]]

# ddram:0.dq
set_property LOC AB13 [get_ports ddram_dq[1]]
set_property SLEW FAST [get_ports ddram_dq[1]]
set_property IOSTANDARD POD12_DCI [get_ports ddram_dq[1]]

# ddram:0.dq
set_property LOC AF12 [get_ports ddram_dq[2]]
set_property SLEW FAST [get_ports ddram_dq[2]]
set_property IOSTANDARD POD12_DCI [get_ports ddram_dq[2]]

# ddram:0.dq
set_property LOC AE12 [get_ports ddram_dq[3]]
set_property SLEW FAST [get_ports ddram_dq[3]]
set_property IOSTANDARD POD12_DCI [get_ports ddram_dq[3]]

# ddram:0.dq
set_property LOC AF13 [get_ports ddram_dq[4]]
set_property SLEW FAST [get_ports ddram_dq[4]]
set_property IOSTANDARD POD12_DCI [get_ports ddram_dq[4]]

# ddram:0.dq
set_property LOC AE13 [get_ports ddram_dq[5]]
set_property SLEW FAST [get_ports ddram_dq[5]]
set_property IOSTANDARD POD12_DCI [get_ports ddram_dq[5]]

# ddram:0.dq
set_property LOC AE14 [get_ports ddram_dq[6]]
set_property SLEW FAST [get_ports ddram_dq[6]]
set_property IOSTANDARD POD12_DCI [get_ports ddram_dq[6]]

# ddram:0.dq
set_property LOC AD14 [get_ports ddram_dq[7]]
set_property SLEW FAST [get_ports ddram_dq[7]]
set_property IOSTANDARD POD12_DCI [get_ports ddram_dq[7]]

# ddram:0.dq
set_property LOC AG8 [get_ports ddram_dq[8]]
set_property SLEW FAST [get_ports ddram_dq[8]]
set_property IOSTANDARD POD12_DCI [get_ports ddram_dq[8]]

# ddram:0.dq
set_property LOC AF8 [get_ports ddram_dq[9]]
set_property SLEW FAST [get_ports ddram_dq[9]]
set_property IOSTANDARD POD12_DCI [get_ports ddram_dq[9]]

# ddram:0.dq
set_property LOC AG10 [get_ports ddram_dq[10]]
set_property SLEW FAST [get_ports ddram_dq[10]]
set_property IOSTANDARD POD12_DCI [get_ports ddram_dq[10]]

# ddram:0.dq
set_property LOC AG11 [get_ports ddram_dq[11]]
set_property SLEW FAST [get_ports ddram_dq[11]]
set_property IOSTANDARD POD12_DCI [get_ports ddram_dq[11]]

# ddram:0.dq
set_property LOC AH13 [get_ports ddram_dq[12]]
set_property SLEW FAST [get_ports ddram_dq[12]]
set_property IOSTANDARD POD12_DCI [get_ports ddram_dq[12]]

# ddram:0.dq
set_property LOC AG13 [get_ports ddram_dq[13]]
set_property SLEW FAST [get_ports ddram_dq[13]]
set_property IOSTANDARD POD12_DCI [get_ports ddram_dq[13]]

# ddram:0.dq
set_property LOC AJ11 [get_ports ddram_dq[14]]
set_property SLEW FAST [get_ports ddram_dq[14]]
set_property IOSTANDARD POD12_DCI [get_ports ddram_dq[14]]

# ddram:0.dq
set_property LOC AH11 [get_ports ddram_dq[15]]
set_property SLEW FAST [get_ports ddram_dq[15]]
set_property IOSTANDARD POD12_DCI [get_ports ddram_dq[15]]

# ddram:0.dq
set_property LOC AK9 [get_ports ddram_dq[16]]
set_property SLEW FAST [get_ports ddram_dq[16]]
set_property IOSTANDARD POD12_DCI [get_ports ddram_dq[16]]

# ddram:0.dq
set_property LOC AJ9 [get_ports ddram_dq[17]]
set_property SLEW FAST [get_ports ddram_dq[17]]
set_property IOSTANDARD POD12_DCI [get_ports ddram_dq[17]]

# ddram:0.dq
set_property LOC AK10 [get_ports ddram_dq[18]]
set_property SLEW FAST [get_ports ddram_dq[18]]
set_property IOSTANDARD POD12_DCI [get_ports ddram_dq[18]]

# ddram:0.dq
set_property LOC AJ10 [get_ports ddram_dq[19]]
set_property SLEW FAST [get_ports ddram_dq[19]]
set_property IOSTANDARD POD12_DCI [get_ports ddram_dq[19]]

# ddram:0.dq
set_property LOC AL12 [get_ports ddram_dq[20]]
set_property SLEW FAST [get_ports ddram_dq[20]]
set_property IOSTANDARD POD12_DCI [get_ports ddram_dq[20]]

# ddram:0.dq
set_property LOC AK12 [get_ports ddram_dq[21]]
set_property SLEW FAST [get_ports ddram_dq[21]]
set_property IOSTANDARD POD12_DCI [get_ports ddram_dq[21]]

# ddram:0.dq
set_property LOC AL10 [get_ports ddram_dq[22]]
set_property SLEW FAST [get_ports ddram_dq[22]]
set_property IOSTANDARD POD12_DCI [get_ports ddram_dq[22]]

# ddram:0.dq
set_property LOC AL11 [get_ports ddram_dq[23]]
set_property SLEW FAST [get_ports ddram_dq[23]]
set_property IOSTANDARD POD12_DCI [get_ports ddram_dq[23]]

# ddram:0.dq
set_property LOC AM8 [get_ports ddram_dq[24]]
set_property SLEW FAST [get_ports ddram_dq[24]]
set_property IOSTANDARD POD12_DCI [get_ports ddram_dq[24]]

# ddram:0.dq
set_property LOC AM9 [get_ports ddram_dq[25]]
set_property SLEW FAST [get_ports ddram_dq[25]]
set_property IOSTANDARD POD12_DCI [get_ports ddram_dq[25]]

# ddram:0.dq
set_property LOC AM10 [get_ports ddram_dq[26]]
set_property SLEW FAST [get_ports ddram_dq[26]]
set_property IOSTANDARD POD12_DCI [get_ports ddram_dq[26]]

# ddram:0.dq
set_property LOC AM11 [get_ports ddram_dq[27]]
set_property SLEW FAST [get_ports ddram_dq[27]]
set_property IOSTANDARD POD12_DCI [get_ports ddram_dq[27]]

# ddram:0.dq
set_property LOC AP11 [get_ports ddram_dq[28]]
set_property SLEW FAST [get_ports ddram_dq[28]]
set_property IOSTANDARD POD12_DCI [get_ports ddram_dq[28]]

# ddram:0.dq
set_property LOC AN11 [get_ports ddram_dq[29]]
set_property SLEW FAST [get_ports ddram_dq[29]]
set_property IOSTANDARD POD12_DCI [get_ports ddram_dq[29]]

# ddram:0.dq
set_property LOC AP9 [get_ports ddram_dq[30]]
set_property SLEW FAST [get_ports ddram_dq[30]]
set_property IOSTANDARD POD12_DCI [get_ports ddram_dq[30]]

# ddram:0.dq
set_property LOC AP10 [get_ports ddram_dq[31]]
set_property SLEW FAST [get_ports ddram_dq[31]]
set_property IOSTANDARD POD12_DCI [get_ports ddram_dq[31]]

# ddram:0.dqs_p
set_property LOC AC12 [get_ports ddram_dqs_p[0]]
set_property SLEW FAST [get_ports ddram_dqs_p[0]]
set_property IOSTANDARD DIFF_POD12_DCI [get_ports ddram_dqs_p[0]]

# ddram:0.dqs_p
set_property LOC AG9 [get_ports ddram_dqs_p[1]]
set_property SLEW FAST [get_ports ddram_dqs_p[1]]
set_property IOSTANDARD DIFF_POD12_DCI [get_ports ddram_dqs_p[1]]

# ddram:0.dqs_p
set_property LOC AK8 [get_ports ddram_dqs_p[2]]
set_property SLEW FAST [get_ports ddram_dqs_p[2]]
set_property IOSTANDARD DIFF_POD12_DCI [get_ports ddram_dqs_p[2]]

# ddram:0.dqs_p
set_property LOC AN9 [get_ports ddram_dqs_p[3]]
set_property SLEW FAST [get_ports ddram_dqs_p[3]]
set_property IOSTANDARD DIFF_POD12_DCI [get_ports ddram_dqs_p[3]]

# ddram:0.dqs_n
set_property LOC AD12 [get_ports ddram_dqs_n[0]]
set_property SLEW FAST [get_ports ddram_dqs_n[0]]
set_property IOSTANDARD DIFF_POD12_DCI [get_ports ddram_dqs_n[0]]

# ddram:0.dqs_n
set_property LOC AH9 [get_ports ddram_dqs_n[1]]
set_property SLEW FAST [get_ports ddram_dqs_n[1]]
set_property IOSTANDARD DIFF_POD12_DCI [get_ports ddram_dqs_n[1]]

# ddram:0.dqs_n
set_property LOC AL8 [get_ports ddram_dqs_n[2]]
set_property SLEW FAST [get_ports ddram_dqs_n[2]]
set_property IOSTANDARD DIFF_POD12_DCI [get_ports ddram_dqs_n[2]]

# ddram:0.dqs_n
set_property LOC AN8 [get_ports ddram_dqs_n[3]]
set_property SLEW FAST [get_ports ddram_dqs_n[3]]
set_property IOSTANDARD DIFF_POD12_DCI [get_ports ddram_dqs_n[3]]

# ddram:0.clk_p
set_property LOC AF18 [get_ports ddram_clk_p]
set_property SLEW FAST [get_ports ddram_clk_p]
set_property IOSTANDARD DIFF_SSTL12_DCI [get_ports ddram_clk_p]

# ddram:0.clk_n
set_property LOC AG18 [get_ports ddram_clk_n]
set_property SLEW FAST [get_ports ddram_clk_n]
set_property IOSTANDARD DIFF_SSTL12_DCI [get_ports ddram_clk_n]

# ddram:0.cke
set_property LOC AD17 [get_ports ddram_cke]
set_property SLEW FAST [get_ports ddram_cke]
set_property IOSTANDARD SSTL12_DCI [get_ports ddram_cke]

# ddram:0.odt
set_property LOC AE15 [get_ports ddram_odt]
set_property SLEW FAST [get_ports ddram_odt]
set_property IOSTANDARD SSTL12_DCI [get_ports ddram_odt]

# ddram:0.reset_n
set_property LOC AB14 [get_ports ddram_reset_n]
set_property SLEW FAST [get_ports ddram_reset_n]
set_property IOSTANDARD LVCMOS12 [get_ports ddram_reset_n]

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
