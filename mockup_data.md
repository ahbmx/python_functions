Here's an enhanced version that allows you to generate data for a specific date or a date range, with proper datetime formatting and optimized data types:

```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Union, Tuple

def generate_storage_mock_data(
    start_date: str = "27/07/2025",
    end_date: Union[str, None] = None,
    interval_minutes: int = 10
) -> pd.DataFrame:
    """
    Generate mock storage system data for a date or date range with configurable intervals.
    
    Args:
        start_date (str): Start date in DD/MM/YYYY format (default: "27/07/2025")
        end_date (str|None): End date in DD/MM/YYYY format (None for single day)
        interval_minutes (int): Data interval in minutes (default: 10)
        
    Returns:
        pd.DataFrame: DataFrame containing mock storage metrics with proper dtypes
    """
    # Parse dates
    start = datetime.strptime(start_date, "%d/%m/%Y")
    end = datetime.strptime(end_date, "%d/%m/%Y") if end_date else start
    
    # Ensure end date is not before start date
    if end < start:
        raise ValueError("End date cannot be before start date")
    
    # Generate time points
    time_points = []
    current = start
    while current <= end:
        for minute in range(0, 1440, interval_minutes):  # 1440 minutes = 24 hours
            time_points.append(current + timedelta(minutes=minute))
        current += timedelta(days=1)
    
    # Storage system configurations
    storage_systems = {
        "SAN_Cluster_A": {
            "type": "FibreChannel SAN",
            "base_iops": 15000,
            "capacity_gb": 500000,
            "host_count": 24,
            "daily_capacity_decrease": 0.3  # % per day
        },
        "NAS_Cluster_B": {
            "type": "Scale-Out NAS",
            "base_iops": 8000,
            "capacity_gb": 1200000,
            "host_count": 32,
            "daily_capacity_decrease": 0.2
        },
        "Hyperconverged_C": {
            "type": "Hyperconverged",
            "base_iops": 20000,
            "capacity_gb": 250000,
            "host_count": 16,
            "daily_capacity_decrease": 0.4
        },
        "ObjectStore_D": {
            "type": "Object Storage",
            "base_iops": 5000,
            "capacity_gb": 3000000,
            "host_count": 8,
            "daily_capacity_decrease": 0.1
        }
    }
    
    # Generate mock data
    data = []
    for timestamp in time_points:
        days_since_start = (timestamp.date() - start.date()).days
        
        for system, specs in storage_systems.items():
            # Business hours pattern (9AM-6PM has higher activity)
            hour = timestamp.hour
            is_business_hours = 9 <= hour < 18
            daily_pattern = 1.3 if is_business_hours else 0.7
            
            # Add some minute-level variation
            minute_variation = 0.9 + 0.2 * (timestamp.minute / 60)
            
            # Calculate IOPS with variation
            iops = int(specs["base_iops"] * daily_pattern * minute_variation * np.random.uniform(0.95, 1.05))
            
            # Capacity decreases daily with some noise
            capacity_pct = 100 - (specs["daily_capacity_decrease"] * days_since_start * np.random.uniform(0.9, 1.1))
            capacity_pct = max(10, min(100, capacity_pct))
            
            # Host count occasionally increases
            host_count = specs["host_count"] + int(days_since_start / 7)  # +1 per week
            
            data.append({
                "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "storage_system": system,
                "system_type": specs["type"],
                "iops": iops,
                "capacity_percent": round(capacity_pct, 2),
                "capacity_gb": specs["capacity_gb"],
                "host_count": host_count,
                "iops_per_host": round(iops / host_count),
                "is_weekend": timestamp.weekday() >= 5  # Saturday/Sunday
            })
    
    # Create DataFrame with proper types
    df = pd.DataFrame(data)
    
    # Convert and set dtypes
    dtypes = {
        'timestamp': 'datetime64[ns]',
        'storage_system': 'category',
        'system_type': 'category',
        'iops': 'int32',
        'capacity_percent': 'float32',
        'capacity_gb': 'int64',
        'host_count': 'int16',
        'iops_per_host': 'int32',
        'is_weekend': 'bool'
    }
    
    df = df.astype(dtypes)
    
    # Add derived datetime features
    df['date'] = df['timestamp'].dt.date.astype('datetime64[ns]')
    df['hour'] = df['timestamp'].dt.hour.astype('int8')
    
    return df

# Example usage:
# Single day
single_day_data = generate_storage_mock_data("27/07/2025")
print(f"Single day data shape: {single_day_data.shape}")

# Date range (3 days)
range_data = generate_storage_mock_data("27/07/2025", "29/07/2025")
print(f"Date range data shape: {range_data.shape}")
print("\nSample data:")
print(range_data.sample(5))
```

### Key Features:

1. **Flexible Date Generation**:
   - Generate data for a single day (just provide start_date)
   - Generate data for a range (provide start_date and end_date)
   - Configurable interval (default 10 minutes)

2. **Realistic Patterns**:
   - Business hours (9AM-6PM) have higher IOPS
   - Capacity slowly decreases each day
   - Host count grows gradually over time
   - Weekend/weekday differentiation

3. **Optimized Data Types**:
   - Proper datetime formatting ("%Y-%m-%d %H:%M:%S")
   - Memory-efficient numeric types (int16, int32, float32)
   - Categorical types for strings with few unique values

4. **Additional Features**:
   - Derived datetime features (date, hour)
   - Weekend flag for analysis
   - Minute-level variation in metrics

5. **Usage Examples**:
```python
# Single day
df = generate_storage_mock_data("01/08/2025")

# 5-day range with 15-minute intervals
df = generate_storage_mock_data(
    start_date="01/08/2025",
    end_date="05/08/2025",
    interval_minutes=15
)
```

This version gives you complete control over the time period while maintaining realistic storage system behavior patterns and optimal DataFrame structure for database insertion.
