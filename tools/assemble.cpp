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

#include <iostream>
#include <fstream>
#include <string>
#include <unordered_set>
#include <unordered_map>
#include <map>
#include <set>
#include <cassert>
#include <stdexcept>
#include <stdarg.h>
#include "common.h"

enum BitstreamRegister : uint16_t {
	#define X(a, b) a = b,
	#include "registers.inc"
	#undef X
};


ChipData chip;

std::unordered_set<uint32_t> roi_frames;
std::map<uint32_t, std::vector<bool>> frames;
std::map<uint32_t, uint32_t> next_frame;
std::string db_root;


void set_tile_bit(const TileInstance &tile, int bit) {
	int pos = 0;
	for (auto &bm : tile.bits) {
		if (bit >= pos && bit < (pos + bm.size)) {
			frames.at(bm.frame_offset).at(bm.bit_offset + (bit - pos)) = true;
			return;
		}
		pos += bm.size;
	}
	throw std::runtime_error("bad bit " + tile.name + "." + std::to_string(bit));
}


void set_feature(const std::string &tile, const std::string &feature) {
	auto &db = chip.load_tile_database(tile);
	if (!db.features.count(feature)) {
		throw std::runtime_error("unknown feature " + feature + " in tile " + tile);
	}
	const auto &fbits = db.features.at(feature);
	auto &t = chip.tiles[tile];
	for (auto bit : fbits)
		set_tile_bit(t, bit);
}

void read_quasi_fasm(const std::string &filename) {
	LineReader rd(filename);
	std::vector<std::string> split;
	for (auto &line : rd) {
		split_str(line, split, ".", true, 1);
		if (split.size() < 2)
			continue;
		set_feature(split.at(0), split.at(1));
	}
}

// Add ECCs to frames
void add_frame_ecc() {

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

	for (auto &fr : frames) {
		auto &bits = fr.second;
		uint64_t ecc = 0;
		for (int word = 0; word < 93; word++) {
			for (int i = 0; i < 32; i++) {
				if (!bits.at(word * 32 + i))
					continue;
				if ((word == 45) || ((word == 46 && (i < 16)))) {
					bits.at(word * 32 + i) = false;
					continue;
				}
				ecc ^= get_ecc_value(word, i);
			}
		}
		for (int i = 0; i < 48; i++)
			if (ecc & (1ULL << i))
				bits.at(45*32 + i) = true;
	}
}


struct ByteStreamWriter {
	std::vector<uint8_t> data;

	uint32_t curr_crc = 0;
	uint32_t curr_addr = 0;

	void write_byte(uint8_t byte) {
		data.push_back(byte);
	}
	void write_bytes(const std::vector<uint8_t> &bytes) {
		data.insert(data.end(), bytes.begin(), bytes.end());
	}
	void write_string(const std::string &str) {
		int len = int(str.length()) + 1;
		data.push_back((len >> 8) & 0xFF);
		data.push_back(len & 0xFF);
		for (char c : str) data.push_back(uint8_t(c));
		data.push_back(0x00);
	}
	void write_u32(uint32_t word, bool update_crc = false) {
		data.push_back((word >> 24) & 0xFF);
		data.push_back((word >> 16) & 0xFF);
		data.push_back((word >>  8) & 0xFF);
		data.push_back((word >>  0) & 0xFF);
		if (update_crc)
			curr_crc = icap_crc(curr_addr, word, curr_crc);
	}
	void write_short_packet(BitstreamOp op, BitstreamRegister reg = BitstreamRegister(0x00), const std::vector<uint32_t> &payload = {}) {
		curr_addr = uint32_t(reg);
		write_u32((0b001UL << 29) | ((uint32_t(op) & 0x03) << 27) | ((uint32_t(reg) & 0x3FFF) << 13) | (uint32_t(payload.size()) & 0x3FFF));
		for (uint32_t x : payload)
			write_u32(x, true);
	}
	void write_long_packet(const std::vector<uint32_t> &payload) {
		write_u32((0b010UL << 29) | (uint32_t(OP_READ) << 27) | (uint32_t(payload.size()) & 0x3FFFFFF));
		for (uint32_t x : payload)
			write_u32(x, true);
	}
	void write_crc() {
		write_short_packet(OP_WRITE, CRC, {curr_crc});
		curr_crc = 0;
	}
};

