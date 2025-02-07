#!/usr/bin/env python3

import os
import subprocess
import copy


class test_manager_base:
    def __init__(self, config):
        self.config = config
        self.config_name = ""
        self.color_green = '\x1b[1;32m'
        self.color_end = '\x1b[0m'
        self.full_command = ""
        self.bench_program_dir = "/home/coder/cudf/cpp/build/latest/benchmarks"
        self.test_name = ""

    def _add_sep_if_necessary(self, my_str):
        if my_str != "":
            my_str += "_"
        return my_str

    def _setup(self):
        if "CONFIG_NAME_PREFIX" in self.config:
            self.config_name += self.config["CONFIG_NAME_PREFIX"]

        self.config_name = self._add_sep_if_necessary(self.config_name)
        self.config_name += self.test_name

        self.config_name = self._add_sep_if_necessary(self.config_name)
        if "CUDF_BENCHMARK_DROP_CACHE" in self.config:
            self.config_name += "cold"
        else:
            self.config_name += "hot"

        if "CUFILE_LOGFILE_PATH" in self.config:
            self.config["CUFILE_LOGFILE_PATH"] = f"{self.config_name}.txt"

    def _generate_cmd(self):
        if "OUTPUT_TO_CSV" in self.config:
            self.full_command += " --csv stdout"

    def _run(self):
        print(f"{self.color_green}--> {self.config_name}{self.color_end}")
        print(f"--> Full command: {self.full_command}")
        print(f"    Test config: {self.config}")

        if "DRY_RUN" not in self.config:
            subprocess.run(self.full_command.split(),
                           env=self.config)

    def run(self):
        self._setup()
        self._generate_cmd()
        self._run()


class test_manager_parquet(test_manager_base):
    def __init__(self, config):
        super().__init__(config)
        self.test_name = "parquet"

    def _generate_cmd(self):
        my_bin = os.path.join(self.bench_program_dir, "PARQUET_READER_NVBENCH")
        my_option = "parquet_read_io_compression"
        self.full_command = f"{my_bin} -d 0 -b {my_option} -a compression_type=NONE -a io_type=FILEPATH -a cardinality=0 -a run_length=1 --min-samples 40"
        super()._generate_cmd()


class test_manager_orc(test_manager_base):
    def __init__(self, config):
        super().__init__(config)
        self.test_name = "orc"

    def _generate_cmd(self):
        my_bin = os.path.join(self.bench_program_dir, "ORC_READER_NVBENCH")
        my_option = "orc_read_io_compression"
        self.full_command = f"{my_bin} -d 0 -b {my_option} -a compression=NONE -a io=FILEPATH -a cardinality=0 -a run_length=1 --min-samples 40"
        super()._generate_cmd()


class test_manager_json(test_manager_base):
    def __init__(self, config):
        super().__init__(config)
        self.test_name = "json"

    def _generate_cmd(self):
        my_bin = os.path.join(self.bench_program_dir, "JSON_READER_NVBENCH")
        my_option = "json_read_io"
        self.full_command = f"{my_bin} -d 0 -b {my_option} -a io=FILEPATH --min-samples 40"
        super()._generate_cmd()


class test_manager_csv(test_manager_base):
    def __init__(self, config):
        super().__init__(config)
        self.test_name = "csv"

    def _generate_cmd(self):
        my_bin = os.path.join(self.bench_program_dir, "CSV_READER_NVBENCH")
        my_option = "csv_read_io"
        self.full_command = f"{my_bin} -d 0 -b {my_option} -a io=FILEPATH --min-samples 40"
        super()._generate_cmd()


if __name__ == '__main__':
    config = {
        # "TMPDIR": "/mnt/nvme/run_benchmark",
        "TMPDIR": "/mnt/nvme_ubuntu_test",
        "KVIKIO_COMPAT_MODE": "on",
        # "CUFILE_ALLOW_COMPAT_MODE": "false",
        "CUDF_BENCHMARK_DROP_CACHE": "true",
        # "CUDA_VISIBLE_DEVICES": "1",
        "CONFIG_NAME_PREFIX": "kvikIOPosix",
        # "DRY_RUN": "true",
        "OUTPUT_TO_CSV": "true"
    }

    tm_list = [test_manager_parquet(config),
               test_manager_orc(config),
               test_manager_json(config),
               test_manager_csv(config)]

    for tm in tm_list:
        tm.run()
