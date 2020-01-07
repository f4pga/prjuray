#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2020 Project U-Ray Authors
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file.
#
# SPDX-License-Identifier: ISC

import csv
import copy
import itertools
from utils.util import create_xy_fun

# Use fewer IOSTANDARD's initially to reduce required sample counts.
LIMITED_STANDARDS = True

DRIVES = {
    ("HPIOB", "LVCMOS18"): ["2", "4", "6", "8", "12"],
    ("HPIOB", "LVCMOS15"): ["2", "4", "6", "8", "12"],
    ("HPIOB", "LVCMOS12"): ["2", "4", "6", "8"],
    ("HDIOB", "LVCMOS33"): ["4", "8", "12", "16"],
    ("HDIOB", "LVCMOS25"): ["4", "8", "12", "16"],
    ("HDIOB", "LVCMOS18"): ["4", "8", "12", "16"],
    ("HDIOB", "LVCMOS15"): ["4", "8", "12", "16"],
    ("HDIOB", "LVCMOS12"): ["4", "8", "12"],
}

# A set of pin configurations that toggle all bits so that each IOB can be
# decoupled from every other.
#
# If this is wrong, it may result in output instability.
SINGLE_ENDED_MAX_STANDARDS = {
    "HDIOB": [
        ("LVCMOS12", "1.2", "12", "SLOW"),
        ("LVCMOS18", "1.8", "12", "FAST"),
        ("LVCMOS25", "2.5", "16", "SLOW"),
    ],
    "HPIOB": [
        ("LVCMOS15", "1.5", "2", "SLOW"),
        ("LVCMOS12", "1.2", "6", "SLOW"),
        ("SSTL15", "1.5", None, None),
        ("POD12_DCI", "1.2", None, None),
    ],
}

DIFF_MAX_STANDARDS = {
    "HDIOB": [],
    "HPIOB": [],
}

if LIMITED_STANDARDS:
    DIFF_STANDARDS = {
        ("HPIOB", "1.8"):
        ["DIFF_SSTL18_I", "DIFF_SSTL18_I_DCI", "SLVS_400_18", "LVDS"],
        ("HPIOB", "1.5"): ["DIFF_SSTL15", "DIFF_SSTL15_DCI"],
        ("HPIOB", "1.35"): ["DIFF_SSTL135", "DIFF_SSTL135_DCI"],
        ("HPIOB", "1.2"): [
            "DIFF_SSTL12", "DIFF_SSTL12_DCI", "DIFF_HSUL_12",
            "DIFF_HSUL_12_DCI", "DIFF_POD12", "DIFF_POD12_DCI"
        ],
        ("HPIOB", "1.0"): ["DIFF_POD10", "DIFF_POD10_DCI"],
    }

    SINGLE_ENDED_STANDARDS = {
        ("HPIOB", "1.8"): [
            "LVCMOS18",
            "SSTL18_I",
        ],
        ("HPIOB", "1.5"): [
            "LVCMOS15",
            "SSTL15",
        ],
        ("HPIOB", "1.35"): [],
        ("HPIOB", "1.2"): [
            "LVCMOS12",
            "SSTL12_DCI",
            "POD12_DCI",
        ],
        ("HPIOB", "1.0"): [],
        ("HDIOB", "3.3"): ["LVCMOS33", "LVTTL"],
        ("HDIOB", "2.5"): ["LVCMOS25"],
        ("HDIOB", "1.8"): ["LVCMOS18"],
        ("HDIOB", "1.5"): ["LVCMOS15"],
        ("HDIOB", "1.2"): ["LVCMOS12"]
    }
