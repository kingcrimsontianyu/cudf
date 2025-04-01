#!/usr/bin/env bash

export CUDA_LAUNCH_BLOCKING=1
ctest --test-dir /home/coder/cudf/cpp/build/latest -V -R PARQUET_TEST  --stop-on-failure