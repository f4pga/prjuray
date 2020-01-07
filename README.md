# Project U-Ray

Project U-Ray is an attempt at documenting the bitstream format for the
[Xilinx Ultrascale and Ultrascale+ parts](https://www.xilinx.com/products/technology/ultrascale.html)
including all parts from the following lines;
 * Kintex Ultrascale
 * Virtex Ultrascale
 * Zynq UltraScale MPSoC
 * Kintex UltraScale+
 * Virtex UltraScale+
 * Zynq UltraScale+ MPSoC

It takes a lot of the learning from
[Project X-Ray](https://github.com/SymbiFlow/prjxray) and
[Project Trellis](https://github.com/SymbiFlow/prjtrellis).

# Target Parts

## Ultrascale

### Kintex UltraScale

#### Parts

 * TBD

#### Boards

 * TBD

### Virtex UltraScale

#### Parts

 * TBD

#### Boards

 * TBD

## Ultrascale+

### Kintex UltraScale+

#### Parts

 * TBD - Targetting XCKU11P?

#### Boards

 * TBD

### Virtex UltraScale+

#### Parts

 * TBD - Targetting XCVU13P?

#### Boards

 * TBD

### Zynq UltraScale+

#### Parts

 * Zynq Ultrascale+ MPSoC - **ZU3EG**

#### Boards

| Board | Maker | Price | Part |
| ----- | ----- | ----- | ---- |
| [Ultra96-V2 Zynq UltraScale+ ZU3EG Development Board (ULTRA96-V2-G)](https://www.avnet.com/shop/us/products/avnet-engineering-services/aes-ultra96-v2-g-3074457345638646173/) | ??? | Xilinx Zynq UltraScale+ MPSoC ZU3EG | $USD249 |
| [Genesys ZU: Zynq Ultrascale+ MPSoC Development Board](https://store.digilentinc.com/genesys-zu-zynq-ultrascale-mpsoc-development-board/) | Digilent | Xilinx Zynq UltraScale+ MPSoC ZU3EG | $USD1,149 |


## WebPack Parts

We have a goal of initially targeting parts supported by WebPack so that anyone
can contribute.

WebPack supports the following parts;
 * Kintex UltraScale FPGA  - XCKU025, XCKU035
 * Kintex UltraScale+ FPGA - XCKU3P,  XCKU5P

Zynq UltraScale+ MPSoC -- UltraScale+ MPSoC
 * XCZU2EG, XCZU2CG, XCZU3EG, XCZU3CG, XCZU4EG, XCZU4CG, XCZU4EV, XCZU5EG,
   XCZU5CG, XCZU5EV, XCZU7EV, XCZU7EG, and XCZU7CG

# Contributing

There are a couple of guidelines when contributing to Project U-Ray which are
listed here.

### Sending

All contributions should be sent as
[GitHub Pull requests](https://help.github.com/articles/creating-a-pull-request-from-a-fork/).

### License

All software (code, associated documentation, support files, etc) in the
Project U-Ray repository are licensed under the very permissive
[ISC License](COPYING). A copy can be found in the [`COPYING`](COPYING) file.

All new contributions must also be released under this license.

### Code of Conduct

By contributing you agree to the [code of conduct](CODE_OF_CONDUCT.md). We
follow the open source best practice of using the [Contributor
Covenant](https://www.contributor-covenant.org/) for our Code of Conduct.

### Sign your work

To improve tracking of who did what, we follow the Linux Kernel's
["sign your work" system](https://github.com/wking/signed-off-by).
This is also called a
["DCO" or "Developer's Certificate of Origin"](https://developercertificate.org/).

**All** commits are required to include this sign off and we use the
[Probot DCO App](https://github.com/probot/dco) to check pull requests for
this.

The sign-off is a simple line at the end of the explanation for the
patch, which certifies that you wrote it or otherwise have the right to
pass it on as a open-source patch.  The rules are pretty simple: if you
can certify the below:

        Developer's Certificate of Origin 1.1

        By making a contribution to this project, I certify that:

        (a) The contribution was created in whole or in part by me and I
            have the right to submit it under the open source license
            indicated in the file; or

        (b) The contribution is based upon previous work that, to the best
            of my knowledge, is covered under an appropriate open source
            license and I have the right under that license to submit that
            work with modifications, whether created in whole or in part
            by me, under the same open source license (unless I am
            permitted to submit under a different license), as indicated
            in the file; or

        (c) The contribution was provided directly to me by some other
            person who certified (a), (b) or (c) and I have not modified
            it.

	(d) I understand and agree that this project and the contribution
	    are public and that a record of the contribution (including all
	    personal information I submit with it, including my sign-off) is
	    maintained indefinitely and may be redistributed consistent with
	    this project or the open source license(s) involved.

then you just add a line saying

	Signed-off-by: Random J Developer <random@developer.example.org>

using your real name (sorry, no pseudonyms or anonymous contributions.)

You can add the signoff as part of your commit statement. For example:

    git commit --signoff -a -m "Fixed some errors."

*Hint:* If you've forgotten to add a signoff to one or more commits, you can use the
following command to add signoffs to all commits between you and the upstream
master:

    git rebase --signoff upstream/master

### Contributing to the docs

In addition to the above contribution guidelines, see the guide to
[updating the Project U-Ray docs](UPDATING-THE-DOCS.md).
