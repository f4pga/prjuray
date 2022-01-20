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


class LutMaker(object):
    def __init__(self):
        self.input_lut_idx = 0
        self.output_lut_idx = 0
        self.lut_input_idx = 0

    def get_next_input_net(self):
        net = 'lut_{}_i[{}]'.format(self.input_lut_idx, self.lut_input_idx)

        self.lut_input_idx += 1
        if self.lut_input_idx > 5:
            self.lut_input_idx = 0
            self.input_lut_idx += 1

        return net

    def get_next_output_net(self):
        net = 'lut_{}_o'.format(self.output_lut_idx)
        self.output_lut_idx += 1
        return net

    def create_wires_and_luts(self):
        if self.output_lut_idx > self.input_lut_idx:
            nluts = self.output_lut_idx
        else:
            nluts = self.input_lut_idx
            if self.lut_input_idx > 0:
                nluts += 1

        for lut in range(nluts):
            yield """
            wire [5:0] lut_{lut}_i;
            wire lut_{lut}_o;

            (* KEEP, DONT_TOUCH *)
            LUT6 lut_{lut} (
                .I0(lut_{lut}_i[0]),
                .I1(lut_{lut}_i[1]),
                .I2(lut_{lut}_i[2]),
                .I3(lut_{lut}_i[3]),
                .I4(lut_{lut}_i[4]),
                .I5(lut_{lut}_i[5]),
                .O(lut_{lut}_o)
            );
            """.format(lut=lut)
