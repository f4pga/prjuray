#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
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

import os
import os.path
import numpy as np
from utils import util
from utils.verilog import top_harness_clk
from prjuray.db import Database


def gen_sites():
    db = Database(util.get_db_root(), util.get_part())
    grid = db.grid()
    for tile_name in sorted(grid.tiles()):
        loc = grid.loc_of_tilename(tile_name)
        gridinfo = grid.gridinfo_at_loc(loc)

        for site, site_type in gridinfo.sites.items():
            if site_type in ['SLICEM']:
                yield site


def emit_ultra_slice_memory(f, site, root_cell, modes, dimuxes):
    ram = modes[-1].startswith('RAM')

    # First unplace all elements
    print('set site [get_sites {}]'.format(site), file=f)
    print('unplace_cell [get_cells -of $site]', file=f)
    print('', file=f)

    def loc_cell(name, c, leaf, lut):
        bel = '{c}{lut}LUT'.format(c=c.upper(), lut=lut)
        print(
            'set {name} [get_cells {root_cell}/{c}lut_i/{leaf}]'.format(
                root_cell=root_cell, name=name, c=c, leaf=leaf),
            file=f)
        print(
            'set_property BEL {bel} ${name}'.format(bel=bel, name=name),
            file=f)
        print(
            'set_property LOC {site} ${name}'.format(site=site, name=name),
            file=f)
        print('', file=f)

    if ram:
        for c, mode, dimux in zip('hgfedcba', modes[::-1], dimuxes[::-1]):
            if mode in ['RAMD64', 'RAMS64']:
                loc_cell('ram', c, 'ram_i', lut='6')
            elif mode in ['RAMD32', 'RAMS32']:
                loc_cell('ram1', c, 'ram1_i', lut='6')
                loc_cell('ram0', c, 'ram0_i', lut='5')
            elif mode == 'LOGIC':
                loc_cell('lut6', c, 'lut6', lut='6')
                loc_cell('lut5', c, 'lut5', lut='5')
            else:
                assert False, mode
    else:
        for c, mode, dimux in zip('abcdefgh', modes, dimuxes):
            if mode == 'LOGIC':
                loc_cell('lut6', c, 'lut6', lut='6')
                loc_cell('lut5', c, 'lut5', lut='5')
            elif mode == 'SRL16':
                loc_cell('srl6', c, 'srl6', lut='6')
                loc_cell('srl5', c, 'srl5', lut='5')
            elif mode == 'SRL32':
                loc_cell('srl6', c, 'srl6', lut='6')
            else:
                assert False, mode


