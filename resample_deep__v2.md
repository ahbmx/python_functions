Here's a refined solution that packages everything into a function with configurable parameters and returns a single consolidated dataframe:

```python
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from typing import Optional, List

def analyze_storage_capacity(
    df: pd.DataFrame,
    projection_days: int = 30,
    projection_column: str = 'used_cap',
    freq_options: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Analyze storage capacity metrics with configurable projections.
    
    Args:
        df: Input dataframe with storage metrics
        projection_days: Number of days to project into future (0 for no projection)
        projection_column: Column name to use for projections
        freq_options: List of frequencies to include ('D', 'W', 'M')
    
    Returns:
        Consolidated dataframe with all metrics and projections
    """
    # Set default frequency options
    if freq_options is None:
        freq_options = ['D', 'W', 'M']
    
    # Validate input
    required_cols = ['tstamp', 'sid', 'usable_capacity', 'used_cap', 
                    'subscribed_capacity_tb', 'subscribed_allocated_capacity_tb']
    if not all(col in df.columns for col in required_cols):
        raise ValueError(f"Dataframe must contain these columns: {required_cols}")
    
    if projection_column not in df.columns:
        raise ValueError(f"Projection column '{projection_column}' not found in dataframe")
    
    # Convert and sort timestamps
    df['tstamp'] = pd.to_datetime(df['tstamp'])
    df = df.sort_values(['sid', 'tstamp'])
    df['date'] = df['tstamp'].dt.date
    
    # Initialize result dataframe
    result_dfs = []
    
    # Helper function to calculate changes
    def _calculate_changes(group, freq):
        # Resample to target frequency
        resampled = group.set_index('tstamp').resample(freq).agg({
            'usable_capacity': 'mean',
            'used_cap': 'mean',
            'subscribed_capacity_tb': ['mean', 'last'],
            'subscribed_allocated_capacity_tb': 'mean'
        })
        resampled.columns = ['_'.join(col).strip('_') for col in resampled.columns.values]
        resampled = resampled.rename(columns={'subscribed_capacity_tb_last': 'end_capacity'})
        
        # Calculate changes if we have multiple periods
        if len(resampled) > 1:
            resampled['net_change'] = resampled['end_capacity'].diff()
            resampled['provisioned'] = resampled['net_change'].clip(lower=0)
            resampled['recovered'] = resampled['net_change'].clip(upper=0).abs()
        
        resampled['frequency'] = freq
        return resampled.reset_index()
    
    # Process each frequency
    for freq in freq_options:
        if freq == 'D':
            # Daily processing (base for other frequencies)
            daily_df = df.groupby(['sid', pd.Grouper(key='tstamp', freq='D')]).mean().reset_index()
            daily_df['frequency'] = 'D'
            
            # Calculate daily changes
            daily_df['net_change'] = daily_df.groupby('sid')['subscribed_capacity_tb'].diff()
            daily_df['provisioned'] = daily_df['net_change'].clip(lower=0)
            daily_df['recovered'] = daily_df['net_change'].clip(upper=0).abs()
            
            result_dfs.append(daily_df)
        
        elif freq in ['W', 'M']:
            # Weekly/Monthly processing based on daily data
            if 'D' not in freq_options:
                daily_df = df.groupby(['sid', pd.Grouper(key='tstamp', freq='D')]).mean().reset_index()
            
            freq_df = daily_df.groupby('sid').apply(
                lambda x: _calculate_changes(x, 'W-MON' if freq == 'W' else 'MS')
            ).reset_index(drop=True)
            result_dfs.append(freq_df)
    
    # Combine all frequencies
    consolidated = pd.concat(result_dfs, ignore_index=True)
    
    # Add projections if requested
    if projection_days > 0:
        projection_results = []
        
        for (sid, freq), group in consolidated.groupby(['sid', 'frequency']):
            # Filter to most recent frequency group
            last_date = group['tstamp'].max()
            freq_group = group[group['tstamp'] == last_date].copy()
            
            # Prepare historical data for projection
            history = df[df['sid'] == sid].set_index('tstamp')[projection_column]
            
            if len(history) > 1:
                # Create linear regression model
                X = (history.index - history.index.min()).days.values.reshape(-1, 1)
                y = history.values
                
                model = LinearRegression()
                model.fit(X, y)
                
                # Generate future dates
                future_dates = pd.date_range(
                    start=last_date,
                    periods=projection_days + 1,
                    freq='D'
                )[1:]
                
                # Predict values
                future_days = (future_dates - last_date).days.values.reshape(-1, 1) + X[-1][0]
                future_values = model.predict(future_days)
                
                # Create projection records
                projections = pd.DataFrame({
                    'tstamp': future_dates,
                    'sid': sid,
                    'frequency': f'{freq}_projection',
                    projection_column: future_values,
                    'is_projection': True
                })
                
                # Mark original data
                freq_group['is_projection'] = False
                
                # Combine with projections
                projection_results.append(pd.concat([freq_group, projections], ignore_index=True))
        
        if projection_results:
            projections_df = pd.concat(projection_results, ignore_index=True)
            consolidated = pd.concat([consolidated, projections_df], ignore_index=True)
    
    # Clean up and standardize columns
    consolidated['time'] = consolidated['tstamp']
    consolidated.drop(columns=['tstamp'], inplace=True)
    
    # Ensure proper column order
    cols = ['time', 'sid', 'frequency', 'usable_capacity', 'used_cap',
            'subscribed_capacity_tb', 'subscribed_allocated_capacity_tb',
            'net_change', 'provisioned', 'recovered', 'end_capacity']
    
    # Add any missing columns to maintain consistency
    for col in cols:
        if col not in consolidated.columns:
            consolidated[col] = np.nan
    
    # Add is_projection if it doesn't exist
    if 'is_projection' not in consolidated.columns:
        consolidated['is_projection'] = False
    
    return consolidated[cols + ['is_projection'] + [c for c in consolidated.columns if c not in cols + ['is_projection']]]

# Example usage:
# df_processed = analyze_storage_capacity(
#     df,
#     projection_days=30,
#     projection_column='used_cap',
#     freq_options=['D', 'W', 'M']
# )
```

### Key Features:

1. **Configurable Parameters**:
   - `projection_days`: Number of days to project (0 disables projection)
   - `projection_column`: Which metric to project (default: 'used_cap')
   - `freq_options`: Which time frequencies to include (daily, weekly, monthly)

2. **Comprehensive Analysis**:
   - Calculates daily, weekly, and monthly aggregates
   - Tracks provisioned/recovered capacity
   - Maintains end-of-period capacity values

3. **Projection System**:
   - Uses linear regression for forecasting
   - Marks projected values with `is_projection` flag
   - Projects based on historical trends for each storage system

4. **Single Output DataFrame**:
   - Contains all frequencies in one structured dataframe
   - Ready for Grafana with 'time' column naming
   - Preserves original data while adding projections

5. **Error Handling**:
   - Validates input columns
   - Handles edge cases (single data points, missing values)

### Usage Example:
```python
# Process data with 60-day projection on subscribed capacity
processed_data = analyze_storage_capacity(
    df,
    projection_days=60,
    projection_column='subscribed_capacity_tb',
    freq_options=['D', 'W']
)

# Save for Grafana
processed_data.to_csv('storage_metrics_with_projections.csv', index=False)
```

This function gives you complete control over the analysis while ensuring the output is standardized for visualization in Grafana. The projection system can be easily extended to use more sophisticated forecasting methods if needed.
