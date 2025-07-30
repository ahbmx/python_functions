The error occurs because we're trying to perform arithmetic operations between `datetime.date` objects, which isn't supported. Let me fix the function and ensure proper datetime handling throughout:

```python
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from typing import Optional, List, Dict, Union
from datetime import timedelta

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
    
    # Convert and sort timestamps - ensure we use pandas Timestamp
    df['tstamp'] = pd.to_datetime(df['tstamp'])
    df = df.sort_values(['sid', 'tstamp'])
    
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
        projection_end_date = last_real_date + timedelta(days=projection_days)
        
        for sid in consolidated['sid'].unique():
            # Get historical data for this sid
            sid_data = df[df['sid'] == sid]
            if len(sid_data) < 2:
                continue
                
            # Convert to numerical values for regression
            X = (sid_data['tstamp'] - sid_data['tstamp'].min()).dt.days.values.reshape(-1, 1)
            y = sid_data[projection_column].values
            
            # Train model
            model = LinearRegression()
            model.fit(X, y)
            
            # Generate projection dates
            projection_dates = pd.date_range(
                start=last_real_date + timedelta(days=1),
                end=projection_end_date,
                freq='D'
            )
            
            # Calculate days since first observation for projections
            first_date = sid_data['tstamp'].min()
            projection_day_counts = [(d - first_date).days for d in projection_dates]
            
            # Create base projections
            base_projections = model.predict(np.array(projection_day_counts).reshape(-1, 1))
            projected_values = base_projections.copy()
            provision_notes = [""] * len(projection_dates)
            
            # Apply future provisions if they exist
            if future_provisions and sid in future_provisions:
                for event in future_provisions[sid]:
                    event_date = pd.to_datetime(event['date'])
                    if event_date > last_real_date and event_date <= projection_end_date:
                        # Find the index of this date in our projections
                        idx = (projection_dates == event_date).argmax()
                        amount = event['amount_tb']
                        
                        if event.get('type', 'provision') == 'provision':
                            projected_values[idx:] += amount
                        else:
                            projected_values[idx:] -= amount
                        
                        provision_notes[idx] = f"{event['type']} {abs(amount)}TB"
            
            # Create projection records
            projections = pd.DataFrame({
                'tstamp': projection_dates,
                'sid': sid,
                'frequency': 'projection',
                projection_column: projected_values.flatten(),
                'is_projection': True,
                'provision_notes': provision_notes,
                'base_projection': base_projections.flatten(),
                'provision_impact': (projected_values - base_projections).flatten()
            })
            
            # Add all other columns with NaN values
            for col in consolidated.columns:
                if col not in projections.columns:
                    projections[col] = np.nan
            
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
    
    # Ensure all columns exist
    for col in cols:
        if col not in consolidated.columns:
            consolidated[col] = np.nan
    
    return consolidated[cols + [c for c in consolidated.columns if c not in cols]]

# Example usage:
"""
future_provisions = {
    'storage001': [
        {'date': '2023-12-10', 'amount_tb': 100, 'type': 'provision'},
        {'date': '2023-12-20', 'amount_tb': 50, 'type': 'provision'},
        {'date': '2023-12-25', 'amount_tb': 30, 'type': 'recovery'}
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

### Key Fixes and Improvements:

1. **Fixed Datetime Operations**:
   - Replaced problematic date arithmetic with proper `timedelta` operations
   - Ensured consistent use of pandas `Timestamp` throughout

2. **Robust Projection Calculation**:
   - Properly calculates days since first observation for regression
   - Handles date comparisons correctly
   - Uses numpy arrays for numerical operations

3. **Enhanced Provision Application**:
   - More accurate finding of provision dates in projection timeline
   - Better handling of provision impacts on future values

4. **Error Prevention**:
   - Checks for sufficient historical data before attempting regression
   - Better handling of edge cases

5. **Maintained All Features**:
   - Still supports all original functionality
   - Future provisions are properly incorporated
   - Returns a clean dataframe ready for visualization

The function now properly handles all datetime operations while maintaining all the functionality you requested, including the ability to incorporate future provisions into the projections.
