# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

ifeq (${URAY_DATABASE}, kintexus)
N ?= 48
SEGMATCH_ARGS?=-c 40
GENERATE_ARGS?=--oneval 0 --design params.csv --dword 1 --auto_frame --filter_frames 2D,2F
else
N ?= 20
GENERATE_ARGS?=--oneval 0 --design params.csv --dword 0 --dframe 48 --filter_words 45,46
endif
include ../fuzzaddr/common.mk

