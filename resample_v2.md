Great — if you want **all the data grouped in a single DataFrame**, we can modify the function to:

* Add a new column `period` indicating the source of the data: `"daily"`, `"weekly"`, `"monthly"`, or `"projection"`.
* Ensure all outputs have consistent columns (even if some columns are `NaN` for certain periods).
* Concatenate all results into one master DataFrame.

---

### ✅ Unified Function: `process_storage_data_combined`

```python
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

def process_storage_data_combined(df: pd.DataFrame, projection_days: int = 30) -> pd.DataFrame:
    """
    Processes storage array capacity data and returns a unified DataFrame containing
    daily, weekly, monthly, and projected values, tagged by a 'period' column.

    Parameters:
        df (pd.DataFrame): Input DataFrame with columns:
            - tstamp (datetime)
            - sid (string)
            - usable_capacity (float)
            - used_cap (float)
            - subscribed_capacity_tb (float)
            - subscribed_allocated_capacity_tb (float)
        projection_days (int): Number of days to project `used_cap` into the future.

    Returns:
        pd.DataFrame: Unified DataFrame with all periods tagged in 'period' column.
    """

    df = df.copy()
    df['tstamp'] = pd.to_datetime(df['tstamp'])
    df = df.sort_values('tstamp')
    df.set_index('tstamp', inplace=True)

    def resample_and_add_deltas(df_in, freq, label):
        resampled = df_in.groupby('sid').resample(freq).mean().reset_index()
        resampled['used_cap_change'] = resampled.groupby('sid')['used_cap'].diff()
        resampled['provisioned'] = resampled['used_cap_change'].apply(lambda x: x if x > 0 else 0)
        resampled['recovered'] = resampled['used_cap_change'].apply(lambda x: -x if x < 0 else 0)
        resampled['period'] = label

        if freq == 'D':
            ohlc = df_in.groupby(['sid', pd.Grouper(freq='D')])['used_cap'].agg(['first', 'max', 'min', 'last']).reset_index()
            ohlc.columns = ['sid', 'tstamp', 'open', 'high', 'low', 'close']
            resampled = pd.merge(resampled, ohlc, on=['sid', 'tstamp'], how='left')
        else:
            resampled[['open', 'high', 'low', 'close']] = np.nan

        return resampled

    daily = resample_and_add_deltas(df, 'D', 'daily')
    weekly = resample_and_add_deltas(df, 'W', 'weekly')
    monthly = resample_and_add_deltas(df, 'M', 'monthly')

    def project_used_capacity(sid_df, sid, days_into_future):
        sid_df = sid_df.resample('D').mean().dropna(subset=['used_cap'])
        if len(sid_df) < 2:
            return pd.DataFrame()

        sid_df['day'] = (sid_df.index - sid_df.index.min()).days
        X = sid_df[['day']]
        y = sid_df['used_cap']
        model = LinearRegression().fit(X, y)

        last_day = sid_df['day'].max()
        future_days = np.arange(last_day + 1, last_day + 1 + days_into_future)
        future_dates = pd.date_range(start=sid_df.index.max() + pd.Timedelta(days=1), periods=days_into_future)
        future_used_cap = model.predict(future_days.reshape(-1, 1))

        proj = pd.DataFrame({
            'sid': sid,
            'tstamp': future_dates,
            'used_cap': future_used_cap,
            'period': 'projection'
        })
        proj['used_cap_change'] = np.nan
        proj['provisioned'] = np.nan
        proj['recovered'] = np.nan
        proj['open'] = np.nan
        proj['high'] = np.nan
        proj['low'] = np.nan
        proj['close'] = np.nan

        return proj

    projections = pd.concat([
        project_used_capacity(df[df['sid'] == sid], sid, projection_days)
        for sid in df['sid'].unique()
    ], ignore_index=True)

    # Unify column structure
    common_columns = list(set(daily.columns) | set(projections.columns))
    daily = daily.reindex(columns=common_columns)
    weekly = weekly.reindex(columns=common_columns)
    monthly = monthly.reindex(columns=common_columns)
    projections = projections.reindex(columns=common_columns)

    unified_df = pd.concat([daily, weekly, monthly, projections], ignore_index=True).sort_values(['sid', 'tstamp', 'period'])
    return unified_df
```

---

### 📦 Example Usage

```python
unified_df = process_storage_data_combined(df, projection_days=60)

# Preview
print(unified_df.head())
```

---

### 🧾 Columns in Final DataFrame

* `sid`: storage array ID
* `tstamp`: timestamp (daily/weekly/monthly/projection)
* `used_cap`: average or projected used capacity
* `used_cap_change`: change vs. previous time step
* `provisioned`: positive change in used\_cap
* `recovered`: negative change in used\_cap
* `open`, `high`, `low`, `close`: OHLC values for daily candlesticks (NaN for others)
* `period`: one of `"daily"`, `"weekly"`, `"monthly"`, `"projection"`

---

Would you like a CSV export helper or a version that writes directly to a database or Grafana-compatible time-series backend?
