# Tracking Port Status Changes in MySQL

To track when a port goes offline in your MySQL database, you have several options. Here's how you can implement this:

## Option 1: Create a Status Change Log Table

```sql
CREATE TABLE port_status_changes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    port_id INT,  -- or VARCHAR if your ports have names
    old_status VARCHAR(50),
    new_status VARCHAR(50),
    change_timestamp TIMESTAMP,
    INDEX (port_id),
    INDEX (change_timestamp)
);
```

Then modify your Python script to check for changes before inserting:

```python
import pandas as pd
import pymysql

def update_port_status(df):
    connection = pymysql.connect(host='your_host',
                                user='your_user',
                                password='your_password',
                                database='your_db')
    
    try:
        with connection.cursor() as cursor:
            # Check for status changes
            for index, row in df.iterrows():
                # Get current status from DB
                cursor.execute("SELECT port_status FROM your_table WHERE port_id = %s ORDER BY timestamp DESC LIMIT 1", 
                             (row['port_id'],))
                result = cursor.fetchone()
                
                if result and result[0] != row['port_status']:
                    # Status changed - log it
                    cursor.execute("""
                        INSERT INTO port_status_changes 
                        (port_id, old_status, new_status, change_timestamp) 
                        VALUES (%s, %s, %s, %s)
                    """, (row['port_id'], result[0], row['port_status'], row['timestamp']))
                    
                    # Optional: Send alert if port went offline
                    if row['port_status'] == 'offline':
                        print(f"Alert: Port {row['port_id']} went offline at {row['timestamp']}")
            
            # Insert the new data
            # Your existing pandas to_sql or insert logic here
            
        connection.commit()
    finally:
        connection.close()
```

## Option 2: Use MySQL Triggers

Create a trigger that automatically logs changes:

```sql
DELIMITER //
CREATE TRIGGER after_port_status_update
AFTER INSERT ON your_table
FOR EACH ROW
BEGIN
    DECLARE prev_status VARCHAR(50);
    
    -- Get previous status
    SELECT port_status INTO prev_status 
    FROM your_table 
    WHERE port_id = NEW.port_id 
    ORDER BY timestamp DESC LIMIT 1,1;
    
    -- If status changed, log it
    IF prev_status IS NOT NULL AND prev_status != NEW.port_status THEN
        INSERT INTO port_status_changes 
        (port_id, old_status, new_status, change_timestamp)
        VALUES (NEW.port_id, prev_status, NEW.port_status, NEW.timestamp);
    END IF;
END//
DELIMITER ;
```

## Option 3: Query Existing Data for Changes

If you can't modify the insertion process, you can query for changes:

```sql
SELECT 
    t1.port_id,
    t1.port_status AS old_status,
    t2.port_status AS new_status,
    t2.timestamp AS change_time
FROM 
    your_table t1
JOIN 
    your_table t2 ON t1.port_id = t2.port_id
WHERE 
    t1.timestamp < t2.timestamp
    AND t1.port_status != t2.port_status
    AND NOT EXISTS (
        SELECT 1 FROM your_table t3
        WHERE t3.port_id = t1.port_id
        AND t3.timestamp > t1.timestamp
        AND t3.timestamp < t2.timestamp
    )
ORDER BY 
    t2.timestamp DESC;
```

## Python Monitoring Script

You could also create a separate Python script to monitor changes:

```python
import pymysql
from time import sleep

def monitor_port_changes():
    connection = pymysql.connect(host='your_host',
                                user='your_user',
                                password='your_password',
                                database='your_db')
    
    last_checks = {}  # Store last status per port
    
    try:
        while True:
            with connection.cursor() as cursor:
                cursor.execute("SELECT port_id, port_status, timestamp FROM your_table ORDER BY timestamp DESC")
                results = cursor.fetchall()
                
                current_status = {}
                for port_id, status, timestamp in results:
                    if port_id not in current_status:
                        current_status[port_id] = (status, timestamp)
                
                # Check for changes
                for port_id, (status, timestamp) in current_status.items():
                    if port_id in last_checks and last_checks[port_id][0] != status:
                        old_status, old_time = last_checks[port_id]
                        print(f"Port {port_id} changed from {old_status} to {status} at {timestamp}")
                        
                        if status.lower() == 'offline':
                            print(f"ALERT: Port {port_id} went offline!")
                    
                    last_checks[port_id] = (status, timestamp)
            
            sleep(60)  # Check every minute
    finally:
        connection.close()
```

