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
import glob

work_root = 'build'

post_imp_file = os.path.realpath(os.path.join(work_root, 'post.tcl'))

os.makedirs(work_root, exist_ok=True)

synth_tool = 'yosys'

srcs = glob.glob("*.v")

with open(post_imp_file, 'w') as f:
    f.write('write_checkpoint -force design.dcp')

files = [{
    'name':
    os.path.realpath(
        '../src.vivado/lowrisc_systems_top_earlgrey_zcu104_0.1/data/pins_zcu104.xdc'
    ),
    'file_type':
    'xdc'
}]

parameters = {}

for src in srcs:
    files.append({'name': os.path.realpath(src), 'file_type': 'verilogSource'})

tool = 'vivado'

incdirs = {}

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

backend.configure("")
backend.build()
