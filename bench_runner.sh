#!/bin/bash

check_server() {
  local url="127.0.0.1:8080"
  
  # Send HTTP request
  response=$(curl --write-out "%{http_code}" --silent --output /dev/null "$url")
  
  # Check if HTTP response code is 200 (success)
  if [[ "$response" -eq 200 ]]; then
    return 0  # Success (true)
  else
    echo "Error: HTTP request failed with status code $response"
    exit 1  # Exit with an error
  fi
}

bench_name=$1
prepare_command=$2
server_run_command=$3

if [ -z "$3" ]; then
    prepare_command=""
    server_run_command=$2
fi

echo "---------"
echo "Benchmark $bench_name"
echo "Prepare command: $prepare_command"
echo "Server run command: $server_run_command"
echo " "

if [ -n "$prepare_command" ]; then
    eval "$prepare_command"
fi

eval "$server_run_command &"

SERVER_PID=$!
echo "Server started with PID=$SERVER_PID"

sleep 2

SERVER_WORKER_PIDS=$(pgrep -P $SERVER_PID)
SERVER_WORKER_PIDS=$(printf "%s " $SERVER_WORKER_PIDS)
SERVER_WORKER_PIDS="${SERVER_WORKER_PIDS%"${SERVER_WORKER_PIDS##*[![:space:]]}"}"
if [ -n "$SERVER_WORKER_PIDS" ]; then
    SERVER_WORKER_PIDS="$SERVER_PID $SERVER_WORKER_PIDS"
    echo "Watched pids: '$SERVER_WORKER_PIDS'"
else
    SERVER_WORKER_PIDS="$SERVER_PID"
fi

check_server

results_file="./docs/results/$bench_name.json"

ulimit -n 1024

source myenv/bin/activate
./bench_runner.py --out $results_file --pids $SERVER_WORKER_PIDS
deactivate

echo "Kill ${bench_name} server with PID=$SERVER_PID"
kill -TERM $SERVER_PID

sleep 2

echo "End ${bench_name}"
echo "---------"
echo " "