#!/bin/bash
#
# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

# Fix up things related to Xilinx tool chain.

ls -l ~/.Xilinx
sudo chown -R $USER ~/.Xilinx

export XILINX_LOCAL_USER_DATA=no

echo "========================================"
echo "Mounting image with Vivado 2019.2"
echo "----------------------------------------"
sudo mkdir -p /image
sudo mount UUID=aaa2471f-444f-4353-bdda-1822f48c0cd6 /image
export URAY_VIVADO_SETTINGS=/image/Xilinx/Vivado/2019.2/settings64.sh
