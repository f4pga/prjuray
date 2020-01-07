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

import argparse
import re


def create_mask(all_bits):
    mask_bits = set()

    for a_bits in all_bits:
        for b_bits in all_bits:
            if a_bits is b_bits:
                continue

            mask_bits |= a_bits & b_bits

    return mask_bits


def mask_feature(bits, mask_bits):
    mask_bits = set(mask_bits)
    mask_bits -= set(bits)

    output_bits = []
    output_bits.extend(list(bits))
    output_bits.extend('!{}'.format(bit) for bit in mask_bits)

    return sorted(output_bits)


class Iostandard():
    def __init__(self, site, iostandard, in_bits, out_bits, in_out_bits,
                 pulltype_bits):
        self.site = site
        self.iostandard = iostandard
        self.in_bits = in_bits - pulltype_bits
        self.out_bits = out_bits - pulltype_bits
        self.in_out_bits = in_out_bits - pulltype_bits
        self.pulltype_bits = pulltype_bits

        self.drive_slews = {}
        self.options = {}

    def add_drive_slew(self, drive, slew, bits):
        assert drive, slew not in self.drive_slews
        self.drive_slews[drive, slew] = bits - self.pulltype_bits

    def add_option(self, option, value, bits):
        if option not in self.options:
            self.options[option] = {}

        assert value not in self.options[option]
        self.options[option][value] = bits - self.pulltype_bits


