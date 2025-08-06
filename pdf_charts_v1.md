# Horizontal PDF Report with Multiple Charts

Here's how to create a landscape-oriented PDF report with your storage array charts. I'll modify the previous solution to generate a horizontal layout.

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from reportlab.lib.pagesizes import landscape, letter, A4
from reportlab.lib.units import inch, mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io
import os
from datetime import datetime, timedelta

# Set Seaborn style
sns.set(style="whitegrid", palette="muted", font_scale=0.9)
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3

class HorizontalPDFReport:
    def __init__(self, filename, page_size='A4', dpi=150):
        """
        Initialize horizontal PDF report
        
        Args:
            filename: Output PDF filename
            page_size: Either 'A4' or 'letter' (will be landscape oriented)
            dpi: Dots per inch for chart resolution
        """
        self.filename = filename
        self.dpi = dpi
        
        # Set landscape page size
        if page_size == 'A4':
            self.page_width, self.page_height = landscape(A4)
        elif page_size == 'letter':
            self.page_width, self.page_height = landscape(letter)
        else:
            raise ValueError("page_size must be 'A4' or 'letter'")
            
        # Initialize PDF canvas
        self.c = canvas.Canvas(filename, pagesize=(self.page_width, self.page_height))
        self.figures = []
        
    def add_figure(self, fig):
        """Store a figure to be added to the PDF"""
        self.figures.append(fig)
        
    def _draw_figure(self, fig, x, y, width, height):
        """Draw a figure on the PDF"""
        img_data = io.BytesIO()
        fig.savefig(img_data, format='png', dpi=self.dpi, bbox_inches='tight')
        img_data.seek(0)
        img = ImageReader(img_data)
        self.c.drawImage(img, x, y, width=width, height=height, preserveAspectRatio=True)
        plt.close(fig)
        
    def add_title_page(self, title, subtitle=None):
        """Add landscape title page"""
        self.c.setFont("Helvetica-Bold", 24)
        self.c.drawCentredString(self.page_width/2, self.page_height/2 + 36, title)
        
        if subtitle:
            self.c.setFont("Helvetica", 18)
            self.c.drawCentredString(self.page_width/2, self.page_height/2 - 24, subtitle)
        
        self.c.setFont("Helvetica", 12)
        self.c.drawCentredString(self.page_width/2, 72, 
                               f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.c.showPage()
        
    def add_page_with_grid(self, grid_size=(2, 3), margin=15*mm):
        """
        Add a landscape page with charts in grid layout
        
        Args:
            grid_size: (rows, cols) - takes advantage of wider horizontal space
            margin: Page margin
        """
        rows, cols = grid_size
        usable_width = self.page_width - 2 * margin
        usable_height = self.page_height - 2 * margin
        
        col_width = usable_width / cols
        row_height = usable_height / rows
        
        # Get figures for this page
        figures_per_page = rows * cols
        page_figures = self.figures[:figures_per_page]
        self.figures = self.figures[figures_per_page:]
        
        # Draw each figure in grid
        for i, fig in enumerate(page_figures):
            row = i // cols
            col = i % cols
            x = margin + col * col_width
            y = self.page_height - margin - (row + 1) * row_height
            
            self._draw_figure(fig, x, y, col_width, row_height)
            
        self.c.showPage()
        
    def save(self):
        """Save the PDF with all remaining figures"""
        while self.figures:
            # Try to fit remaining figures
            if len(self.figures) >= 6:
                self.add_page_with_grid(grid_size=(2, 3))
            elif len(self.figures) >= 4:
                self.add_page_with_grid(grid_size=(2, 2))
            else:
                self.add_page_with_grid(grid_size=(1, len(self.figures)))
                
        self.c.save()
        print(f"Horizontal report generated: {self.filename}")

# Chart functions optimized for horizontal layout
def create_horizontal_bar_chart(df, title, x_col, y_col):
    """Horizontal bar chart - ideal for landscape reports"""
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(data=df, y=x_col, x=y_col, ax=ax, hue=x_col, palette="Blues_d", legend=False)
    ax.set_title(title, pad=15, fontweight='bold', fontsize=12)
    ax.set_ylabel(x_col, labelpad=10)
    ax.set_xlabel(y_col, labelpad=10)
    sns.despine(left=True)
    plt.tight_layout(pad=2)
    return fig

def create_wide_column_chart(df, title, x_col, y_col):
    """Column chart optimized for wide format"""
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(data=df, x=x_col, y=y_col, ax=ax, hue=x_col, palette="Greens_d", legend=False)
    ax.set_title(title, pad=15, fontweight='bold', fontsize=12)
    ax.set_xlabel(x_col, labelpad=10)
    ax.set_ylabel(y_col, labelpad=10)
    plt.xticks(rotation=45, ha='right')
    sns.despine(left=True)
    plt.tight_layout(pad=2)
    return fig

# Other chart functions (pie, doughnut, etc.) remain similar but with adjusted sizes
def create_wide_time_series(df, title, y_cols):
    fig, ax = plt.subplots(figsize=(12, 5))
    palette = sns.color_palette("husl", len(y_cols))
    for i, col in enumerate(y_cols):
        sns.lineplot(data=df, x=df.index, y=col, ax=ax, 
                    color=palette[i], marker='o', markersize=5, label=col)
    ax.set_title(title, pad=15, fontweight='bold', fontsize=12)
    ax.set_xlabel('Date', labelpad=10)
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xticks(rotation=45)
    sns.despine()
    plt.tight_layout(pad=2)
    return fig

def generate_horizontal_report(output_file):
    # Generate sample data
    capacity_df, perf_df, backup_df, tier_df = generate_sample_data()
    
    # Initialize horizontal PDF
    report = HorizontalPDFReport(output_file, page_size='A4', dpi=150)
    report.add_title_page("Storage Performance Report", 
                        "Landscape Format - Comprehensive Analysis")
    
    # Create figures optimized for horizontal layout
    report.add_figure(create_horizontal_bar_chart(capacity_df, 'Total Capacity by Array (Horizontal)', 
                                                'Array', 'Total Capacity (TB)'))
    report.add_figure(create_wide_column_chart(capacity_df, 'Used Capacity by Array', 
                                            'Array', 'Used Capacity (TB)'))
    report.add_figure(create_pie_chart(backup_df, 'Backup Success Rates', 
                                     'Success Rate', 'Backup Type'))
    report.add_figure(create_doughnut_chart(tier_df, 'Storage Tier Distribution', 
                                          'Distribution (%)', 'Tier'))
    report.add_figure(create_wide_time_series(perf_df, 'Performance Over Time (Wide)', 
                                           ['IOPS (x1000)', 'Latency (ms)', 'Throughput (MB/s)']))
    report.add_figure(create_candlestick_chart(None, 'Daily Latency (Wide)'))
    report.add_figure(create_heatmap(pd.concat([capacity_df, perf_df.reset_index()], axis=1), 
                                   'Metrics Correlation'))
    
    # Generate pages - using 2x3 grid to take advantage of horizontal space
    report.add_page_with_grid(grid_size=(2, 3))  # Fits 6 charts
    report.add_page_with_grid(grid_size=(1, 1))  # Remaining chart
    
    report.save()

if __name__ == "__main__":
    generate_horizontal_report("storage_report_landscape.pdf")
```

## Key Features of This Horizontal Report:

1. **Landscape Orientation**:
   - Uses `landscape()` function from reportlab to rotate page dimensions
   - Standard sizes (A4 or letter) in horizontal format

2. **Optimized Grid Layout**:
   - Default 2x3 grid (6 charts per page) to take advantage of wide format
   - Falls back to smaller grids for remaining charts

3. **Wide Chart Formats**:
   - Horizontal bar charts (categories on Y-axis)
   - Wider time series charts (12x5 inches)
   - Adjusted all chart sizes for better horizontal display

4. **Improved Layout**:
   - Better spacing between charts
   - Consistent margins
   - Automatic handling of remaining charts

5. **Visual Enhancements**:
   - Larger fonts that work well in landscape
   - Better use of white space
   - Rotated charts where appropriate

To use this:
1. Call `generate_horizontal_report()` with your output filename
2. Replace the sample data functions with your actual data loading code
3. Adjust grid sizes or chart sizes as needed

The report will automatically:
- Create a landscape title page
- Arrange charts in optimal grid layouts
- Handle page breaks correctly
- Maintain high quality output with 150 DPI resolution
