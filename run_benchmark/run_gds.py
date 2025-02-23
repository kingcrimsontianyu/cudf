#!/usr/bin/env python3

import os
import subprocess
import copy


class test_manager:
    def __init__(self, config):
        self.config = config
        self.color_green = '\x1b[1;32m'
        self.color_end = '\x1b[0m'

    def run_bench_command(self, subtest_config):
        config_name = ""

        if "CONFIG_NAME_PREFIX" in subtest_config:
            config_name += subtest_config["CONFIG_NAME_PREFIX"] + "_"

        if "LIBCUDF_CUFILE_POLICY" in subtest_config:
            config_name += subtest_config["LIBCUDF_CUFILE_POLICY"] + "_"

        if "CUDF_BENCHMARK_DROP_CACHE" in subtest_config:
            config_name += "_cold"
        else:
            config_name += "_hot"

        subtest_config["CUFILE_LOGFILE_PATH"] = f"{config_name}.txt"

        # Parquet
        my_bin = "/home/coder/cudf/cpp/build/latest/benchmarks/PARQUET_READER_NVBENCH"
        my_option = "parquet_read_io_compression"
        full_command = f"{my_bin} -d 0 -b {my_option} -a compression_type=NONE -a io_type=FILEPATH -a cardinality=0 -a run_length=1 --min-samples 80 --timeout 60 --csv stdout"

        # CSV
        # my_bin = "/home/coder/cudf/cpp/build/latest/benchmarks/CSV_READER_NVBENCH"
        # my_option = "csv_read_io"
        # full_command = "{} -d 0 -b {} -a io=FILEPATH --min-samples 80 --timeout 60 --csv stdout".format(
        #     my_bin, my_option)

        print(f"{self.color_green}--> {config_name}{self.color_end}")
        print(f"--> Full command: {full_command}")
        print(f"    Subtest config: {subtest_config}")
        subprocess.run(full_command.split(),
                       env=subtest_config)

    def run(self):
        subtest_config = copy.deepcopy(self.config)
        self.run_bench_command(subtest_config)


if __name__ == '__main__':
    config = {
        "TMPDIR": "/mnt/nvme/run_benchmark",
        "LIBCUDF_CUFILE_POLICY": "KVIKIO",
        "KVIKIO_COMPAT_MODE": "on",
        "KVIKIO_NTHREADS": "4",
        "CUFILE_ALLOW_COMPAT_MODE": "false",
        "CUDF_BENCHMARK_DROP_CACHE": "true",
        "CUDA_VISIBLE_DEVICES": "1",
        "CONFIG_NAME_PREFIX": "KvikIOPosix"
    }

    tm = test_manager(config)
    tm.run()

    config = {
        "TMPDIR": "/mnt/nvme/run_benchmark",
        "LIBCUDF_CUFILE_POLICY": "KVIKIO",
        "KVIKIO_COMPAT_MODE": "off",
        "KVIKIO_NTHREADS": "4",
        "CUFILE_ALLOW_COMPAT_MODE": "false",
        "CUDF_BENCHMARK_DROP_CACHE": "true",
        "CUDA_VISIBLE_DEVICES": "1",
        "CONFIG_NAME_PREFIX": "cuFileGds"
    }

    tm = test_manager(config)
    tm.run()

    config = {
        "TMPDIR": "/mnt/nvme/run_benchmark",
        "LIBCUDF_CUFILE_POLICY": "KVIKIO",
        "KVIKIO_COMPAT_MODE": "off",
        "KVIKIO_NTHREADS": "4",
        "CUFILE_ALLOW_COMPAT_MODE": "true",
        "CUFILE_FORCE_COMPAT_MODE": "true",
        "CUDF_BENCHMARK_DROP_CACHE": "true",
        "CUDA_VISIBLE_DEVICES": "1",
        "CONFIG_NAME_PREFIX": "cuFilePosix"
    }

    tm = test_manager(config)
    tm.run()
