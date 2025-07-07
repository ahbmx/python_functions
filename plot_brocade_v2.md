# Fixing "Axes Not Compatible with Tight Layout" Error

The error occurs because the top bar axes (where you place your logo and title) isn't compatible with `tight_layout()`. Here's how to fix this while maintaining all your requirements:

## Solution: Manual Layout Adjustment

```python
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg

# Create figure with specific dimensions (1920x1200 pixels)
fig = plt.figure(figsize=(19.2, 12.0), dpi=100)  # 1920/100=19.2, 1200/100=12.0

# Create a grid layout with proper spacing
gs = fig.add_gridspec(nrows=3, ncols=1, 
                     height_ratios=[1.5, 10, 10],  # 150px top bar, then two charts
                     hspace=0.6,  # Increased spacing between subplots
                     left=0.1, right=0.95,  # Add side margins
                     top=0.95, bottom=0.05)  # Add top/bottom margins

# Top bar for logo and title
top_bar = fig.add_subplot(gs[0])
top_bar.axis('off')

# Add logo (if available)
try:
    logo = mpimg.imread('logo.png')
    imagebox = OffsetImage(logo, zoom=0.2)
    ab = AnnotationBbox(imagebox, (0.1, 0.5), frameon=False, boxcoords="axes fraction")
    top_bar.add_artist(ab)
except:
    print("Logo not found, proceeding without it")

# Add title
top_bar.text(0.5, 0.5, 'Brocade CPU and Memory Use', 
            ha='center', va='center', fontsize=24, fontweight='bold')

# Create CPU usage bar chart
cpu_ax = fig.add_subplot(gs[1])
cpu_bars = cpu_ax.bar(df['switch'], df['cpu_usage'], color='skyblue', width=0.6)
cpu_ax.set_title('Current CPU Usage by Switch', fontsize=16)
cpu_ax.set_ylabel('CPU Usage (%)', fontsize=12)
cpu_ax.set_ylim(0, 100)
cpu_ax.grid(True, axis='y', linestyle='--', alpha=0.7)

# Rotate and adjust switch labels
plt.setp(cpu_ax.get_xticklabels(), rotation=45, ha='right', fontsize=10)
cpu_ax.tick_params(axis='x', pad=5)

# Create Memory usage bar chart
mem_ax = fig.add_subplot(gs[2])
mem_bars = mem_ax.bar(df['switch'], df['mem_usage'], color='lightgreen', width=0.6)
mem_ax.set_title('Current Memory Usage by Switch', fontsize=16)
mem_ax.set_ylabel('Memory Usage (%)', fontsize=12)
mem_ax.set_ylim(0, 100)
mem_ax.grid(True, axis='y', linestyle='--', alpha=0.7)

# Rotate and adjust switch labels
plt.setp(mem_ax.get_xticklabels(), rotation=45, ha='right', fontsize=10)
mem_ax.tick_params(axis='x', pad=5)

# Add timestamp
fig.text(0.5, 0.01, f"Data as of: {df['timestamp'].iloc[0]}", 
        ha='center', va='bottom', fontsize=12, alpha=0.7)

# Save without tight_layout
plt.savefig('brocade_usage_bars.png', dpi=100, bbox_inches='tight')
plt.close()
```

## Key Changes Made:

1. **Removed `tight_layout()`**: Instead using manual grid specification with:
   - Explicit `height_ratios`
   - Added margins (`left`, `right`, `top`, `bottom`)
   - Increased `hspace` between subplots

2. **Proper Label Rotation**: Using `plt.setp()` for safe label rotation

3. **Maintained All Features**:
   - 1920×1200 pixel output
   - 150px top bar with logo and title
   - Two vertical bar charts
   - Percentage values on Y-axis
   - Switch names on X-axis
   - Data timestamp

This approach gives you more control over the layout while avoiding the compatibility issues with `tight_layout()`. The result should be properly spaced and formatted without any overlapping elements.
