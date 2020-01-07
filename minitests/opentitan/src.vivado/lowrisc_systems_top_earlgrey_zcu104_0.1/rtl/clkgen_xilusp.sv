// Copyright lowRISC contributors.
// Licensed under the Apache License, Version 2.0, see LICENSE for details.
// SPDX-License-Identifier: Apache-2.0

module clkgen_xilusp (
  input IO_CLK,
  input IO_RST_N,
  output clk_sys,
  output clk_48MHz,
  output rst_sys_n
);
  logic locked_pll;
  logic io_clk_buf;
  logic clk_50_buf;
  logic clk_50_unbuf;
  logic clk_fb_buf;
  logic clk_fb_unbuf;
  logic clk_48_buf;
  logic clk_48_unbuf;

  PLLE4_ADV #(
    .CLKFBOUT_MULT        (10),
    .CLKOUT0_DIVIDE       (25),
    .CLKOUT1_DIVIDE       (26),
    .CLKIN_PERIOD         (8.000)
  ) pll (
    .CLKFBOUT            (clk_fb_unbuf),
    .CLKOUT0             (clk_50_unbuf),
    .CLKOUT1             (clk_48_unbuf),
     // Input clock control
    .CLKFBIN             (clk_fb_buf),
    .CLKIN               (IO_CLK),
    // Ports for dynamic reconfiguration
    .DADDR               (7'h0),
    .DCLK                (1'b0),
    .DEN                 (1'b0),
    .DI                  (16'h0),
    .DO                  (),
    .DRDY                (),
    .DWE                 (1'b0),
    // Other control and status signals
    .LOCKED              (locked_pll),
    .PWRDWN              (1'b0),
    // Do not reset PLL on external reset, otherwise ILA disconnects at a reset
    .RST                 (1'b0));

  // output buffering
  BUFG clk_fb_bufg (
    .I (clk_fb_unbuf),
    .O (clk_fb_buf)
  );

  BUFG clk_50_bufg (
    .I (clk_50_unbuf),
    .O (clk_50_buf)
  );

  BUFG clk_48_bufg (
    .I (clk_48_unbuf),
    .O (clk_48_buf)
  );

  // outputs
  // clock
  assign clk_sys = clk_50_buf; // TODO: choose 50 MHz clock as sysclock for now
  assign clk_48MHz = clk_48_buf;

  // reset
  assign rst_sys_n = locked_pll & IO_RST_N;
endmodule