else:
    DIFF_STANDARDS = {
        ("HPIOB", "1.8"):
        ["DIFF_SSTL18_I", "DIFF_SSTL18_I_DCI", "SLVS_400_18", "LVDS"],
        ("HPIOB", "1.5"): ["DIFF_SSTL15", "DIFF_SSTL15_DCI"],
        ("HPIOB", "1.35"): ["DIFF_SSTL135", "DIFF_SSTL135_DCI"],
        ("HPIOB", "1.2"): [
            "DIFF_SSTL12", "DIFF_SSTL12_DCI", "DIFF_HSUL_12",
            "DIFF_HSUL_12_DCI", "DIFF_POD12", "DIFF_POD12_DCI"
        ],
        ("HPIOB", "1.0"): ["DIFF_POD10", "DIFF_POD10_DCI"],
    }

    SINGLE_ENDED_STANDARDS = {
        ("HPIOB", "1.8"): [
            "LVCMOS18", "LVDCI_18", "HSLVDCI_18", "HSTL_I_18", "HSTL_I_DCI_18",
            "SSTL18_I", "SSTL18_I_DCI"
        ],
        ("HPIOB", "1.5"): [
            "LVCMOS15", "LVDCI_15", "HSLVDCI_15", "HSTL_I", "HSTL_I_DCI",
            "SSTL15", "SSTL15_DCI"
        ],
        ("HPIOB", "1.35"): ["SSTL135", "SSTL135_DCI"],
        ("HPIOB", "1.2"): [
            "LVCMOS12", "HSTL_I_12", "HSTL_I_DCI_12", "SSTL12", "SSTL12_DCI",
            "HSUL_12", "HSUL_12_DCI", "POD12", "POD12_DCI"
        ],
        ("HPIOB", "1.0"): ["POD10", "POD10_DCI"],
        ("HDIOB", "3.3"): ["LVCMOS33", "LVTTL"],
        ("HDIOB", "2.5"): ["LVCMOS25"],
        ("HDIOB", "1.8"): ["LVCMOS18"],
        ("HDIOB", "1.5"): ["LVCMOS15"],
        ("HDIOB", "1.2"): ["LVCMOS12"]
    }

DIFF_PRIMATIVES = {
    "HPIOB": ["IBUFDS", "OBUFDS", "OBUFTDS", "IOBUFDS", "IOBUFDSE3"],
    #"HDIOB": ["IBUF","OBUF", "OBU", "IOBUF"]
}

SINGLE_ENDED_PRIMATIVES = {
    "HPIOB": ["IBUF", "IBUF_IBUFDISABLE", "OBUF", "OBUFT", "IOBUF", "IOBUFE3"],
    "HDIOB": ["IBUF", "OBUF", "OBUFT", "IOBUF"]
}


def choose_iobank_voltage_uniform_by_iostandard(bank_to_iotype, standards,
                                                drives, random_lib):
    """ Return a voltage for each IO bank, with probability uniform by IOSTANDARD.

    Some voltages have more IOSTANDARD's than others, so to minimize the
    number of required samples, IO bank voltage is choosen with a probability
    such that IOSTANDARD's are uniform, rather than uniform by IO bank voltage
    level.

    """
    # Determine how many IOSTANDARD's per voltage level,
    # and weight the uniform randomness over that count to give each
    # IOSTANDARD about uniform probability.
    bank_volt_to_iostandard_count = {}
    for (bank_type, voltage), iostds in standards.items():
        if bank_type not in bank_volt_to_iostandard_count:
            bank_volt_to_iostandard_count[bank_type] = {}

        assert voltage not in bank_volt_to_iostandard_count[bank_type], (
            bank_type, voltage)

        count = 0
        for iostandard in iostds:
            if (bank_type, iostandard) in drives:
                count += len(drives[bank_type, iostandard])
            else:
                # Fixed DRIVE, so only add 1 count
                count += 1

        bank_volt_to_iostandard_count[bank_type][voltage] = count

    bank_type_to_voltages = {}
    bank_type_to_voltage_probability = {}
    for bank_type in bank_volt_to_iostandard_count:
        total_iostds = 0

        for _, count in bank_volt_to_iostandard_count[bank_type].items():
            total_iostds += count

        voltages = []
        probability = []

        for voltage, count in bank_volt_to_iostandard_count[bank_type].items():
            voltages.append(voltage)
            probability.append(float(count) / total_iostds)

        bank_type_to_voltages[bank_type] = voltages
        bank_type_to_voltage_probability[bank_type] = probability

    bank_to_vcc = {}
    for bank, bank_type in sorted(bank_to_iotype.items()):
        if bank_type not in bank_type_to_voltages:
            continue

        bank_to_vcc[bank] = random_lib.choice(
            bank_type_to_voltages[bank_type],
            p=bank_type_to_voltage_probability[bank_type])

    return bank_to_vcc


