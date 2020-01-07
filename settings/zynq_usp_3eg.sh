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
export URAY_PART="xczu3eg-sfvc784-1-e"
export URAY_ARCH="UltraScalePlus"

export URAY_ROI_FRAMES="0x00000000:0xffffffff"

# All CLB's in part, all BRAM's in part, all DSP's in part.
export URAY_ROI_TILEGRID="SLICE_X0Y120:SLICE_X28Y179 DSP48E2_X0Y48:DSP48E2_X2Y71 RAMB18_X0Y70:RAMB18_X2Y71 RAMB36_X0Y24:RAMB36_X2Y35"

# These settings must remain in sync
export URAY_ROI="SLICE_X0Y120:SLICE_X28Y179 DSP48E2_X0Y48:DSP48E2_X2Y71 RAMB18_X0Y70:RAMB18_X2Y71 RAMB36_X0Y24:RAMB36_X2Y35"

# Most of CMT X0Y2.
export URAY_ROI_GRID_X1="159"
export URAY_ROI_GRID_X2="239"
# Include VBRK / VTERM
export URAY_ROI_GRID_Y1="0"
export URAY_ROI_GRID_Y2="62"

export URAY_PIN_00="E12"
export URAY_PIN_01="C12"
export URAY_PIN_02="D12"
export URAY_PIN_03="A11"

source $(dirname ${BASH_SOURCE[0]})/../utils/environment.sh