void write_bitstream(std::ofstream &f) {
#if 0
	// FIXME - write an actual binary bitstream
	for (auto &frame : frames) {
		for (size_t i = 0; i < frame.second.size(); i++) {
			if (frame.second.at(i))
				f << stringf("F%08xW%03dB%02d", frame.first, int(i / 32), int(i % 32)) << std::endl;
		}
	}
#else

	add_frame_ecc();

	ByteStreamWriter bsw;
	// Header
	bsw.write_bytes({0x00, 0x09, 0x0F, 0xF0, 0x0F, 0xF0, 0x0F, 0xF0, 0x0F, 0xF0, 0x00, 0x00, 0x01, 0x61});
	bsw.write_string("top;UserID=0XFFFFFFFF;Version=2019.1");
	bsw.write_byte(0x62);
	bsw.write_string("xczu7ev-ffvc1156-2-e");
	bsw.write_byte(0x63);
	bsw.write_string("2019/09/08");
	bsw.write_byte(0x64);
	bsw.write_string("00:00:00");
	bsw.write_bytes({0x65, 0x01, 0x36, 0x6F, 0xB0});
	for (int i = 0; i < 64; i++)
		bsw.write_byte(0xFF);
	bsw.write_bytes({0x00, 0x00, 0x00, 0xBB, 0x11, 0x22, 0x00, 0x44});
	for (int i = 0; i < 8; i++)
		bsw.write_byte(0xFF);
	// Preamble
	bsw.write_u32(0xAA995566);
	// Initial commands
	bsw.write_short_packet(OP_NOP);
	bsw.write_short_packet(OP_NOP);
	bsw.write_short_packet(OP_WRITE, TIMER, {0x00000000});
	bsw.write_short_packet(OP_WRITE, WBSTAR, {0x00000000});
	bsw.write_short_packet(OP_WRITE, CMD, {0x00000000});
	bsw.write_short_packet(OP_NOP);
	bsw.write_short_packet(OP_WRITE, CMD, {0x00000007});
	bsw.curr_crc = 0;
	bsw.write_short_packet(OP_NOP);
	bsw.write_short_packet(OP_NOP);
	bsw.write_short_packet(OP_WRITE, FAR, {0x00000000});
	bsw.write_short_packet(OP_WRITE, BitstreamRegister(0x13), {0x00000000});
	bsw.write_short_packet(OP_WRITE, COR0, {0x38003fe5});
	bsw.write_short_packet(OP_WRITE, COR1, {0x00400000});
	bsw.write_short_packet(OP_WRITE, IDCODE, {0x04a5a093});
	bsw.write_short_packet(OP_WRITE, CMD, {0x00000009});
	bsw.write_short_packet(OP_NOP);
	bsw.write_short_packet(OP_WRITE, MASK, {0x00000001});
	bsw.write_short_packet(OP_WRITE, CTL0, {0x00000101});
	bsw.write_short_packet(OP_WRITE, MASK, {0x00200000});
	bsw.write_short_packet(OP_WRITE, CTL1, {0x00200000});
	for (int i = 0; i < 8; i++)
		bsw.write_short_packet(OP_NOP);
	bsw.write_short_packet(OP_WRITE, CMD, {0x00000001});
	bsw.write_short_packet(OP_NOP);
	// Frame data
	std::vector<uint32_t> fdata(93, 0x00000000);
	bsw.write_short_packet(OP_WRITE, FAR, {frames.begin()->first});
	for (auto &fr : frames) {
		for (int i = 0; i < 93; i++) {
			fdata[i] = 0x00000000;
			for (int j = 0; j < 32; j++)
				if (fr.second.at(i * 32 + j))
					fdata[i] |= (1 << j);
		}
		bsw.write_short_packet(OP_WRITE, FDRI, fdata);
		bsw.write_short_packet(OP_WRITE, FAR, {fr.first});
		bsw.write_crc();
		if (!next_frame.count(fr.first) || ((next_frame.at(fr.first) ^ fr.first) & 0xFFFC0000)) {
			// Duplicate last frame in a row, but empty??
			for (int i = 0; i < 93; i++)
				fdata[i] = 0;
			bsw.write_short_packet(OP_WRITE, FDRI, fdata);
			bsw.write_short_packet(OP_WRITE, FAR, {fr.first});
			bsw.write_crc();
			if (next_frame.count(fr.first)) {
				// CMD 1 (WCFG)
				bsw.write_short_packet(OP_WRITE, CMD, {0x00000001});
				bsw.write_short_packet(OP_NOP);
				// Next frame address
				bsw.write_short_packet(OP_WRITE, FAR, {next_frame.at(fr.first)});
			}
		}

		//bsw.write_long_packet(fdata);
	}
	// End of bitstream
	bsw.write_short_packet(OP_WRITE, CMD, {0x00000000});
	bsw.write_short_packet(OP_NOP);
	bsw.write_short_packet(OP_NOP);
	bsw.write_short_packet(OP_WRITE, MASK, {0x00200000});
	bsw.write_short_packet(OP_WRITE, CTL1, {0x00000000});
	bsw.write_crc();
	bsw.write_short_packet(OP_NOP);
	bsw.write_short_packet(OP_NOP);
	bsw.write_short_packet(OP_WRITE, CMD, {0x0000000a});
	bsw.write_short_packet(OP_NOP);
	bsw.write_short_packet(OP_NOP);
	bsw.write_short_packet(OP_WRITE, CMD, {0x00000003});
	for (int i = 0; i < 20; i++)
		bsw.write_short_packet(OP_NOP);
	bsw.write_short_packet(OP_WRITE, CMD, {0x00000005});
	bsw.write_short_packet(OP_NOP);
	bsw.write_short_packet(OP_WRITE, FAR, {0x07FC0000});
	bsw.write_short_packet(OP_WRITE, MASK, {0x00000101});
	bsw.write_short_packet(OP_WRITE, CTL0, {0x00000101});
	bsw.write_crc();
	bsw.write_short_packet(OP_NOP);
	bsw.write_short_packet(OP_NOP);
	bsw.write_short_packet(OP_WRITE, CMD, {0x0000000d});
	for (int i = 0; i < 400; i++)
		bsw.write_short_packet(OP_NOP);
	f.write(reinterpret_cast<const char *>(&(bsw.data[0])), bsw.data.size());
#endif
}

