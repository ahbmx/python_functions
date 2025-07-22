# Python 3.12 Script for PureStorage Array Data Collection (Without distutils)

Here's an updated version of the script that doesn't rely on the `distutils` module (which was deprecated in Python 3.12):

```python
import logging
import threading
from queue import Queue
import pandas as pd
from purestorage import FlashArray
from sqlalchemy import create_engine, types
from sqlalchemy.engine import Engine
import time
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('purestorage_data_collection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
ARRAYS = [
    # List of 30 PureStorage array IPs/hostnames
    'array1.example.com', 'array2.example.com', 'array3.example.com'  # Add all 30 arrays
]
USERNAME = 'your_username'
PASSWORD = 'your_password'
MYSQL_CONN_STRING = 'mysql+pymysql://user:password@host/database'

# Global DataFrames to store collected data
capacity_df = pd.DataFrame()
hosts_df = pd.DataFrame()
alerts_df = pd.DataFrame()
health_df = pd.DataFrame()
wwns_df = pd.DataFrame()
host_disks_df = pd.DataFrame()

# Lock for thread-safe DataFrame operations
data_lock = threading.Lock()

def calculate_column_lengths(df):
    """Calculate maximum lengths for string columns to optimize database storage."""
    dtypes = {}
    for col in df.columns:
        if df[col].dtype == 'object':
            # Handle potential NaN values in string columns
            if df[col].isna().any():
                filled = df[col].fillna('')
                max_len = filled.str.len().max()
            else:
                max_len = df[col].str.len().max()
            
            # Add 10% buffer and round up
            safe_len = int(max_len * 1.1) + 5 if pd.notna(max_len) else 255
            dtypes[col] = types.VARCHAR(safe_len)
        elif 'int' in str(df[col].dtype):
            dtypes[col] = types.BIGINT()
        elif 'float' in str(df[col].dtype):
            dtypes[col] = types.FLOAT()
        elif 'bool' in str(df[col].dtype):
            dtypes[col] = types.BOOLEAN()
        elif 'datetime' in str(df[col].dtype):
            dtypes[col] = types.DATETIME()
    return dtypes

def create_mysql_key(df, key_columns, table_name):
    """Generate MySQL key creation SQL statement."""
    key_name = f"idx_{table_name}_{'_'.join(key_columns)}"
    columns = ', '.join(key_columns)
    return f"ALTER TABLE {table_name} ADD INDEX {key_name} ({columns});"

def connect_to_array(array_host):
    """Connect to a PureStorage array with error handling."""
    try:
        array = FlashArray(array_host, username=USERNAME, password=PASSWORD)
        array.get()
        logger.info(f"Successfully connected to {array_host}")
        return array
    except Exception as e:
        logger.error(f"Failed to connect to {array_host}: {str(e)}")
        return None

def get_array_capacity(array, array_host):
    """Get capacity information from the array."""
    try:
        capacity = array.get(space=True)
        return {
            'array_name': array_host,
            'total_capacity_gb': capacity['capacity'] / 1024**3,
            'used_capacity_gb': capacity['total'] / 1024**3,
            'free_capacity_gb': capacity['capacity'] / 1024**3 - capacity['total'] / 1024**3,
            'percent_used': (capacity['total'] / capacity['capacity']) * 100,
            'data_reduction': capacity['data_reduction'],
            'snapshot_space_gb': capacity['snapshots'] / 1024**3,
            'shared_space_gb': capacity['shared_space'] / 1024**3,
            'system_space_gb': capacity['system'] / 1024**3,
            'thin_provisioning': capacity['thin_provisioning'],
            'timestamp': pd.Timestamp.now()
        }
    except Exception as e:
        logger.error(f"Error getting capacity from {array_host}: {str(e)}")
        return None

def get_connected_hosts(array, array_host):
    """Get information about connected hosts."""
    try:
        hosts = []
        for host in array.list_hosts():
            host_info = {
                'array_name': array_host,
                'host_name': host['name'],
                'host_count': len(host['iqns']) + len(host['wwns']) + len(host['nqn']),
                'iqns': ', '.join(host['iqns']),
                'wwns': ', '.join(host['wwns']),
                'nqn': ', '.join(host['nqn']),
                'port_count': len(host['iqns']) + len(host['wwns']) + len(host['nqn']),
                'volumes': ', '.join([vol['vol'] for vol in array.list_host_connections(host['name'])]),
                'timestamp': pd.Timestamp.now()
            }
            hosts.append(host_info)
        return hosts
    except Exception as e:
        logger.error(f"Error getting hosts from {array_host}: {str(e)}")
        return []

def get_array_alerts(array, array_host):
    """Get alerts from the array."""
    try:
        alerts = []
        for alert in array.list_messages(flagged=True):
            alert_info = {
                'array_name': array_host,
                'alert_id': alert['id'],
                'alert_code': alert['code'],
                'severity': alert['severity'],
                'category': alert['category'],
                'component_name': alert['component_name'],
                'component_type': alert['component_type'],
                'created': pd.to_datetime(alert['created']),
                'description': alert['description'],
                'summary': alert['summary'],
                'state': alert['state'],
                'timestamp': pd.Timestamp.now()
            }
            alerts.append(alert_info)
        return alerts
    except Exception as e:
        logger.error(f"Error getting alerts from {array_host}: {str(e)}")
        return []

def get_array_health(array, array_host):
    """Get health information from the array."""
    try:
        health = array.get(action='monitor')
        return {
            'array_name': array_host,
            'status': health['status'],
            'version': health['version'],
            'revision': health['revision'],
            'model': health['model'],
            'serial': health['serial'],
            'uptime_seconds': health['uptime'],
            'temperature_status': health['temperature']['status'],
            'temperature_value': health['temperature']['value'],
            'power_status': health['power']['status'],
            'timestamp': pd.Timestamp.now()
        }
    except Exception as e:
        logger.error(f"Error getting health from {array_host}: {str(e)}")
        return None

def get_array_wwns(array, array_host):
    """Get WWNs from array ports."""
    try:
        wwns = []
        for port in array.list_ports():
            wwn_info = {
                'array_name': array_host,
                'port_name': port['name'],
                'wwn': port['wwn'],
                'speed': port['speed'],
                'port_type': port['type'],
                'status': port['status'],
                'target': port['target'],
                'timestamp': pd.Timestamp.now()
            }
            wwns.append(wwn_info)
        return wwns
    except Exception as e:
        logger.error(f"Error getting WWNs from {array_host}: {str(e)}")
        return []

def get_host_disk_assignments(array, array_host):
    """Get disk assignments for each host."""
    try:
        assignments = []
        for host in array.list_hosts():
            for connection in array.list_host_connections(host['name']):
                vol_info = array.get_volume(connection['vol'])
                assignment = {
                    'array_name': array_host,
                    'host_name': host['name'],
                    'volume_name': connection['vol'],
                    'lun': connection['lun'],
                    'size_gb': vol_info['size'] / 1024**3,
                    'serial': vol_info['serial'],
                    'created': pd.to_datetime(vol_info['created']),
                    'timestamp': pd.Timestamp.now()
                }
                assignments.append(assignment)
        return assignments
    except Exception as e:
        logger.error(f"Error getting host disk assignments from {array_host}: {str(e)}")
        return []

def process_array(array_host, result_queue):
    """Process a single array and collect all data."""
    logger.info(f"Starting processing for {array_host}")
    start_time = time.time()
    
    array = connect_to_array(array_host)
    if not array:
        result_queue.put((array_host, None, None, None, None, None, None))
        return
    
    # Collect all data
    capacity_data = get_array_capacity(array, array_host)
    hosts_data = get_connected_hosts(array, array_host)
    alerts_data = get_array_alerts(array, array_host)
    health_data = get_array_health(array, array_host)
    wwns_data = get_array_wwns(array, array_host)
    host_disks_data = get_host_disk_assignments(array, array_host)
    
    # Close the connection
    array.invalidate_cookie()
    
    elapsed = time.time() - start_time
    logger.info(f"Completed processing for {array_host} in {elapsed:.2f} seconds")
    
    result_queue.put((array_host, capacity_data, hosts_data, alerts_data, health_data, wwns_data, host_disks_data))

def update_global_dataframes(results):
    """Update global DataFrames with thread-safe locking."""
    array_host, capacity_data, hosts_data, alerts_data, health_data, wwns_data, host_disks_data = results
    
    with data_lock:
        global capacity_df, hosts_df, alerts_df, health_df, wwns_df, host_disks_df
        
        # Update capacity DataFrame
        if capacity_data:
            temp_df = pd.DataFrame([capacity_data])
            capacity_df = pd.concat([capacity_df, temp_df], ignore_index=True)
        
        # Update hosts DataFrame
        if hosts_data:
            temp_df = pd.DataFrame(hosts_data)
            hosts_df = pd.concat([hosts_df, temp_df], ignore_index=True)
        
        # Update alerts DataFrame
        if alerts_data:
            temp_df = pd.DataFrame(alerts_data)
            alerts_df = pd.concat([alerts_df, temp_df], ignore_index=True)
        
        # Update health DataFrame
        if health_data:
            temp_df = pd.DataFrame([health_data])
            health_df = pd.concat([health_df, temp_df], ignore_index=True)
        
        # Update WWNs DataFrame
        if wwns_data:
            temp_df = pd.DataFrame(wwns_data)
            wwns_df = pd.concat([wwns_df, temp_df], ignore_index=True)
        
        # Update host disks DataFrame
        if host_disks_data:
            temp_df = pd.DataFrame(host_disks_data)
            host_disks_df = pd.concat([host_disks_df, temp_df], ignore_index=True)

def collect_all_data():
    """Collect data from all arrays using multithreading."""
    logger.info("Starting data collection from all arrays")
    start_time = time.time()
    
    result_queue = Queue()
    
    # Using ThreadPoolExecutor for better resource management
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_array, array_host, result_queue) for array_host in ARRAYS]
        
        # Wait for all tasks to complete
        for future in futures:
            future.result()
    
    # Process all results
    while not result_queue.empty():
        update_global_dataframes(result_queue.get())
    
    elapsed = time.time() - start_time
    logger.info(f"Completed data collection from all arrays in {elapsed:.2f} seconds")

def export_to_mysql(engine):
    """Export all DataFrames to MySQL database."""
    logger.info("Starting export to MySQL database")
    
    # Define table names
    table_mapping = {
        'capacity_df': 'pure_capacity',
        'hosts_df': 'pure_hosts',
        'alerts_df': 'pure_alerts',
        'health_df': 'pure_health',
        'wwns_df': 'pure_wwns',
        'host_disks_df': 'pure_host_disks'
    }
    
    # Export each DataFrame
    for df_name, table_name in table_mapping.items():
        df = globals()[df_name]
        if not df.empty:
            try:
                # Clean data - replace NaN with None for MySQL
                df = df.where(pd.notnull(df), None)
                
                dtypes = calculate_column_lengths(df)
                df.to_sql(
                    name=table_name,
                    con=engine,
                    if_exists='append',
                    index=False,
                    dtype=dtypes,
                    method='multi',
                    chunksize=1000
                )
                logger.info(f"Successfully exported {table_name} with {len(df)} records")
                
                # Generate and log key creation SQL
                if table_name == 'pure_hosts':
                    key_sql = create_mysql_key(df, ['array_name', 'host_name'], table_name)
                    logger.info(f"Recommended index for {table_name}:\n{key_sql}")
                elif table_name == 'pure_alerts':
                    key_sql = create_mysql_key(df, ['array_name', 'alert_id'], table_name)
                    logger.info(f"Recommended index for {table_name}:\n{key_sql}")
                
            except Exception as e:
                logger.error(f"Error exporting {table_name}: {str(e)}")
        else:
            logger.warning(f"Skipping empty DataFrame {df_name}")

def main():
    """Main execution function."""
    try:
        # Create MySQL engine
        engine = create_engine(MYSQL_CONN_STRING)
        
        # Collect data from all arrays
        collect_all_data()
        
        # Export to MySQL
        export_to_mysql(engine)
        
        logger.info("Script completed successfully")
    except Exception as e:
        logger.error(f"Script failed: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()
```

## Key Improvements:

1. **Removed distutils dependency**: The script no longer uses any deprecated modules.

2. **Enhanced string length calculation**: Improved the `calculate_column_lengths` function to:
   - Handle NaN values in string columns
   - Provide a default length (255) when max length can't be determined
   - More robust type checking

3. **Better MySQL export handling**:
   - Added explicit NaN to None conversion for MySQL compatibility
   - Added batch insertion with `method='multi'` and `chunksize=1000`
   - More robust error handling

4. **General robustness improvements**:
   - Better handling of edge cases in data collection
   - More detailed logging
   - Improved error messages

5. **Performance optimizations**:
   - More efficient DataFrame concatenation
   - Better memory management with connection cleanup

This version maintains all the original functionality while being more robust and compatible with Python 3.12's module changes. The script still collects all the requested PureStorage array information and exports it to MySQL efficiently.
