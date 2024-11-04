#!/usr/bin/env bash

nsys_bin="/usr/local/cuda-12.5/bin/nsys"
parquet_reader_bench_bin=/home/coder/cudf/cpp/build/latest/benchmarks/PARQUET_READER_NVBENCH

color_reset='\e[m'
color_green='\e[1;32m'

# export CUDF_BENCHMARK_DROP_CACHE=true

$nsys_bin profile \
-o /mnt/profile/my-report-nvtx-str-reg \
--force-overwrite=true \
--backtrace=none \
--gpu-metrics-device=0 \
--cpuctxsw=none \
--trace=cuda,nvtx \
--env-var KVIKIO_NTHREADS=8,LIBCUDF_CUFILE_POLICY=KVIKIO,KVIKIO_COMPAT_MODE=ON \
${parquet_reader_bench_bin} -d 0 -b parquet_read_io_compression \
-a compression_type=NONE -a io_type=FILEPATH -a cardinality=0 -a run_length=1 --min-samples 40

# export KVIKIO_NTHREADS=8
# export LIBCUDF_CUFILE_POLICY=KVIKIO
# export KVIKIO_COMPAT_MODE=ON

# ${parquet_reader_bench_bin} -d 0 -b parquet_read_io_compression \
# -a compression_type=NONE -a io_type=FILEPATH -a cardinality=0 -a run_length=1 --min-samples 40