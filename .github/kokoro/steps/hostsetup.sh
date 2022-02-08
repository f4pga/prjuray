#!/bin/bash
#
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

set -e

echo
echo "========================================"
echo "Removing older packages"
echo "----------------------------------------"
sudo apt-get remove -y cmake
echo "----------------------------------------"

echo
echo "========================================"
echo "Update the CA certificates"
echo "----------------------------------------"
sudo apt-get install -y ca-certificates
echo "----------------------------------------"
sudo update-ca-certificates
echo "----------------------------------------"

echo
echo "========================================"
echo "Remove the expire letsencrypt.org cert "
echo "----------------------------------------"
wget https://helloworld.letsencrypt.org/ || true
echo "----------------------------------------"
sudo rm /usr/share/ca-certificates/mozilla/DST_Root_CA_X3.crt
echo "----------------------------------------"
sudo update-ca-certificates
echo "----------------------------------------"
wget https://helloworld.letsencrypt.org/ || true
echo "----------------------------------------"


echo
echo "========================================"
echo "Host adding PPAs"
echo "----------------------------------------"
wget -O - https://apt.kitware.com/keys/kitware-archive-latest.asc 2>/dev/null | sudo apt-key add -
sudo apt-add-repository 'deb https://apt.kitware.com/ubuntu/ xenial main'
echo "----------------------------------------"

echo
echo "========================================"
echo "Host updating packages"
echo "----------------------------------------"
sudo apt-get update
echo "----------------------------------------"

echo
echo "========================================"
echo "Host remove packages"
echo "----------------------------------------"
sudo apt-get remove -y \
	python-pytest \


sudo apt-get autoremove -y

echo "----------------------------------------"
echo
echo "========================================"
echo "Host install packages"
echo "----------------------------------------"
sudo apt-get install -y \
        bash \
        bison \
        build-essential \
        ca-certificates \
        clang-format \
        cmake \
        colordiff \
        coreutils \
        curl \
        flex \
        fontconfig \
        git \
        jq \
        nodejs \
        psmisc \
        python \
        python3 \
        python3-dev \
        python3-virtualenv \
        python3-yaml \
        virtualenv \

echo "----------------------------------------"

(
	cd /tmp
	# Upgrade pstree to support the -T flag.
	wget https://storage.googleapis.com/prjxray-deps-debs/psmisc_23.2-1_amd64.deb
	sudo dpkg --install psmisc_23.2-1_amd64.deb
	which pstree
	pstree --help || true
)

echo "----------------------------------------"

echo
echo "========================================"
echo "Getting diff2html to produce pretty database diffs"
echo "----------------------------------------"
(
	sudo npm install -g diff2html-cli
)
