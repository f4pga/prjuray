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

#include "common.h"


void ChipData::open(const std::string &root) {
	this->root = root;
	load_frames();
	load_tiles();
}

void ChipData::load_frames() {
	LineReader rd(root + "/frames.txt");
	for (const std::string &line : rd) {
		all_frames.insert(std::strtoul(line.c_str(), nullptr, 16));
	}
}

void ChipData::load_tiletype_database(int type) {
	auto &tt = tiletypes.at(type);
	if (tt.loaded_db)
		return;
	LineReader rd(root + "/" + tt.type + ".bits");
	std::vector<std::string> split;
	for (const std::string &line : rd) {
		split_str(line, split);
		if (split.size() < 1)
			continue;
		auto &feat = tt.features[split.at(0)];
		for (size_t i = 1; i < split.size(); i++)
			feat.push_back(std::stoi(split.at(i)));
	}
	tt.loaded_db = true;
}

void ChipData::load_tiles() {
	LineReader rd(root + "/tiles.txt");
	std::vector<std::string> split;
	TileInstance *curr = nullptr;

	for (const std::string &line : rd) {
		split_str(line, split);
		if (split.size() < 1)
			continue;
		if (split.at(0) == ".tile") {
			curr = &(tiles[split.at(1)]);
			curr->name = split.at(1);
			if (!tiletype_by_name.count(split.at(2))) {
				tiletype_by_name[split.at(2)] = int(tiletypes.size());
				curr->type = int(tiletypes.size());
				tiletypes.emplace_back();
				tiletypes.back().type = split.at(2);
			} else {
				curr->type = tiletype_by_name.at(split.at(2));
			}
			curr->x = std::stoi(split.at(3));
			curr->y = std::stoi(split.at(4));
		} else if (split.at(0) == "frame") {
			TileInstance::TileBitMapping tbm;
			tbm.frame_offset = std::strtoul(split.at(1).c_str(), nullptr, 16);
			tbm.bit_offset = std::stoi(split.at(3));
			tbm.size = std::stoi(split.at(5));
			curr->bits.push_back(tbm);
		}
	}
}


