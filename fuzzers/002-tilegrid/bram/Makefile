# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

N ?= 12
ifeq (${URAY_DATABASE}, kintexus)
GENERATE_ARGS?=--oneval 1 --design params.csv --dword 2 --dframe 03
else
GENERATE_ARGS?=--oneval 1 --design params.csv --dword 3 --dframe 04
endif
include ../fuzzaddr/common.mk

