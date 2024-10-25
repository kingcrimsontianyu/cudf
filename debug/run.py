#!/usr/bin/env python3

import os
import subprocess


class test_manager:
    def __init__(self):
        self.test_env = os.environ.copy()

        self.test_env["LIBCUDF_CUFILE_POLICY"] = "KVIKIO"
        self.test_env["KVIKIO_COMPAT_MODE"] = "on"
        # self.test_env["CUFILE_ALLOW_COMPAT_MODE"] = "false"
        self.test_env["CUFILE_LOGGING_LEVEL"] = "WARN"

        self.test_env["TMPDIR"] = "/mnt/cyberpunk/tmp"

        self.color_green = '\x1b[1;32m'
        self.color_end = '\x1b[0m'

        self.my_bin = "/home/coder/cudf/cpp/build/latest/benchmarks/PARQUET_READER_NVBENCH"

    def run_io_compression(self, subtest_env, cardinality):
        current_setup = "{}_cache_{}_cardinality_{}_{}".format("io_compression",
                                                               "cold" if "CUDF_BENCHMARK_DROP_CACHE" in subtest_env else "hot",
                                                               cardinality,
                                                               subtest_env["KVIKIO_NTHREADS"])
        print("{}--> {}{}".format(self.color_green,
                                  current_setup, self.color_end))
        full_command = "{} -d 0 -b parquet_read_io_compression -a compression_type=SNAPPY -a io_type=FILEPATH -a cardinality={} -a run_length=1 --min-samples 40".format(
            self.my_bin, cardinality)
        print("    Full command: {}".format(full_command))
        subprocess.run([full_command], shell=True,
                       env=subtest_env)

    def run_io_small_mixed(self, subtest_env, cardinality):
        current_setup = "{}_cache_{}_cardinality_{}_{}".format("io_small_mixed",
                                                               "cold" if "CUDF_BENCHMARK_DROP_CACHE" in subtest_env else "hot",
                                                               cardinality,
                                                               subtest_env["KVIKIO_NTHREADS"])
        print("{}--> {}{}".format(self.color_green,
                                  current_setup, self.color_end))
        full_command = "{} -d 0 -b parquet_read_io_small_mixed -a io_type=FILEPATH -a num_string_cols=3 -a cardinality={} -a run_length=1 --min-samples 40".format(
            self.my_bin, cardinality)
        print("    Full command: {}".format(full_command))
        subprocess.run([full_command], shell=True,
                       env=subtest_env)

    # Let KVIKIO use cuFile API that uses GDS
    def run(self, is_cold_cache, cardinality):
        num_threads_options = [1, 8]

        subtest_env = self.test_env.copy()

        # Hot cache (not set) or cold cache (set)
        if is_cold_cache:
            subtest_env["CUDF_BENCHMARK_DROP_CACHE"] = "true"

        for num_threads in num_threads_options:
            subtest_env["KVIKIO_NTHREADS"] = str(num_threads)
            self.run_io_compression(subtest_env, cardinality)

        for num_threads in num_threads_options:
            subtest_env["KVIKIO_NTHREADS"] = str(num_threads)
            self.run_io_small_mixed(subtest_env, cardinality)


if __name__ == '__main__':
    tm = test_manager()
    tm.run(False, 0)
    tm.run(True, 0)

    tm.run(False, 1000)
    tm.run(True, 1000)
