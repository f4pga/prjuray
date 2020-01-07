#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

import edalize
import os

work_root = 'build'

post_imp_file = os.path.realpath(os.path.join(work_root, 'post.tcl'))

os.makedirs(work_root, exist_ok=True)

synth_tool = 'yosys' if 'USE_YOSYS' in os.environ else 'vivado'

with open(post_imp_file, 'w') as f:
    f.write('write_checkpoint -force design.dcp')

files = [
    {
        'name': os.path.realpath('top.v'),
        'file_type': 'verilogSource'
    },
    {
        'name': os.path.realpath('VexRiscv_Linux.v'),
        'file_type': 'verilogSource'
    },
    {
        'name': os.path.realpath('top.xdc'),
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
            'post_imp': post_imp_file,
            'synth': synth_tool
        }
    }
}

backend = edalize.get_edatool(tool)(edam=edam, work_root=work_root)

backend.configure("")
backend.build()
