# Copyright (C) 2020-2021  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

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

