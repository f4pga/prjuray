# Connect to OpenOCD instance
target remote localhost:3333

# Load FSBL elf, but leave CPU halted
load build/fsbl.elf 0x0

# Tell OpenOCD to load the FPGA
monitor pld load 0 build/top.bit

# Tell OpenOCD to resume core 0
monitor resume

# Have GDB quit
detach
quit

