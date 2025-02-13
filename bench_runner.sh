#!/bin/bash

bench_name=$1
server_command=$2
results_file="./docs/results/$bench_name.json"
echo "---------"
echo "Benchmark $bench_name"
echo "---------"
eval "$server_command &"
server_pid=$!
sleep 2
source myenv/bin/activate
./bench_runner.py --pid=$server_pid --out=$results_file
deactivate
kill $server_pid