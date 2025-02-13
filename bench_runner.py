#!/usr/bin/env python3

import subprocess
import psutil
import time
import json
import os
import sys
import argparse

def get_system_metrics(pid):
    if pid is None:
        return None, None
    try:
        process = psutil.Process(pid)
        if process.is_running():
            cpu_percent = process.cpu_percent(interval=1)  # CPU usage in percentage
            memory_used = process.memory_info().rss / (1024 * 1024)  # Memory usage in MB
            return cpu_percent, memory_used
        else:
            print(f"Process with PID {pid} is not running.", file=sys.stderr)
            return None, None
    except psutil.NoSuchProcess:
        print(f"Process with PID {pid} does not exist.", file=sys.stderr)
        return None, None

# Function to run Apache Benchmark (ab) and capture the results
def run_ab_test(total_requests, concurrency, url):
    # Build the command for Apache Benchmark (ab)
    cmd = [
        "ab", "-n", str(total_requests), "-c", str(concurrency), url
    ]

    # print(' '.join(cmd))

    # Run the command and capture the output in a separate process
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    return process

# Main function that runs the tests
def main(out=None, pid=None):
    print(f"Running benchmark: output {out}, pid = {pid}")

    # Results will be stored in this list
    out_results = []
    
    # URL for the test (can be changed)
    url = "http://127.0.0.1:8080/"
    
    # Test parameters: Min, Max concurrency and the step increment for concurrency
    min_concurrency = 1
    max_concurrency = 20
    step = 1
    
    # Loop to increase concurrency step by step
    for concurrency in range(min_concurrency, max_concurrency + 1, step):
        print(f"Running test with {concurrency} concurrent requests...")
        
        total_requests = concurrency * 1000

        # Start the ab test
        ab_process = run_ab_test(total_requests, concurrency, url)

        # Variables to accumulate total CPU and memory usage during the test
        total_cpu = 0
        total_memory = 0
        sample_count = 0

        # Loop to periodically get system metrics during the test
        while ab_process.poll() is None:  # While the ab test is running
            cpu, memory = get_system_metrics(pid)
            if cpu is not None and memory is not None:
                total_cpu += cpu
                total_memory += memory
                sample_count += 1
            time.sleep(1)  # Wait 1 second before polling again

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

        # Calculate the averages for CPU and memory usage
        if sample_count > 0:
            avg_cpu = total_cpu / sample_count
            avg_memory = total_memory / sample_count
        else:
            avg_cpu = 0.0
            avg_memory = 0.0

        # Save the result in the results list
        result_data = {
            "total_requests": total_requests,
            "avg_cpu_percent": avg_cpu,
            "avg_memory_used_mb": avg_memory,
            "rps": rps,
            "latency_median_ms": latency_median
        }
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
    parser.add_argument('--pid', type=int, help="PID of server process")

    args = parser.parse_args()

    main(out=args.out, pid=args.pid)
