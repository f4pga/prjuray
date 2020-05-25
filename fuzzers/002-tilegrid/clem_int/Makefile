# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

ifeq (${URAY_DATABASE}, kintexus)
N ?= 24
SEGMATCH_ARGS?=-c 5
GENERATE_ARGS?=--oneval 0 --design params.csv --dword 1 --auto_frame --filter_word 60,61
else
N ?= 15
GENERATE_ARGS?=--oneval 0 --design params.csv --dword 1 --dframe 0A --filter_word 45,46
endif
include ../fuzzaddr/common.mk

