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
#include <unordered_set>
#include <unordered_map>
#include <set>
#include <sstream>
#include <algorithm>
#include <filesystem>
namespace fs = std::filesystem;

struct FeatureData {
	std::unordered_set<int> always_set_with_feature;
	std::unordered_set<int> never_set_with_feature;
	std::unordered_set<int> always_set_without_feature;

	std::vector<std::pair<int, bool>> featbits;
	std::set<std::string> deps;
	int count;
};

struct TileTypeData {
	std::unordered_map<std::string, std::unordered_set<std::string>> inst_features;
	std::unordered_map<std::string, std::unordered_set<int>> inst_bits;
	std::unordered_set<int> settable_bits;
	std::set<std::string> extant_features;
	std::unordered_map<std::string, FeatureData> features;
};

std::map<std::string, TileTypeData> tiletypes;
std::set<std::string> include_tts;

std::pair<std::string, std::string> split_tilename(const std::string &name) {
	size_t idx = name.find(':');
	return std::make_pair(name.substr(0, idx), name.substr(idx+1));
}

void parse_bits(const std::string &prefix, std::istream &in) {
	std::string line;
	std::unordered_set<int> *bits = nullptr;
	std::unordered_set<int> *settable_bits = nullptr;
	bool skip = false;

	while (std::getline(in, line)) {
		if (line.empty())
			continue;
		std::istringstream iss(line);
		if (line.front() == '.') {
			std::string t, tn;
			iss >> t >> tn;
			auto spn = split_tilename(tn);
			if (!include_tts.empty() && !include_tts.count(spn.second)) {
				skip = true;
				continue;
			} else {
				skip = false;
			}
			settable_bits = &(tiletypes[spn.second].settable_bits);
			bits = &(tiletypes[spn.second].inst_bits[prefix + spn.first]);
		} else {
			int bit = -1;
			iss >> bit;
			if (!skip && bit != -1) {
				bits->insert(bit);
				settable_bits->insert(bit);
			}
		}
	}
}

void parse_features(const std::string &prefix, std::istream &in) {
	std::string line;
	std::unordered_set<std::string> *feats = nullptr;
	std::set<std::string> *ext_feats = nullptr;
	bool skip = false;

	while (std::getline(in, line)) {
		if (line.empty())
			continue;
		std::istringstream iss(line);
		if (line.front() == '.') {
			std::string t, tn;
			iss >> t >> tn;
			auto spn = split_tilename(tn);
			if (!include_tts.empty() && !include_tts.count(spn.second)) {
				skip = true;
				continue;
			} else {
				skip = false;
			}
			ext_feats = &(tiletypes[spn.second].extant_features);
			feats = &(tiletypes[spn.second].inst_features[prefix + spn.first]);
		} else {
			std::string feat;
			iss >> feat;
			if (!feat.empty() && !skip) {
				feats->insert(feat);
				ext_feats->insert(feat);
			}
		}
	}
}

template <typename Tc, typename Tv, typename Tf> void set_erase_if(Tc &target, std::vector<Tv> &temp, Tf pred) {
	temp.clear();
	for (auto &entry : target)
		if (pred(entry))
			temp.push_back(entry);
	for (auto &toerase : temp)
		target.erase(toerase);
}

void find_feature_deps(TileTypeData &tt) {
	for (auto &f : tt.extant_features) {
		auto &fd = tt.features[f];
		fd.deps = tt.extant_features;
		fd.deps.erase(f);
		std::vector<std::string> temp;
		for (auto &inst : tt.inst_features) {
			if (!inst.second.count(f))
				continue;
			set_erase_if(fd.deps, temp, [&](const std::string &ef){ return !inst.second.count(ef); });
		}
	}
}

void process_feature(TileTypeData &tt, const std::string &feature) {

	FeatureData &fd = tt.features[feature];

	fd.always_set_with_feature = tt.settable_bits;
	//fd.never_set_with_feature = tt.settable_bits;
	fd.always_set_without_feature = tt.settable_bits;

	std::vector<int> temp;
	fd.count = 0;
	bool always_have_feature = true;
	for (auto &inst : tt.inst_bits) {
		if (!tt.inst_features.count(inst.first))
			continue;
		auto &ib = inst.second;
		bool has_feature =  tt.inst_features.at(inst.first).count(feature);
		if (!has_feature)
			always_have_feature = false;

		if (has_feature)
			++fd.count;

		if (has_feature)
			set_erase_if(fd.always_set_with_feature, temp, [&](int bit){ return !ib.count(bit); });
		//if (has_feature)
		//	set_erase_if(fd.never_set_with_feature, temp, [&](int bit){ return ib.count(bit); });
		if (!has_feature)
			set_erase_if(fd.always_set_without_feature, temp, [&](int bit){ return !ib.count(bit); });
	}
	for (int as : fd.always_set_with_feature)
		if (always_have_feature || !fd.always_set_without_feature.count(as))
			if (std::all_of(fd.deps.begin(), fd.deps.end(), [&](const std::string &dep) {
						auto &dd = tt.features[dep];
						return std::find(dd.featbits.begin(), dd.featbits.end(), std::make_pair(as, false)) == dd.featbits.end();
					}))
				fd.featbits.emplace_back(as, false);
	/*for (int nv : fd.never_set_with_feature)
		if (fd.always_set_without_feature.count(nv))
			fd.featbits.emplace_back(nv, true);*/
	// FIXME: inverted feature bits?
	std::sort(fd.featbits.begin(), fd.featbits.end());
}

int main(int argc, char *argv[]) {
	if (argc < 3) {
		std::cerr << "usage: correlate specfolder tiledata" << std::endl;
		return 2;
	}

	if (argc > 3) {
		for (int i = 3; i < argc; i++)
			include_tts.insert(argv[i]);
	}

	for (const auto &entry : fs::directory_iterator(argv[1])) {
		auto p = entry.path();
		if (p.extension() != ".features")
			continue;
		std::ifstream tilebits(p.parent_path().string() + "/" + p.stem().string() + ".tbits");
		if (!tilebits) {
			std::cerr << "Failed to open " << (p.parent_path().string() + "/" + p.stem().string() + ".tbits") << std::endl;
			return 1;
		}
		parse_bits(p.stem().string(), tilebits);
		std::ifstream features(p.string());
		if (!features) {
			std::cerr << "Failed to open " << p.string() << std::endl;
			return 1;
		}
		parse_features(p.stem().string(), features);
	}



	for (auto &tiletype : tiletypes) {
		auto &t = tiletype.second;
		std::ofstream td(std::string(argv[2]) + "/" + tiletype.first + ".bits");
		find_feature_deps(tiletype.second);
		std::vector<std::string> ord_feats(t.extant_features.begin(),
			t.extant_features.end());
		std::stable_sort(ord_feats.begin(), ord_feats.end(), [&](const std::string &a, const std::string &b) {
			return t.features[a].deps.size() < t.features[b].deps.size();
		});

		for (auto &feat : ord_feats) {
			std::cerr << "Processing " << tiletype.first << "." << feat << std::endl;
			FeatureData fd;
			process_feature(t, feat);
		}

		for (auto &feat : t.extant_features) {
			auto &fd = t.features[feat];
			if (fd.count < 2)
				continue;
			td << feat;
			for (auto &fb : fd.featbits)
				td << " " << (fb.second ? "!" : "") << fb.first;
			td << " # count: " << fd.count;
			if  (fd.deps.size() > 0) {
				td << ", deps: ";
				for (auto &d : fd.deps)
					td << " " << d;
			}
			td << std::endl;
		}
	}

	return 0;
}