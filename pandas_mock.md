# Python Function to Generate Time-Based Mock DataFrames

Here's a modified version of the function that generates a DataFrame based solely on a time range and interval, automatically determining the number of rows from these parameters:

```python
import pandas as pd
import numpy as np
import random
from datetime import datetime
from typing import List, Dict, Union, Optional

def generate_time_series_data(
    columns: List[Dict] = None,
    date_range: Dict = None,
    random_seed: Optional[int] = None
) -> pd.DataFrame:
    """
    Generate a pandas DataFrame with mock time series data for testing charts.
    The number of rows is determined by the date range and frequency.
    
    Parameters:
    -----------
    columns : List[Dict]
        List of column specifications. Each dict should contain:
        - 'name': column name (str)
        - 'type': data type ('int', 'float', 'str', 'bool', 'category')
        - 'min': minimum value (for numeric types)
        - 'max': maximum value (for numeric types)
        - 'values': list of possible values (for str/category)
        - 'null_pct': percentage of null values (0-1, default: 0)
    date_range : Dict
        Specification for date column. Should contain:
        - 'name': column name (str, default: 'date')
        - 'start': start date (str or datetime)
        - 'end': end date (str or datetime)
        - 'freq': frequency ('D', 'M', 'Y', 'H', 'T', 'S' or pandas offset alias)
        - 'random': whether to randomize dates (bool, default: False)
    random_seed : Optional[int]
        Seed for random number generation for reproducibility
    
    Returns:
    --------
    pd.DataFrame
        Generated DataFrame with mock time series data
    """
    if random_seed is not None:
        np.random.seed(random_seed)
        random.seed(random_seed)
    
    # Default columns if none provided
    if columns is None:
        columns = [
            {'name': 'value', 'type': 'float', 'min': 0, 'max': 100},
            {'name': 'category', 'type': 'category', 'values': ['A', 'B', 'C', 'D']},
        ]
    
    # Validate date range
    if date_range is None:
        date_range = {
            'name': 'date',
            'start': '2020-01-01',
            'end': '2020-12-31',
            'freq': 'D',
            'random': False
        }
    
    # Generate date column
    date_name = date_range.get('name', 'date')
    start = pd.to_datetime(date_range.get('start', '2020-01-01'))
    end = pd.to_datetime(date_range.get('end', '2020-12-31'))
    freq = date_range.get('freq', 'D')
    random_dates = date_range.get('random', False)
    
    if random_dates:
        # For random dates, we need to calculate a reasonable number of points
        # based on the frequency and time span
        temp_range = pd.date_range(start, end, freq=freq)
        num_points = len(temp_range)
        date_series = pd.to_datetime(np.random.choice(
            temp_range, 
            size=num_points,
            replace=False
        )).sort_values()
    else:
        date_series = pd.date_range(start, end, freq=freq)
    
    num_rows = len(date_series)
    
    # Initialize DataFrame with dates
    df = pd.DataFrame({date_name: date_series})
    
    # Generate each column
    for col_spec in columns:
        col_name = col_spec['name']
        col_type = col_spec['type']
        null_pct = col_spec.get('null_pct', 0)
        
        # Generate base data
        if col_type in ['int', 'float']:
            min_val = col_spec.get('min', 0)
            max_val = col_spec.get('max', 100)
            
            if col_type == 'int':
                data = np.random.randint(min_val, max_val + 1, size=num_rows)
            else:  # float
                data = np.random.uniform(min_val, max_val, size=num_rows)
                
        elif col_type in ['str', 'category']:
            values = col_spec.get('values', [f'item_{i}' for i in range(1, 6)])
            data = np.random.choice(values, size=num_rows)
            
        elif col_type == 'bool':
            data = np.random.choice([True, False], size=num_rows)
            
        else:
            raise ValueError(f"Unsupported column type: {col_type}")
        
        # Add null values if specified
        if null_pct > 0:
            null_mask = np.random.random(size=num_rows) < null_pct
            data[null_mask] = None
        
        # Add to DataFrame
        df[col_name] = data
        
        # Convert to category if specified
        if col_type == 'category':
            df[col_name] = df[col_name].astype('category')
    
    return df


# Example usage
if __name__ == "__main__":
    # Example 1: Daily data for one year
    df1 = generate_time_series_data(
        columns=[
            {'name': 'temperature', 'type': 'float', 'min': -10, 'max': 35},
            {'name': 'weather', 'type': 'category', 'values': ['sunny', 'cloudy', 'rainy', 'snowy']},
        ],
        date_range={
            'name': 'date',
            'start': '2023-01-01',
            'end': '2023-12-31',
            'freq': 'D'
        }
    )
    print("Example 1 - Daily weather data for one year:")
    print(df1.head())
    print(f"\nTotal rows: {len(df1)}")
    
    # Example 2: Intraday trading data (5-minute intervals)
    df2 = generate_time_series_data(
        columns=[
            {'name': 'price', 'type': 'float', 'min': 100, 'max': 200},
            {'name': 'volume', 'type': 'int', 'min': 1000, 'max': 50000},
        ],
        date_range={
            'name': 'timestamp',
            'start': '2023-06-01 09:30:00',
            'end': '2023-06-01 16:00:00',
            'freq': '5T'  # 5 minutes
        }
    )
    print("\nExample 2 - Intraday trading data (5-minute intervals):")
    print(df2.head())
    print(f"\nTotal rows: {len(df2)}")
    
    # Example 3: Random monthly samples over 5 years
    df3 = generate_time_series_data(
        columns=[
            {'name': 'sales', 'type': 'float', 'min': 5000, 'max': 50000},
            {'name': 'region', 'type': 'category', 'values': ['NA', 'EU', 'APAC']},
        ],
        date_range={
            'name': 'month',
            'start': '2018-01-01',
            'end': '2022-12-31',
            'freq': 'M',
            'random': True
        },
        random_seed=42
    )
    print("\nExample 3 - Random monthly samples over 5 years:")
    print(df3.head())
    print(f"\nTotal rows: {len(df3)}")
```

## Key Changes:

1. **Removed `num_rows` parameter**: The number of rows is now determined automatically based on:
   - The time range (start to end)
   - The frequency (daily, hourly, etc.)

2. **Improved date generation**:
   - For sequential dates, uses `pd.date_range` which automatically creates the correct number of points
   - For random dates, first calculates how many points would exist in a regular sequence, then samples that many random points

3. **Better examples** showing different time frequencies:
   - Daily data for a year
   - Intraday 5-minute intervals
   - Random monthly samples

4. **Output includes row count** to demonstrate how many points were generated

This version is more suitable for time series data visualization testing, as it ensures your data points are properly spaced according to your time specifications.
