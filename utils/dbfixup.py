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
"""
This utility script "fixes up" an initial fuzzer solution. This includes:

- Removal of unsolved tags,
- Removal of duplicated solutions (duplicated tags with the same bits),
- Optional zeroing bits according to the zero group(s) specification,
- Optional grouping exclusive tags together according to tag group(s)
  specification.
"""

import argparse
import sys, os, re
import itertools

from utils import util


def zero_range(tag, bits, wordmin, wordmax):
    """
    If any bits occur wordmin <= word <= wordmax,
    default bits in wordmin <= word <= wordmax to 0
    """

    # The bit index, if any, that needs to be one hotted
    bitidx = None
    for bit in bits:
        if bit[0] == "!":
            continue
        fidx, bidx = [int(s) for s in bit.split("_")]
        if wordmin <= fidx <= wordmax:
            if bitidx is not None and bidx != bitidx:
                print("Old bit index: %u, new: %u" % (bitidx, bidx))
                print("%s bits: %s" % (tag, str(bits)))
                raise ValueError("%s: inconsistent bit index" % tag)
            bitidx = bidx

    if bitidx is None:
        return

    for fidx in range(wordmin, wordmax + 1):
        bit = "%02d_%02d" % (fidx, bitidx)
        # Preserve 1 bits, set others to 0
        if bit not in bits:
            bits.add("!" + bit)


def bits_str(bits):
    """Convert a set into canonical form"""
    return ' '.join(sorted(list(bits)))


class ZeroGroups(object):
    def __init__(self, zero_db):
        self.groups = []
        self.bit_to_group = {}
        self.tag_to_groups = {}
        self.zero_tag_to_group = {}
        self.parse_zero_db(zero_db)

    def print_groups(self):
        print('Zero groups:')
        for bits in self.groups:
            print(bits_str(bits))

        print('Zero tags:')
        for tag in self.zero_tag_to_group:
            print(tag, bits_str(self.zero_tag_to_group[tag]))

    def parse_zero_db(self, zero_db):
        """ Convert zero db format into data structure

        Zero db format examples:

        Ex: 01_02 04_05
        Means find a line that has either of these bits
        If either of them occurs, default bits in that set to zero

        Ex: 01_02 04_05|07_08 10_11
        If any bits from the first group occur,
        default bits in the second group to zero

        Ex: 01_02 04_05,ALL_ZERO
        ALL_ZERO is an enum that is part of the group but is all 0
        It must have 0 candidates

        Ex: CLB.SLICE_X0.CLKINV ^ CLB.SLICE_X0.NOCLKINV
        CLB.SLICE_X0.NOCLKINV is all bits in CLB.SLICE_X0.CLKINV unset

        Ex: A | B ^ C
        C is all bits in (A)|(B) unset


        """

        if not zero_db:
            return

        for zdb in zero_db:

            if "^" in zdb:
                self.groups.append(set())
                zero_group = self.groups[-1]

                other_tags, allzero_tag = zdb.split('^')
                allzero_tag = allzero_tag.strip()

                for tag in other_tags.split():
                    self.tag_to_groups[tag.strip()] = [zero_group]

                self.zero_tag_to_group[allzero_tag] = zero_group
                continue

            allzero_tag = None
            if "," in zdb:
                zdb, allzero_tag = zdb.split(",")

            if "|" in zdb:
                a, b = zdb.split("|")
                a = a.split()
                b = b.split()

                self.groups.append(set(b))
                zero_group = self.groups[-1]
            else:
                a = zdb.split()
                self.groups.append(set(a))
                zero_group = self.groups[-1]

            if allzero_tag is not None:
                self.zero_tag_to_group[allzero_tag] = zero_group

            for bit in a:
                self.bit_to_group[bit] = zero_group

    def add_tag_bits(self, tag, bits):
        if tag in self.zero_tag_to_group:
            return

        group_ids = set()
        groups = []

        if tag in self.tag_to_groups:
            assert len(self.tag_to_groups[tag]) == 1

            self.tag_to_groups[tag][0] |= bits

            for bit in bits:
                if bit in self.bit_to_group:
                    # Make sure each bit only belongs to one group
                    assert id(self.bit_to_group[bit]) == id(
                        self.tag_to_groups[tag])
                else:
                    self.bit_to_group[bit] = self.tag_to_groups[tag]

            group_ids.add(id(self.tag_to_groups[tag]))
            groups = self.tag_to_groups[tag]

        for bit in bits:
            if bit in self.bit_to_group:
                if id(self.bit_to_group[bit]) not in group_ids:
                    group_ids.add(id(self.bit_to_group[bit]))
                    groups.append(self.bit_to_group[bit])

        self.tag_to_groups[tag] = groups

    def add_bits_from_zero_groups(self, tag, bits, strict=True, verbose=False):
        """ Add bits from a zero group, if needed

        Arguments
        ---------
        tag : str
            Tag being to examine for zero group
        bits : set of str
            Set of bits set on this tag
        strict : bool
            Assert that the size of the given group is the size of the given
            mask.
        verbose : bool
            Print to stdout grouping being made
        """

        tag_is_masked = tag in self.tag_to_groups
        tag_is_zero = tag in self.zero_tag_to_group

        # Should not have a tag that is both masked and a zero tag.
        assert not (tag_is_masked and tag_is_zero)

        if tag_is_masked:
            for b in self.tag_to_groups[tag]:
                bits_orig = set(bits)
                for bit in b:
                    if bit not in bits:
                        bits.add("!" + bit)

                verbose and print("Grouped %s: %s => %s" %
                                  (tag, bits_str(bits_orig), bits_str(bits)))

        if tag_is_zero:
            for bit in self.zero_tag_to_group[tag]:
                bits.add("!" + bit)


