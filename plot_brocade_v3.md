# Moving the Timestamp Below the Top Bar

To place the date/timestamp right below the top bar (instead of at the very bottom of the image), here's the modified solution:

```python
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg

# Create figure with specific dimensions (1920x1200 pixels)
fig = plt.figure(figsize=(19.2, 12.0), dpi=100)  # 1920/100=19.2, 1200/100=12.0

# Create a grid layout with 4 rows: top bar, timestamp, and two charts
gs = fig.add_gridspec(nrows=4, ncols=1, 
                     height_ratios=[1.5, 0.3, 10, 10],  # 150px top bar, 30px timestamp, then charts
                     hspace=0.4,  # Spacing between subplots
                     left=0.1, right=0.95)  # Side margins

# Top bar for logo and title (row 0)
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

# Timestamp row (row 1)
timestamp_ax = fig.add_subplot(gs[1])
timestamp_ax.axis('off')
timestamp_ax.text(0.5, 0.5, f"Data as of: {df['timestamp'].iloc[0]}", 
                ha='center', va='center', fontsize=12, alpha=0.7)

# Create CPU usage bar chart (row 2)
cpu_ax = fig.add_subplot(gs[2])
cpu_bars = cpu_ax.bar(df['switch'], df['cpu_usage'], color='skyblue', width=0.6)
cpu_ax.set_title('Current CPU Usage by Switch', fontsize=16)
cpu_ax.set_ylabel('CPU Usage (%)', fontsize=12)
cpu_ax.set_ylim(0, 100)
cpu_ax.grid(True, axis='y', linestyle='--', alpha=0.7)
plt.setp(cpu_ax.get_xticklabels(), rotation=45, ha='right', fontsize=10)
cpu_ax.tick_params(axis='x', pad=5)

# Create Memory usage bar chart (row 3)
mem_ax = fig.add_subplot(gs[3])
mem_bars = mem_ax.bar(df['switch'], df['mem_usage'], color='lightgreen', width=0.6)
mem_ax.set_title('Current Memory Usage by Switch', fontsize=16)
mem_ax.set_ylabel('Memory Usage (%)', fontsize=12)
mem_ax.set_ylim(0, 100)
mem_ax.grid(True, axis='y', linestyle='--', alpha=0.7)
plt.setp(mem_ax.get_xticklabels(), rotation=45, ha='right', fontsize=10)
mem_ax.tick_params(axis='x', pad=5)

# Save the figure
plt.savefig('brocade_usage_bars.png', dpi=100, bbox_inches='tight')
plt.close()
```

## Key Changes:

1. **Added a dedicated row for the timestamp** in the grid layout (row 1)
2. **Adjusted height ratios** to accommodate the new row:
   - `height_ratios=[1.5, 0.3, 10, 10]` (top bar, timestamp, CPU chart, memory chart)
3. **Created a new axes just for the timestamp** that's centered below the top bar
4. **Removed the timestamp from the bottom** of the figure

This creates a cleaner layout with the timestamp positioned logically right below your header section, while maintaining all other formatting and chart properties.