Choose the option that best fits your architecture and requirements. Option 1 is generally the most robust as it captures changes at insertion time.




# Tracking Port Status Changes with Pandas

Yes, you can absolutely use pandas to efficiently track port status changes without iterating through each port individually. Here's how to do it:

## Method 1: Compare Current Data with Previous Data

```python
import pandas as pd
from sqlalchemy import create_engine

# Set up database connection
engine = create_engine('mysql+pymysql://user:password@host/database')

def track_port_changes():
    # Get the two most recent readings for all ports
    query = """
    WITH ranked_data AS (
        SELECT 
            port_id,
            port_status,
            timestamp,
            ROW_NUMBER() OVER (PARTITION BY port_id ORDER BY timestamp DESC) as row_num
        FROM your_table
    )
    SELECT * FROM ranked_data WHERE row_num <= 2
    """
    
    # Load data into DataFrame
    df = pd.read_sql(query, engine)
    
    # Pivot to get current and previous status side by side
    status_changes = df.pivot(index='port_id', columns='row_num', values=['port_status', 'timestamp'])
    
    # Flatten multi-index columns
    status_changes.columns = [f'{col[0]}_{col[1]}' for col in status_changes.columns]
    
    # Filter for ports where status changed
    changed_ports = status_changes[
        (status_changes['port_status_1'] != status_changes['port_status_2']) & 
        (status_changes['port_status_1'].notna() & status_changes['port_status_2'].notna())
    ]
    
    # Add meaningful columns
    changed_ports = changed_ports.assign(
        old_status=changed_ports['port_status_2'],
        new_status=changed_ports['port_status_1'],
        change_time=changed_ports['timestamp_1'],
        time_since_last_change=changed_ports['timestamp_1'] - changed_ports['timestamp_2']
    )
    
    # Filter for ports that went offline
    offline_ports = changed_ports[changed_ports['new_status'].str.lower() == 'offline']
    
    return offline_ports
```

## Method 2: Compare New Data with Last Known State

```python
def detect_status_changes(new_data_df):
    # Get last known status for all ports
    last_status = pd.read_sql("""
        SELECT port_id, port_status 
        FROM (
            SELECT port_id, port_status,
                   ROW_NUMBER() OVER (PARTITION BY port_id ORDER BY timestamp DESC) as rn
            FROM your_table
        ) t WHERE rn = 1
    """, engine)
    
    # Merge with new data
    merged = new_data_df.merge(last_status, on='port_id', 
                             suffixes=('_current', '_previous'),
                             how='left')
    
    # Find changes
    changes = merged[merged['port_status_current'] != merged['port_status_previous']]
    
    # Filter for offline events
    offline_events = changes[changes['port_status_current'].str.lower() == 'offline']
    
    return offline_events
```

## Method 3: Using pandas diff() with Time Series Data

If your data is properly timestamped:

```python
def track_changes_time_series(hours_to_check=24):
    # Get recent data
    df = pd.read_sql(f"""
        SELECT port_id, port_status, timestamp
        FROM your_table
        WHERE timestamp >= NOW() - INTERVAL {hours_to_check} HOUR
        ORDER BY port_id, timestamp
    """, engine)
    
    # For each port, find status changes
    changes = (df.groupby('port_id')['port_status']
               .apply(lambda x: x[x.ne(x.shift())])
               .reset_index()
               .dropna())
    
    # Get offline events
    offline = changes[changes['port_status'].str.lower() == 'offline']
    
    return offline
```

## Usage Example

```python
# Example 1: Check for recent changes
offline_ports = track_port_changes()
print("Ports that recently went offline:")
print(offline_ports[['port_id', 'old_status', 'new_status', 'change_time']])

# Example 2: Check new data before insertion
new_data = pd.DataFrame(...)  # Your new data
offline_events = detect_status_changes(new_data)
if not offline_events.empty:
    print("Alert: The following ports went offline:")
    print(offline_events)
    
    # Optional: Send notifications or log to database
    offline_events.to_sql('port_offline_events', engine, if_exists='append', index=False)
```

## Advantages of this approach:

1. **Vectorized operations**: Pandas operates on entire columns at once, much faster than row-by-row iteration
2. **Minimal database queries**: Only 1-2 queries needed regardless of number of ports
3. **Clean syntax**: Expressive pandas operations make the logic clear
4. **Flexible output**: Results stay in DataFrames for easy further processing

For very large datasets, you might want to add limits to your SQL queries or process data in chunks.
