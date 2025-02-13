#!/usr/bin/env python3

import psutil
import platform
import json
import sys

name = sys.argv[1] if len(sys.argv) > 1 else None

# Get CPU information
cpu_info = {
    "cpu_count": psutil.cpu_count(logical=True),
    "cpu_frequency": psutil.cpu_freq().current,
    "cpu_usage": psutil.cpu_percent(interval=1)
}

# Get memory information
memory_info = psutil.virtual_memory()
memory_info_dict = {
    "total_memory_gb": memory_info.total / (1024 ** 3),
    "available_memory_gb": memory_info.available / (1024 ** 3),
    "used_memory_gb": memory_info.used / (1024 ** 3),
    "memory_usage_percent": memory_info.percent
}

# Get OS information
os_info = {
    "os": platform.system(),
    "os_version": platform.version(),
    "architecture": platform.architecture(),
    "machine": platform.machine(),
    "processor": platform.processor()
}

# Combine all the information into one dictionary
system_info = {
    "cpu_info": cpu_info,
    "memory_info": memory_info_dict,
    "os_info": os_info
}

# If name is empty, generate a default name
if not name:
    name = f"{os_info['os']} {os_info['architecture'][0]} {memory_info_dict['total_memory_gb']:.2f}GB {cpu_info['cpu_count']} CPUs {os_info['processor']}"

# Add name to the output
system_info["name"] = name

# Convert the dictionary to JSON
system_info_json = json.dumps(system_info, indent=4)

# Print the JSON
print(system_info_json)