def print_top(seed):
    np.random.seed(seed)
    DCLK_N = 10
    DIN_N = (16 * 2 + 8)
    DOUT_N = 32
    top_harness_clk(DCLK_N, DIN_N, DOUT_N)

    print("")
    print("""
        module roi(input [{DCLK_N}-1:0] clk, input [{DIN_N}-1:0] din, output [31:0] dout);

        wire [15:0] sr;
        wire [15:0] ce;
        wire [7:0] d;
        wire [31:0] q;

        assign sr = din[0+:16];
        assign ce = din[16+:16];
        assign d = din[32+:8];

        assign dout = q;
        """.format(DCLK_N=DCLK_N, DIN_N=DIN_N, DOUT_N=DOUT_N))

    N = 150
    D = ["d[%d]" % i for i in range(8)]

    slices = sorted(gen_sites())

    np.random.shuffle(slices)

    with open('top.tcl', 'w') as f:
        for i in range(N):
            sl = slices.pop()
            clk = tuple(np.random.randint(DCLK_N, size=2))
            wclk = None
            while wclk is None or wclk in clk:
                wclk = np.random.randint(DCLK_N)
            sr = tuple([
                "1'b1" if y >= 16 else "sr[%d]" % y
                for y in np.random.randint(25, size=2)
            ])
            ce = tuple([
                "1'b1" if y >= 16 else "ce[%d]" % y
                for y in np.random.randint(25, size=4)
            ])
            we = np.random.randint(16)

            def random_fftype(mode):
                if mode == 0:
                    return np.random.choice(["NONE", "FDSE", "FDRE"])
                elif mode == 1:
                    return np.random.choice(["NONE", "FDPE", "FDCE"])
                elif mode == 2:
                    return np.random.choice(["NONE", "LDPE", "LDCE"])

            def random_bit():
                return np.random.choice(D)

            def random_data(width):
                return "{%s}" % (", ".join(
                    [random_bit() for k in range(width)]))

            #fftypes = [random_fftype(ffmode[j // 8]) for j in range(16)]
            fftypes = ["NONE" for j in range(16)]

            dimux = []
            mode = []
            ram_legal = True
            for lut in "HGFEDCBA":
                choices = ["LOGIC"]
                if len(dimux) >= 2 and dimux[1] == 'SIN':
                    mode.append("SRL32")
                    dimux.append("SIN")
                    continue

                if lut == "H":
                    choices += ["RAMD64", "RAMS64", "RAMD32", "SRL16", "SRL32"]
                else:
                    if mode[0][0:3] != "RAM":
                        choices += ["SRL16", "SRL32"]
                    if ram_legal:
                        choices.append(mode[0])
                p = [0.1]
                for j in range(1, len(choices)):
                    p.append(0.9 / (len(choices) - 1))
                if len(choices) == 1:
                    p[0] = 1
                next_mode = np.random.choice(choices, p=p)
                if len(mode
                       ) > 0 and mode[-1] == "SRL32" and next_mode == "SRL32":
                    dimux.append(np.random.choice(["DI", "SIN"], p=[0.2, 0.8]))
                else:
                    dimux.append("DI")
                if next_mode[0:3] != "RAM":
                    ram_legal = False
                mode.append(next_mode)

            dimux = list(reversed(dimux))
            mode = list(reversed(mode))

            emit_ultra_slice_memory(f, sl, 'roi/slice{}'.format(i), mode,
                                    dimux)

            print('   wire [31:0] d%d;' % i)
            print('   ultra_slice_memory #(')
            print('      .LOC("%s"),' % sl)
            for j in range(8):
                print('      .%s_MODE("%s"),' % ("ABCDEFGH" [j], mode[j]))
            for lut in "ABCDEFGH":
                print("      .%sLUT_INIT(64'b%s)," % (lut, "".join(
                    str(_) for _ in np.random.randint(2, size=64))))
            for j in range(16):
                print('      .%sFF%s_TYPE("%s"),' %
                      ("ABCDEFGH" [j // 2], "2" if
                       (j % 2) == 1 else "", fftypes[j]))
            print("      .FF_INIT(16'b%s)," % "".join(
                str(_) for _ in np.random.randint(2, size=16)))
            for j1 in "ABCDEFGH":
                for j2 in ("1", "2"):
                    print('        .FFMUX%s%s("%s"),' %
                          (j1, j2, np.random.choice(["F7F8", "D6", "D5"])))
            for j in "ABCDEFGH":
                print('        .OUTMUX%s("%s"),' %
                      (j, np.random.choice(["F7F8", "D6", "D5"])))
            for j in range(7):
                print('      .DIMUX%s("%s"),' % ("ABCDEFG" [j], dimux[j]))
            print("      .WCLKINV(1'd%d)," % np.random.randint(2))

            waused = np.random.randint(4)

            print("      .WA6USED(1'd%d)," % (1 if waused > 0 else 0))
            print("      .WA7USED(1'd%d)," % (1 if waused > 1 else 0))
            print("      .WA8USED(1'd%d)," % (1 if waused > 2 else 0))
            print("      .CLKINV(2'd%d)," % np.random.randint(4))
            print("      .SRINV(2'd%d)" % np.random.randint(4))
            print('   ) slice%d (' % i)
            for j in range(1, 7):
                print("      .A%d(%s)," % (j, random_data(8)))
            print("      .I(%s)," % random_data(8))
            print("      .X(%s)," % random_data(8))
            print("      .CLK({clk[%d], clk[%d]})," % clk[0:2])
            print("      .WCLK(clk[%d])," % wclk)
            print("      .SR({%s, %s})," % sr)
            print("      .CE({%s, %s, %s, %s})," % ce[0:4])
            print("      .WE(ce[%d])," % we)
            print("      .O(d%d[7:0])," % i)
            print("      .Q(d%d[15:8])," % i)
            print("      .Q2(d%d[23:16])," % i)
            print("      .MUX(d%d[31:24])" % i)
            print('   );')
            print()
            D.clear()
            for j in range(8):
                D.append("d%d[%d]" % (i, j))
                D.append("d%d[%d]" % (i, 24 + j))
                if fftypes[2 * j] != "NONE":
                    D.append("d%d[%d]" % (i, 8 + j))
                if fftypes[2 * j + 1] != "NONE":
                    D.append("d%d[%d]" % (i, 16 + j))
        print("    assign q = d%d;" % (N - 1))
        print("endmodule")

    with open(os.path.join(os.getenv('URAY_DIR'), 'spec',
                           'slice_memory.v')) as f:
        for l in f:
            print(l.rstrip())
