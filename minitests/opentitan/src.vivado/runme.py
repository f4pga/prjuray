#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2020-2022 F4PGA Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

import edalize
import os

work_root = 'build'

post_imp_file = os.path.realpath(os.path.join(work_root, 'post.tcl'))

os.makedirs(work_root, exist_ok=True)

synth_tool = 'vivado'

srcs = [
    'lowrisc_constants_top_pkg_0/rtl/top_pkg.sv',
    'lowrisc_dv_pins_if_0/pins_if.sv',
    'lowrisc_prim_generic_clock_gating_0/rtl/prim_generic_clock_gating.sv',
    'lowrisc_prim_generic_clock_mux2_0/rtl/prim_generic_clock_mux2.sv',
    'lowrisc_prim_generic_flash_0/rtl/prim_generic_flash.sv',
    'lowrisc_prim_generic_pad_wrapper_0/rtl/prim_generic_pad_wrapper.sv',
    'lowrisc_prim_generic_ram_1p_0/rtl/prim_generic_ram_1p.sv',
    'lowrisc_prim_generic_ram_2p_0/rtl/prim_generic_ram_2p.sv',
    'lowrisc_prim_prim_pkg_0.1/rtl/prim_pkg.sv',
    'lowrisc_prim_xilinx_clock_gating_0/rtl/prim_xilinx_clock_gating.sv',
    'lowrisc_prim_xilinx_clock_mux2_0/rtl/prim_xilinx_clock_mux2.sv',
    'lowrisc_prim_xilinx_pad_wrapper_0/rtl/prim_xilinx_pad_wrapper.sv',
    'lowrisc_prim_xilinx_ram_2p_0/rtl/prim_xilinx_ram_2p.sv',
    'lowrisc_ibex_ibex_core_0.1/rtl/ibex_pkg.sv',
    'lowrisc_ibex_ibex_core_0.1/rtl/ibex_alu.sv',
    'lowrisc_ibex_ibex_core_0.1/rtl/ibex_compressed_decoder.sv',
    'lowrisc_ibex_ibex_core_0.1/rtl/ibex_controller.sv',
    'lowrisc_ibex_ibex_core_0.1/rtl/ibex_cs_registers.sv',
    'lowrisc_ibex_ibex_core_0.1/rtl/ibex_decoder.sv',
    'lowrisc_ibex_ibex_core_0.1/rtl/ibex_ex_block.sv',
    'lowrisc_ibex_ibex_core_0.1/rtl/ibex_fetch_fifo.sv',
    'lowrisc_ibex_ibex_core_0.1/rtl/ibex_id_stage.sv',
    'lowrisc_ibex_ibex_core_0.1/rtl/ibex_if_stage.sv',
    'lowrisc_ibex_ibex_core_0.1/rtl/ibex_load_store_unit.sv',
    'lowrisc_ibex_ibex_core_0.1/rtl/ibex_multdiv_fast.sv',
    'lowrisc_ibex_ibex_core_0.1/rtl/ibex_multdiv_slow.sv',
    'lowrisc_ibex_ibex_core_0.1/rtl/ibex_prefetch_buffer.sv',
    'lowrisc_ibex_ibex_core_0.1/rtl/ibex_pmp.sv',
    'lowrisc_ibex_ibex_core_0.1/rtl/ibex_register_file_ff.sv',
    'lowrisc_ibex_ibex_core_0.1/rtl/ibex_core.sv',
    'lowrisc_ip_flash_ctrl_pkg_0.1/rtl/flash_ctrl_pkg.sv',
    'lowrisc_prim_clock_gating_0/abstract/prim_clock_gating.sv',
    'lowrisc_prim_clock_mux2_0/abstract/prim_clock_mux2.sv',
    'lowrisc_prim_diff_decode_0/rtl/prim_diff_decode.sv',
    'lowrisc_prim_pad_wrapper_0/abstract/prim_pad_wrapper.sv',
    'lowrisc_prim_ram_1p_0/abstract/prim_ram_1p.sv',
    'lowrisc_prim_ram_2p_0/abstract/prim_ram_2p.sv',
    'lowrisc_tlul_headers_0.1/rtl/tlul_pkg.sv',
    'lowrisc_prim_all_0.1/rtl/prim_clock_inverter.sv',
    'lowrisc_prim_all_0.1/rtl/prim_alert_receiver.sv',
    'lowrisc_prim_all_0.1/rtl/prim_alert_sender.sv',
    'lowrisc_prim_all_0.1/rtl/prim_arbiter_ppc.sv',
    'lowrisc_prim_all_0.1/rtl/prim_arbiter_tree.sv',
    'lowrisc_prim_all_0.1/rtl/prim_esc_receiver.sv',
    'lowrisc_prim_all_0.1/rtl/prim_esc_sender.sv',
    'lowrisc_prim_all_0.1/rtl/prim_sram_arbiter.sv',
    'lowrisc_prim_all_0.1/rtl/prim_fifo_async.sv',
    'lowrisc_prim_all_0.1/rtl/prim_fifo_sync.sv',
    'lowrisc_prim_all_0.1/rtl/prim_flop_2sync.sv',
    'lowrisc_prim_all_0.1/rtl/prim_lfsr.sv',
    'lowrisc_prim_all_0.1/rtl/prim_packer.sv',
    'lowrisc_prim_all_0.1/rtl/prim_pulse_sync.sv',
    'lowrisc_prim_all_0.1/rtl/prim_filter.sv',
    'lowrisc_prim_all_0.1/rtl/prim_filter_ctr.sv',
    'lowrisc_prim_all_0.1/rtl/prim_subreg.sv',
    'lowrisc_prim_all_0.1/rtl/prim_subreg_ext.sv',
    'lowrisc_prim_all_0.1/rtl/prim_intr_hw.sv',
    'lowrisc_prim_all_0.1/rtl/prim_secded_39_32_enc.sv',
    'lowrisc_prim_all_0.1/rtl/prim_secded_39_32_dec.sv',
    'lowrisc_prim_all_0.1/rtl/prim_ram_2p_adv.sv',
    'lowrisc_prim_all_0.1/rtl/prim_ram_2p_async_adv.sv',
    'lowrisc_prim_flash_0/abstract/prim_flash.sv',
    'lowrisc_top_earlgrey_alert_handler_reg_0.1/rtl/autogen/alert_handler_reg_pkg.sv',
    'lowrisc_top_earlgrey_alert_handler_reg_0.1/rtl/autogen/alert_handler_reg_top.sv',
    'lowrisc_top_earlgrey_pinmux_reg_0.1/rtl/autogen/pinmux_reg_pkg.sv',
    'lowrisc_top_earlgrey_pinmux_reg_0.1/rtl/autogen/pinmux_reg_top.sv',
    'lowrisc_ip_usb_fs_nb_pe_0.1/rtl/usb_consts_pkg.sv',
    'lowrisc_ip_usb_fs_nb_pe_0.1/rtl/usb_fs_nb_in_pe.sv',
    'lowrisc_ip_usb_fs_nb_pe_0.1/rtl/usb_fs_nb_out_pe.sv',
    'lowrisc_ip_usb_fs_nb_pe_0.1/rtl/usb_fs_nb_pe.sv',
    'lowrisc_ip_usb_fs_nb_pe_0.1/rtl/usb_fs_rx.sv',
    'lowrisc_ip_usb_fs_nb_pe_0.1/rtl/usb_fs_tx.sv',
    'lowrisc_ip_usb_fs_nb_pe_0.1/rtl/usb_fs_tx_mux.sv',
    'lowrisc_prim_generic_rom_0/rtl/prim_generic_rom.sv',
    'lowrisc_prim_xilinx_rom_0/rtl/prim_xilinx_rom.sv',
    'lowrisc_tlul_common_0.1/rtl/tlul_fifo_sync.sv',
    'lowrisc_tlul_common_0.1/rtl/tlul_fifo_async.sv',
    'lowrisc_tlul_common_0.1/rtl/tlul_assert.sv',
    'lowrisc_tlul_common_0.1/rtl/tlul_err.sv',
    'lowrisc_tlul_common_0.1/rtl/tlul_assert_multiple.sv',
    'pulp-platform_riscv-dbg_0.1_0/pulp_riscv_dbg/debug_rom/debug_rom.sv',
    'pulp-platform_riscv-dbg_0.1_0/pulp_riscv_dbg/src/dm_pkg.sv',
    'pulp-platform_riscv-dbg_0.1_0/pulp_riscv_dbg/src/dm_sba.sv',
    'pulp-platform_riscv-dbg_0.1_0/pulp_riscv_dbg/src/dm_csrs.sv',
    'pulp-platform_riscv-dbg_0.1_0/pulp_riscv_dbg/src/dm_mem.sv',
    'pulp-platform_riscv-dbg_0.1_0/pulp_riscv_dbg/src/dmi_cdc.sv',
    'pulp-platform_riscv-dbg_0.1_0/pulp_riscv_dbg/src/dmi_jtag.sv',
    'pulp-platform_riscv-dbg_0.1_0/pulp_riscv_dbg/src/dmi_jtag_tap.sv',
    'lowrisc_prim_rom_0/abstract/prim_rom.sv',
    'lowrisc_tlul_adapter_reg_0.1/rtl/tlul_adapter_reg.sv',
    'lowrisc_tlul_adapter_sram_0.1/rtl/tlul_adapter_sram.sv',
    'lowrisc_tlul_socket_1n_0.1/rtl/tlul_err_resp.sv',
    'lowrisc_tlul_socket_1n_0.1/rtl/tlul_socket_1n.sv',
    'lowrisc_tlul_socket_m1_0.1/rtl/tlul_socket_m1.sv',
    'lowrisc_tlul_sram2tlul_0.1/rtl/sram2tlul.sv',
    'lowrisc_ip_aes_0.5/rtl/aes_pkg.sv',
    'lowrisc_ip_aes_0.5/rtl/aes_reg_pkg.sv',
    'lowrisc_ip_aes_0.5/rtl/aes_reg_top.sv',
    'lowrisc_ip_aes_0.5/rtl/aes_core.sv',
    'lowrisc_ip_aes_0.5/rtl/aes_control.sv',
    'lowrisc_ip_aes_0.5/rtl/aes_cipher_core.sv',
    'lowrisc_ip_aes_0.5/rtl/aes_cipher_control.sv',
    'lowrisc_ip_aes_0.5/rtl/aes_sub_bytes.sv',
    'lowrisc_ip_aes_0.5/rtl/aes_sbox.sv',
    'lowrisc_ip_aes_0.5/rtl/aes_sbox_lut.sv',
    'lowrisc_ip_aes_0.5/rtl/aes_sbox_canright.sv',
    'lowrisc_ip_aes_0.5/rtl/aes_shift_rows.sv',
    'lowrisc_ip_aes_0.5/rtl/aes_mix_columns.sv',
    'lowrisc_ip_aes_0.5/rtl/aes_mix_single_column.sv',
    'lowrisc_ip_aes_0.5/rtl/aes_key_expand.sv',
    'lowrisc_ip_aes_0.5/rtl/aes.sv',
    'lowrisc_ip_alert_handler_component_0.1/rtl/alert_pkg.sv',
    'lowrisc_ip_alert_handler_component_0.1/rtl/alert_handler_reg_wrap.sv',
    'lowrisc_ip_alert_handler_component_0.1/rtl/alert_handler_class.sv',
    'lowrisc_ip_alert_handler_component_0.1/rtl/alert_handler_ping_timer.sv',
    'lowrisc_ip_alert_handler_component_0.1/rtl/alert_handler_esc_timer.sv',
    'lowrisc_ip_alert_handler_component_0.1/rtl/alert_handler_accu.sv',
    'lowrisc_ip_alert_handler_component_0.1/rtl/alert_handler.sv',
    'lowrisc_ip_flash_ctrl_0.1/rtl/flash_ctrl_reg_pkg.sv',
    'lowrisc_ip_flash_ctrl_0.1/rtl/flash_ctrl_reg_top.sv',
    'lowrisc_ip_flash_ctrl_0.1/rtl/flash_ctrl.sv',
    'lowrisc_ip_flash_ctrl_0.1/rtl/flash_erase_ctrl.sv',
    'lowrisc_ip_flash_ctrl_0.1/rtl/flash_prog_ctrl.sv',
    'lowrisc_ip_flash_ctrl_0.1/rtl/flash_rd_ctrl.sv',
    'lowrisc_ip_flash_ctrl_0.1/rtl/flash_mp.sv',
    'lowrisc_ip_flash_ctrl_0.1/rtl/flash_phy.sv',
    'lowrisc_ip_gpio_0.1/rtl/gpio_reg_pkg.sv',
    'lowrisc_ip_gpio_0.1/rtl/gpio.sv',
    'lowrisc_ip_gpio_0.1/rtl/gpio_reg_top.sv',
    'lowrisc_ip_hmac_0.1/rtl/hmac_pkg.sv',
    'lowrisc_ip_hmac_0.1/rtl/sha2.sv',
    'lowrisc_ip_hmac_0.1/rtl/sha2_pad.sv',
    'lowrisc_ip_hmac_0.1/rtl/hmac_reg_pkg.sv',
    'lowrisc_ip_hmac_0.1/rtl/hmac_reg_top.sv',
    'lowrisc_ip_hmac_0.1/rtl/hmac_core.sv',
    'lowrisc_ip_hmac_0.1/rtl/hmac.sv',
    'lowrisc_ip_nmi_gen_0.1/rtl/nmi_gen_reg_pkg.sv',
    'lowrisc_ip_nmi_gen_0.1/rtl/nmi_gen_reg_top.sv',
    'lowrisc_ip_nmi_gen_0.1/rtl/nmi_gen.sv',
    'lowrisc_ip_pinmux_component_0.1/rtl/pinmux.sv',
    'lowrisc_ip_rv_core_ibex_0.1/rtl/rv_core_ibex.sv',
    'lowrisc_ip_rv_dm_0.1/rtl/rv_dm.sv',
    'lowrisc_ip_rv_dm_0.1/rtl/tlul_adapter_host.sv',
    'lowrisc_ip_rv_plic_component_0.1/rtl/rv_plic_gateway.sv',
    'lowrisc_ip_rv_plic_component_0.1/rtl/rv_plic_target.sv',
    'lowrisc_ip_rv_timer_0.1/rtl/rv_timer_reg_pkg.sv',
    'lowrisc_ip_rv_timer_0.1/rtl/rv_timer_reg_top.sv',
    'lowrisc_ip_rv_timer_0.1/rtl/timer_core.sv',
    'lowrisc_ip_rv_timer_0.1/rtl/rv_timer.sv',
    'lowrisc_ip_spi_device_0.1/rtl/spi_device_reg_pkg.sv',
    'lowrisc_ip_spi_device_0.1/rtl/spi_device_reg_top.sv',
    'lowrisc_ip_spi_device_0.1/rtl/spi_device_pkg.sv',
    'lowrisc_ip_spi_device_0.1/rtl/spi_fwm_rxf_ctrl.sv',
    'lowrisc_ip_spi_device_0.1/rtl/spi_fwm_txf_ctrl.sv',
    'lowrisc_ip_spi_device_0.1/rtl/spi_fwmode.sv',
    'lowrisc_ip_spi_device_0.1/rtl/spi_device.sv',
    'lowrisc_ip_uart_0.1/rtl/uart_reg_pkg.sv',
    'lowrisc_ip_uart_0.1/rtl/uart_reg_top.sv',
    'lowrisc_ip_uart_0.1/rtl/uart_rx.sv',
    'lowrisc_ip_uart_0.1/rtl/uart_tx.sv',
    'lowrisc_ip_uart_0.1/rtl/uart_core.sv',
    'lowrisc_ip_uart_0.1/rtl/uart.sv',
    'lowrisc_ip_usbdev_0.1/rtl/usbdev_reg_pkg.sv',
    'lowrisc_ip_usbdev_0.1/rtl/usbdev_reg_top.sv',
    'lowrisc_ip_usbdev_0.1/rtl/usbdev_usbif.sv',
    'lowrisc_ip_usbdev_0.1/rtl/usbdev_flop_2syncpulse.sv',
    'lowrisc_ip_usbdev_0.1/rtl/usbdev_linkstate.sv',
    'lowrisc_ip_usbdev_0.1/rtl/usbdev_iomux.sv',
    'lowrisc_ip_usbdev_0.1/rtl/usbdev.sv',
    'lowrisc_ip_xbar_main_0.1/tl_main_pkg.sv',
    'lowrisc_ip_xbar_main_0.1/xbar_main.sv',
    'lowrisc_ip_xbar_peri_0.1/tl_peri_pkg.sv',
    'lowrisc_ip_xbar_peri_0.1/xbar_peri.sv',
    'lowrisc_top_earlgrey_rv_plic_0.1/rtl/autogen/rv_plic_reg_pkg.sv',
    'lowrisc_top_earlgrey_rv_plic_0.1/rtl/autogen/rv_plic_reg_top.sv',
    'lowrisc_top_earlgrey_rv_plic_0.1/rtl/autogen/rv_plic.sv',
    'lowrisc_systems_top_earlgrey_0.1/rtl/padctl.sv',
    'lowrisc_systems_top_earlgrey_0.1/rtl/autogen/top_earlgrey.sv',
    'lowrisc_systems_top_earlgrey_zcu104_0.1/rtl/clkgen_xilusp.sv',
    'lowrisc_systems_top_earlgrey_zcu104_0.1/rtl/top_earlgrey_zcu104.sv',
]

