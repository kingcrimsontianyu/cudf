#!/usr/bin/env bash

# my_debugger=gdb
my_debugger=cuda-gdb

root_dir=/home/coder/cudf/cpp/examples/orc_io

$my_debugger -ex start --ex 'source breakpoints.txt' --args $example_bin