def read_segbits(fn_in):
    """
    Reads a segbits file. Removes duplcated lines. Returns a list of the lines.
    """
    lines = []
    llast = None

    with open(fn_in, "r") as f:
        for line in f:
            # Hack: skip duplicate lines
            # This happens while merging a new multibit entry
            line = line.strip()
            if len(line) == 0:
                continue
            if line == llast:
                continue

            lines.append(line)

    return lines


def add_zero_bits(fn_in, lines, zero_db, strict=True, verbose=False):
    '''
    Add multibit entries
    This requires adding some zero bits (ex: !31_09)
    If an entry has any of the
    '''

    zero_groups = ZeroGroups(zero_db)

    new_lines = set()
    changes = 0

    drops = 0

    for line in lines:

        tag, bits, mode, _ = util.parse_db_line(line)

        if bits is not None and mode is None:
            zero_groups.add_tag_bits(tag, bits)

    if verbose:
        zero_groups.print_groups()

    for line in lines:
        tag, bits, mode, _ = util.parse_db_line(line)
        # an enum that needs masking
        # check below asserts that a mask was actually applied
        if mode and mode != "<0 candidates>" and not strict:
            verbose and print("WARNING: dropping unresolved line: %s" % line)
            drops += 1
            continue

        assert mode not in (
            "<const0>",
            "<const1>"), "Entries must be resolved. line: %s" % (line, )

        if mode == "always":
            new_line = line
        else:
            if mode:
                assert mode == "<0 candidates>", line
                bits = set()
            else:
                bits = set(bits)

            zero_groups.add_bits_from_zero_groups(
                tag, bits, strict=strict, verbose=verbose)

            if strict:
                assert len(bits) > 0, 'Line {} found no bits.'.format(line)
            elif len(bits) == 0:
                verbose and print(
                    "WARNING: dropping unresolved line: %s" % line)
                drops += 1
                continue

            new_line = " ".join([tag] + sorted(bits))

        if re.match(r'.*<.*>.*', new_line):
            print("Original line: %s" % line)
            assert 0, "Failed to remove line mode: %s" % (new_line)

        if new_line != line:
            changes += 1
        new_lines.add(new_line)
        llast = line

    if drops:
        print("WARNING: %s dropped %s unresolved lines" % (fn_in, drops))

    return changes + drops, new_lines


def load_zero_db(fn):
    # Remove comments and convert to list of lines
    ret = []
    for l in open(fn, "r"):
        pos = l.find("#")
        if pos >= 0:
            l = l[0:pos]
        l = l.strip()
        if not l:
            continue
        ret.append(l)
    return ret


def remove_ambiguous_solutions(fn_in, db_lines, strict=True, verbose=True):
    """ Removes features with identical solutions.

    During solving, some tags may be tightly coupled and solve to the same
    solution.  In these cases, those solutions must be dropped until
    disambiguating information can be found.
    """
    solutions = {}
    dropped_solutions = set()

    for l in db_lines:
        parts = l.split()
        feature = parts[0]
        bits = frozenset(parts[1:])

        if bits in solutions:
            if strict:
                assert False, "Found solution {} at least twice, in {} and {}".format(
                    bits, feature, solutions[bits])
            else:
                dropped_solutions.add(bits)
        else:
            solutions[bits] = feature

    if strict:
        return 0, db_lines

    drops = 0
    output_lines = set()

    for l in db_lines:
        parts = l.split()
        feature = parts[0]
        bits = frozenset(parts[1:])

        if bits not in dropped_solutions:
            output_lines.add(l)
        else:
            drops += 1
            if verbose:
                print(
                    "WARNING: dropping line due to duplicate solution: %s" % l)

    if drops > 0:
        print("WARNING: %s dropped %s duplicate solutions" % (fn_in, drops))

    return drops, output_lines


