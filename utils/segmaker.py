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
'''
NOTE: "segments" as used in this file is mostly unrelated to tilegrid.json usage
ie tilegrid.json has names like SEG_CLBLL_L_X2Y50 where as here they are tile based and named like seg_00400100_02
Instead of using tilegrid.json "segments, segments are formed by looking for tiles that use the same address + offset

Sample segdata.txt output (from 015-clbnffmux/specimen_001/segdata_clbll_r.txt):
seg 00020880_048
bit 30_00
bit 31_49
tag CLB.SLICE.AFF.DMUX.CY 1
tag CLB.SLICE.BFF.DMUX.BX 0

tilegrid.json provides tile addresses
'''

import os, json, re
from utils import util

BLOCK_TYPES = set(('CLB_IO_CLK', 'BLOCK_RAM', 'CFG_CLB'))


def recurse_sum(x):
    '''Count number of nested iterable occurances'''
    if type(x) in (str, bytearray):
        return 1
    if type(x) in (dict, ):
        return sum([recurse_sum(y) for y in x.values()])
    else:
        try:
            return sum([recurse_sum(y) for y in x])
        except TypeError:
            return 1


def json_hex2i(s):
    '''Convert a JSON hex literal into an integer (it can't store hex natively)'''
    # TODO: maybe just do int(x, 0)
    return int(s[2:], 16)


def add_site_group_zero(segmk, site, prefix, vals, zero_val, val):
    '''
    Correctly add tags for a multi-bit enumerated value
    Naively adding them directly doesn't work correctly because overlapping bits won't solve correctly
    Instead, you need to carefully diff against a known zero value
    Good zero values:
    -An enum known to be zero
    -A site that doesn't contain the enum

    segmak: Segmaker object
    site: the site to add tags to
    prefix: tag string to prefix onto vals
    vals: all possible tag enum vals
    zero_val: tag value known to have no bits set
    '''
    # assert zero_val in vals, "Got %s, need %s" % (zero_val, vals)
    assert val in vals or val == zero_val, "Got %s, need %s" % (val, vals)

    if val == zero_val:
        # Zero symbol occured, none of the others did
        for aval in vals:
            tag = prefix + aval
            segmk.add_site_tag(site, tag, aval == val)
    else:
        # Only add the occured symbol
        tag = prefix + val
        segmk.add_site_tag(site, tag, True)
        if zero_val in vals:
            # And zero so that it has something to solve against
            tag = prefix + zero_val
            segmk.add_site_tag(site, tag, False)


