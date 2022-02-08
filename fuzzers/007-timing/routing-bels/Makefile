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

all: build/sdf.ok

clean:
	rm -rf build
	rm -rf debug*.json

build/sdf.ok: build/run.ok tim2sdf.py
	PYTHONPATH=../utils python3 tim2sdf.py --timings build/bel_timings.txt --sdf build/ --debug
	touch build/sdf.ok

build/run.ok:
	bash runme.sh

.PHONY: all clean