with open(post_imp_file, 'w') as f:
    f.write('write_checkpoint -force design.dcp')

files = [{
    'name':
    os.path.realpath(
        'lowrisc_systems_top_earlgrey_zcu104_0.1/data/pins_zcu104.xdc'),
    'file_type':
    'xdc'
},
         {
             'name':
             os.path.realpath('lowrisc_prim_assert_0.1/rtl/prim_assert.sv'),
             'file_type':
             'systemVerilogSource',
             'is_include_file':
             'true'
         }]

parameters = {
    'ROM_INIT_FILE': {
        'datatype': 'str',
        'paramtype': 'vlogdefine'
    },
    'PRIM_DEFAULT_IMPL': {
        'datatype': 'str',
        'paramtype': 'vlogdefine'
    },
}

for src in srcs:
    files.append({
        'name': os.path.realpath(src),
        'file_type': 'systemVerilogSource'
    })

tool = 'vivado'

incdirs = [os.path.realpath('lowrisc_prim_assert_0.1/rtl')]

edam = {
    'files': files,
    'name': 'design',
    'toplevel': 'top_earlgrey_zcu104',
    'parameters': parameters,
    'tool_options': {
        'vivado': {
            'part': os.environ['URAY_PART'],
            'post_imp': post_imp_file,
            'synth': synth_tool
        }
    }
}

backend = edalize.get_edatool(tool)(edam=edam, work_root=work_root)

args = [
    '--ROM_INIT_FILE={}'.format(
        os.path.realpath('boot_rom_fpga_nexysvideo.vmem')),
    '--PRIM_DEFAULT_IMPL=prim_pkg::ImplXilinx'
]

backend.configure(args)
backend.build()
