import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

# Sample DataFrame creation
# Assuming 'date_time' is your datetime column and the DataFrame is named df
# df = pd.DataFrame({
#     'date_time': pd.date_range(start='2024-01-01', periods=100, freq='H'),
#     'used_capacity': np.random.rand(100) * 100,
#     'util_percent': np.random.rand(100) * 100,
#     'extra_col1': np.random.rand(100),
#     'extra_col2': np.random.rand(100),
#     'extra_col3': np.random.rand(100),
#     'extra_col4': np.random.rand(100)
# })

# Ensure 'date_time' is the index
df.set_index('date_time', inplace=True)

# Resample to get daily mean
daily_means = df.resample('D').mean()

# Prepare data for linear regression
daily_means['day_number'] = np.arange(len(daily_means))  # Create a day number for regression
X = daily_means['day_number'].values.reshape(-1, 1)  # Features
y_capacity = daily_means['used_capacity'].values  # Target for used_capacity
y_util = daily_means['util_percent'].values  # Target for util_percent

# Fit linear regression models
model_capacity = LinearRegression().fit(X, y_capacity)
model_util = LinearRegression().fit(X, y_util)

# Predict future values
future_days = 30  # Number of days to project into the future
future_day_numbers = np.arange(len(daily_means), len(daily_means) + future_days).reshape(-1, 1)

# Projected values
projected_capacity = model_capacity.predict(future_day_numbers)
projected_util = model_util.predict(future_day_numbers)

# Create a DataFrame for projections
projection_dates = pd.date_range(start=daily_means.index[-1] + pd.Timedelta(days=1), periods=future_days, freq='D')
projection_df = pd.DataFrame({
    'used_capacity': projected_capacity,
    'util_percent': projected_util,
}, index=projection_dates)

# Combine the original daily means with the projections
result_df = pd.concat([daily_means[['used_capacity', 'util_percent']], projection_df], axis=0)

# Add a projection column
result_df['projection'] = np.nan
result_df.loc[projection_df.index, 'projection'] = result_df.loc[projection_df.index, 'used_capacity']

# Reset index if needed
result_df.reset_index(inplace=True)

# Plotting the results
plt.figure(figsize=(12, 6))
plt.plot(result_df['date_time'], result_df['used_capacity'], label='Daily Mean Used Capacity', color='blue')
plt.plot(result_df['date_time'], result_df['projection'], label='Projected Used Capacity', color='orange', linestyle='--')
plt.xlabel('Date')
plt.ylabel('Used Capacity')
plt.title('Used Capacity and Projections')
plt.legend()
plt.show()
