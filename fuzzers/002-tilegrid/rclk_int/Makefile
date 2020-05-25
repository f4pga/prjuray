# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

ifeq (${URAY_DATABASE}, kintexus)
N ?= 12
SEGMATCH_ARGS?=-c 5
GENERATE_ARGS?=--oneval 1 --design params.csv --dword 1 --dframe 12 --filter_words 60
else
N ?= 10
SEGMATCH_ARGS?=-c 8
GENERATE_ARGS?=--oneval 1 --design params.csv --dword 0 --dframe 02
endif
include ../fuzzaddr/common.mk
