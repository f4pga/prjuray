#ifndef COMMON_H
#define COMMON_H

#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <stdarg.h>
#include <stdexcept>
#include <stdint.h>
#include <string>
#include <unordered_map>
#include <vector>
constexpr uint32_t kCrc32CastagnoliPolynomial = 0x82F63B78;

// From prjxray
// The CRC is calculated from each written data word and the current
// register address the data is written to.

// Extend the current CRC value with one register address (5bit) and
// frame data (32bit) pair and return the newly computed CRC value.

inline uint32_t icap_crc(uint32_t addr, uint32_t data, uint32_t prev) {
  constexpr int kAddressBitWidth = 5;
  constexpr int kDataBitWidth = 32;

  uint64_t poly = static_cast<uint64_t>(kCrc32CastagnoliPolynomial) << 1;
  uint64_t val = (static_cast<uint64_t>(addr) << 32) | data;
  uint64_t crc = prev;

  for (int i = 0; i < kAddressBitWidth + kDataBitWidth; i++) {
    if ((val & 1) != (crc & 1))
      crc ^= poly;

    val >>= 1;
    crc >>= 1;
  }
  return crc;
}

// From Yosys
inline std::string vstringf(const char *fmt, va_list ap) {
  std::string string;
  char *str = NULL;

#if defined(_WIN32) || defined(__CYGWIN__)
  int sz = 64, rc;
  while (1) {
    va_list apc;
    va_copy(apc, ap);
    str = (char *)realloc(str, sz);
    rc = vsnprintf(str, sz, fmt, apc);
    va_end(apc);
    if (rc >= 0 && rc < sz)
      break;
    sz *= 2;
  }
#else
  if (vasprintf(&str, fmt, ap) < 0)
    str = NULL;
#endif

  if (str != NULL) {
    string = str;
    free(str);
  }

  return string;
}

inline std::string stringf(const char *fmt, ...) {
  std::string string;
  va_list ap;

  va_start(ap, fmt);
  string = vstringf(fmt, ap);
  va_end(ap);

  return string;
}

// Bitstream definitions

enum BitstreamOp : uint8_t { OP_NOP = 0, OP_READ = 1, OP_WRITE = 2 };

// File and database convenience functions
// Line-by-line reader, skipping over blank lines and comments
struct LineReader {
  LineReader(const std::string &filename) {
    in.open(filename);
    if (!in) {
      throw std::runtime_error("failed to open " + filename);
    }
  }
  std::ifstream in;
  std::string linebuf;
  bool at_sof = true;

  struct iterator {
    LineReader *parent = nullptr;
    bool at_end = false;
    inline bool operator!=(const iterator &other) const {
      return at_end != other.at_end;
    };
    inline const std::string &operator*() const { return parent->linebuf; }
    inline iterator &operator++() {
      parent->next();
      at_end = parent->linebuf.empty();
      return *this;
    }
  };

  void next() {
    while (std::getline(in, linebuf)) {
      auto cpos = linebuf.find('#');
      if (cpos != std::string::npos)
        linebuf = linebuf.substr(0, cpos);
      if (linebuf.empty())
        continue;
      linebuf = linebuf.substr(linebuf.find_first_not_of(" \t"));
      if (linebuf.empty())
        continue;
      break;
    }
    at_sof = false;
  }

  iterator begin() {
    if (at_sof)
      next();
    return iterator{this, linebuf.empty()};
  }

  iterator end() { return iterator{this, true}; }
};

struct TileInstance {
  std::string name;
  int type;
  int x, y;
  struct TileBitMapping {
    int frame_offset;
    int bit_offset;
    int size;
  };
  std::vector<TileBitMapping> bits;
};

struct TileType {
  std::string type;
  bool loaded_db = false;
  std::unordered_map<std::string, std::vector<int>> features;
};

struct ChipData {

  std::string root;
  void open(const std::string &root);
  void load_frames();
  void load_tiles();
  void load_tiletype_database(int type);

  std::unordered_map<std::string, TileInstance> tiles;
  inline TileInstance &get_tile_by_name(const std::string &name) {
    return tiles.at(name);
  }

  std::vector<TileType> tiletypes;
  std::unordered_map<std::string, int> tiletype_by_name;
  TileType &get_tiletype_by_name(const std::string &name) {
    return tiletypes.at(tiletype_by_name.at(name));
  }
  TileType &load_tile_database(const std::string &tile) {
    int type = tiles.at(tile).type;
    load_tiletype_database(type);
    return tiletypes.at(type);
  }

  std::set<uint32_t> all_frames;
};

inline void split_str(const std::string &s, std::vector<std::string> &dest,
                      const std::string &delim = " ", bool skip_empty = true,
                      int lim = -1) {
  dest.clear();
  std::string buf;

  for (char c : s) {
    if (delim.find(c) != std::string::npos &&
        (lim == -1 || int(dest.size()) < lim)) {
      if (!buf.empty() || !skip_empty)
        dest.push_back(buf);
      buf.clear();
    } else {
      buf += c;
    }
  }

  if (!buf.empty())
    dest.push_back(buf);
}

#endif