#!/usr/bin/env bash

# export CUFILE_ALLOW_COMPAT_MODE=false
# export CUFILE_FORCE_COMPAT_MODE=false
export CUFILE_LOGFILE_PATH=debug_cufile_log.txt
export CUFILE_LOGGING_LEVEL=TRACE
export TMPDIR="/mnt/nvme/run_benchmark"

filepath_1=$TMPDIR/foo1
filepath_2=$TMPDIR/foo2
gds_sample_dir=/mnt/nvme/MagnumIO/gds/samples
test_bin=$gds_sample_dir/cufile_sample_013.bin

# gdb -ex start --args $test_bin $filepath_1 $filepath_2
$test_bin $filepath_1 $filepath_2