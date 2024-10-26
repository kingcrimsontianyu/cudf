#!/usr/bin/env bash

parquet_reader_bench_bin=/home/coder/cudf/cpp/build/latest/benchmarks/PARQUET_READER_NVBENCH

color_reset='\e[m'
color_green='\e[1;32m'

export CUDF_BENCHMARK_DROP_CACHE=true


export KVIKIO_NTHREADS=1
export KVIKIO_COMPAT_MODE=ON

export LIBCUDF_CUFILE_POLICY="KVIKIO"

#-----------------------------------
# parquet_read_io_compression
#-----------------------------------
gdb -ex start --args ${parquet_reader_bench_bin} -d 0 -b parquet_read_io_compression \
-a compression_type=SNAPPY -a io_type=FILEPATH -a cardinality=0 -a run_length=1 --run-once

#-----------------------------------
# parquet_read_io_small_mixed
#-----------------------------------
# ${parquet_reader_bench_bin} -d 0 -b parquet_read_io_small_mixed \
# -a io_type=FILEPATH -a num_string_cols=3 -a cardinality=0 -a run_length=1 --min-samples 40