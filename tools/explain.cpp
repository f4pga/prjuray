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
#include <filesystem>
#include <map>
#include <set>
#include <cassert>
#include "common.h"

ChipData chip;

struct Tile {
	std::string name, type;
	TileInstance *data;
	std::set<int> set_bits;
	std::set<int> unknown_bits;
	std::set<std::string> matched_features;
};

std::vector<Tile> tiles;
std::unordered_map<std::string, int> tile_by_name;

struct InverseTileBitMap {
	int tile;
	int offset_in_frame;
	int offset_in_tile;
	int size;
};

std::unordered_map<uint32_t, std::vector<InverseTileBitMap>> tiles_by_frame;

void parse_bits(const std::string &filename) {
	LineReader rd(filename);
	for (auto &line : rd) {
		assert(line.at(0) == 'F');
		const char *curr = line.c_str() + 1;
		char *next = nullptr;
		uint32_t frame = std::strtoul(curr, &next, 16);
		assert(*next == 'W');
		curr = next + 1;
		int word = std::strtol(curr, &next, 10);
		curr = next + 1;
		assert(*next == 'B');
		int bit = std::strtol(curr, &next, 10);
		if (tiles_by_frame.count(frame)) {
			int fb = word * 32 + bit;
			for (auto &t : tiles_by_frame.at(frame)) {
				if (fb >= t.offset_in_frame && fb < (t.offset_in_frame + t.size)) {
					int tilebit = (fb - t.offset_in_frame) + t.offset_in_tile;
					tiles[t.tile].set_bits.insert(tilebit);
					tiles[t.tile].unknown_bits.insert(tilebit);
				}
			}
		}
	}
}

// Currently have poor quality DBs for these tiles,
// skip outputting them
std::set<std::string> skip_tiles = {
	"CLEL_L", "CLEM_R", "RCLK_INT_R",
};


void setup_tiles() {
	for (auto &tile : chip.tiles) {
		auto &ti = tile.second;
		if (skip_tiles.count(chip.tiletypes[ti.type].type))
			continue;
		Tile t;
		t.name = ti.name;
		t.type = chip.tiletypes[ti.type].type;
		t.data = &ti;
		tile_by_name[ti.name] = int(tiles.size());

		int off = 0;
		for (auto &b : ti.bits) {
			tiles_by_frame[b.frame_offset].push_back(InverseTileBitMap{int(tiles.size()), b.bit_offset, off, b.size});
			off += b.size;
		}

		tiles.push_back(t);

	}
}


void process_tile(Tile &t) {
	if (t.set_bits.empty())
		return;
	auto &td = chip.load_tile_database(t.name);
	for (const auto &feat : td.features) {
		if (feat.second.empty())
			continue;
		bool matched = true;
		for (auto bit : feat.second)
			if (!t.set_bits.count(bit)) {
				matched = false;
				break;
			}
		if (!matched)
			continue;
		t.matched_features.insert(feat.first);
		for (auto bit : feat.second)
			t.unknown_bits.erase(bit);
	}
}

int main(int argc, char *argv[]) {
	if (argc < 3) {
		std::cerr << "usage: explain dbdir/ bitstream.dump" << std::endl;
		return 2;
	}
	chip.open(argv[1]);
	setup_tiles();
	parse_bits(argv[2]);
	for (auto &t : tiles) {
		process_tile(t);
		for (auto &f : t.matched_features)
			std::cout << t.name << "." << f << std::endl;
		for (auto b : t.unknown_bits)
			std::cout << t.name << ".?" << b << std::endl;
		if (!t.matched_features.empty() || !t.unknown_bits.empty())
			std::cout << std::endl;
	}
}