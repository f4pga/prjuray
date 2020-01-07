# Linux on Litex minitest

This folder contains minitest for Linux on Litex SoC.

## Synthesis+implementation

There are two flows supported - Vivado only and Yosys-Vivado.
In order to run them choose `make vivado` or `make yosys-vivado` respectively in the `src` directory.

##Running the design on hardware

In order to connect to the serial terminal use the baudrate rate of 1000000.