def voltage_for_bank_type(bank_type):
    if bank_type == "HPIOB":
        return ['1.0', '1.2', '1.35', '1.5', '1.8']
    elif bank_type == 'HDIOB':
        return ['1.2', '1.5', '1.8', '2.5', '3.3']
    else:
        assert False, bank_type


def drives_for_bank_iostandard(bank_type, iostandard):
    return DRIVES.get((bank_type, iostandard), [None])


def slew_for_bank(bank_type):
    if bank_type == "HPIOB":
        return ["SLOW", "MEDIUM", "FAST"]
    elif bank_type == 'HDIOB':
        return ["SLOW", "FAST"]
    else:
        assert False, bank_type


def primative_has_output(primative):
    return primative in [
        'OBUF', 'OBUFT', 'IOBUF', 'IOBUFE3', "OBUFDS", "OBUFTDS", "IOBUFDS",
        "IOBUFDSE3"
    ]


def iostandards_for_bank_and_voltage(bank_type, voltage, single_ended):
    if single_ended:
        return SINGLE_ENDED_STANDARDS.get((bank_type, voltage), [])
    else:
        return DIFF_STANDARDS.get((bank_type, voltage), [])


def vref_for_bank(bank_type, iostandard):
    if bank_type == "HDIOB":
        if iostandard in ("HSTL_I_18", "SSTL18_I", "SSTL18_II"):
            return "0.90"
        elif iostandard in ("HSTL_I", "SSTL15", "SSTL15_II"):
            return "0.75"
        elif iostandard in ("SSTL135", "SSTL135_II"):
            return "0.675"
        elif iostandard == "SSTL12":
            return "0.60"

    if iostandard in ("POD12", "POD12_DCI"):
        return "0.84"

    if iostandard in ("HSTL_I_12", "HSTL_I_DCI_12", "SSTL12", "SSTL12_DCI",
                      "HSUL_12", "HSUL_12_DCI"):
        return "0.60"

    return None


def primatives_for_bank(bank_type, single_ended):
    if single_ended:
        return SINGLE_ENDED_PRIMATIVES.get(bank_type, [])
    else:
        return DIFF_STANDARDS.get(bank_type, [])


def inner_iob_configurations(bank_type, voltage, iostandard, prim):
    opts = [('SLEW', slew_for_bank(bank_type))]

    if bank_type == "HPIOB" and ("POD" in iostandard or "SSTL" in iostandard):
        opts.append(('OUTPUT_IMPEDANCE',
                     ["RDRV_40_40", "RDRV_48_48", "RDRV_60_60"]))

    opt_names, opt_values = zip(*opts)
    for opt_val in itertools.product(*opt_values):
        params = dict(zip(opt_names, opt_val))
        yield voltage, iostandard, prim, params


def iob_configurations(bank_type, single_ended):
    for voltage in voltage_for_bank_type(bank_type):
        for iostandard in iostandards_for_bank_and_voltage(
                bank_type, voltage, single_ended):
            for prim in primatives_for_bank(bank_type, single_ended):
                if not primative_has_output(prim):
                    yield voltage, iostandard, prim, {}
                    continue

                for drive in drives_for_bank_iostandard(bank_type, iostandard):
                    if drive is None:
                        for config in inner_iob_configurations(
                                bank_type, voltage, iostandard, prim):
                            yield config

                        continue

                    for slew in slew_for_bank(bank_type):
                        yield voltage, iostandard, prim, {
                            "DRIVE": drive,
                            "SLEW": slew,
                        }


