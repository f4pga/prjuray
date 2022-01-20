# Copyright 2020-2022 F4PGA Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

create_project -force -name $env(PROJECT_NAME) -part $env(URAY_PART)

read_verilog ../$env(PROJECT_NAME).v
synth_design -top top

source ../ultra96v2.xdc

place_design
route_design

write_checkpoint -force ../$env(PROJECT_NAME).dcp
write_bitstream  -force ../$env(PROJECT_NAME).bit
