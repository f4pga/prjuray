# The CARRY8 PRECYINIT input muxes fuzzer

Each CARRY8 can be split into two sections. Each section has its own carry chain initialization mux. These are refered to as `PRECYINIT_BOT` for the first 4 stages and `PRECYINIT_TOP` for the second 4 stages.

## CARRY8.DUAL_CY4

When set makes a single CARRY8 split into two independent 4-bit carry chains.

## CARRY8.PRECYINIT_BOT

Selects data source for the bottom input of the CARRY8.

| feature           | selection |
|-------------------|-----------|
| PRECYINIT_BOT.C0  | <const 0> |
| PRECYINIT_BOT.C1  | <const 1> |
| PRECYINIT_BOT.AX  | AX        |
| PRECYINIT_BOT.CIN | CIN       |

## CARRY8.PRECYINIT_TOP

Selects data source for the middle input of the CARRY8. Effectively for the top part of the BEL.

| feature           | selection |
|-------------------|-----------|
| PRECYINIT_TOP.C0  | <const 0> |
| PRECYINIT_TOP.C1  | <const 1> |
| PRECYINIT_TOP.EX  | EX        |
| PRECYINIT_TOP.CO3 | CO3       |

Selecting the `CO3` effectively makes the CARRY8 not being split into two. It is unclear how it relates to the `CARRY8.DUAL_CY4` bit.
