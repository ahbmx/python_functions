# Updated Solution: Bar Charts for CPU and Memory Usage by Switch

Here's how to create a 1920x1200 pixel image with two bar charts (CPU and memory usage by switch) and a 150px top bar containing a logo and title:

```python
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg

# Sample data (replace with your actual DataFrame)
data = {
    'timestamp': ['2023-11-15']*4,
    'switch': ['SW1', 'SW2', 'SW3', 'SW4'],
    'cpu_usage': [45, 62, 38, 71],
    'mem_usage': [32, 58, 41, 65]
}
df = pd.DataFrame(data)

# Create figure with specific dimensions (1920x1200 pixels)
fig = plt.figure(figsize=(19.2, 12.0), dpi=100)  # 1920/100=19.2, 1200/100=12.0

# Create a grid layout: 150px top bar (1.5 inches at 100dpi), then two charts
gs = fig.add_gridspec(3, 1, height_ratios=[1.5, 10, 10], hspace=0.4)

# Top bar for logo and title
top_bar = fig.add_subplot(gs[0])
top_bar.axis('off')

# Add your logo (replace 'logo.png' with your actual logo path)
try:
    logo = mpimg.imread('logo.png')
    imagebox = OffsetImage(logo, zoom=0.2)  # Adjust zoom as needed
    ab = AnnotationBbox(imagebox, (0.1, 0.5), frameon=False, boxcoords="axes fraction")
    top_bar.add_artist(ab)
except:
    print("Logo not found, proceeding without it")

# Add title
top_bar.text(0.5, 0.5, 'Brocade CPU and Memory Use', 
             ha='center', va='center', fontsize=24, fontweight='bold')

# Create CPU usage bar chart
cpu_ax = fig.add_subplot(gs[1])
cpu_bars = cpu_ax.bar(df['switch'], df['cpu_usage'], color='skyblue')
cpu_ax.set_title('Current CPU Usage by Switch', fontsize=16)
cpu_ax.set_ylabel('CPU Usage (%)', fontsize=12)
cpu_ax.set_ylim(0, 100)  # Percentage scale
cpu_ax.grid(True, axis='y', linestyle='--', alpha=0.7)

# Add value labels on top of each bar
for bar in cpu_bars:
    height = bar.get_height()
    cpu_ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height}%',
                ha='center', va='bottom', fontsize=10)

# Create Memory usage bar chart
mem_ax = fig.add_subplot(gs[2])
mem_bars = mem_ax.bar(df['switch'], df['mem_usage'], color='lightgreen')
mem_ax.set_title('Current Memory Usage by Switch', fontsize=16)
mem_ax.set_ylabel('Memory Usage (%)', fontsize=12)
mem_ax.set_ylim(0, 100)  # Percentage scale
mem_ax.grid(True, axis='y', linestyle='--', alpha=0.7)

# Add value labels on top of each bar
for bar in mem_bars:
    height = bar.get_height()
    mem_ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height}%',
                ha='center', va='bottom', fontsize=10)

# Add timestamp as subtitle
fig.text(0.5, 0.95, f"Data as of: {df['timestamp'].iloc[0]}", 
         ha='center', va='top', fontsize=12, alpha=0.7)

# Adjust layout and save
plt.tight_layout()
plt.savefig('brocade_usage_bars.png', dpi=100, bbox_inches='tight')
plt.close()
```

## Key Features:

1. **Bar Charts**: Shows CPU and memory usage as separate bar charts
2. **Switch on X-axis**: Each bar represents a different switch
3. **Percentage Values**: 
   - Y-axis shows percentage scale (0-100%)
   - Actual values displayed on top of each bar
4. **Timestamp**: Shows the date of the data in the top bar
5. **Visual Improvements**:
   - Different colors for CPU (skyblue) and memory (lightgreen)
   - Grid lines for better readability
   - Consistent 100% scale for both charts

## Customization Options:

- Change colors by modifying the `color` parameter in the `bar()` calls
- Adjust the logo size with the `zoom` parameter
- Modify font sizes in the `set_title()`, `set_ylabel()`, and `text()` calls
- Change the output filename by editing the `savefig()` parameter
