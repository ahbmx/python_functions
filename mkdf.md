Perfect! We can extend your `mkdf` function to handle a `convert_to_utc` parameter. This parameter will accept a string (single column) or a list of columns, convert them to datetime, assume they are in `America/Mexico_City` timezone, and then convert them to UTC.

Here’s the updated function:

```python
import pandas as pd
import os
import pytz

def mkdf(data, convert_to_utc="event_time"):
    """
    Converts input data to a pandas DataFrame and optionally converts specified datetime columns to UTC.

    Parameters:
        data (dict, str): Dictionary, CSV file path, or Excel file path.
        convert_to_utc (str or list, optional): Column name or list of column names to convert to UTC. Default is 'event_time'.

    Returns:
        pd.DataFrame: Converted DataFrame with datetime columns converted to UTC.
    """
    # Load data into DataFrame
    if isinstance(data, dict):
        df = pd.DataFrame(data)
    elif isinstance(data, str) and os.path.isfile(data):
        file_ext = os.path.splitext(data)[1].lower()
        if file_ext == '.csv':
            df = pd.read_csv(data)
        elif file_ext in ['.xls', '.xlsx']:
            df = pd.read_excel(data)
        else:
            raise ValueError("Unsupported file type. Only CSV or Excel files are allowed.")
    else:
        raise TypeError("Input must be a dictionary or a valid CSV/Excel file path.")

    # Ensure convert_to_utc is a list
    if convert_to_utc is not None:
        if isinstance(convert_to_utc, str):
            convert_to_utc = [convert_to_utc]

        # Convert specified columns to datetime and then to UTC
        for col in convert_to_utc:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')  # Convert to datetime
                df[col] = df[col].dt.tz_localize('America/Mexico_City', ambiguous='NaT', nonexistent='NaT')  # Localize
                df[col] = df[col].dt.tz_convert('UTC')  # Convert to UTC
            else:
                raise ValueError(f"Column '{col}' not found in DataFrame.")
    
    return df
```

### ✅ Example Usage:

```python
# From a dictionary
data_dict = {
    "event_time": ["2025-12-12 08:00:00", "2025-12-12 15:00:00"],
    "value": [10, 20]
}
df = mkdf(data_dict)
print(df)

# Convert multiple columns
data_dict = {
    "event_time": ["2025-12-12 08:00:00", "2025-12-12 15:00:00"],
    "update_time": ["2025-12-12 09:00:00", "2025-12-12 16:00:00"]
}
df = mkdf(data_dict, convert_to_utc=["event_time", "update_time"])
print(df)
```

This function now:

* Handles dictionaries, CSV, or Excel.
* Converts single or multiple datetime columns to UTC, assuming they start in `America/Mexico_City`.
* Safely raises errors if columns are missing.

If you want, I can **also make it automatically handle columns that are already timezone-aware**, so it won’t fail if some timestamps are already in UTC.

Do you want me to add that?
