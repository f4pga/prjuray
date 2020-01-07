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
'''
UltraScalePlus bitstream analyzer tool.

This script reads a UltraScalePlus bitstream and prints out some useful information.
It can also create a frames file with the configuration data words.
The bitstream is analyzed word by word and interpreted according to
the UG570 Configuration User Guide.

The tool can be used to derive the initialization, startup and finalization
sequence as well as the configuration data. The latter is written to a frames
file which can be used by the bitstream tools such as frames2bit to generate
a valid bitstream.
'''

import argparse
from io import StringIO

conf_regs = {
    0: "CRC",
    1: "FAR",
    2: "FDRI",
    3: "FDRO",
    4: "CMD",
    5: "CTL0",
    6: "MASK",
    7: "STAT",
    8: "LOUT",
    9: "COR0",
    10: "MFWR",
    11: "CBC",
    12: "IDCODE",
    13: "AXSS",
    14: "COR1",
    16: "WBSTAR",
    17: "TIMER",
    22: "BOOTSTS",
    24: "CTL1",
    31: "BSPI"
}

cmd_reg_codes = {
    0: "NULL",
    1: "WCFG",
    2: "MFW",
    3: "LFRM",
    4: "RCFG",
    5: "START",
    7: "RCRC",
    8: "AGHIGH",
    9: "SWITCH",
    10: "GRESTORE",
    11: "SHUTDOWN",
    13: "DESYNC",
    15: "IPROG",
    16: "CRCC",
    17: "LTIMER",
    18: "BSPI_READ",
    19: "FALL_EDGE"
}

opcodes = ("NOP", "READ", "WRITE", "UNKNOWN")


def knuth_morris_pratt(text, pattern):
    '''
    Yields all starting positions of copies of the pattern in the text.
    Calling conventions are similar to string.find, but its arguments can be
    lists or iterators, not just strings, it returns all matches, not just
    the first one, and it does not need the whole text in memory at once.
    Whenever it yields, it will have read the text exactly up to and including
    the match that caused the yield.
    '''

    # allow indexing into pattern and protect against change during yield
    pattern = list(pattern)

    # build table of shift amounts
    shifts = [1] * (len(pattern) + 1)
    shift = 1
    for pos in range(len(pattern)):
        while shift <= pos and pattern[pos] != pattern[pos - shift]:
            shift += shifts[pos - shift]
        shifts[pos + 1] = shift

    # do the actual search
    startPos = 0
    matchLen = 0
    for c in text:
        while matchLen == len(pattern) or \
              matchLen >= 0 and pattern[matchLen] != c:
            startPos += shifts[matchLen]
            matchLen -= shifts[matchLen]
        matchLen += 1
        if matchLen == len(pattern):
            yield startPos


