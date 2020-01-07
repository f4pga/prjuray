# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

all: dump_bitstream correlate explain stripdb assemble

CXXFLAGS := -std=c++17 -O3 -g
LINK.o = $(LINK.cc)

%.o: common.h

dump_bitstream: dump_bitstream.o common.o

correlate: correlate.o

explain: explain.o common.o

stripdb: stripdb.o

assemble: assemble.o common.o

clean:
	rm *.o dump_bitstream correlate stripdb assemble
.PHONY: clean