def group_tags(lines, tag_groups, bit_groups):
    """
    Implements tag grouping. If a tag belongs to a group then the common bits
    of that group are added to is as zeros.

    >>> tg = [{"A", "B"}]
    >>> bg = [{(1, 2), (3, 4)}]
    >>> res = group_tags({"A 01_02", "B 03_04"}, tg, bg)
    >>> (res[0], sorted(list(res[1])))
    (2, ['A 01_02 !03_04', 'B !01_02 03_04'])

    >>> tg = [{"A", "B"}]
    >>> bg = [{(1, 2), (3, 4)}]
    >>> res = group_tags({"A 01_02", "B 03_04", "C 01_02"}, tg, bg)
    >>> (res[0], sorted(list(res[1])))
    (2, ['A 01_02 !03_04', 'B !01_02 03_04', 'C 01_02'])
    """

    changes = 0
    new_lines = set()

    # Process lines
    for line in lines:

        line = line.strip()
        if not len(line):
            continue

        # Parse the line
        tag, bits, mode, _ = util.parse_db_line(line)
        if not bits:
            bits = set()
        else:
            bits = set([util.parse_tagbit(b) for b in bits])

        # Check if the tag belongs to a group
        for tag_group, bit_group in zip(tag_groups, bit_groups):
            if tag in tag_group:

                # Add zero bits to the tag if not already there
                bit_coords = set([b[1] for b in bits])
                for zero_bit in bit_group:
                    if zero_bit not in bit_coords:
                        bits.add((False, zero_bit))

                # Format the line
                bit_strs = []
                for bit in sorted(list(bits), key=lambda b: b[1]):
                    s = "!" if not bit[0] else ""
                    s += "{:02d}_{:02d}".format(bit[1][0], bit[1][1])
                    bit_strs.append(s)

                new_line = " ".join([tag] + bit_strs)

                # Add the line
                new_lines.add(new_line)
                changes += 1
                break

        # It does not, pass it through unchanged
        else:
            new_lines.add(line)

    return changes, new_lines


def filter_bits(lines, filtered_bits):
    changes = 0
    new_lines = set()

    print(filtered_bits)

    # Process lines
    for line in lines:
        line = line.strip()
        if not len(line):
            continue

        tag, bits, mode, _ = util.parse_db_line(line)
        if not bits:
            bits = set()
        else:
            bits = set(util.parse_tagbit(b) for b in bits)

        set_bits = set(bit[1] for bit in bits if bit[0])
        unset_bits = set(bit[1] for bit in bits if not bit[0])
        new_set_bits = set_bits - filtered_bits

        if len(set_bits) != len(new_set_bits):
            changes += 1

            bit_strs = []
            for bit in unset_bits:
                bit_strs.append('!{:02d}_{:02d}'.format(bit[0], bit[1]))

            for bit in set_bits:
                bit_strs.append('{:02d}_{:02d}'.format(bit[0], bit[1]))

            new_line = " ".join([tag] + bit_strs)
            new_lines.add(new_line)
        else:
            new_lines.add(line)

    return changes, new_lines


def update_seg_fns(fn_inouts,
                   zero_db,
                   tag_groups,
                   filter_across_groups,
                   lazy=False,
                   strict=True,
                   verbose=False):

    seg_files = 0
    seg_lines = 0
    for fn_in, fn_out in fn_inouts:
        verbose and print("zb %s: %s" % (fn_in, os.path.exists(fn_in)))
        if lazy and not os.path.exists(fn_in):
            continue

        lines = read_segbits(fn_in)
        changes = 0

        # Find common bits for tag groups
        bit_groups, filtered_bits = find_common_bits_for_tag_groups(
            lines, tag_groups, filter_across_groups)

        if len(filtered_bits) > 0:
            new_changes, lines = filter_bits(lines, filtered_bits)
            changes += new_changes

        # Group tags
        new_changes, lines = group_tags(lines, tag_groups, bit_groups)
        changes += new_changes

        new_changes, lines = add_zero_bits(
            fn_in, lines, zero_db, strict=strict, verbose=verbose)
        changes += new_changes

        new_changes, lines = remove_ambiguous_solutions(
            fn_in,
            lines,
            strict=strict,
            verbose=verbose,
        )
        changes += new_changes

        with open(fn_out, "w") as f:
            for line in sorted(lines):
                print(line, file=f)

        if changes is not None:
            seg_files += 1
            seg_lines += changes
    print("Segbit: checked %u files w/ %u changed lines" % (seg_files,
                                                            seg_lines))


