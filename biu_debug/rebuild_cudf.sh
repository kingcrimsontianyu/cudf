#!/usr/bin/env bash

clean-all
build-cudf-cpp -j 16 -DCMAKE_CUDA_ARCHITECTURES=native -DBUILD_BENCHMARKS=OFF -DBUILD_TESTS=ON -DBUILD_DISABLE_LARGE_STRINGS=OFF

# configure-cudf-cpp -DCMAKE_BUILD_TYPE=Debug -j 16 -DCMAKE_CUDA_ARCHITECTURES=native -DBUILD_BENCHMARKS=OFF -DBUILD_TESTS=ON -DBUILD_DISABLE_LARGE_STRINGS=OFF

# cd $HOME/cudf/cpp/build/latest
# sed -i 's|LAUNCHER = /usr/bin/sccache|LAUNCHER =|g' build.ninja
# ninja -j16
