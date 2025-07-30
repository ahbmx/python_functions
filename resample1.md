Here's a reusable function that wraps all the logic we discussed, making it easy to apply to your DataFrame and generate:

* Daily, weekly, and monthly aggregates
* Provisioned and recovered capacity
* OHLC data for Grafana candlesticks
* Linear projection of `used_cap` for future dates

---

### ✅ Reusable Function

```python
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

def process_storage_data(
    df: pd.DataFrame,
    projection_days: int = 30,
) -> dict:
    """
    Processes storage array capacity data.

    Parameters:
        df (pd.DataFrame): Input DataFrame with columns:
            - tstamp (datetime)
            - sid (string)
            - usable_capacity (float)
            - used_cap (float)
            - subscribed_capacity_tb (float)
            - subscribed_allocated_capacity_tb (float)
        projection_days (int): Number of days to project used_cap into the future.

    Returns:
        dict: {
            'daily': pd.DataFrame,
            'weekly': pd.DataFrame,
            'monthly': pd.DataFrame,
            'projections': pd.DataFrame
        }
    """

    df = df.copy()
    df['tstamp'] = pd.to_datetime(df['tstamp'])
    df = df.sort_values('tstamp')
    df.set_index('tstamp', inplace=True)

    def resample_and_add_deltas(df_in, freq='D'):
        resampled = df_in.groupby('sid').resample(freq).mean().reset_index()

        resampled['used_cap_change'] = resampled.groupby('sid')['used_cap'].diff()
        resampled['provisioned'] = resampled['used_cap_change'].apply(lambda x: x if x > 0 else 0)
        resampled['recovered'] = resampled['used_cap_change'].apply(lambda x: -x if x < 0 else 0)

        # OHLC for Grafana (only daily needed typically)
        if freq == 'D':
            ohlc = df_in.groupby(['sid', pd.Grouper(freq='D')])['used_cap'].agg(['first', 'max', 'min', 'last']).reset_index()
            ohlc.columns = ['sid', 'tstamp', 'open', 'high', 'low', 'close']
            resampled = pd.merge(resampled, ohlc, on=['sid', 'tstamp'], how='left')

        return resampled

    daily = resample_and_add_deltas(df, 'D')
    weekly = resample_and_add_deltas(df, 'W')
    monthly = resample_and_add_deltas(df, 'M')

    def project_used_capacity(sid_df, sid, days_into_future):
        sid_df = sid_df.resample('D').mean().dropna(subset=['used_cap'])
        if len(sid_df) < 2:
            return pd.DataFrame()  # Not enough data to fit

        sid_df['day'] = (sid_df.index - sid_df.index.min()).days
        X = sid_df[['day']]
        y = sid_df['used_cap']

        model = LinearRegression().fit(X, y)

        last_day = sid_df['day'].max()
        future_days = np.arange(last_day + 1, last_day + 1 + days_into_future)
        future_dates = pd.date_range(start=sid_df.index.max() + pd.Timedelta(days=1), periods=days_into_future)
        future_used_cap = model.predict(future_days.reshape(-1, 1))

        return pd.DataFrame({
            'sid': sid,
            'tstamp': future_dates,
            'used_cap_proj': future_used_cap
        })

    projections = pd.concat([
        project_used_capacity(df[df['sid'] == sid], sid, projection_days)
        for sid in df['sid'].unique()
    ], ignore_index=True)

    return {
        'daily': daily,
        'weekly': weekly,
        'monthly': monthly,
        'projections': projections
    }
```

---

### 📦 Example Usage

```python
result = process_storage_data(df, projection_days=60)

# Access the individual DataFrames
daily_df = result['daily']
weekly_df = result['weekly']
monthly_df = result['monthly']
proj_df = result['projections']
```

---

Would you like this saved as a `.py` module file or ready to plug into a Jupyter notebook or a Grafana API integration?
