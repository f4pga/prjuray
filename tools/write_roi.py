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

import sys
import json


def main():
    """ Usage: tilegrid.json """
    with open(sys.argv[1]) as tb_f:
        tbj = json.load(tb_f)
    tile_to_frames = {}
    frame_to_tiles = {}
    for tilename, tiledata in tbj.items():
        tn = tilename.split(":")[0]
        tile_to_frames[tn] = []
        for chunk in tiledata:
            frame, start, size = chunk
            tile_to_frames[tn].append(frame)
            if frame not in frame_to_tiles:
                frame_to_tiles[frame] = []
            frame_to_tiles[frame].append(tn)
    basis_tiles = [
        "CLEM_X41Y120", "INT_X41Y120", "CLEL_R_X41Y120", "BRAM_X42Y120",
        "INT_INTF_L_X42Y120", "INT_X42Y120", "CLEL_R_X42Y120", "CLEM_X43Y120",
        "INT_X43Y120", "INT_INTF_R_X43Y120", "DSP_X43Y120", "CLEM_X44Y120",
        "INT_X44Y120", "CLEL_R_X44Y120", "CLEM_X45Y120", "INT_X45Y120",
        "INT_INTF_R_X45Y120", "DSP_X45Y120", "CLEM_X46Y120", "INT_X46Y120",
        "CLEL_R_X46Y120", "INT_X47Y120", "CLEL_R_X47Y120"
    ]

    roi_frames = set()

    for tile in basis_tiles:
        if tile not in tile_to_frames:
            continue
        for frame in tile_to_frames[tile]:
            roi_frames.add(frame)

    roi_tiles = set()
    for frame in roi_frames:
        for tile in frame_to_tiles[frame]:
            roi_tiles.add(tile)

    with open(sys.argv[2], "w") as frames_f:
        for frame in sorted(roi_frames):
            print("0x%08x" % frame, file=frames_f)

    with open(sys.argv[3], "w") as tiles_f:
        for tile in sorted(roi_tiles):
            print("tile %s" % tile, file=tiles_f)


if __name__ == "__main__":
    main()