def update_segs(db_root,
                seg_fn_in,
                seg_fn_out,
                zero_db_fn,
                tag_groups,
                filter_across_groups,
                strict=True,
                verbose=False):

    assert seg_fn_in
    lazy = False

    if not seg_fn_out:
        seg_fn_out = seg_fn_in

    fn_inouts = [(seg_fn_in, seg_fn_out)]

    if zero_db_fn:
        zero_db = load_zero_db(zero_db_fn)
        print("Segbit groups: %s" % len(zero_db))
    else:
        zero_db = None

    update_seg_fns(
        fn_inouts,
        zero_db,
        tag_groups,
        filter_across_groups,
        lazy=lazy,
        strict=strict,
        verbose=verbose)


def find_common_bits_for_tag_groups(lines, tag_groups, filter_across_groups):
    """
    For each tag group finds a common set of bits that have value of one.
    """

    bit_groups = []

    for tag_group in tag_groups:
        bit_group = set()

        for line in lines:
            tag, bits, mode, _ = util.parse_db_line(line)
            if not bits:
                continue

            bits = set([util.parse_tagbit(b) for b in bits])

            if tag in tag_group and len(bits):
                ones = set([b[1] for b in bits if b[0]])
                bit_group |= ones

        bit_groups.append(bit_group)

    filtered_bits = set()
    if filter_across_groups:
        bit_usage_count = {}

        for bit_group in bit_groups:
            for bit in bit_group:
                bit_usage_count[bit] = bit_usage_count.get(bit, 0) + 1

        for bit, count in bit_usage_count.items():
            if count > 1:
                filtered_bits.add(bit)

        for bit in sorted(filtered_bits):
            print("WARNING: filtering bit {:02d}_{:02d} from groups".format(
                bit[0], bit[1]))

        for bit_group in bit_groups:
            bit_group -= filtered_bits

    return bit_groups, filtered_bits


def load_tag_groups(file_name):
    """
    Loads tag groups from a text file.

    A tag group is defined by specifying a space separated list of tags within
    a single line. Lines that are empty or start with '#' are ignored.
    """
    tag_groups = []

    # Load tag group specifications
    with open(file_name, "r") as fp:
        for line in fp:
            line = line.strip()

            if len(line) == 0 or line.startswith("#"):
                continue

            group = set(line.split())
            if len(group):
                tag_groups.append(group)

    # Check if all tag groups are exclusive
    for tag_group_a, tag_group_b in itertools.combinations(tag_groups, 2):

        tags = tag_group_a & tag_group_b
        if len(tags):
            raise RuntimeError(
                "Tag(s) {} are present in multiple groups".format(
                    " ".join(tags)))

    return tag_groups


def run(db_root,
        zero_db_fn=None,
        seg_fn_in=None,
        seg_fn_out=None,
        groups_fn_in=None,
        filter_across_groups=False,
        strict=False,
        verbose=False):

    # Load tag groups
    tag_groups = []
    if groups_fn_in is not None:
        tag_groups = load_tag_groups(groups_fn_in)

    # Probably should split this into two programs
    update_segs(
        db_root,
        seg_fn_in=seg_fn_in,
        seg_fn_out=seg_fn_out,
        zero_db_fn=zero_db_fn,
        tag_groups=tag_groups,
        filter_across_groups=filter_across_groups,
        strict=strict,
        verbose=verbose)


def main():

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    util.db_root_arg(parser)

    parser.add_argument(
        '--seg-fn-in', required=True, help='Input segbits db file')

    parser.add_argument(
        '--seg-fn-out', required=True, help='Output segbits db file')

    parser.add_argument(
        '--zero-db',
        default=None,
        help='Input file name with zero group(s) definitions')

    parser.add_argument(
        "-g",
        "--groups",
        type=str,
        default=None,
        help="Input tag group definition file")

    parser.add_argument(
        '--strict', action='store_true', help='Strict db checks')

    parser.add_argument(
        '--filter_across_groups',
        help='Filter out bits that match between groups',
        action='store_true')

    parser.add_argument(
        '--verbose', action='store_true', help='Be more verbose')

    args = parser.parse_args()

    run(args.db_root,
        args.zero_db,
        args.seg_fn_in,
        args.seg_fn_out,
        args.groups,
        args.filter_across_groups,
        strict=args.strict,
        verbose=args.verbose)


if __name__ == '__main__':
    main()
