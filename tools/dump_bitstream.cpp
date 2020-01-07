// Copyright 2020 Project U-Ray Authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include <vector>
#include <iostream>
#include <map>
#include <string>
#include <fstream>
#include <stdexcept>
#include <iterator>
#include <stdarg.h>
#include <iomanip>
#include "common.h"

const uint32_t preamble = 0xAA995566;

#define SKIP_CRC
#define SKIP_CHECKSUM
#define SKIP_COMMENT

class dummy_ostream : public std::ostream {

};

dummy_ostream dummy_out;

bool verbose_flag = false;

#define COMMENT(x) (verbose_flag ? std::cout : dummy_out) << x << std::endl


struct ByteStreamReader {
	std::vector<uint8_t> data;
	std::size_t ptr = 0;
	void reset() {
		ptr = 0;
	}
	bool done() {
		return ptr >= (data.size() - 3);
	}
	uint32_t curr_crc = 0;
	uint32_t curr_addr = 0;

	uint32_t next_u32(bool skip_crc = false) {
		if (done())
			throw std::runtime_error("at end of bitstream");
		uint32_t val = data[ptr] << 24UL | data[ptr+1] << 16UL | data[ptr+2] << 8UL | data[ptr+3];
		ptr += 4;
		if (!skip_crc)
			curr_crc = icap_crc(curr_addr, val, curr_crc);
		return val;
	}

	uint32_t peek_u32() {
		if (done())
			throw std::runtime_error("at end of bitstream");
		uint32_t val = data[ptr] << 24UL | data[ptr+1] << 16UL | data[ptr+2] << 8UL | data[ptr+3];
		return val;
	}
	void skip_till_preamble() {
		while (peek_u32() != preamble)
			++ptr;
		COMMENT("# found preamble at offset " << ptr);
		ptr += 4;
	}
};



enum BitstreamRegister : uint16_t {
	#define X(a, b) a = b,
	#include "registers.inc"
	#undef X
};



std::string get_register_name(uint16_t val) {
	BitstreamRegister r = (BitstreamRegister)val;
	#define X(a, b) if (val == a) return #a;
	#include "registers.inc"
	#undef X
	return stringf("reg%04x", val);
}

std::map<uint32_t, uint32_t> next_frame;

