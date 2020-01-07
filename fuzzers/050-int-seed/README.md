INT Spec fuzzer
---------------

This fuzzer is structured using specimen files that generate top.v and top.tcl
files for generating bitstreams that toggle CLE[LM] features.  After the
bitstream is generated, a design.features is generated using
dump\_features.tcl. Once all samples have generated design.features, segdata
is generated from the design.features and passed to segmatch.

Remaining features to document
------------------------------

A handful of bidirection pips are not solved currently.
