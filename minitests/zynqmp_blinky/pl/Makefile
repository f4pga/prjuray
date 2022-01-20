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

URAY_PART=xczu3eg-sbva484-1-e

.PHONY: clean all
.PRECIOUS: top.bit top_out.bit top.fasm top_out.fasm

all: top.bit

%.bit: %.v
	mkdir -p build-$(basename $@)
	cd build-$(basename $@) && \
		env PROJECT_NAME=$(basename $@) URAY_PART=${URAY_PART} \
		$(URAY_VIVADO) -mode batch -source ../syn+par.tcl -nojournal -log ../$@.log
	rm -rf *.backup.log

%.fasm: %.bit
	env URAY_PART=${URAY_PART} \
		$(URAY_BIT2FASM) \
		--bits-file $<s \
		--suppress_zero_features --verbose $< > $@ || rm -rf $@

%_out.frames: %.fasm
	$(URAY_FASM2FRAMES) $< > $@ || rm -rf $@

%_out.bits: %.fasm
	$(URAY_FASM2FRAMES) --dump_bits $< > $@ || rm -rf $@

%_out.bit: %.fasm
	env URAY_PART=${URAY_PART} \
		$(URAY_FASM2BIT) \
			--bits-file $@.bits \
			--frames-file $@.frames \
			$< $@ || rm -rf $@

%_out.fasm: %_out.bit
	env URAY_PART=${URAY_PART} \
		$(URAY_BIT2FASM) \
		--bits-file $<s \
		--suppress_zero_features --verbose $< > $@ || rm -rf $@

clean:
	rm -rf *.fasm
	rm -rf *.bit
	rm -rf *.bits
	rm -rf *.dcp
	rm -rf *.log
	rm -rf *.jou
	rm -rf build-*