void parse_bitstream(ByteStreamReader &rd) {
	rd.reset();
	rd.skip_till_preamble();
	uint32_t frame = 0;
	uint16_t last_reg = 0;
	uint64_t checksum = 0, exp_checksum = 0;
	int word = 0;
	auto is_checksum = [] (int w, int b) {
		return ((w == 45 && b <= 31) || (w == 46 && b <= 15));
	};

	auto get_ecc_value = [](int word, int bit) {
		int nib = bit / 4;
		int nibbit = bit % 4;
		// ECC offset is expanded to 1 bit per nibble,
		// and then shifted based on the bit index in nibble
		// e.g. word 3, bit 9
		// offset: 0b10100110010 - concatenate (3 + (255 - 92)) [frame offset] and 9/4 [nibble offset]
		// becomes: 0x10100110010
		// shifted by bit in nibble (9%4): 0x20200220020
		uint32_t offset =  (word + (255 - 92)) << 3  | nib;
		uint64_t exp_offset = 0;
		// Odd parity
		offset ^= (1 << 11);
		for (int i = 0; i < 11; i++)
			if (offset & (1 << i)) offset ^= (1 << 11);
		// Expansion
		for (int i = 0; i < 12; i++)
			if (offset & (1 << i)) exp_offset |= (1ULL << (4 * i));
		return exp_offset << nibbit;
	};

	auto process_word = [&](uint32_t data) {


		for (int i = 0; i < 32; i++)
			if (data & (1 << i)) {
				if (is_checksum(word, i)) {
					checksum |= 1ULL << ((word - 45) * 32 + i);
#ifdef SKIP_CHECKSUM
					continue;
#endif
				} else {
					exp_checksum ^= get_ecc_value(word, i);
				}
				std::cout <<  stringf("F0x%08xW%03dB%02d", frame, word, i) << std::endl;
			}
		++word;
		if (word >= 93 && next_frame.count(frame)) {
			// 4 parity bits for each bit in nibbles
#if 0
			for (int i = 0; i < 4; i++)
				for (int j = 0; j < 11; j++)
					if (exp_checksum & (1ULL << (4 * j + i)))
						exp_checksum ^= (1ULL << (44 + i));
#endif
			COMMENT(stringf("# checksum: 0x%012llX calc: 0x%012llX %s", checksum, exp_checksum, (checksum == exp_checksum) ? "" : "~~~~~"));
			checksum = 0;
			exp_checksum = 0;
			frame = next_frame.at(frame);
		}
	};

	while (!rd.done()) {
		uint32_t hdr = rd.next_u32(true);
		if (hdr == 0xFFFFFFFF) {
			COMMENT("# desync");
			rd.skip_till_preamble();
			continue;
		}
		uint8_t type = (hdr >> 29) & 0x07;
		if (type == 0b001) {
			// Type 1 (short) packet
			uint8_t op = (hdr >> 27) & 0x03;
			switch(op) {
				case 0x00:
					COMMENT("# NOP ");
					// NOP
					break;
				case 0x01:
				    // READ
				    break;
				case 0x02: {
					// WRITE
					uint16_t reg = (hdr >> 13) & 0x3FFF;
					rd.curr_addr = reg;
					last_reg = reg;
					int count = hdr & 0x3FF;
					COMMENT("# write " << get_register_name(reg));
					if (reg == FAR) {
						if (count != 1)
							COMMENT("# bad FAR length " << count);
						exp_checksum = 0;
						checksum = 0;
						frame = rd.next_u32();
						word = 0;
						COMMENT(stringf("# frame 0x%08x", frame));
					} else if (reg == CRC) {
						uint32_t crc = 0;
						for(int i = 0; i < count; i++)
							crc = rd.next_u32(true);
						COMMENT(stringf("# CRC written=%08x calc=%08x %s", crc, rd.curr_crc, (crc == rd.curr_crc) ? "" : "*****"));
						rd.curr_crc = 0;
					} else if (reg == FDRI) {
						for(int i = 0; i < count; i++)
							process_word(rd.next_u32());
					} else if (reg == CMD) {
						uint32_t cmd = 0;
						for(int i = 0; i < count; i++)
							cmd = rd.next_u32();
						COMMENT(stringf("#     CMD %08x", cmd));
						if (cmd == 0x7)
							rd.curr_crc = 0;
					} else {
						for(int i = 0; i < count; i++)
							COMMENT(stringf("#     data %08x", rd.next_u32()));
					}

					if (reg == CRC && next_frame.count(frame)) {
						exp_checksum = 0;
						checksum = 0;
						frame = next_frame.at(frame);
					}

				} break;
			}
		} else if (type == 0b010) {
			// Type 2 (long) packet
			int count = hdr & 0x3FFFFFF;
			if (last_reg == FDRI) {
				for(int i = 0; i < count; i++)
					process_word(rd.next_u32());
			} else {
				for(int i = 0; i < count; i++)
					COMMENT(stringf("#     data %08x", rd.next_u32()));
			}
		} else {
			std::cout << stringf("# unknown packet type %01x (header: %08x)", type, hdr) << std::endl;
			return;
		}
	}
}

int main(int argc, char *argv[]) {
	if (argc < 2) {
		std::cerr << "Usage: dump_bitstream file.bit [frames.txt] [verbose]" << std::endl;
		return 2;
	}

	if (argc > 2) {
		std::ifstream frame_db(argv[2]);
		bool had_last = false;
		uint32_t last;
		uint32_t val;
		frame_db.unsetf(std::ios::dec);
		frame_db.unsetf(std::ios::hex);
		frame_db.unsetf(std::ios::oct);
		while (frame_db >> val) {
			if (had_last)
				next_frame[last] = val;
			last = val;
			had_last = true;
		}
	}

	if (argc > 3) {
		if (std::string(argv[3]) == "verbose")
			verbose_flag = true;
	}

	ByteStreamReader rd;
	std::ifstream file(argv[1], std::ios::binary);
	file.unsetf(std::ios::skipws);
	if (!file) {
		std::cerr << "Failed to open input file" << std::endl;
		return 2;
	}
	rd.data.insert(rd.data.begin(), std::istream_iterator<uint8_t>(file), std::istream_iterator<uint8_t>());
	parse_bitstream(rd);
}