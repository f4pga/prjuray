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
