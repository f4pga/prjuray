#!/usr/bin/env bash
# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

for x in $1/*.dump; do
	python bits_to_tiles.py $2 $x > ${x%.*}.tbits
done
