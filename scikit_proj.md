Here's an improved solution using scikit-learn that maintains all historical data while adding projections, making it perfect for charting the full timeline:

```python
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta

def project_capacity_with_history(df, target_date, datetime_col='datetime', 
                                used_col='used_capacity', util_col='util_percent'):
    """
    Project capacity while preserving historical data for complete charting.
    
    Args:
        df: pandas DataFrame with datetime, used capacity, and utilization
        target_date: date to project to (datetime object or string)
        datetime_col: name of datetime column
        used_col: name of used capacity column
        util_col: name of utilization percentage column
        
    Returns:
        tuple: (full_df, full_util_date)
            full_df: DataFrame combining history and projections
            full_util_date: estimated date when 100% utilization will be reached
    """
    # Prepare data
    df = df.copy()
    df[datetime_col] = pd.to_datetime(df[datetime_col])
    start_date = df[datetime_col].min()
    target_date = pd.to_datetime(target_date)
    
    # Convert datetime to numeric (days since first date)
    df['days_since_start'] = (df[datetime_col] - start_date).dt.total_seconds() / (24 * 3600)
    
    # Fit models for both metrics
    X = df[['days_since_start']].values
    models = {
        used_col: LinearRegression().fit(X, df[used_col].values),
        util_col: LinearRegression().fit(X, df[util_col].values)
    }
    
    # Create future dates for projection
    last_historical_date = df[datetime_col].max()
    future_dates = pd.date_range(
        start=last_historical_date + timedelta(days=1),
        end=target_date,
        freq='D'
    )
    
    if len(future_dates) == 0:
        future_dates = pd.date_range(
            start=last_historical_date,
            end=target_date,
            freq='D'
        )
    
    future_days = (future_dates - start_date).days.values.astype(float)
    
    # Create projection DataFrame
    projection = pd.DataFrame({
        datetime_col: future_dates,
        'days_since_start': future_days,
        'is_projection': True  # Flag for projections
    })
    
    # Add projections for each metric
    for col, model in models.items():
        projection[col] = model.predict(future_days.reshape(-1, 1))
    
    # Mark historical data
    df['is_projection'] = False
    
    # Combine history and projections
    full_df = pd.concat([df, projection], ignore_index=True).sort_values(datetime_col)
    
    # Calculate when 100% utilization will be reached
    util_model = models[util_col]
    intercept = util_model.intercept_
    slope = util_model.coef_[0]
    
    if slope <= 0:
        print("Warning: Utilization is not increasing. 100% will not be reached.")
        full_util_date = None
    else:
        days_to_full = (100 - intercept) / slope
        full_util_date = start_date + timedelta(days=days_to_full)
        
        # Clip to target date if needed
        if full_util_date > target_date:
            print(f"Note: 100% utilization projected after target date on {full_util_date}")
        elif full_util_date < start_date:
            print("Warning: 100% utilization was reached before historical data begins")
            full_util_date = None
    
    return full_df, full_util_date
```

### How to Use This Function:

```python
# Example usage
target_date = '2025-12-31'  # Or datetime object

# Get combined historical + projected data
full_df, full_util_date = project_capacity_with_history(df, target_date)

# Plotting example
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

plt.figure(figsize=(12, 6))

# Plot historical data
historical = full_df[~full_df['is_projection']]
plt.plot(historical['datetime'], historical['util_percent'], 
         'b-', label='Historical Utilization')

# Plot projected data
projected = full_df[full_df['is_projection']]
plt.plot(projected['datetime'], projected['util_percent'], 
         'b--', label='Projected Utilization')

# Mark 100% utilization line
plt.axhline(100, color='r', linestyle=':', label='100% Utilization')

# Mark when 100% will be reached if applicable
if full_util_date:
    plt.axvline(full_util_date, color='r', linestyle=':', 
                label=f'100% on {full_util_date.date()}')

# Formatting
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))
plt.gcf().autofmt_xdate()

plt.title('Capacity Utilization Projection')
plt.ylabel('Utilization %')
plt.legend()
plt.grid(True)
plt.show()
```

### Key Features:

1. **Preserves Historical Data**: The returned DataFrame includes both original data and projections
2. **Clear Projection Flag**: The 'is_projection' column helps distinguish real vs projected data
3. **Visualization-Ready**: Output is structured for easy charting
4. **Accurate Date Handling**: Properly manages datetime conversions and projections
5. **Comprehensive Warnings**: Provides clear feedback about projection validity

### Alternative: Polynomial Regression

For non-linear trends, you can easily modify the code to use polynomial features:

```python
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline

# Replace the LinearRegression with this pipeline
degree = 2  # Quadratic fit
model = make_pipeline(
    PolynomialFeatures(degree),
    LinearRegression()
).fit(X, y)
```

This solution gives you everything needed to visualize the complete timeline from historical data through future projections while using scikit-learn as requested.
