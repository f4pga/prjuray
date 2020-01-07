# Zynq US+ PS clock

This is a simple test of PS -> PL interface for ZynqUS+.

The PL design "instantiates" the PS8 and uses the PSCLK0-3 fabric clock outputs to drive the PL logic.
The PS is running a FSBL (First Stage Bootloader) to setup the clocks that are driving the PL.

# Building & loading

## Prerequisites

* AArch64 ELF bare-metal target (aarch64-none-elf) toolchain - can be downloaded from the [ARM developer site](https://developer.arm.com/tools-and-software/open-source-software/developer-tools/gnu-toolchain/gnu-a/downloads)
* OpenOCD 0.10 rebuilt with patch for the avnet_ultra96v2. Steps to fetch the patch:
  1. git clone http://openocd.zylin.com/openocd
  2. cd openocd
  3. git fetch http://openocd.zylin.com/openocd refs/changes/79/5579/2 && git checkout FETCH_HEAD
  4. Rebuild OpenOCD
* GNU GDB with aarch64 support or gdb-multiarch

## PS

Run `make fsbl.elf` to compile the firmware.

## PL

Run `make top.bit` to generate the bitstream.

## Loading

Run `make program` to program the board.