class IobFeatures():
    def __init__(self):
        self.site_iostandards = {}

    def add_iostandard(self, iostd_obj):
        if iostd_obj.site not in self.site_iostandards:
            self.site_iostandards[iostd_obj.site] = {}
        self.site_iostandards[iostd_obj.site][iostd_obj.iostandard] = iostd_obj

    def output_all_standards(self, prefix, f_out):
        all_in_bits = set()
        all_out_bits = set()
        all_in_out_bits = set()
        all_in_bits_by_site = {}
        all_out_bits_by_site = {}
        all_in_out_bits_by_site = {}

        for iostds_within_site in self.site_iostandards.values():
            for iostd_obj in iostds_within_site.values():
                if iostd_obj.site not in all_in_bits_by_site:
                    all_in_bits_by_site[iostd_obj.site] = set()
                    all_out_bits_by_site[iostd_obj.site] = set()
                    all_in_out_bits_by_site[iostd_obj.site] = set()

                all_in_bits |= iostd_obj.in_bits
                all_in_bits_by_site[iostd_obj.site] |= iostd_obj.in_bits
                all_out_bits |= iostd_obj.out_bits
                all_out_bits_by_site[iostd_obj.site] |= iostd_obj.out_bits

                for bits in iostd_obj.drive_slews.values():
                    all_out_bits |= bits
                    all_out_bits_by_site[iostd_obj.site] |= bits

                remaining_in_out_bits = set(iostd_obj.in_out_bits)
                remaining_in_out_bits -= iostd_obj.in_bits
                remaining_in_out_bits -= iostd_obj.out_bits

                all_in_out_bits |= remaining_in_out_bits
                all_in_out_bits_by_site[iostd_obj.
                                        site] |= remaining_in_out_bits

        bits_to_in_features = {}
        bits_to_out_features = {}
        bits_to_in_out_features = {}

        for site in sorted(self.site_iostandards.keys()):
            for iostd in sorted(self.site_iostandards[site].keys()):
                iostd_obj = self.site_iostandards[site][iostd]

                in_bits = frozenset(iostd_obj.in_bits)
                if in_bits not in bits_to_in_features:
                    bits_to_in_features[in_bits] = []

                bits_to_in_features[in_bits].append((site, iostd))

                if len(iostd_obj.drive_slews) == 0:
                    out_bits = frozenset(iostd_obj.out_bits)

                    if out_bits not in bits_to_out_features:
                        bits_to_out_features[out_bits] = []

                    bits_to_out_features[out_bits].append(
                        (site, iostd, '{}_FIXED'.format(iostd)))
                else:
                    for (drive, slew), bits in iostd_obj.drive_slews.items():
                        out_bits = frozenset(bits)

                        if out_bits not in bits_to_out_features:
                            bits_to_out_features[out_bits] = []

                        bits_to_out_features[out_bits].append(
                            (site, iostd, 'I{}_SLEW_{}'.format(drive, slew)))

                remaining_in_out_bits = set(iostd_obj.in_out_bits)
                remaining_in_out_bits -= iostd_obj.in_bits
                remaining_in_out_bits -= iostd_obj.out_bits

                if len(remaining_in_out_bits) > 0:
                    in_out_bits = frozenset(remaining_in_out_bits)

                    if in_out_bits not in bits_to_in_out_features:
                        bits_to_in_out_features[in_out_bits] = []

                    bits_to_in_out_features[in_out_bits].append((site, iostd))

        site_to_in_bits = {}
        site_to_out_bits = {}
        site_to_in_out_bits = {}

        for bits, features in bits_to_in_features.items():
            print('IN(count: {}) {} :'.format(len(features), bits))

            sites = set()
            for f in features:
                print('  {}'.format(f))

                site = f[0]
                sites.add(site)

                if site not in site_to_in_bits:
                    site_to_in_bits[site] = set()
                site_to_in_bits[site].add(bits)

            assert len(sites) == 1, (bits, features)

        for bits, features in bits_to_out_features.items():
            print('OUT (count: {}) {}:'.format(len(features), bits))

            sites = set()
            for f in features:
                print('  {}'.format(f))

                site = f[0]
                sites.add(site)

                if site not in site_to_out_bits:
                    site_to_out_bits[site] = set()
                site_to_out_bits[site].add(bits)

            assert len(sites) == 1, (bits, features)

        for bits, features in bits_to_in_out_features.items():
            print('IN_OUT (count: {}) {}:'.format(len(features), bits))

            sites = set()
            for f in features:
                print('  {}'.format(f))

                site = f[0]
                sites.add(site)

                if site not in site_to_in_out_bits:
                    site_to_in_out_bits[site] = set()
                site_to_in_out_bits[site].add(bits)

            assert len(sites) == 1, (bits, features)

        all_sites = set()
        site_in_mask = {}
        for site, all_in_bits in site_to_in_bits.items():
            all_sites.add(site)
            site_in_mask[site] = create_mask(all_in_bits)

        site_out_mask = {}
        for site, all_out_bits in site_to_out_bits.items():
            all_sites.add(site)
            site_out_mask[site] = create_mask(all_out_bits)

        site_in_out_mask = {}
        for site, all_in_out_bits in site_to_out_bits.items():
            all_sites.add(site)
            site_in_out_mask[site] = create_mask(all_in_out_bits)

        for site in sorted(all_sites):
            for in_bits in site_to_in_bits[site]:
                print(
                    '{prefix}.{site}.IOSTANDARD_IN.{features} {bits}'.format(
                        prefix=prefix,
                        site=site,
                        features='_'.join(
                            iostd
                            for site, iostd in bits_to_in_features[in_bits]),
                        bits=' '.join(
                            mask_feature(in_bits, site_in_mask[site]))),
                    file=f_out)

            for out_bits in site_to_out_bits[site]:
                print(
                    '{prefix}.{site}.IOSTANDARD_OUT.{features} {bits}'.format(
                        prefix=prefix,
                        site=site,
                        features='_'.join('{}_{}'.format(iostd, drive)
                                          for site, iostd, drive in
                                          bits_to_out_features[out_bits]),
                        bits=' '.join(
                            mask_feature(out_bits, site_out_mask[site]))),
                    file=f_out)

            for in_out_bits in site_to_in_out_bits[site]:
                print(
                    '{prefix}.{site}.IOSTANDARD_IN_OUT.{features} {bits}'.
                    format(
                        prefix=prefix,
                        site=site,
                        features='_'.join(
                            iostd for site, iostd in
                            bits_to_in_out_features[in_out_bits]),
                        bits=' '.join(
                            mask_feature(in_out_bits,
                                         site_in_out_mask[site]))),
                    file=f_out)


def zero_candidates(parts):
    return len(parts) == 3 and parts[1] == '<0' and parts[2] == 'candidates>'


def parse_out_features(iostds, option):
    iostd_length = 0
    iostd = None

    for match_iostd in iostds:
        if option.startswith(match_iostd) and len(match_iostd) > iostd_length:
            iostd_length = len(match_iostd)
            iostd = match_iostd

    assert iostd is not None, (iostds, option)

    return iostd, option[len(iostd) + 1:]