def check_vref(vref, bank_type, iostandard):
    pin_vref = vref_for_bank(bank_type, iostandard)
    if pin_vref is not None:
        if vref is None:
            # No VREF required yet, maintain it now
            vref = pin_vref
            return True, vref
        elif pin_vref != vref:
            # VREF required does not match VREF required,
            # get next configuration.
            return False, vref

    return True, vref


def bank_planner(random_lib, bank_type, single_ended, pins):
    remaining_configurations = {}
    used_configurations = {}

    configurations = list(iob_configurations(bank_type, single_ended))

    remaining_configs = 0
    for pin in pins:
        remaining_configurations[pin] = copy.deepcopy(configurations)
        remaining_configs += len(remaining_configurations[pin])
        used_configurations[pin] = []
        random_lib.shuffle(remaining_configurations[pin])

    while remaining_configs > 0:
        config = []
        pin_order = sorted(pins)
        random_lib.shuffle(pin_order)

        voltage = None
        vref = None
        first_pin = None
        for pin in pin_order:
            if len(remaining_configurations[pin]) > 0:
                pin_config = remaining_configurations[pin].pop()
                remaining_configs -= 1

                used_configurations[pin].append(pin_config)
                config.append((pin, pin_config))
                first_pin = pin
                voltage, iostandard, _, _ = pin_config
                vref = vref_for_bank(bank_type, iostandard)
                break

        assert first_pin is not None
        assert voltage is not None

        for pin in pin_order:
            if pin == first_pin:
                continue

            used_idx = None
            for idx, pin_config in enumerate(remaining_configurations[pin]):
                pin_voltage, iostandard, prim, params = pin_config

                ok, vref = check_vref(vref, bank_type, iostandard)
                if not ok:
                    continue

                if pin_voltage == voltage:
                    used_idx = idx
                    config.append((pin, pin_config))
                    used_configurations[pin].append(pin_config)
                    break

            if used_idx is not None:
                remaining_configs -= 1
                del remaining_configurations[pin][used_idx]
            else:
                random_lib.shuffle(used_configurations[pin])
                for pin_config in used_configurations[pin]:
                    pin_voltage, iostandard, _, _ = pin_config

                    ok, vref = check_vref(vref, bank_type, iostandard)
                    if not ok:
                        continue

                    if pin_voltage == voltage:
                        config.append((pin, pin_config))
                        break

        yield config

    for configs in remaining_configurations.values():
        assert len(configs) == 0, len(configs)


