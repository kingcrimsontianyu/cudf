#!/usr/bin/env bash

export TMPDIR="/mnt/nvme/run_benchmark"
export CUDA_VISIBLE_DEVICES=1
export LIBCUDF_CUFILE_POLICY="KVIKIO"
export KVIKIO_COMPAT_MODE="OFF"
export CUFILE_ALLOW_COMPAT_MODE=false
export CUDF_BENCHMARK_DROP_CACHE=true

parquet_reader_bench_bin=/home/coder/cudf/cpp/build/latest/benchmarks/PARQUET_READER_NVBENCH
parquet_benchmark_name=parquet_read_io_compression

$parquet_reader_bench_bin \
-d 0 \
-b $parquet_benchmark_name \
-a compression_type=NONE \
-a io_type=FILEPATH \
-a cardinality=0 \
-a run_length=1 \
--min-samples 10 --timeout 20 --csv stdout
