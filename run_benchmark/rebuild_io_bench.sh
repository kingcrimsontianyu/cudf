#!/usr/bin/env bash

configure-cudf-cpp -DCMAKE_CUDA_ARCHITECTURES=native -DBUILD_BENCHMARKS=ON -DBUILD_TESTS=ON

cmake --build /home/coder/cudf/cpp/build/latest -j 10 -t PARQUET_READER_NVBENCH
cmake --build /home/coder/cudf/cpp/build/latest -j 10 -t ORC_READER_NVBENCH
cmake --build /home/coder/cudf/cpp/build/latest -j 10 -t JSON_READER_NVBENCH
cmake --build /home/coder/cudf/cpp/build/latest -j 10 -t CSV_READER_NVBENCH