def bank_planner2(random_lib, bank_type, single_ended, pins, pin_to_banks,
                  pin_to_site_offsets, pin_to_tile_types, pin_to_tiles):
    remaining_configurations = {}
    used_configurations = {}

    configurations = list(iob_configurations(bank_type, single_ended))

    site_offsets = set()
    for pin in pins:
        site_offsets.add((pin_to_tile_types[pin], pin_to_site_offsets[pin]))

    remaining_configs = 0
    remaining_pin_offs = {}

    if single_ended:
        max_standards = copy.deepcopy(SINGLE_ENDED_MAX_STANDARDS[bank_type])
    else:
        max_standards = copy.deepcopy(DIFF_MAX_STANDARDS[bank_type])

    for tile_type, site_offset in site_offsets:
        remaining_configurations[tile_type, site_offset] = copy.deepcopy(
            configurations)
        used_configurations[tile_type, site_offset] = []
        remaining_configs += len(
            remaining_configurations[tile_type, site_offset])

        random_lib.shuffle(remaining_configurations[tile_type, site_offset])

        if tile_type not in remaining_pin_offs:
            remaining_pin_offs[tile_type] = set()

        for standard in max_standards:
            remaining_pin_offs[tile_type].add((site_offset, standard))

    banks = set()
    for pin in pins:
        banks.add(pin_to_banks[pin])

    while remaining_configs > 0:
        config = []
        pin_order = sorted(pins)
        random_lib.shuffle(pin_order)

        bank_voltage = {}
        bank_vref = {}

        for bank in banks:
            bank_voltage[bank] = None
            bank_vref[bank] = None

        leftover_pins = []
        for pin in pin_order:
            site_offset = pin_to_site_offsets[pin]
            tile_type = pin_to_tile_types[pin]
            bank = pin_to_banks[pin]
            assert bank in banks

            used_idx = None
            for idx, pin_config in enumerate(
                    remaining_configurations[tile_type, site_offset]):
                pin_voltage, iostandard, prim, params = pin_config
                assert pin_voltage is not None

                if bank_voltage[bank] is not None and bank_voltage[
                        bank] != pin_voltage:
                    continue

                ok, bank_vref[bank] = check_vref(bank_vref[bank], bank_type,
                                                 iostandard)
                if not ok:
                    continue

                assert bank_voltage[bank] is None or bank_voltage[
                    bank] == pin_voltage
                if bank_voltage[bank] is None:
                    bank_voltage[bank] = pin_voltage

                used_idx = idx
                config.append((pin, pin_config))
                used_configurations[tile_type, site_offset].append(pin_config)
                break

            if used_idx is not None:
                remaining_configs -= 1
                del remaining_configurations[tile_type, site_offset][used_idx]
            else:
                # Save these pins for later!
                leftover_pins.append(pin)

        leftover_pins.sort()
        random_lib.shuffle(leftover_pins)

        for pin in leftover_pins:
            site_offset = pin_to_site_offsets[pin]
            tile_type = pin_to_tile_types[pin]
            bank = pin_to_banks[pin]

            random_lib.shuffle(used_configurations[tile_type, site_offset])
            for pin_config in used_configurations[tile_type, site_offset]:
                pin_voltage, iostandard, _, _ = pin_config

                if bank_voltage[bank] is None:
                    bank_voltage[bank] = pin_voltage
                elif bank_voltage[bank] != pin_voltage:
                    continue

                ok, bank_vref[bank] = check_vref(bank_vref[bank], bank_type,
                                                 iostandard)
                if not ok:
                    continue

                config.append((pin, pin_config))
                break

        # Sanity check bank configs for consistency.
        pins_in_config = set()
        for pin, (pin_voltage, iostandard, _, _) in config:
            pins_in_config.add(pin)
            bank = pin_to_banks[pin]
            assert bank_voltage[bank] == pin_voltage, (bank, pin, iostandard)
            pin_vref = vref_for_bank(bank_type, iostandard)

            if pin_vref is not None:
                assert bank_vref[bank] == pin_vref, (bank, pin, iostandard)

        for pin in pins:
            assert pin in pins_in_config

        yield config

    tiles = {}
    tile_offset_to_pin = {}
    for pin in pins:
        tile = pin_to_tiles[pin]
        if tile not in tiles:
            tiles[tile] = pin_to_tile_types[pin]
        else:
            assert tiles[tile] == pin_to_tile_types[pin]

        key = (tile, pin_to_site_offsets[pin])
        assert key not in tile_offset_to_pin

        tile_offset_to_pin[key] = pin

    while True:
        more_configs = False
        for remaining_configs in remaining_pin_offs.values():
            if len(remaining_configs) > 0:
                more_configs = True
                break

        if not more_configs:
            break

        pins_left = set(pins)

        config = []
        bank_voltage = {}
        bank_vref = {}
        for bank in banks:
            bank_voltage[bank] = None
            bank_vref[bank] = None

        for tile in tiles:
            if len(remaining_pin_offs[tiles[tile]]) == 0:
                continue

            found_config = False
            for pin_off_config in remaining_pin_offs[tiles[tile]]:
                site_offset, _ = pin_off_config
                key = tile, site_offset
                if key not in tile_offset_to_pin:
                    continue

                bank = pin_to_banks[tile_offset_to_pin[key]]

                (site_offset, (iostandard, voltage, drive,
                               slew)) = pin_off_config
                if bank_voltage[bank] is not None and bank_voltage[
                        bank] != voltage:
                    continue

                ok, bank_vref[bank] = check_vref(bank_vref[bank], bank_type,
                                                 iostandard)

                if not ok:
                    continue

                assert bank_voltage[bank] is None or bank_voltage[
                    bank] == voltage
                if bank_voltage[bank] is None:
                    bank_voltage[bank] = voltage

                found_config = True
                break

            if not found_config:
                continue

            remaining_pin_offs[tiles[tile]].remove(pin_off_config)
            (site_offset, (iostandard, voltage, drive, slew)) = pin_off_config

            if drive is not None:
                attr = {
                    "DRIVE": drive,
                    "SLEW": slew,
                }
            else:
                attr = {}

            pin_config = (voltage, iostandard, "OBUF", attr)

            assert key in tile_offset_to_pin, (key, bank_type)
            off_pin = tile_offset_to_pin[tile, site_offset]
            config.append((off_pin, None))
            pins_left.remove(off_pin)

            for pin in pins:
                if off_pin == pin:
                    continue

                if tile != pin_to_tiles[pin]:
                    continue

                config.append((pin, pin_config))
                pins_left.remove(pin)

        for pin in pins_left:
            config.append((pin, None))

        pins_in_config = set()
        for pin, _ in config:
            pins_in_config.add(pin)

        bank_voltage = {}
        bank_vref = {}
        for bank in banks:
            bank_voltage[bank] = set()
            bank_vref[bank] = set()

        for pin, pin_config in config:
            if pin_config is None:
                continue

            pin_voltage, iostandard, prim, params = pin_config

            bank_voltage[pin_to_banks[pin]].add(pin_voltage)
            pin_vref = vref_for_bank(bank_type, iostandard)
            if pin_vref is not None:
                bank_vref[pin_to_banks[pin]].add(pin_vref)

        for bank in bank_voltage:
            assert len(bank_voltage[bank]) in [0, 1], (bank,
                                                       bank_voltage[bank])
            assert len(bank_vref[bank]) in [0, 1], (bank, bank_vref[bank])

        assert len(pins_in_config - set(pins)) == 0

        yield config

    for configs in remaining_configurations.values():
        assert len(configs) == 0, len(configs)


