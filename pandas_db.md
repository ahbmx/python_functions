# Python Script for Auto-Detecting Column Types and Maximum Lengths in Pandas DataFrames

Here's a comprehensive solution to automatically detect column data types and maximum lengths for SQLAlchemy schema definition:

```python
import pandas as pd
import numpy as np
from sqlalchemy import types as sa_types

def detect_column_types(df):
    """
    Automatically detect appropriate SQLAlchemy column types for each column in a DataFrame.
    
    Args:
        df (pd.DataFrame): Input DataFrame to analyze
        
    Returns:
        dict: Dictionary mapping column names to SQLAlchemy types
    """
    type_mapping = {
        'int64': sa_types.Integer,
        'float64': sa_types.Float,
        'bool': sa_types.Boolean,
        'datetime64[ns]': sa_types.DateTime,
        'timedelta64[ns]': sa_types.Interval,
        'object': sa_types.String,
        'category': sa_types.String
    }
    
    dtypes = {}
    
    for col in df.columns:
        col_type = str(df[col].dtype)
        
        # Handle datetime separately as pandas often stores these as objects
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            dtypes[col] = sa_types.DateTime()
        elif pd.api.types.is_timedelta64_dtype(df[col]):
            dtypes[col] = sa_types.Interval()
        elif col_type in type_mapping:
            # For string types, we'll handle length separately
            if col_type == 'object' or col_type == 'category':
                max_len = df[col].astype(str).str.len().max()
                # Handle NaN in max_len
                max_len = int(max_len) if not np.isnan(max_len) else 255
                dtypes[col] = sa_types.String(length=max_len)
            else:
                dtypes[col] = type_mapping[col_type]()
        else:
            # Default to String if type not recognized
            max_len = df[col].astype(str).str.len().max()
            max_len = int(max_len) if not np.isnan(max_len) else 255
            dtypes[col] = sa_types.String(length=max_len)
    
    return dtypes

def get_max_lengths(df):
    """
    Calculate maximum string lengths for all columns in DataFrame.
    
    Args:
        df (pd.DataFrame): Input DataFrame to analyze
        
    Returns:
        dict: Dictionary mapping column names to maximum lengths
    """
    max_lengths = {}
    
    for col in df.columns:
        # Convert to string and calculate lengths
        str_series = df[col].astype(str)
        max_len = str_series.str.len().max()
        
        # Handle NaN (if entire column is NA)
        if pd.isna(max_len):
            max_lengths[col] = 1  # Default minimum length
        else:
            max_lengths[col] = int(max_len)
    
    return max_lengths

def get_column_metadata(df):
    """
    Get comprehensive column metadata including types and lengths.
    
    Args:
        df (pd.DataFrame): Input DataFrame to analyze
        
    Returns:
        dict: Dictionary with column metadata including:
              - 'dtypes': SQLAlchemy types
              - 'max_lengths': Maximum string lengths
              - 'nullable': List of nullable columns
    """
    # Get SQLAlchemy dtypes
    dtypes = detect_column_types(df)
    
    # Get max lengths
    max_lengths = get_max_lengths(df)
    
    # Detect nullable columns
    nullable_cols = [
        col for col in df.columns 
        if df[col].isnull().any() or pd.api.types.is_categorical_dtype(df[col])
    ]
    
    return {
        'dtypes': dtypes,
        'max_lengths': max_lengths,
        'nullable': nullable_cols
    }

# Example usage:
if __name__ == "__main__":
    # Sample DataFrame
    data = {
        'id': [1, 2, 3],
        'name': ['Alice', 'Bob', 'Charlie'],
        'age': [25, 30, 35],
        'salary': [50000.50, 60000.75, 70000.00],
        'is_manager': [True, False, True],
        'hire_date': pd.to_datetime(['2020-01-01', '2019-05-15', '2018-11-20']),
        'notes': ['Short note', 'A bit longer note', 'A very much longer note that exceeds typical length'],
        'department': ['HR', 'IT', 'Finance'],
        'nullable_col': [1, None, 3]
    }
    
    df = pd.DataFrame(data)
    
    # Get column metadata
    metadata = get_column_metadata(df)
    
    print("Detected SQLAlchemy dtypes:")
    for col, dtype in metadata['dtypes'].items():
        print(f"{col}: {dtype}")
    
    print("\nMaximum lengths:")
    for col, length in metadata['max_lengths'].items():
        print(f"{col}: {length}")
    
    print("\nNullable columns:", metadata['nullable'])
```

## Key Features:

1. **Automatic Type Detection**:
   - Handles numeric types (Integer, Float)
   - Detects boolean, datetime, and timedelta types
   - Defaults to String for object and category types
   - Special handling for datetime columns

2. **Length Calculation**:
   - Calculates maximum string lengths for text columns
   - Handles NaN values in length calculations
   - Provides sensible defaults when length can't be determined

3. **Nullable Columns Detection**:
   - Identifies columns containing null values
   - Useful for SQL schema definition

4. **SQLAlchemy Integration**:
   - Returns proper SQLAlchemy type objects ready for schema definition

5. **Comprehensive Metadata**:
   - Returns all necessary information in a single function call

You can use the output from `get_column_metadata()` directly when creating SQL tables with SQLAlchemy. The `dtypes` dictionary can be passed as the `dtype` parameter when using pandas' `to_sql()` method with SQLAlchemy.

Would you like me to modify any part of this solution to better fit your specific needs?
