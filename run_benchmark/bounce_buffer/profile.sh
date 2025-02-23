#!/usr/bin/env bash

# Run this script with sudo in order to collect performance counters

export KVIKIO_COMPAT_MODE="ON"
export KVIKIO_NTHREADS=72
export LIBCUDF_LOGGING_LEVEL=INFO

my_python=/home/coder/.local/share/venvs/rapids/bin/python
my_program=basic.py

# Warm up to fill the file cache
$my_python $my_program

# Profile
nsys profile \
-o lock-free-$KVIKIO_NTHREADS \
-t nvtx,cuda,osrt \
-f true \
-b none \
--gpu-metrics-devices=0 \
--cpuctxsw=none \
--gpuctxsw=true \
--cuda-memory-usage=true \
$my_python $my_program