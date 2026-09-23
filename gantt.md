```python


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
from matplotlib.ticker import MultipleLocator


PLOT_SIZE = (12, 8)
FONT_SIZE = 12
BAR_HEIGHT = 0.6
OPACITY_FULL = 1.0
OPACITY_HALF = 0.5
GRID_FREQUENCY_DAYS = 5  # Default to weekly gridlines
CHART_TITLE = 'Test Title'

ASSIGNEE_COLORS = [
    '#FF6B6B',    # Red
    "#21CCC1",    # Teal
    "#17A4C4",    # Blue
    "#29CA7F",    # Green
    "#F0C331",    # Yellow
    "#CA23CA",    # Plum
    "#47A38C",    # Mint
    '#F7DC6F',     # Golden
    '#BB8FCE',    # Lavender
    '#85C1E9'     # Sky Blue
]

GRID_ENABLED = True
GRID_TYPE = 'both'  # 'vertical', 'horizontal', or 'both'
GRID_COLOR = "#9B9B9B"  # Customizable grid color

def create_gantt_chart(excel_file='plan.xlsx', 
                       plot_size=PLOT_SIZE,
                       font_size=FONT_SIZE,
                       bar_height=BAR_HEIGHT,
                       opacity_full=OPACITY_FULL,
                       opacity_half=OPACITY_HALF,
                       assignee_colors=ASSIGNEE_COLORS,
                       grid_enabled=GRID_ENABLED,
                       grid_type=GRID_TYPE,
                       grid_color=GRID_COLOR):

    df = pd.read_excel(excel_file)
    
    df['start_date'] = pd.to_datetime(df['start_date'])
    df['end_date'] = pd.to_datetime(df['end_date'])
    
    fig, ax = plt.subplots(1, 1, figsize=plot_size)
    
    plt.rcParams.update({
        'font.size': font_size,
        'font.family': 'DejaVu Sans',
        'axes.titlesize': font_size + 2,
        'axes.labelsize': font_size,
        'xtick.labelsize': font_size - 1,
        'ytick.labelsize': font_size - 1
    })
    
    df = df.iloc[::-1].reset_index(drop=True)

    y_positions = range(len(df))

    unique_assignees = df['assignee'].unique()
    
    assignee_to_color_index = {}

    for i, assignee in enumerate(unique_assignees):
        assignee_to_color_index[assignee] = i % len(assignee_colors)
    
    for i, (idx, row) in enumerate(df.iterrows()):
        start_date = row['start_date']
        end_date = row['end_date']
        duration_days = (end_date - start_date).days
        progress_pct = int(row['pct_complete'])
        task_name = row['task']
        assignee = row['assignee']
        
        progress_days = (duration_days * progress_pct) / 100
        
        color_index = assignee_to_color_index[assignee]
        color = assignee_colors[color_index]
        
        ax.barh(y_positions[i], 
                duration_days, 
                left=start_date,
                height=bar_height,
                color=color,
                alpha=opacity_half,
                edgecolor='none')  # No outline
        
        ax.barh(y_positions[i], 
                progress_days, 
                left=start_date,
                height=bar_height,
                color=color,
                alpha=opacity_full,
                edgecolor='none')  # No outline
        
        task_label = f"{task_name} ({progress_pct}%)"
        ax.text(end_date + pd.Timedelta(hours=6), #end_date + pd.Timedelta(days=1), 
                y_positions[i], 
                task_label, 
                va='center',
                ha='left',
                fontsize=font_size)
    
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))  # Daily gridlines
    
    plt.xticks(rotation=0, ha='center')
    
    ax.set_yticks([])
    
    ax.set_xlabel('')
    ax.set_ylabel('')
    
    if grid_enabled:
        if grid_type == 'vertical' or grid_type == 'both':
            ax.grid(True, axis='x', alpha=0.3, color=grid_color)
            if GRID_FREQUENCY_DAYS > 0:
                ax.xaxis.set_major_locator(MultipleLocator(GRID_FREQUENCY_DAYS))
        if grid_type == 'horizontal' or grid_type == 'both':
            ax.grid(True, axis='y', alpha=0.3, color=grid_color)
    
    ax.margins(x=0.02)  # Add small margin on x-axis
    
    ax.set_title(CHART_TITLE, fontsize=FONT_SIZE + 2, fontweight='bold')
    
    if len(unique_assignees) > 1:
        legend_elements = []
        for assignee in unique_assignees:
            color_index = assignee_to_color_index[assignee]
            color = assignee_colors[color_index]
            legend_elements.append(Rectangle((0,0),1,1, facecolor=color, alpha=opacity_full))
        
        ax.legend(legend_elements, unique_assignees, 
                 loc='upper center', bbox_to_anchor=(0.5, -0.1), 
                 ncol=len(unique_assignees), frameon=False, fontsize=font_size-1)
    
    plt.tight_layout()
    
    return fig, ax

if __name__ == "__main__":
    fig, ax = create_gantt_chart()
    plt.savefig('gantt_chart_daily_grid.png', dpi=300, bbox_inches='tight')
    plt.show()




```
