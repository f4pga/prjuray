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
export URAY_DATABASE="zynqusp"
export URAY_PART="xczu7ev-ffvc1156-2-i"
export URAY_ARCH="UltraScalePlus"

export URAY_ROI_FRAMES="0x00000000:0xffffffff"

# All CLB's in part, all BRAM's in part, all DSP's in part.
export URAY_ROI_TILEGRID="SLICE_X42Y240:SLICE_X65Y299 RAMB18_X1Y96:RAMB18_X1Y119 RAMB36_X1Y48:RAMB36_X1Y59 DSP48E2_X3Y96:DSP48E2_X6Y119 URAM288_X0Y64:URAM288_X0Y79"

# These settings must remain in sync
export URAY_ROI="SLICE_X42Y240:SLICE_X65Y299 RAMB18_X1Y96:RAMB18_X1Y119 RAMB36_X1Y48:RAMB36_X1Y59 DSP48E2_X3Y96:DSP48E2_X6Y119 URAM288_X0Y64:URAM288_X0Y79"

# Most of CMT X0Y2.
export URAY_ROI_GRID_X1="148"
export URAY_ROI_GRID_X2="214"
# Include VBRK / VTERM
export URAY_ROI_GRID_Y1="63"
export URAY_ROI_GRID_Y2="123"

export URAY_PIN_00="C4"
export URAY_PIN_01="B4"
export URAY_PIN_02="E4"
export URAY_PIN_03="D4"

source $(dirname ${BASH_SOURCE[0]})/../utils/environment.sh
