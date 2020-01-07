# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

ifeq (,$(shell which sv2v))
$(error "No sv2v in $(PATH), you need to install it first")
endif

SV_FILES=$(shell find ../src.vivado -name "*.sv")
V_FILES=$(foreach SV_FILE,$(SV_FILES),$(patsubst %.sv,%.v,$(notdir $(SV_FILE))))

all: yosys-vivado

define sv2v_conv =
$(1):
	sv2v.sh $(1) $(2)
endef

$(foreach SV_FILE,$(SV_FILES),$(eval $(call sv2v_conv,$(patsubst %.sv,%.v,$(notdir $(SV_FILE))),$(SV_FILE))))

yosys-vivado: sv2v
	python3 runme.py

sv2v: $(V_FILES)
	@true

clean:
	rm -rf *.v build
