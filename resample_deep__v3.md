Here's an enhanced version that allows you to input future planned provisions, which will be incorporated into the projections:

```python
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from typing import Optional, List, Dict, Union

def analyze_storage_capacity(
    df: pd.DataFrame,
    projection_days: int = 30,
    projection_column: str = 'used_cap',
    freq_options: Optional[List[str]] = None,
    future_provisions: Optional[Dict[str, List[Dict[str, Union[str, float, pd.Timestamp]]]]] = None
) -> pd.DataFrame:
    """
    Analyze storage capacity metrics with configurable projections and future provisions.
    
    Args:
        df: Input dataframe with storage metrics
        projection_days: Number of days to project into future (0 for no projection)
        projection_column: Column name to use for projections
        freq_options: List of frequencies to include ('D', 'W', 'M')
        future_provisions: Dictionary of future provisions by sid in format:
            {
                'sid1': [
                    {'date': '2023-12-01', 'amount_tb': 100, 'type': 'provision'},
                    {'date': '2023-12-15', 'amount_tb': -50, 'type': 'recovery'}
                ],
                ...
            }
    
    Returns:
        Consolidated dataframe with all metrics, projections, and future provisions
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
        resampled = group.set_index('tstamp').resample(freq).agg({
            'usable_capacity': 'mean',
            'used_cap': 'mean',
            'subscribed_capacity_tb': ['mean', 'last'],
            'subscribed_allocated_capacity_tb': 'mean'
        })
        resampled.columns = ['_'.join(col).strip('_') for col in resampled.columns.values]
        resampled = resampled.rename(columns={'subscribed_capacity_tb_last': 'end_capacity'})
        
        if len(resampled) > 1:
            resampled['net_change'] = resampled['end_capacity'].diff()
            resampled['provisioned'] = resampled['net_change'].clip(lower=0)
            resampled['recovered'] = resampled['net_change'].clip(upper=0).abs()
        
        resampled['frequency'] = freq
        return resampled.reset_index()
    
    # Process each frequency
    for freq in freq_options:
        if freq == 'D':
            daily_df = df.groupby(['sid', pd.Grouper(key='tstamp', freq='D')]).mean().reset_index()
            daily_df['frequency'] = 'D'
            daily_df['net_change'] = daily_df.groupby('sid')['subscribed_capacity_tb'].diff()
            daily_df['provisioned'] = daily_df['net_change'].clip(lower=0)
            daily_df['recovered'] = daily_df['net_change'].clip(upper=0).abs()
            result_dfs.append(daily_df)
        
        elif freq in ['W', 'M']:
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
        last_real_date = consolidated['tstamp'].max()
        projection_end_date = last_real_date + pd.Timedelta(days=projection_days)
        
        for sid in consolidated['sid'].unique():
            # Get historical data for this sid
            sid_history = df[df['sid'] == sid].set_index('tstamp')[projection_column]
            
            if len(sid_history) > 1:
                # Prepare known future provisions for this sid
                future_events = []
                if future_provisions and sid in future_provisions:
                    for event in future_provisions[sid]:
                        event_date = pd.to_datetime(event['date'])
                        if event_date > last_real_date and event_date <= projection_end_date:
                            future_events.append({
                                'date': event_date,
                                'amount': event['amount_tb'],
                                'type': event.get('type', 'provision')
                            })
                
                # Create projection timeline
                projection_dates = pd.date_range(
                    start=last_real_date + pd.Timedelta(days=1),
                    end=projection_end_date,
                    freq='D'
                )
                
                # Prepare data for modeling
                X = (sid_history.index - sid_history.index.min()).days.values.reshape(-1, 1)
                y = sid_history.values
                
                # Train model
                model = LinearRegression()
                model.fit(X, y)
                
                # Generate base projections (without provisions)
                projection_days = (projection_dates - last_real_date).days.values.reshape(-1, 1) + X[-1][0]
                base_projections = model.predict(projection_days)
                
                # Apply future provisions
                projected_values = base_projections.copy()
                provision_notes = [""] * len(projection_dates)
                
                for event in future_events:
                    idx = (projection_dates == event['date']).argmax()
                    if event['type'] == 'provision':
                        projected_values[idx:] += event['amount']
                    else:
                        projected_values[idx:] -= event['amount']
                    provision_notes[idx] = f"{event['type']} {abs(event['amount'])}TB"
                
                # Create projection records
                projections = pd.DataFrame({
                    'tstamp': projection_dates,
                    'sid': sid,
                    'frequency': 'projection',
                    projection_column: projected_values,
                    'is_projection': True,
                    'provision_notes': provision_notes,
                    'base_projection': base_projections,
                    'provision_impact': projected_values - base_projections
                })
                
                projection_results.append(projections)
        
        if projection_results:
            projections_df = pd.concat(projection_results, ignore_index=True)
            
            # Mark original data
            consolidated['is_projection'] = False
            consolidated['provision_notes'] = ""
            consolidated['base_projection'] = np.nan
            consolidated['provision_impact'] = np.nan
            
            # Combine with projections
            consolidated = pd.concat([consolidated, projections_df], ignore_index=True)
    
    # Final processing
    consolidated['time'] = consolidated['tstamp']
    consolidated.drop(columns=['tstamp'], inplace=True)
    
    # Standardize columns
    cols = ['time', 'sid', 'frequency', 'usable_capacity', 'used_cap',
            'subscribed_capacity_tb', 'subscribed_allocated_capacity_tb',
            'net_change', 'provisioned', 'recovered', 'end_capacity',
            'is_projection', 'provision_notes', 'base_projection', 'provision_impact']
    
    # Add missing columns if needed
    for col in cols:
        if col not in consolidated.columns:
            consolidated[col] = np.nan
    
    return consolidated[cols + [c for c in consolidated.columns if c not in cols]]

# Example usage with future provisions:
"""
future_provisions = {
    'storage001': [
        {'date': '2023-12-10', 'amount_tb': 100, 'type': 'provision'},
        {'date': '2023-12-20', 'amount_tb': 50, 'type': 'provision'},
        {'date': '2023-12-25', 'amount_tb': 30, 'type': 'recovery'}
    ],
    'storage002': [
        {'date': '2023-12-15', 'amount_tb': 200, 'type': 'provision'}
    ]
}

result = analyze_storage_capacity(
    df,
    projection_days=60,
    projection_column='subscribed_capacity_tb',
    freq_options=['D', 'W'],
    future_provisions=future_provisions
)
"""
```

