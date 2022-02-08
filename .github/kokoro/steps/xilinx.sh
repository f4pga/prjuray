#!/bin/bash
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

# Fix up things related to Xilinx tool chain.

ls -l ~/.Xilinx
sudo chown -R $USER ~/.Xilinx

export XILINX_LOCAL_USER_DATA=no

if [[ ! -d /image/Xilinx ]]; then
	echo "========================================"
	echo "Mounting image with Vivado 2019.2"
	echo "----------------------------------------"
	sudo mkdir -p /image
	sudo mount UUID=aaa2471f-444f-4353-bdda-1822f48c0cd6 /image
else
	echo "========================================"
	echo "Xilinx image with Vivado 2019.2 mounted"
	echo "----------------------------------------"
fi
ls -l /image/
ls -l /image/Xilinx/Vivado/
export URAY_VIVADO_SETTINGS=/image/Xilinx/Vivado/2019.2/settings64.sh
ls -l $URAY_VIVADO_SETTINGS
echo "----------------------------------------"
