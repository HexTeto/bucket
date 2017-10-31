#!/bin/bash

################
# Ubuntu 
################
# install deps
apt install libffi-dev libssl-dev zlib1g-dev openssl-dev readline-common libreadline-dev gcc g++ make

# install python
wget https://www.python.org/ftp/python/2.7.14/Python-2.7.14.tar.xz

tar Jxvf Python-2.7.14.tar.xz
cd Python-2.7.14.tar.xz
./configure --enable-optimizations
make
make install

# install pip
wget https://bootstrap.pypa.io/get-pip.py