def read_io_pins(f):
    pin_to_banks = {}
    pin_to_sites = {}
    pin_to_site_offsets = {}

    tile_to_pins = {}
    tile_to_bank_types = {}
    pin_to_tile_types = {}

    bank_type_to_tiles = {}

    for row in csv.DictReader(f):
        bank = row['bank']
        pin = row['pin']
        site_name = row['site_name']
        site_type = row['site_type']
        tile = row['tile']
        tile_type = row['tile_type']

        assert pin not in pin_to_sites
        pin_to_sites[pin] = site_name

        assert pin not in pin_to_banks
        pin_to_banks[pin] = bank

        if tile not in tile_to_pins:
            tile_to_pins[tile] = []
        tile_to_pins[tile].append(pin)

        assert pin not in pin_to_tile_types
        pin_to_tile_types[pin] = tile_type

        bank_type = site_type.split('_')[0]
        if tile not in tile_to_bank_types:
            tile_to_bank_types[tile] = bank_type
        else:
            assert tile_to_bank_types[tile] == bank_type, tile

    bank_type_to_tiles = {}
    for tile, bank_type in tile_to_bank_types.items():
        if bank_type not in bank_type_to_tiles:
            bank_type_to_tiles[bank_type] = []
        bank_type_to_tiles[bank_type].append(tile)

    xy_fun = create_xy_fun('IOB_')

    for tile, tile_pins in tile_to_pins.items():
        assert len(tile_pins) > 0
        min_x, min_y = xy_fun(pin_to_sites[tile_pins[0]])

        for pin in tile_pins:
            x, y = xy_fun(pin_to_sites[pin])

            if x < min_x:
                min_x = x

            if y < min_y:
                min_y = y

        for pin in tile_pins:
            x, y = xy_fun(pin_to_sites[pin])
            pin_to_site_offsets[pin] = (x - min_x, y - min_y)

    return bank_type_to_tiles, tile_to_pins, pin_to_banks, pin_to_site_offsets, pin_to_tile_types
