# The CARRY8 DIn input mux fuzzer

## CARRY8.[A-H]CY0

Each CARRY8 DIn input has a mux that selects between the O5 of the corresponding LUT and the mX SLICE input. The n ranges from 0 to 7 while m ranges from A to H.

| mCY0   | CARRY8.DIN       |
|--------|------------------|
| 0      | mX               |
| 1      | mLUT.O5          |

