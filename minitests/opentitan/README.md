# OpenTitan/Ibex minitest

This folder contains minitest for OpenTitan Earlgrey SoC.

## Synthesis+implementation

There is only one supportd flow at the moment - Vivado only.

In order to run it, run `make` in `src` sub-directory.

## HDL Code generation

To generate HDL code use the `zcu104` branch from <https://github.com/antmicro/opentitan> repository (commit `e459aca` was used).

After installing all OpenTitan dependencies, you can run the following command to generate HDL sources: `fusesoc --cores-root . run --target=synth lowrisc:systems:top_earlgrey_zcu104`.
Resulting files will be located inside `build/lowrisc_systems_top_earlgrey_zcu104_0.1/src` directory.
