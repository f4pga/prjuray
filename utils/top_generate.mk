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

all: OK

OK: generate.ok
	touch OK

# Some projects have hard coded top.v, others are generated
top.v.ok:
	if [ -f ${FUZDIR}/top.py ] ; then export FUZDIR=${FUZDIR} && python3 ${FUZDIR}/top.py >top.v; fi
	touch top.v.ok

vivado.ok: top.v.ok ${FUZDIR}/generate.tcl
	${URAY_VIVADO} -mode batch -source ${FUZDIR}/generate.tcl
	test -z "$(fgrep CRITICAL vivado.log)"
	touch vivado.ok

design_bits.ok: vivado.ok
	\
        for x in design*.bit; do \
            ${URAY_BITREAD} -F ${URAY_ROI_FRAMES} -o $${x}s -z -y $$x ; \
			${URAY_BIT2FASM} --architecture ${URAY_ARCH} --verbose $$x > $${x%.*}.fasm; \
        done
	touch design_bits.ok

generate.ok: design_bits.ok
	if [ -f ${FUZDIR}/generate.py ] ; then python3 ${FUZDIR}/generate.py ${GENERATE_FLAGS}; else python3 ${URAY_DIR}/fuzzers/int_generate.py; fi
	touch generate.ok

