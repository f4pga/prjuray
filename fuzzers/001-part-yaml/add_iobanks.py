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
'''
Script for adding the IO Banks information to the Part's generated JSON.
'''
import argparse
import json


def main(argv):
    with open(args.part_json) as json_file, open(
            args.iobanks_info) as iobanks_info:
        part_data = json.load(json_file)
        json_file.close()
        iobank_data = dict()
        for iobank in iobanks_info:
            iobank = iobank.strip()
            bank, coordinates = iobank.split(",")
            iobank_data[bank] = coordinates
        iobanks_info.close()
        if len(iobank_data) > 0:
            part_data["iobanks"] = iobank_data
        print(json.dumps(part_data, indent=4))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--part_json', help='Input json')
    parser.add_argument('--iobanks_info', help='Input IO Banks info file')
    args = parser.parse_args()
    main(args)
