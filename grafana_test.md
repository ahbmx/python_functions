Here's a complete example with mock data, database structure, and Grafana query:

### 1. Example DataFrame with Mock Data

```python
import pandas as pd
from datetime import datetime, timedelta

# Generate time series data
timestamps = [datetime(2023, 6, 1) + timedelta(minutes=5*i) for i in range(12)]
arrays = ['Array_A', 'Array_B', 'Array_C']

data = {
    'timestamp': [],
    'array_name': [],
    'iops_read': [],
    'iops_write': [],
    'latency_ms': [],
    'capacity_used_pct': []
}

for ts in timestamps:
    for array in arrays:
        data['timestamp'].append(ts)
        data['array_name'].append(array)
        # Generate realistic mock values
        base_read = 5000 if array == 'Array_A' else 8000 if array == 'Array_B' else 3000
        base_write = 3000 if array == 'Array_A' else 5000 if array == 'Array_B' else 2000
        data['iops_read'].append(base_read + int(2000 * (ts.hour/24)))
        data['iops_write'].append(base_write + int(1000 * (ts.hour/24)))
        data['latency_ms'].append(2.5 if array == 'Array_A' else 1.8 if array == 'Array_B' else 3.2)
        data['capacity_used_pct'].append(65 if array == 'Array_A' else 45 if array == 'Array_B' else 80)

df = pd.DataFrame(data)
print(df.head(6))
```

Sample output:
```
            timestamp array_name  iops_read  iops_write  latency_ms  capacity_used_pct
0 2023-06-01 00:00:00    Array_A       5000        3000         2.5                 65
1 2023-06-01 00:00:00    Array_B       8000        5000         1.8                 45
2 2023-06-01 00:00:00    Array_C       3000        2000         3.2                 80
3 2023-06-01 00:05:00    Array_A       5083        3041         2.5                 65
4 2023-06-01 00:05:00    Array_B       8083        5041         1.8                 45
5 2023-06-01 00:05:00    Array_C       3083        2041         3.2                 80
```

### 2. MySQL Table Structure

```sql
CREATE TABLE storage_array_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    array_name VARCHAR(50) NOT NULL,
    iops_read INT NOT NULL,
    iops_write INT NOT NULL,
    latency_ms DECIMAL(5,2) NOT NULL,
    capacity_used_pct DECIMAL(5,2) NOT NULL,
    INDEX (timestamp),
    INDEX (array_name)
) ENGINE=InnoDB;

-- Optional: For better performance with time-series data
ALTER TABLE storage_array_metrics 
PARTITION BY RANGE (TO_DAYS(timestamp)) (
    PARTITION p2023_q2 VALUES LESS THAN (TO_DAYS('2023-07-01')),
    PARTITION p2023_q3 VALUES LESS THAN (TO_DAYS('2023-10-01')),
    PARTITION future VALUES LESS THAN MAXVALUE
);
```

### 3. Loading Data to MySQL from Pandas

```python
from sqlalchemy import create_engine

engine = create_engine('mysql+pymysql://user:password@localhost/storage_db')
df.to_sql('storage_array_metrics', engine, if_exists='append', index=False, method='multi')
```

### 4. Grafana Query for Multi-Array Visualization

For a time-series panel showing all arrays together:

```sql
SELECT
    timestamp as time,
    array_name,
    iops_read,
    iops_write,
    latency_ms,
    capacity_used_pct
FROM storage_array_metrics
WHERE
    $__timeFilter(timestamp) AND
    array_name IN ($array)  -- Use Grafana variable for filtering
ORDER BY timestamp
```

### 5. Grafana Dashboard Setup Tips

1. **Create Variables**:
   - Add a dashboard variable named `array` with query:
     ```sql
     SELECT DISTINCT array_name FROM storage_array_metrics ORDER BY array_name
     ```
   - Set to multi-select with "All" option

2. **Panel Configuration**:
   - Use a Time Series visualization
   - Add multiple series:
     - Field: `iops_read` (alias as `${__field.labels.array_name} Read IOPS`)
     - Field: `iops_write` (alias as `${__field.labels.array_name} Write IOPS`)
   - Add right Y-axis for `latency_ms`
   - Add another panel for `capacity_used_pct` as a stat/gauge

3. **Display Options**:
   - Enable "Points" to see individual values
   - Set line width to 2
   - Use "Override" to give each array a distinct color

### Example Visualization Output:
You'll get a chart showing:
- Multiple colored lines for each array's read IOPS
- Dashed lines for write IOPS
- Right axis showing latency
- Tooltips showing all metrics when hovering
- Legend showing array names that you can click to filter

Would you like me to provide specific Grafana JSON for this dashboard or any additional visualization examples?
