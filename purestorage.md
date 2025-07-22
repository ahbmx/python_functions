# Python Script to Collect Pure Storage Array Information

Here's a Python script that uses the `purestorage` library to collect various information from Pure Storage arrays and stores the data in Pandas DataFrames:

```python
import purestorage
import pandas as pd
from getpass import getpass

def connect_to_array(array_ip, username, password):
    """Connect to the Pure Storage array"""
    try:
        array = purestorage.FlashArray(array_ip, username, password)
        print(f"Successfully connected to {array_ip}")
        return array
    except Exception as e:
        print(f"Failed to connect to {array_ip}: {str(e)}")
        return None

def collect_array_info(array):
    """Collect basic array information"""
    array_info = array.get()
    array_info_df = pd.DataFrame([array_info])
    return array_info_df

def collect_array_capacity(array):
    """Collect array capacity information"""
    capacity = array.get(space=True)
    capacity_df = pd.DataFrame([capacity])
    return capacity_df

def collect_array_health(array):
    """Collect array health information"""
    health = array.get(action='monitor')
    health_df = pd.DataFrame([health])
    return health_df

def collect_hosts_with_wwns(array):
    """Collect hosts with their WWNs"""
    hosts = array.list_hosts()
    hosts_data = []
    
    for host in hosts:
        host_info = array.get_host(host['name'], hgroup=True)
        wwns = array.list_host_connections(host['name'])
        host_info['wwns'] = [wwn['wwn'] for wwn in wwns]
        hosts_data.append(host_info)
    
    hosts_df = pd.DataFrame(hosts_data)
    return hosts_df

def collect_array_wwns(array):
    """Collect array WWNs (ports)"""
    ports = array.list_ports()
    ports_df = pd.DataFrame(ports)
    return ports_df

def collect_host_groups(array):
    """Collect host groups information"""
    hgroups = array.list_hgroups()
    hgroups_data = []
    
    for hgroup in hgroups:
        hgroup_info = array.get_hgroup(hgroup['name'])
        hgroups_data.append(hgroup_info)
    
    hgroups_df = pd.DataFrame(hgroups_data)
    return hgroups_df

def collect_volumes(array):
    """Collect volumes information"""
    volumes = array.list_volumes()
    volumes_data = []
    
    for volume in volumes:
        vol_info = array.get_volume(volume['name'])
        volumes_data.append(vol_info)
    
    volumes_df = pd.DataFrame(volumes_data)
    return volumes_df

def main():
    # Get user credentials
    array_ip = input("Enter Pure Storage array IP: ")
    username = input("Enter username: ")
    password = getpass("Enter password: ")
    
    # Connect to the array
    array = connect_to_array(array_ip, username, password)
    if not array:
        return
    
    # Collect all information
    print("\nCollecting array information...")
    array_info_df = collect_array_info(array)
    capacity_df = collect_array_capacity(array)
    health_df = collect_array_health(array)
    hosts_df = collect_hosts_with_wwns(array)
    ports_df = collect_array_wwns(array)
    hgroups_df = collect_host_groups(array)
    volumes_df = collect_volumes(array)
    
    # Display summary
    print("\nCollection complete. Here's a summary of the data collected:")
    print(f"- Array Info: {array_info_df.shape}")
    print(f"- Capacity: {capacity_df.shape}")
    print(f"- Health: {health_df.shape}")
    print(f"- Hosts: {hosts_df.shape}")
    print(f"- Array WWNs: {ports_df.shape}")
    print(f"- Host Groups: {hgroups_df.shape}")
    print(f"- Volumes: {volumes_df.shape}")
    
    # You can now work with these DataFrames or save them to files
    # Example: save to CSV
    # array_info_df.to_csv('array_info.csv', index=False)
    # capacity_df.to_csv('array_capacity.csv', index=False)
    # etc.

if __name__ == "__main__":
    main()
```

## Requirements

To run this script, you'll need to install the following packages:
```
pip install purestorage pandas
```

## Features

1. **Authentication**: Uses username and password to connect to the Pure Storage array
2. **Data Collection**:
   - Array information (name, version, etc.)
   - Capacity metrics
   - Health status
   - Hosts with their WWNs
   - Array WWNs (ports)
   - Host groups
   - Volumes information
3. **Data Storage**: All data is stored in Pandas DataFrames for easy manipulation and analysis
4. **Security**: Uses `getpass` for secure password input

## Usage

1. Run the script
2. Enter the array IP, username, and password when prompted
3. The script will collect all requested information and display a summary
4. You can then work with the DataFrames or save them to files (commented examples are provided)

## Notes

- The script handles one array at a time. If you need to query multiple arrays, you can modify it to loop through a list of arrays.
- You may need to adjust the data collection methods based on your specific Pure Storage array version and configuration.
- For production use, consider adding error handling and logging.



# Enhanced Python Script for Multiple Pure Storage Arrays with Multithreading

Here's an improved version of the script that can handle multiple arrays (up to 30) using multithreading for faster data collection:

```python
import purestorage
import pandas as pd
from getpass import getpass
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from queue import Queue
import time
import json

# Thread-safe data storage
results_lock = threading.Lock()
results = {
    'array_info': [],
    'capacity': [],
    'health': [],
    'hosts': [],
    'ports': [],
    'hgroups': [],
    'volumes': []
}

def connect_to_array(array_ip, username, password):
    """Connect to the Pure Storage array"""
    try:
        array = purestorage.FlashArray(array_ip, username, password)
        print(f"Successfully connected to {array_ip}")
        return array
    except Exception as e:
        print(f"Failed to connect to {array_ip}: {str(e)}")
        return None

def collect_array_data(array_ip, username, password):
    """Collect all data from a single array"""
    array = connect_to_array(array_ip, username, password)
    if not array:
        return None
    
    try:
        # Collect all information
        array_info = array.get()
        capacity = array.get(space=True)
        health = array.get(action='monitor')
        
        # Collect hosts with WWNs
        hosts = array.list_hosts()
        hosts_data = []
        for host in hosts:
            host_info = array.get_host(host['name'], hgroup=True)
            wwns = array.list_host_connections(host['name'])
            host_info['wwns'] = [wwn['wwn'] for wwn in wwns]
            host_info['array_ip'] = array_ip
            hosts_data.append(host_info)
        
        # Collect array WWNs (ports)
        ports = array.list_ports()
        for port in ports:
            port['array_ip'] = array_ip
        
        # Collect host groups
        hgroups = array.list_hgroups()
        hgroups_data = []
        for hgroup in hgroups:
            hgroup_info = array.get_hgroup(hgroup['name'])
            hgroup_info['array_ip'] = array_ip
            hgroups_data.append(hgroup_info)
        
        # Collect volumes
        volumes = array.list_volumes()
        volumes_data = []
        for volume in volumes:
            vol_info = array.get_volume(volume['name'])
            vol_info['array_ip'] = array_ip
            volumes_data.append(vol_info)
        
        # Store results with thread-safe lock
        with results_lock:
            array_info['array_ip'] = array_ip
            capacity['array_ip'] = array_ip
            health['array_ip'] = array_ip
            
            results['array_info'].append(array_info)
            results['capacity'].append(capacity)
            results['health'].append(health)
            results['hosts'].extend(hosts_data)
            results['ports'].extend(ports)
            results['hgroups'].extend(hgroups_data)
            results['volumes'].extend(volumes_data)
            
        print(f"Completed data collection for {array_ip}")
        return array_ip
    
    except Exception as e:
        print(f"Error collecting data from {array_ip}: {str(e)}")
        return None
    finally:
        if array:
            array.invalidate_session()

def save_to_excel(dataframes, filename):
    """Save all DataFrames to an Excel file with different sheets"""
    with pd.ExcelWriter(filename) as writer:
        for name, df in dataframes.items():
            df.to_excel(writer, sheet_name=name, index=False)
    print(f"All data saved to {filename}")

def main():
    # Get user credentials
    username = input("Enter Pure Storage username: ")
    password = getpass("Enter password: ")
    
    # Load array IPs (could also read from a file)
    array_ips = []
    print("Enter Pure Storage array IPs (one per line, empty line to finish):")
    while True:
        ip = input("> ").strip()
        if not ip:
            break
        array_ips.append(ip)
    
    if not array_ips:
        print("No arrays specified. Exiting.")
        return
    
    print(f"\nStarting data collection for {len(array_ips)} arrays...")
    start_time = time.time()
    
    # Use ThreadPoolExecutor to parallelize the collection
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(collect_array_data, ip, username, password) for ip in array_ips]
        
        for future in as_completed(futures):
            result = future.result()
            if result:
                print(f"Finished processing {result}")
    
    # Convert collected data to DataFrames
    dataframes = {
        'array_info': pd.DataFrame(results['array_info']),
        'capacity': pd.DataFrame(results['capacity']),
        'health': pd.DataFrame(results['health']),
        'hosts': pd.DataFrame(results['hosts']),
        'ports': pd.DataFrame(results['ports']),
        'hgroups': pd.DataFrame(results['hgroups']),
        'volumes': pd.DataFrame(results['volumes'])
    }
    
    # Display summary
    print("\nCollection complete. Here's a summary of the data collected:")
    for name, df in dataframes.items():
        print(f"- {name.replace('_', ' ').title():<12}: {df.shape[0]} rows from {df['array_ip'].nunique()} arrays")
    
    # Save to Excel
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    excel_filename = f"pure_storage_report_{timestamp}.xlsx"
    save_to_excel(dataframes, excel_filename)
    
    # Print performance metrics
    duration = time.time() - start_time
    print(f"\nTotal collection time: {duration:.2f} seconds")
    print(f"Average per array: {duration/len(array_ips):.2f} seconds")

if __name__ == "__main__":
    main()
```

## Key Improvements:

1. **Multithreading Support**:
   - Uses `ThreadPoolExecutor` with up to 10 concurrent workers
   - Processes multiple arrays simultaneously for faster data collection

2. **Thread-Safe Data Collection**:
   - Implements locking mechanism to safely aggregate data from multiple threads
   - Each array's data is collected independently and merged safely

3. **Bulk Processing**:
   - Handles input of multiple array IPs (up to 30 or more)
   - Tracks progress for each array individually

4. **Enhanced Output**:
   - Saves all data to a single Excel file with multiple sheets
   - Includes array IP in each record for traceability
   - Generates timestamped output filename

5. **Performance Metrics**:
   - Measures and reports total collection time
   - Calculates average time per array

## Usage Instructions:

1. Run the script
2. Enter your Pure Storage username and password
3. Enter the IP addresses of all your arrays (one per line, empty line to finish)
4. The script will:
   - Connect to all arrays in parallel
   - Collect all requested information
   - Save the results to an Excel file with multiple sheets
   - Display performance metrics

## Requirements:

```
pip install purestorage pandas openpyxl
```

Note: The `openpyxl` package is required for Excel export functionality.