def process_site(iob_features, f_out, site, site_lines):
    print('Processing site {}'.format(site))
    feature_roots = {}

    roots = []

    iostds = set()
    pulltype_features = []
    pulltype_bits = set()
    for l in site_lines:
        if 'PULLTYPE' not in l:
            continue

        parts = l.strip().split(' ')

        feature = parts[0]
        bits = parts[1:]
        if len(bits) == 2 and bits[0] == '<0' and bits[1] == 'candidates>':
            bits = []

        pulltype_features.append(feature)

        feat_parts = feature.split('.')
        assert len(feat_parts) == 4, feature
        assert feat_parts[1] == site, (feature, site)

        for bit in bits:
            pulltype_bits.add(bit)

    assert len(pulltype_bits) == 0 or len(pulltype_bits) == 3, (
        pulltype_features, pulltype_bits)

    for l in site_lines:
        if 'IOSTANDARD' not in l:
            f_out.write(l)
            continue

        parts = l.strip().split(' ')

        feature = parts[0]
        bits = parts[1:]
        if len(bits) == 2 and bits[0] == '<0' and bits[1] == 'candidates>':
            bits = []

        feature_parts = feature.split('.')
        roots.append(tuple(feature_parts[:2]))

        if feature_parts[2] not in feature_roots:
            feature_roots[feature_parts[2]] = []

        feature_roots[feature_parts[2]].append((feature_parts[3:], bits))

        if feature_parts[2] in [
                'IOSTANDARD', 'IOSTANDARD_IN', 'IOSTANDARD_OUT',
                'IOSTANDARD_IN_OUT'
        ]:
            iostds.add(feature_parts[3])

    if len(roots) == 0:
        return

    print('Site {}:'.format(site))
    for root, features in feature_roots.items():
        print('  {}: {}'.format(
            root, ', '.join('.'.join(feats) for feats, bits in features)))

    print()

    print("  IOSTANDARD's from site {}: {}".format(site, ', '.join(
        sorted(iostds))))

    features_by_iostd = {}
    for l in site_lines:
        if 'IOSTANDARD' not in l:
            continue

        parts = l.strip().split(' ')

        feature = parts[0]
        bits = parts[1:]
        if len(bits) == 2 and bits[0] == '<0' and bits[1] == 'candidates>':
            bits = []

        feature_parts = feature.split('.')

        if feature_parts[2] == 'IOSTANDARD':
            iostd = feature_parts[3]
            feature = 'IOSTANDARD'
        elif feature_parts[2] in [
                'IOSTANDARD_IN', 'IOSTANDARD_OUT', 'IOSTANDARD_IN_OUT'
        ]:
            iostd = feature_parts[3]
            feature = feature_parts[2][len('IOSTANDARD_'):]
        else:
            iostd, feature_part = parse_out_features(iostds, feature_parts[3])
            print('   ', feature_parts[3], iostd, feature_part)
            feature = '{}.{}'.format(feature_parts[2][len('IOSTANDARD_'):],
                                     feature_part)

        if iostd not in features_by_iostd:
            features_by_iostd[iostd] = []

        features_by_iostd[iostd].append((feature, set(bits)))

    for iostd in sorted(features_by_iostd.keys()):
        if iostd == 'NONE':
            continue

        print('    IOSTANDARD {}'.format(iostd))

        features = {}

        for feature, bits in sorted(
                features_by_iostd[iostd], key=lambda x: x[0]):
            print('      {}: {}'.format(feature, bits))

            assert feature not in features, feature
            features[feature] = set(bits)

        if 'IN' not in features:
            print(
                ' *** Skipping IOSTANDARD {} because no IN ***'.format(iostd))
            print()
            continue

        if 'OUT' not in features:
            print(
                ' *** Skipping IOSTANDARD {} because no OUT ***'.format(iostd))
            print()
            continue

        if 'IN_OUT' not in features:
            print(
                ' *** Skipping IOSTANDARD {} because no OUT ***'.format(iostd))
            print()
            continue

        print()
        print('        IN - OUT: {}'.format(features['IN'] - features['OUT']))
        print('        IN_OUT - OUT: {}'.format(features['IN_OUT'] -
                                                features['OUT']))

        drives = {}
        drives_slews = {}

        for feature, bits in features.items():
            if not feature.startswith('DRIVE'):
                continue

            if feature.startswith('DRIVE.'):
                parts = feature.split('.')
                assert len(parts) == 2
                drives[parts[1]] = bits

            if feature.startswith('DRIVE_SLEW.'):
                parts = feature.split('.')
                assert len(parts) == 2
                drives_slews[parts[1]] = bits

            assert len(features['OUT'] - bits) == 0, feature

            print('        {} - OUT: {}'.format(feature,
                                                bits - features['OUT']))

        print()

        iostd_obj = Iostandard(
            site=site,
            iostandard=iostd,
            in_bits=features['IN'],
            out_bits=features['OUT'],
            in_out_bits=features['IN_OUT'],
            pulltype_bits=pulltype_bits)

        if len(drives) == 1 and list(drives.keys())[0] == 'DRIVE_I_FIXED':
            assert len(drives_slews) == 0
            assert drives['DRIVE_I_FIXED'] == features['OUT'], iostd
        else:
            for feature, bits in drives_slews.items():
                drive_for_slew = None
                for drive in drives:
                    if feature.startswith(drive + '_'):
                        assert drive_for_slew is None
                        drive_for_slew = drive

                assert drive_for_slew is not None

                assert len(drives[drive_for_slew] - bits) == 0, (feature,
                                                                 drive)

                iostd_obj.add_drive_slew(
                    drive=drive_for_slew,
                    slew=feature[len(drive_for_slew) + 1:],
                    bits=bits)

        for feature, bits in features.items():
            parts = feature.split('.')
            if len(parts) != 2 or parts[1] == '':
                continue

            if parts[0] == 'DRIVE' or parts[0] == 'DRIVE_SLEW':
                continue

            remaining_bits = set(bits)
            remaining_bits -= features['IN']
            remaining_bits -= features['IN_OUT']
            remaining_bits -= features['OUT']
            print('{}: {}'.format(feature, sorted(remaining_bits)))

            iostd_obj.add_option(
                option=parts[0], value=parts[1], bits=remaining_bits)

        iob_features.add_iostandard(iostd_obj)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--rdb_in', required=True)
    parser.add_argument('--rdb_out', required=True)
    parser.add_argument('--iob_features', required=True)

    args = parser.parse_args()

    feature_filters = []

    with open(args.iob_features) as f:
        for l in f:
            feature_filters.append(re.compile(l.strip()))

    feature_to_line = {}
    lines_by_site = {}
    bits_by_site = {}

    bits_with_intersect = set()

    prefix = None

    with open(args.rdb_in) as f, open(args.rdb_out, 'w') as f_out:
        for l in f:
            if '<const1>' in l or '<const0>' in l:
                f_out.write(l)
                continue

            if '<0 candidates>' not in l and 'candidates>' in l:
                f_out.write(l)
                continue

            feature_match = False
            for filt in feature_filters:
                m = filt.search(l.strip())
                if m is not None:
                    feature_match = True

            if not feature_match:
                f_out.write(l)
                continue

            parts = l.split(' ')
            feature_to_line[parts[0]] = l

            if prefix is None:
                prefix = parts[0].split('.')[0]
            else:
                assert prefix == parts[0].split('.')[0]

            site = parts[0].split('.')[1]
            if site not in lines_by_site:
                lines_by_site[site] = []
                bits_by_site[site] = set()

            lines_by_site[site].append(l)

        for site, lines in lines_by_site.items():
            for l in lines:
                parts = l.strip().split(' ')

                if zero_candidates(parts):
                    continue

                bits_by_site[site] |= set(parts[1:])

        sites = sorted(bits_by_site.keys())
        for site in sites:
            for site2 in sites:
                if site == site2:
                    continue

                bits_with_intersect |= (
                    bits_by_site[site] & bits_by_site[site2])

        print('Sites with intersection bits:')
        for site, bits in bits_by_site.items():
            intersect_bits = bits_with_intersect & bits
            if len(intersect_bits) == 0:
                continue

            print('Site {}, bits {}'.format(site, ' '.join(intersect_bits)))

        print()

        iob_features = IobFeatures()

        for site in sites:
            process_site(iob_features, f_out, site, lines_by_site[site])
            print()

        iob_features.output_all_standards(prefix, f_out)


if __name__ == "__main__":
    main()
