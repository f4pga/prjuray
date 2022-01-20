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

pins = {
    'clk': os.environ['URAY_PIN_00'],
    'stb': os.environ['URAY_PIN_01'],
    'di': os.environ['URAY_PIN_02'],
    'do': os.environ['URAY_PIN_03'],
}

xdc_file = os.path.realpath(os.path.join(work_root, 'top.xdc'))
pre_imp_file = os.path.realpath(os.path.join(work_root, 'pre.tcl'))
post_imp_file = os.path.realpath(os.path.join(work_root, 'post.tcl'))

os.makedirs(work_root, exist_ok=True)

synth_tool = 'yosys' if 'USE_YOSYS' in os.environ else 'vivado'

with open(xdc_file, 'w') as f:
    f.write('set_property CLOCK_DEDICATED_ROUTE FALSE [get_nets *]\n')
    for key, val in pins.items():
        f.write('set_property PACKAGE_PIN {} [get_ports {}]\n'.format(
            val, key))
        f.write(
            'set_property IOSTANDARD LVCMOS33 [get_ports {}]\n'.format(key))

with open(pre_imp_file, 'w') as f:
    f.write('create_pblock roi\n')
    f.write('add_cells_to_pblock [get_pblocks roi] [get_cells roi]\n')
    f.write('resize_pblock [get_pblocks roi] -add "{}"\n'.format(
        os.environ['URAY_ROI']))
    f.write(
        'set_property BITSTREAM.GENERAL.PERFRAMECRC YES [current_design]\n')

with open(post_imp_file, 'w') as f:
    f.write('write_checkpoint -force design.dcp')

files = [
    {
        'name': os.path.realpath('top.v'),
        'file_type': 'verilogSource'
    },
    {
        'name': xdc_file,
        'file_type': 'xdc'
    },
]

tool = 'vivado'

edam = {
    'files': files,
    'name': 'design',
    'toplevel': 'top',
    'tool_options': {
        'vivado': {
            'part': os.environ['URAY_PART'],
            'pre_imp': pre_imp_file,
            'post_imp': post_imp_file,
            'synth': synth_tool
        }
    }
}

backend = edalize.get_edatool(tool)(edam=edam, work_root=work_root)

backend.configure("")
backend.build()