class Segmaker:
    def __init__(self,
                 bitsfile,
                 verbose=False,
                 db_root=None,
                 part=None,
                 bits_per_word=32):
        self.db_root = db_root
        if self.db_root is None:
            self.db_root = util.get_db_root()

        self.part = part
        if self.part is None:
            self.part = util.get_part()
            assert self.part, "No part specified."

        self.verbose = verbose if verbose is not None else os.getenv(
            'VERBOSE', 'N') == 'Y'
        self.bits_per_word = bits_per_word
        self.load_grid()
        self.load_bits(bitsfile)
        '''
        self.tags[site][name] = value
        Where:
        -site: ex 'SLICE_X13Y101'
        -name: ex 'CLB.SLICE_X0.AFF.DMUX.CY'
        '''
        self.site_tags = dict()
        self.tile_tags = dict()

        # output after compiling
        self.segments_by_type = None

        # hacky...improve if we encounter this more
        self.def_bt = 'CLB_IO_CLK'
        self.index_sites()

    def index_sites(self):
        self.verbose and print("Indexing sites")
        self.sites = {}
        for tilename, tiledata in self.grid.items():
            for site in tiledata["sites"]:
                self.sites[site] = tilename
        self.verbose and print("Sites indexed")

    def set_def_bt(self, block_type):
        '''Set default block type when more than one block present'''
        assert block_type in BLOCK_TYPES, (
            "Unknown block type %r (known %r)" % (block_type, BLOCK_TYPES))
        self.def_bt = block_type

    def load_grid(self):
        '''Load self.grid holding tile addresses'''
        with open(os.path.join(self.db_root, self.part, "tilegrid.json"),
                  "r") as f:
            self.grid = json.load(f)
        assert "segments" not in self.grid, "Old format tilegrid.json"

    def load_bits(self, bitsfile):
        '''Load self.bits holding the bits that occured in the bitstream'''
        '''
        Format:
        self.bits[base_frame][bit_wordidx] = set()
        Where elements are (bit_frame, bit_wordidx, bit_bitidx))
        bit_frame is a relatively large number forming the FDRI address
        base_frame is a truncated bit_frame address of related FDRI addresses
        0 <= bit_wordidx <= 100
        0 <= bit_bitidx < 31

        Sample bits input
        bit_00020500_000_08
        bit_00020500_000_14
        bit_00020500_000_17
        '''
        self.bits = dict()
        print("Loading bits from %s." % bitsfile)
        with open(bitsfile, "r") as f:
            for line in f:
                # ex: bit_00020500_000_17
                line = line.split("_")
                bit_frame = int(line[1], 16)
                # Word indexes in the .bits file for US+/US assume 32-bits per word
                bit_wordidx = int(line[2],
                                  10) * (32 / self.bits_per_word) + int(
                                      line[3], 10) // self.bits_per_word
                bit_bitidx = int(line[3], 10) % self.bits_per_word
                # Bit ranges in the Frame Address Register Description differs between US+ and US devices
                # For US the ranges are identical to 7-series, but US+ is shifted 1 bit left
                # Refer to UG570 Table 9-21
                base_frame = bit_frame & (~0xff if os.getenv("URAY_ARCH") in
                                          "UltraScalePlus" else ~0x7f)
                self.bits.setdefault(base_frame, dict()).setdefault(
                    bit_wordidx, set()).add((bit_frame, bit_wordidx,
                                             bit_bitidx))
        if self.verbose:
            print('Loaded bits: %u bits in %u base frames' % (recurse_sum(
                self.bits), len(self.bits)))

    def add_site_tag(self, site, name, value):
        '''
        XXX: can add tags in two ways:
        -By site name
        -By tile name (used for pips?)
        Consider splitting into two separate data structures

        Record, according to value, if (site, name) exists

        Ex:
        self.addtag('SLICE_X13Y101', 'CLB.SLICE_X0.AFF.DMUX.CY', 1)
        Indicates that the SLICE_X13Y101 site has an element called 'CLB.SLICE_X0.AFF.DMUX.CY'
        '''
        if '"' in site:
            raise ValueError("Invalid site: %s" % site)
        self.verbose and print(
            'segmaker add tag: site %s tag %s = %s' % (site, name, value))
        assert site in self.sites, "Unknown site %s" % (site, )
        self.site_tags.setdefault(site, dict())[name] = value

    def add_tile_tag(self, tile, name, value):
        # TODO: test this out
        # assert tile in self.grid
        self.verbose and print(
            'segmaker add tag: tile %s tag %s = %s' % (tile, name, value))
        self.tile_tags.setdefault(tile, dict())[name] = value

    def compile(self, bitfilter=None):
        print("Compiling segment data.")
        tags_used = set()
        sites_used = set()
        tile_types_found = set()

        self.segments_by_type = dict()

        def add_segbits(segments, segname, tilename, tiledata, bitfilter=None):
            '''
            Add and populate segments[segname]["bits"]
            Gives all of the bits that could exist for the space we are exploring
            Also add segments[segname]["tags"], but don't fill

            segments is a group related to a specific tile type (ex: CLBLM_L)
            It is composed of bits (possible bits) and tags (observed instances)
            segments[segname]["bits"].add(bitname)
            segments[segname]["tags"][tag] = value

            segname: FDRI address + word offset string
            tiledata: tilegrid info for this tile
            '''
            assert segname not in segments
            segment = segments.setdefault(
                segname,
                {
                    "bits": set(),
                    "tags": dict(),
                    'name': tilename,
                    'tile_type_norm': tile_type_norm,
                    # verify new entries match this
                    "offset": bitj["offset"],
                    "words": bitj["words"],
                    "frames": bitj["frames"],
                })

            base_frame = json_hex2i(bitj["baseaddr"])
            for wordidx in range(bitj["offset"],
                                 bitj["offset"] + bitj["words"]):
                if base_frame not in self.bits:
                    continue
                if wordidx not in self.bits[base_frame]:
                    continue
                for bit_frame, bit_wordidx, bit_bitidx in self.bits[
                        base_frame][wordidx]:
                    bitname_frame = bit_frame - base_frame
                    bitname_bit = self.bits_per_word * (
                        bit_wordidx - bitj["offset"]) + bit_bitidx

                    # Skip bits above the frame limit.
                    if bitname_frame >= bitj["frames"]:
                        continue

                    # some bits are hard to de-correlate
                    # allow force dropping some bits from search space for practicality
                    if bitfilter is None or bitfilter(bitname_frame,
                                                      bitname_bit):
                        bitname = "%02d_%02d" % (bitname_frame, bitname_bit)
                        segment["bits"].add(bitname)

            return segment

        '''
        XXX: wouldn't it be better to iterate over tags? Easy to drop tags
        For now, add a check that all tags are used
        '''
        for tilename, tiledata in self.grid.items():

            def getseg(segname):
                if not segname in segments:
                    return add_segbits(
                        segments,
                        segname,
                        tilename,
                        tiledata,
                        bitfilter=bitfilter)
                else:
                    segment = segments[segname]
                    assert segment["offset"] == bitj["offset"]
                    assert segment["words"] == bitj["words"]
                    assert segment["frames"] == bitj["frames"]
                    return segment

            def add_tilename_tags():
                self.verbose and print("Tile %s: check tags" % tilename)
                segment = getseg(segname)

                for name, value in self.tile_tags[tilename].items():
                    tags_used.add((tilename, name))
                    tag = "%s.%s" % (tile_type_norm, name)
                    segment["tags"][tag] = value

            def add_site_tags():
                site_prefix = site.split('_')[0]

                def name_slice():
                    '''
                    Simplify SLICE names like:
                    -SLICE_X12Y102 => SLICE
                    '''
                    if re.match(r"SLICE_X[0-9]*[0123456789]Y", site):
                        return "SLICE"
                    else:
                        assert False, "Invalid name in %s" % site

                def name_bram18():
                    # RAMB18_X0Y41
                    if re.match(r"^RAMB18_X.*Y[0-9]*[02468]$", site):
                        return "RAMB18_Y0"
                    elif re.match(r"^RAMB18_X.*Y[0-9]*[13579]$", site):
                        return "RAMB18_Y1"
                    else:
                        assert False, "Invalid name in %s" % site

                def name_y0y1():
                    # RAMB18_X0Y41
                    m = re.match(r"^(.*)_X.*Y[0-9]*[02468]$", site)
                    if m:
                        return "%s_Y0" % m.group(1)

                    m = re.match(r"^(.*)_X.*Y[0-9]*[13579]$", site)
                    if m:
                        return "%s_Y1" % m.group(1)

                    assert 0, site

                def name_default():
                    # most sites are unique within their tile
                    # TODO: maybe verify against DB?
                    return site_prefix

                sitekey = {
                    'SLICE': name_slice,
                    'RAMB18': name_bram18,
                    'IOB': name_y0y1,
                    'IDELAY': name_y0y1,
                    'ILOGIC': name_y0y1,
                    'OLOGIC': name_y0y1,
                }.get(site_prefix, name_default)()
                self.verbose and print('site %s w/ %s prefix => tag %s' %
                                       (site, site_prefix, sitekey))

                for name, value in self.site_tags[site].items():
                    self.verbose and print("Site %s: check tags" % site)

                    tags_used.add((site, name))
                    tag = "%s.%s.%s" % (tile_type_norm, sitekey, name)
                    # XXX: does this come from name?
                    tag = tag.replace(".SLICEM.", ".")
                    tag = tag.replace(".SLICEL.", ".")
                    segment = getseg(segname)
                    segment["tags"][tag] = value
                sites_used.add(site)

            tile_type = tiledata["type"]
            tile_types_found.add(tile_type)
            segments = self.segments_by_type.setdefault(tile_type, dict())

            tile_type_norm = tile_type
            if tile_type_norm in ['CLEL_L', 'CLEL_R', 'CLEM', 'CLEM_R']:
                tile_type_norm = 'CLE'

            if tile_type_norm in ['RCLK_INT_L', 'RCLK_INT_R']:
                tile_type_norm = 'RCLK_INT'

            if tile_type_norm in [
                    'RCLK_CLEL_L_L', 'RCLK_CLEM_R', 'RCLK_CLEM_L'
            ]:
                tile_type_norm = 'RCLK_CLE'

            if tile_type_norm in [
                    'RCLK_BRAM_INTF_L', 'RCLK_BRAM_INTF_TD_L',
                    'RCLK_BRAM_INTF_TD_R'
            ]:
                tile_type_norm = 'RCLK_BRAM_INTF'

            if tile_type_norm in ['RCLK_DSP_INTF_L', 'RCLK_DSP_INTF_R']:
                tile_type_norm = 'RCLK_DSP_INTF'

            # ignore dummy tiles (ex: VBRK)
            if len(tiledata['bits']) == 0:
                if self.verbose:
                    for site in tiledata["sites"]:
                        assert site not in self.site_tags, "Site %s does not have bitstream info" % site
                this_tile_tags = len(self.tile_tags.get(tilename, {}))
                assert this_tile_tags == 0, "Tile %s does not have bitstream info but %s tags" % (
                    tilename, this_tile_tags)
                continue
            elif len(tiledata['bits']) == 1:
                bitj = list(tiledata['bits'].values())[0]
            else:
                assert self.def_bt in tiledata[
                    'bits'], 'Default block not present: %s' % self.def_bt
                bitj = tiledata['bits'][self.def_bt]

            # NOTE: multiple tiles may have the same base addr + offset
            segname = "%s_%03d" % (
                # truncate 0x to leave hex string
                bitj["baseaddr"][2:],
                bitj["offset"])

            # process tile name tags
            if tilename in self.tile_tags:
                add_tilename_tags()

            # process site name tags
            for site in tiledata["sites"]:
                if site not in self.site_tags:
                    continue
                add_site_tags()

        n_site_tags = recurse_sum(self.site_tags)
        n_tile_tags = recurse_sum(self.tile_tags)
        ntags = n_site_tags + n_tile_tags
        if self.verbose:
            assert ntags, "No tags"
            print("Used %u / %u tags" % (len(tags_used), ntags))
            print("Tag sites: %u" % (n_site_tags, ))
            if n_site_tags:
                print('  Ex: %s' % list(self.site_tags.keys())[0])
            print("Tag tiles: %u" % (n_tile_tags, ))
            print("Used %u sites" % len(sites_used))
            print("Grid DB had %u tile types" % len(tile_types_found))
        assert ntags == len(tags_used), "Unused tags, %s used out of %s" % (
            len(tags_used), ntags)

    def write(self, suffix=None, roi=False, allow_empty=False,
              extra_tags=None):
        assert self.segments_by_type, 'No data to write'

        if not allow_empty:
            assert sum([
                len(segments) for segments in self.segments_by_type.values()
            ]) != 0, "Didn't generate any segments"

        for segtype in self.segments_by_type.keys():
            if suffix is not None:
                filename = "segdata_%s_%s.txt" % (segtype.lower(), suffix)
            else:
                filename = "segdata_%s.txt" % (segtype.lower())

            segments = self.segments_by_type[segtype]
            if segments:
                print("Writing %s." % filename)
                with open(filename, "w") as f:
                    for segname, segdata in sorted(segments.items()):
                        # seg 00020300_010
                        print("seg %s" % segname, file=f)
                        for bitname in sorted(segdata["bits"]):
                            print("bit %s" % bitname, file=f)

                        if extra_tags is not None:
                            for tagname, tagval in extra_tags(segdata['name']):
                                segdata["tags"]['{}.{}'.format(
                                    segdata['tile_type_norm'],
                                    tagname)] = tagval
                        for tagname, tagval in sorted(segdata["tags"].items()):
                            print("tag %s %d" % (tagname, tagval), file=f)
