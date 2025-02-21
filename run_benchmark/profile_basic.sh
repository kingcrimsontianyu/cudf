#!/usr/bin/env bash

# Run this script with sudo in order to collect performance counters

export TMPDIR="/mnt/nvme_ubuntu_test"
export CUDF_BENCHMARK_DROP_CACHE=true
# export CUDA_VISIBLE_DEVICES=1
# export CUFILE_ALLOW_COMPAT_MODE=false

parquet_reader_bench_bin=/home/coder/cudf/cpp/build/latest/benchmarks/PARQUET_READER_NVBENCH
parquet_benchmark_name=parquet_read_io_compression

nsys profile \
-o basic \
-t nvtx,cuda,osrt \
-f true \
-b none \
--gpu-metrics-devices=0 \
--cpuctxsw=none \
--gpuctxsw=true \
--cuda-memory-usage=true \
-e KVIKIO_COMPAT_MODE=ON,KVIKIO_NTHREADS=4 \
$parquet_reader_bench_bin \
-d 0 \
-b $parquet_benchmark_name \
-a compression_type=NONE \
-a io_type=FILEPATH \
-a cardinality=0 \
-a run_length=1 \
--min-samples 10 --timeout 20 --csv stdout
