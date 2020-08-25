#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2020  The Project U-Ray Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC

import json
import util as localutil
import os

if os.getenv('URAY_ARCH') == 'UltraScale':
    BITS_PER_WORD = 32
else:
    BITS_PER_WORD = 16


def check_frames(tagstr, addrlist):
    frames = set()
    for addrstr in addrlist:
        frame = parse_addr(addrstr, get_base_frame=True)
        frames.add(frame)
    assert len(frames) == 1, ("{}: More than one base address".format(tagstr),
                              map(hex, frames))


def parse_addr(line, only_frame=False, get_base_frame=False):
    # 00020027_003_03
    line = line.split("_")
    frame = int(line[0], 16)
    wordidx = int(line[1], 10) * (32 / BITS_PER_WORD) + int(
        line[2], 10) // BITS_PER_WORD
    bitidx = int(line[2], 10) % BITS_PER_WORD

    if get_base_frame:
        delta = frame % 128
        frame -= delta
        return frame

    return frame, wordidx, bitidx


def load_db(fn):
    for l in open(fn, "r"):
        l = l.strip()
        # FIXME: add offset to name
        # IOB_X0Y101.DFRAME:27.DWORD:3.DBIT:3 00020027_003_03
        parts = l.split(' ')
        tagstr = parts[0]
        addrlist = parts[1:]
        check_frames(tagstr, addrlist)
        # Take the first address in the list
        frame, wordidx, bitidx = parse_addr(addrlist[0])

        bitidx_up = False

        tparts = tagstr.split('.')
        tile = tparts[0]
        for part in tparts[1:]:
            # Auto align the frame address to the next lowest multiple of 0x100.
            if part == 'AUTO_FRAME':
                frame -= (frame % (
                    0x80 if os.getenv('URAY_ARCH') == 'UltraScale' else 0x100))
                continue

            k, v = part.split(':')
            if k == "DFRAME":
                frame -= int(v, 16)
            elif k == "DWORD":
                wordidx -= int(v, 10)
            elif k == "DBIT":
                bitidx -= int(v, 10)
                bitidx_up = True
            else:
                assert 0, (l, part)

        # XXX: maybe just ignore bitidx and always set to 0 instead of allowing explicit
        # or detect the first delta auto and assert they are all the same
        if not bitidx_up:
            bitidx = 0
        assert bitidx == 0, l
        assert frame % (0x80 if os.getenv('URAY_ARCH') == 'UltraScale' else
                        0x100) == 0, "Unaligned frame at 0x%08X" % frame
        yield (tile, frame, wordidx)


def run(fn_in, fn_out, verbose=False):
    database = json.load(open(fn_in, "r"))
    cle_frames, cle_words = localutil.get_entry('CLE', 'CLB_IO_CLK')
    int_frames, int_words = localutil.get_entry('INT', 'CLB_IO_CLK')
    rclk_frames, rclk_words = localutil.get_entry('RCLK_INT_L', 'CLB_IO_CLK')
    xiphy_frames, xiphy_words = localutil.get_entry("XIPHY", "CLB_IO_CLK")
    bram_frames, bram_words = localutil.get_entry('BRAM', 'CLB_IO_CLK')
    bram_block_frames, bram_block_words = localutil.get_entry(
        'BRAM', 'BRAM_BLOCK')
    if os.getenv('URAY_ARCH') == 'UltraScalePlus':
        ps8_intf_frames, ps8_intf_words = localutil.get_entry(
            "PS8_INTF", "CLB_IO_CLK")

    build_dir = "build_" + os.getenv('URAY_PART')
    tdb_fns = [
        ("cle/" + build_dir + "/segbits_tilegrid.tdb", cle_frames, cle_words),
        ("clem_r/" + build_dir + "/segbits_tilegrid.tdb", cle_frames,
         cle_words),
        ("clel_int/" + build_dir + "/segbits_tilegrid.tdb", int_frames,
         int_words),
        ("clem_int/" + build_dir + "/segbits_tilegrid.tdb", int_frames,
         int_words),
        ("rclk_int/" + build_dir + "/segbits_tilegrid.tdb", rclk_frames,
         rclk_words),
        ("bram/" + build_dir + "/segbits_tilegrid.tdb", bram_frames,
         bram_words),
        ("bram_block/" + build_dir + "/segbits_tilegrid.tdb",
         bram_block_frames, bram_block_words),
    ]
    if os.getenv('URAY_ARCH') == 'UltraScalePlus':
        tdb_fns += [
            ("rclk_other/" + build_dir + "/segbits_tilegrid.tdb", rclk_frames,
             rclk_words),
            ("rclk_hdio/" + build_dir + "/segbits_tilegrid.tdb", rclk_frames,
             rclk_words),
            ("rclk_dsp_intf_clkbuf/" + build_dir + "/segbits_tilegrid.tdb",
             rclk_frames, rclk_words),
            ("rclk_pss_alto/" + build_dir + "/segbits_tilegrid.tdb",
             rclk_frames, rclk_words),
            ("intf_r_pcie4_hdio/" + build_dir + "/segbits_tilegrid.tdb", 36,
             3),
            ("ps8_intf/" + build_dir + "/segbits_tilegrid.tdb",
             ps8_intf_frames, ps8_intf_words),
            ("cmt_right/" + build_dir + "/segbits_tilegrid.tdb", 36, 10),
            ("pss_alto/" + build_dir + "/segbits_tilegrid.tdb", 36, 93 * 2),
            ("hdio_top_right/" + build_dir + "/segbits_tilegrid.tdb", 76, 93),
            ("hdio_bot_right/" + build_dir + "/segbits_tilegrid.tdb", 76, 93),
            ("hpio_right/" + build_dir + "/segbits_tilegrid.tdb", 76, 85),
            ("bitslice_tiles/" + build_dir + "/segbits_tilegrid.tdb",
             xiphy_frames, xiphy_words),
        ]

    tile_frames_map = localutil.TileFrames()
    for (tdb_fn, frames, words) in tdb_fns:
        if not os.path.exists(tdb_fn):
            verbose and print('Skipping {}, file not found!'.format(tdb_fn))
            continue
        for (tile, frame, wordidx) in load_db(tdb_fn):
            tilej = database[tile]
            verbose and print("Add %s %08X_%03u" % (tile, frame, wordidx))
            localutil.add_tile_bits(tile, tilej, frame, wordidx, frames, words,
                                    tile_frames_map)

    # Save
    json.dump(
        database,
        open(fn_out, "w"),
        sort_keys=True,
        indent=4,
        separators=(",", ": "))


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Annotate tilegrid addresses using solved base addresses")
    parser.add_argument("--verbose", action="store_true", help="")
    parser.add_argument("--fn-in", required=True, help="")
    parser.add_argument("--fn-out", required=True, help="")
    args = parser.parse_args()

    run(args.fn_in, args.fn_out, verbose=args.verbose)


if __name__ == "__main__":
    main()