### Key Enhancements:

1. **Future Provisions Input**:
   - Accepts a dictionary of planned provisions/recoveries by storage ID
   - Each provision has a date, amount (TB), and type (provision/recovery)
   - Provisions are applied at specific future dates

2. **Enhanced Projections**:
   - Projects both organic growth (based on historical trends)
   - Incorporates planned provisions at their specified dates
   - Tracks the impact of provisions separately from organic growth

3. **Detailed Tracking**:
   - `base_projection`: The projection without provisions
   - `provision_impact`: The delta caused by provisions
   - `provision_notes`: Human-readable notes about provisions

4. **Flexible Usage**:
   - Works with or without future provisions
   - Provisions can be positive (additions) or negative (recoveries)
   - Can project any numeric column (used_cap, subscribed_capacity_tb, etc.)

5. **Visualization Ready**:
   - Clear separation between actual data and projections
   - All metadata needed for informative tooltips in Grafana

### Example Grafana Visualization Tips:
1. Use `is_projection` to style projected values differently
2. Create annotations from `provision_notes` to mark provision dates
3. Show both the base projection and provision-impacted values
4. Use candlestick charts for daily/weekly capacity changes
5. Create alerts when projected values approach capacity limits

Would you like me to add any specific features or modify how the provisions are applied to the projections?