class Bitstream:
    BITS_PER_WORD = 16
    WORDS_PER_FRAME = 93

    def __init__(self, file_name, verbose=False):
        self.frames_data = dict()
        self.current_far_address = 0
        self.fdri_write_len = 0
        self.fdri_in_progress = False
        self.words = []
        with open(file_name, "rb") as f:
            self.bytes = f.read()
        pos, self.header = self.get_header()
        for byte3, byte2, byte1, byte0 in zip(
                self.bytes[pos::4], self.bytes[pos + 1::4],
                self.bytes[pos + 2::4], self.bytes[pos + 3::4]):
            self.words.append(
                int.from_bytes([byte3, byte2, byte1, byte0], byteorder='big'))
        self.parse_bitstream(verbose)

    def get_header(self):
        '''Return position and content of header'''
        pos = next(knuth_morris_pratt(self.bytes, [0xaa, 0x99, 0x55, 0x66]))
        return pos + 4, self.bytes[:pos + 4]

    def parse_bitstream(self, verbose):
        payload_len = 0
        for word in self.words:
            if payload_len > 0:
                payload_len = self.parse_reg(reg_addr, word, payload_len,
                                             verbose)
                continue
            else:
                packet_header = self.parse_packet_header(word)
                opcode = packet_header["opcode"]
                reg_addr = packet_header["reg_addr"]
                words = packet_header["word_count"]
                type = packet_header["type"]
                if verbose:
                    if not opcode:
                        print("\n\tNOP")
                    else:
                        print(
                            "\n\tConfiguration Register Word: ", hex(word),
                            'Type: {}, Op: {}, Addr: {} ({}), Words: {}'.
                            format(
                                type, opcodes[opcode], conf_regs[reg_addr]
                                if reg_addr in conf_regs else "UNKNOWN",
                                reg_addr, words))
                if opcode and reg_addr in conf_regs:
                    payload_len = words
                    if conf_regs[reg_addr] == "FDRI" and type == 1:
                        self.fdri_in_progress = True
                        self.frames_data[self.current_far_address] = list()
                        self.fdri_write_len = payload_len
                    continue

    def parse_packet_header(self, word):
        type = (word >> 29) & 0x7
        opcode = (word >> 27) & 0x3
        reg_addr = (word >> 13) & 0x1F
        if type == 1:
            word_count = word & 0x7FF
        elif type == 2:
            word_count = word & 0x7FFFFFF
        else:
            word_count = 0
        return {
            "type": type,
            "opcode": opcode,
            "reg_addr": reg_addr,
            "word_count": word_count
        }

    def parse_command(self, word, verbose):
        if verbose:
            print("\tCommand: {} ({})".format(cmd_reg_codes[word], word))

    #TODO Add COR0 options parsing
    def parse_cor0(self, word, verbose):
        if verbose:
            print("\tCOR0 options: {:08X}".format(word))

    def parse_far(self, word, verbose):
        self.current_far_address = word
        block_type = (word >> 24) & 0x7
        row_addr = (word >> 18) & 0x3F
        col_addr = (word >> 8) & 0x3FF
        minor_addr = word & 0xFF
        if verbose:
            print("\tFAR address: {:08X}".format(word))
            print("\tBlock: {:08X}, Row: {:08X}, Col: {:08X}, Minor: {:08X}".
                  format(block_type, row_addr, col_addr, minor_addr))

    def parse_reg(self, reg_addr, word, payload_len, verbose):
        assert reg_addr in conf_regs
        reg = conf_regs[reg_addr]
        if reg == "CMD":
            self.parse_command(word, verbose)
        elif reg == "COR0":
            self.parse_cor0(word, verbose)
        elif reg == "FAR":
            self.parse_far(word, verbose)
        elif reg == "FDRI":
            # We are in progress of a FDRI operation
            # Keep adding data words
            if self.fdri_in_progress:
                if verbose:
                    print("\t{:2d}. 0x{:08X}".format(
                        self.fdri_write_len - payload_len, word))
                # Convert 32-bit word to words with the specified word length
                byte0 = word & 0xFF
                byte1 = (word >> 8) & 0xFF
                byte2 = (word >> 16) & 0xFF
                byte3 = (word >> 24) & 0xFF
                if self.BITS_PER_WORD == 32:
                    self.frames_data[self.current_far_address].append(
                        int.from_bytes([byte3, byte2, byte1, byte0],
                                       byteorder='big'))
                elif self.BITS_PER_WORD == 16:
                    word0 = int.from_bytes([byte1, byte0], byteorder='big')
                    self.frames_data[self.current_far_address].append(word0)
                    word1 = int.from_bytes([byte3, byte2], byteorder='big')
                    self.frames_data[self.current_far_address].append(word1)
                else:
                    assert False
                if payload_len == 1:
                    self.fdri_in_progress = False
                    return 0
            else:
                #FIXME add Type 2 FDRI writes
                assert False
                #self.curr_fdri_write_len = word
                #self.fdri_in_progress = True
                # Check if 0 words actually means read something
                #payload_len = self.curr_fdri_write_len
                #if verbose:
                #    print("\t{}: {}\n".format(reg, self.curr_fdri_write_len))
                #return payload_len
        else:
            if verbose:
                print("\tRegister: {} Value: 0x{:08X}".format(reg, word))
        payload_len -= 1
        return payload_len

    def write_frames_txt(self, file_name):
        '''Write frame data in a more readable format'''
        words_per_frame = self.WORDS_PER_FRAME * (32 / self.BITS_PER_WORD)
        frame_stream = StringIO()
        for addr, words in self.frames_data.items():
            assert len(words) == words_per_frame
            for i in range(len(words)):
                if i % words_per_frame == 0:
                    frame_stream.write("0x{:08x}\n".format(addr))
                frame_stream.write("{}. 0x{:04x}\n".format(i, words[i]))
                if i % words_per_frame == words_per_frame - 1:
                    frame_stream.write("\n")
        with open(file_name, "w") as f:
            print(frame_stream.getvalue(), file=f)

    def write_frames(self, file_name):
        '''Write configuration data to frames file'''
        words_per_frame = self.WORDS_PER_FRAME * (32 / self.BITS_PER_WORD)
        frame_stream = StringIO()
        for addr, words in self.frames_data.items():
            assert len(words) == words_per_frame
            for i in range(len(words)):
                if i % words_per_frame == 0:
                    frame_stream.write("0x{:08x} ".format(addr))
                frame_stream.write("0x{:04x}".format(words[i]))
                if i % words_per_frame == words_per_frame - 1:
                    frame_stream.write("\n")
                elif i < len(words) - 1:
                    frame_stream.write(",")
        with open(file_name, "w") as f:
            print(frame_stream.getvalue(), file=f)


def main(args):
    verbose = not args.silent
    bitstream = Bitstream(args.bitstream, verbose)
    print("Frame data length: ", len(bitstream.frames_data))
    if args.frames_out:
        bitstream.write_frames(args.frames_out)
    if args.frames_txt:
        bitstream.write_frames_txt(args.frames_txt)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--bitstream', help='Input bitstream')
    parser.add_argument('--frames_out', help='Output frames file')
    parser.add_argument(
        '--frames_txt', help='Output frames in more readable form')
    parser.add_argument(
        '--silent', help="Don't print analysis details", action='store_true')
    args = parser.parse_args()
    main(args)
