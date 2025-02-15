#!/usr/bin/env python3

import subprocess
import psutil
import time
import json
import os
import urllib.request
import sys
import argparse

def check_http_server(url):
    try:
        with urllib.request.urlopen(url) as response:
            return response.status == 200
    except Exception as e:
        print(f"Error: {e}")
    return False

def get_process_metrics(pids):
    if not pids:
        return 0, 0
    total_cpu_percent = 0
    total_memory_used = 0
    for pid in pids:
        try:
            process = psutil.Process(pid)
            if process.is_running():
                cpu_percent = process.cpu_percent(interval=0.1)  # CPU usage in percentage
                memory_used = process.memory_info().rss / (1024 * 1024)  # Memory usage in MB
                total_cpu_percent += cpu_percent
                total_memory_used += memory_used
            else:
                print(f"Process with PID {pid} is not running.", file=sys.stderr)
        except psutil.NoSuchProcess:
            print(f"Process with PID {pid} does not exist.", file=sys.stderr)
    return total_cpu_percent, total_memory_used

# Function to run Apache Benchmark (ab) and capture the results
def run_ab_test(total_requests, concurrency, url):
    # Build the command for Apache Benchmark (ab)
    cmd = [
        "ab", "-n", str(total_requests), "-c", str(concurrency), url
    ]
    # Run the command and capture the output in a separate process
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    return process

# Main function that runs the tests
def main(out=None, pids=None):
    print(f"Running benchmark: output {out}, pids = {pids}")

    # Results will be stored in this list
    out_results = []
    
    # URL for the test (can be changed)
    url = "http://127.0.0.1:8080/"

    if not check_http_server(url):
        print("Server {url} not responding")
        exit(1)
    
    steps = (1, 2, 3, 5, 10, 15, 20, 35, 30, 35, 40, 50, 60, 70, 80, 90, 100)
    
    # Loop to increase concurrency step by step
    for concurrency in steps:
        print(f"Running test with {concurrency} concurrent requests...")

        total_requests = concurrency * 1000

        # Start the ab test
        ab_process = run_ab_test(total_requests, concurrency, url)

        # Variables to accumulate total CPU and memory usage during the test
        sample_count = 0
        avg_cpu = 0.0
        avg_memory = 0.0        
        total_cpu = 0
        total_memory = 0

        # Loop to periodically get system metrics during the test
        while ab_process.poll() is None:  # While the ab test is running
            cpu, memory = get_process_metrics(pids)
            if cpu > 0 and memory > 0:
                total_cpu += cpu
                total_memory += memory
                sample_count += 1
            print(f"... cpu {cpu}, memory {memory}")

        # Calculate the averages for CPU and memory usage
        if sample_count > 0:
            avg_cpu = total_cpu / sample_count
            avg_memory = total_memory / sample_count
        else:
            avg_cpu = 0.0
            avg_memory = 0.0

        # Get the final output from the ab test
        result = ab_process.communicate()

        # Process the output of ab test to extract RPS and latency
        output = result[0]

        # Extract Requests per Second (RPS) from the output
        rps_line = [line for line in output.splitlines() if "Requests per second" in line]
        if rps_line:
            rps = float(rps_line[0].split()[3])  # Extract RPS value
        else:
            rps = 0.0  # If no RPS value is found, set it to 0
        
        # Extract latency from the output (connection times)
        latency_line = [line for line in output.splitlines() if "Total:" in line]
        if latency_line:
            # Extract the median total latency from the 'Total' line
            latency_median = latency_line[0].split()[3]  # Median total latency
        else:
            latency_median = "N/A"  # If no latency value is found, set it to "N/A"

        # Save the result in the results list
        result_data = {
            "total_requests": total_requests,
            "avg_cpu_percent": avg_cpu,
            "avg_memory_used_mb": avg_memory,
            "rps": rps,
            "latency_median_ms": latency_median
        }
        print(f"... rps {rps}, latency {latency_median}, cpu {avg_cpu}, memory {avg_memory}")
        out_results.append(result_data)

        # Output the results in JSON format to stdout
        if out is None:
            print(json.dumps(result_data, indent=4))

    if out:
        name = os.path.splitext(os.path.basename(out))[0]
        with open(out, 'w') as json_file:
            json_file.write(name + "_data = ") # This is required to load json files local
            json.dump(out_results, json_file, indent=4)
    
    print("Benchmark completed.")

# Run the script if it's executed directly
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Benchmark runner")
    
    parser.add_argument('--out', type=str, help="Ouptut json file")
    parser.add_argument('--pids', type=int, nargs='+', help="PID of server process")

    args = parser.parse_args()

    main(out=args.out, pids=args.pids)
