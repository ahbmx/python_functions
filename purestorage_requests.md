# Pure Storage REST API Data Collector (Using Requests)

Here's a Python script that collects information from Pure Storage arrays using the REST API with the `requests` library instead of the `purestorage` module:

```python
import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from getpass import getpass
import json
import time
import warnings
from urllib3.exceptions import InsecureRequestWarning

# Disable SSL warnings (only for testing with self-signed certs)
warnings.filterwarnings('ignore', category=InsecureRequestWarning)

class PureStorageAPI:
    def __init__(self, array_ip, username, password, verify_ssl=False):
        self.base_url = f"https://{array_ip}/api/1.19"
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.verify = verify_ssl
        self.session.headers.update({'Content-Type': 'application/json'})
        
    def get_data(self, endpoint):
        try:
            response = self.session.get(f"{self.base_url}/{endpoint}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Error ({endpoint}): {str(e)}")
            return None

def collect_array_data(array_ip, username, password):
    """Collect all data from a single array"""
    start_time = time.time()
    api = PureStorageAPI(array_ip, username, password)
    
    # Dictionary to store all collected data
    data = {
        'array_ip': array_ip,
        'collection_time': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Array information
    array_info = api.get_data('array')
    if array_info:
        data.update(array_info)
    
    # Capacity information
    capacity = api.get_data('array?space=true')
    if capacity:
        data.update({f"capacity_{k}": v for k, v in capacity.items()})
    
    # Alerts
    alerts = api.get_data('message')
    data['alerts'] = alerts if alerts else []
    
    # Hosts with WWNs
    hosts = api.get_data('host')
    host_data = []
    if hosts:
        for host in hosts:
            host_info = api.get_data(f"host/{host['name']}?hgroup=true")
            if host_info:
                wwns = api.get_data(f"host/{host['name']}/connection")
                host_info['wwns'] = [wwn['wwn'] for wwn in wwns] if wwns else []
                host_info['array_ip'] = array_ip
                host_data.append(host_info)
    data['hosts'] = host_data
    
    # Ports (array WWNs)
    ports = api.get_data('port')
    data['ports'] = [dict(p, **{'array_ip': array_ip}) for p in ports] if ports else []
    
    # Host groups
    hgroups = api.get_data('hgroup')
    hgroup_data = []
    if hgroups:
        for hg in hgroups:
            hg_info = api.get_data(f"hgroup/{hg['name']}")
            if hg_info:
                hg_info['array_ip'] = array_ip
                hgroup_data.append(hg_info)
    data['hgroups'] = hgroup_data
    
    # Volumes
    volumes = api.get_data('volume')
    volume_data = []
    if volumes:
        for vol in volumes:
            vol_info = api.get_data(f"volume/{vol['name']}")
            if vol_info:
                vol_info['array_ip'] = array_ip
                volume_data.append(vol_info)
    data['volumes'] = volume_data
    
    duration = time.time() - start_time
    print(f"Completed {array_ip} in {duration:.1f}s")
    return data

def main():
    print("Pure Storage REST API Data Collector\n" + "="*40)
    
    # Get credentials
    username = input("Username: ").strip()
    password = getpass("Password: ")
    
    # Load array IPs
    print("\nEnter array IPs (one per line, blank line to finish):")
    array_ips = []
    while True:
        ip = input("> ").strip()
        if not ip:
            break
        if ip not in array_ips:
            array_ips.append(ip)
    
    if not array_ips:
        print("No arrays specified. Exiting.")
        return
    
    # Process arrays
    print(f"\nProcessing {len(array_ips)} arrays...")
    start_time = time.time()
    
    all_data = {
        'arrays': [],
        'hosts': [],
        'ports': [],
        'hgroups': [],
        'volumes': [],
        'alerts': []
    }
    
    with ThreadPoolExecutor(max_workers=min(10, len(array_ips))) as executor:
        futures = {executor.submit(collect_array_data, ip, username, password): ip for ip in array_ips}
        
        for future in futures:
            try:
                result = future.result()
                if result:
                    all_data['arrays'].append({
                        'array_ip': result['array_ip'],
                        'array_name': result.get('array_name'),
                        'version': result.get('version'),
                        'capacity_total': result.get('capacity_total'),
                        'collection_time': result['collection_time']
                    })
                    all_data['hosts'].extend(result.get('hosts', []))
                    all_data['ports'].extend(result.get('ports', []))
                    all_data['hgroups'].extend(result.get('hgroups', []))
                    all_data['volumes'].extend(result.get('volumes', []))
                    all_data['alerts'].extend([dict(a, **{'array_ip': result['array_ip']}) 
                                              for a in result.get('alerts', [])])
            except Exception as e:
                print(f"Error processing array: {str(e)}")
    
    # Create DataFrames
    dfs = {
        'Arrays': pd.DataFrame(all_data['arrays']),
        'Hosts': pd.DataFrame(all_data['hosts']),
        'Ports': pd.DataFrame(all_data['ports']),
        'HostGroups': pd.DataFrame(all_data['hgroups']),
        'Volumes': pd.DataFrame(all_data['volumes']),
        'Alerts': pd.DataFrame(all_data['alerts'])
    }
    
    # Save to Excel
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"pure_storage_report_{timestamp}.xlsx"
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        for sheet_name, df in dfs.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    # Print summary
    total_time = time.time() - start_time
    print("\nCollection Complete")
    print(f"Total time: {total_time:.1f} seconds")
    print(f"Saved to: {filename}")
    
    for name, df in dfs.items():
        print(f"- {name}: {len(df)} rows")

if __name__ == "__main__":
    main()
```

## Key Features:

1. **Pure REST API Implementation**:
   - Uses only the `requests` library (no `purestorage` module required)
   - Implements proper session management
   - Handles authentication and headers

2. **Comprehensive Data Collection**:
   - Array information (name, version, etc.)
   - Capacity metrics
   - Alerts and messages
   - Hosts with WWNs
   - Array ports (WWNs)
   - Host groups
   - Volumes information

3. **Performance Optimizations**:
   - Multithreaded collection for multiple arrays
   - Connection pooling with session reuse
   - Progress feedback

4. **Data Organization**:
   - Structured output in Pandas DataFrames
   - Excel export with multiple sheets
   - Timestamped filenames

## Requirements:

```bash
pip install requests pandas openpyxl
```

## Usage Instructions:

1. Run the script
2. Enter your Pure Storage username and password
3. Enter the IP addresses of all your arrays (one per line)
4. The script will:
   - Connect to all arrays in parallel
   - Collect all requested information
   - Save the results to an Excel file
   - Display a summary of collected data

## Notes:

- By default, SSL verification is disabled (for self-signed certificates)
- For production use, consider:
  - Enabling SSL verification with proper certificates
  - Adding retry logic for failed requests
  - Implementing rate limiting if needed
  - Adding more detailed error handling
