#!/usr/bin/env bash

parquet_reader_bench_bin=/home/coder/cudf/cpp/build/latest/benchmarks/PARQUET_READER_NVBENCH

color_reset='\e[m'
color_green='\e[1;32m'

export CUDF_BENCHMARK_DROP_CACHE=true

# Only allow GDS IO. Disallow POSIX fallback.
# export CUFILE_ALLOW_COMPAT_MODE=false

export KVIKIO_NTHREADS=8
export KVIKIO_COMPAT_MODE=ON
# export KVIKIO_GDS_THRESHOLD=0

export LIBCUDF_CUFILE_POLICY="KVIKIO"
export LIBCUDF_CUFILE_THREAD_COUNT=1
# export LIBCUDF_LOGGING_LEVEL=INFO

# export TMPDIR=/home/coder/cudf/run_benchmark

export CUFILE_ALLOW_COMPAT_MODE=false
export CUFILE_LOGGING_LEVEL=TRACE

# gdb -ex start --args parquet_read_io_compression -d 0 -b $parquet_benchmark_name \
# -a compression_type=NONE -a io_type=FILEPATH -a cardinality=0 -a run_length=1 \
# --run-once

#-----------------------------------
# parquet_read_io_compression
#-----------------------------------
${parquet_reader_bench_bin} -d 0 -b parquet_read_io_compression \
-a compression_type=NONE -a io_type=FILEPATH -a cardinality=1000 -a run_length=1 --min-samples 40

#-----------------------------------
# parquet_read_io_small_mixed
#-----------------------------------
# ${parquet_reader_bench_bin} -d 0 -b parquet_read_io_small_mixed \
# -a io_type=FILEPATH -a num_string_cols=3 -a cardinality=1000 -a run_length=1 --min-samples 40