#!/bin/bash
#
# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
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
