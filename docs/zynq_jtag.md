Zynq UltraScale+ JTAG Notes
===========================

The Zynq UltraScale+ JTAG chain can be a little confusing, and xsdb interacts
with the JTAG a little different than might be expected.

There are 3 primary JTAG controllers addressed by xsdb:
 - PS TAP
 - PL TAP
 - ARM DAP TAP

See the following figures from UG1085:
 - Figure 93-1 JTAG Chain Block Diagram
 - Figure 39-3 CoreSight Debug Block Diagram

In both of these diagrams, the PS and PL TAP's are shown as different blocks.
However, both xsdb and the openocd configuration
(tcl/target/xilinx\_zynqmp.cfg @83c5aa5c) treat the PS and PL TAP as 1 TAP.
This confusion means some of the documentation of the 3 controllers does not
match expection.

This document explains the apparent behavior of the PS and PL TAP, and how to
match it with existing documentation.

Document References
-------------------

The 3 JTAG TAPs are documented in the following locations:

| TAP         | Documents                                                                                                                                                                |
|-------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| PS TAP      | Table 39-4: PS TAP Controller Instructions from Xilinx UG1085                                                                                                            |
| PL TAP      | Table 6-2: JTAG Registers and Table 6-3: UltraScale FPGA Boundary-Scan Instructions from Xilinx UG570                                                                    |
| ARM DAP TAP | Table 3-209: JTAG-DP register summary from ARM DDI0480F<br>Table 2-6: DPv2 address map from ARM IHI0031C<br>Section 6.2: Selecting and accessing an AP from ARM IHI0031C |

Security gates
--------------

When the Zynq UltraScale+ initially powers on in JTAG mode, only the PS TAP
is actually enabled. The ARM DAP is permanently in BYPASS mode when disabled.
The PL TAP IR is part of the JTAG chian, however the PL TAP DR is by default
**not** in BYPASS mode.  The PL TAP DR register appears to be completely
removed from the JTAG chain.

Enabling PL and ARM TAPs
------------------------

The PS TAP register 0x20 has two control bits (Table 39-5: PS TAP Controller
JTAG Control Register from Xilinx UG1085) that enable the PL and ARM
controllers.  Writing a 32-bit `0x3` to PL TAP IR `0x20` enables both the PL
and ARM controllers (if the security bits allow it).

Once that is written, the ARM DAP controller can be accessed as expected via
OpenOCD.  However, when you look at xilinx\_zynqmp.cfg the following commands
are issued:

```
irscan $_CHIPNAME.ps 0x824
drscan $_CHIPNAME.ps 32 0x00000003
```

The DR scan matches the documentation, but the IR scan does not.  This will be
explained in the next section.

PS / PL DR chain
----------------

The question from the previous section is why does OpenOCD use the following
commands:

```
irscan $_CHIPNAME.ps 0x824
drscan $_CHIPNAME.ps 32 0x00000003
```

to enable the ARM DAP controller?  For additional context here is the TAP
definition lines from higher in the file:

```
jtag newtap $_CHIPNAME tap -irlen 4 -ircapture 0x1 -irmask 0xf -expected-id $_DAP_TAPID
jtag newtap $_CHIPNAME ps -irlen 12 -ircapture 0x1 -irmask 0x03 -expected-id $_PS_TAPID
```

The `-irlen` argument for the ARM DAP matches the documentation indicatinng an
IR register length of 4.  However the PS TAP `-irlen` register length is
reported as 12. xsdb also appears to treat the PS TAP IR register length as
12 bits.

The PS and PL TAP IR length are both 6-bits.  The following table
lists the IR register ordering in the Zynq US+ JTAG chain:

| Shift position | IR chain position | TAP     | Width (bits) |
|----------------|-------------------|---------|--------------|
| 0              | 2                 | ARM TAP | 4            |
| 1              | 1                 | PL TAP  | 6            |
| 2              | 0                 | PS TAP  | 6            |

The ARM TAP should be shifted out first, because it is the last TAP in the
chain, followed by the PL TAP IR, followed last by the PS TAP.

So the question is, why does both xsdb and OpenOCD treat the PL TAP as part of
the PS TAP?  There appears to be an undocumented IR instruction 0x24 in both
the PS and PL TAPs that removes the TAP from the DR shift chain, making the
controller disappear from the DR scan.  In the OpenOCD command, the IR scan'd
was "0x824" which is `(0x20 << 6) | 0x24`, e.g. DR shift into the PS TAP
JTAG\_CTRL register and remove the PL TAP DR register from the DR shift
completely.

In all other respects, the PL TAP and PS TAP behave as documented in their
respective documents list in "Document References" section.