void parse_harness(const std::string &filename) {
	LineReader rd(filename);
	for (auto &line : rd) {
		assert(line.at(0) == 'F');
		const char *curr = line.c_str() + 1;
		char *next = nullptr;
		uint32_t frame = std::strtoul(curr, &next, 16);
		if (roi_frames.count(frame))
			continue;
		assert(*next == 'W');
		curr = next + 1;
		int word = std::strtol(curr, &next, 10);
		curr = next + 1;
		assert(*next == 'B');
		int bit = std::strtol(curr, &next, 10);
		frames[frame].at(word * 32 + bit) = true;
	}
}

void parse_frames(const std::string &filename, std::unordered_set<uint32_t> &dest_set) {
	LineReader rd(filename);
	for (auto &line : rd) {
		const char *start = line.c_str();
		char *end = nullptr;
		uint32_t addr = std::strtol(start, &end, 16);
		if ((end == nullptr) || (end == start))
			continue;
		dest_set.insert(addr);
		frames[addr].clear();
		frames[addr].resize(93*32, false);
	}
}

void setup_base_frames() {
	uint32_t last_frame = 0xFFFFFFFF;
	for (auto addr : chip.all_frames) {
		if (addr == 0x07FC0000)
			continue;
		frames[addr].clear();
		frames[addr].resize(93*32, false);
		if (last_frame != 0xFFFFFFFF)
			next_frame[last_frame] = addr;
		last_frame = addr;
	}
}

int main(int argc, char *argv[]) {
	if (argc < 6) {
		std::cerr << "Usage: ./assemble dbdir roi_frames.txt harness.txt input.fasm out.bit" << std::endl;
		return 2;
	}
	db_root = argv[1];
	chip.open(db_root);
	setup_base_frames();
	parse_frames(argv[2], roi_frames);
	parse_harness(argv[3]);
	read_quasi_fasm(argv[4]);
	std::ofstream obf(argv[5], std::ios::binary);
	if (!obf) {
		std::cerr << "failed to open " << argv[5] << std::endl;
		return 1;
	}
	write_bitstream(obf);
}