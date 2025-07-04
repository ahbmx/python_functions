# XLSXWriter Helper Module

Here's a comprehensive module with helper functions for the `xlsxwriter` module without using the `typing` module:

```python
"""
xlsxwriter_helpers.py

A collection of helper functions for the xlsxwriter module to simplify Excel file creation.
"""

import xlsxwriter
from datetime import datetime


def create_workbook(filename):
    """
    Create a new Excel workbook and return both the workbook and worksheet objects.
    
    Args:
        filename: Path and name for the new Excel file
        
    Returns:
        Tuple of (workbook, worksheet) objects
    """
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet()
    return workbook, worksheet


def add_sheet(workbook, sheet_name=None):
    """
    Add a new worksheet to an existing workbook.
    
    Args:
        workbook: Existing workbook object
        sheet_name: Optional name for the new worksheet
        
    Returns:
        Worksheet object
    """
    if sheet_name:
        return workbook.add_worksheet(sheet_name)
    return workbook.add_worksheet()


def write_data(worksheet, row, col, data, cell_format=None):
    """
    Write data to a worksheet cell with optional formatting.
    
    Args:
        worksheet: Worksheet object
        row: Row index (zero-based)
        col: Column index (zero-based)
        data: Data to write (string, number, datetime)
        cell_format: Optional format object
    """
    if isinstance(data, datetime):
        worksheet.write_datetime(row, col, data, cell_format)
    elif isinstance(data, (int, float)):
        worksheet.write_number(row, col, data, cell_format)
    else:
        worksheet.write_string(row, col, str(data), cell_format)


def write_row(worksheet, row, col, data_list, cell_format=None):
    """
    Write a list of data horizontally starting at the specified cell.
    
    Args:
        worksheet: Worksheet object
        row: Starting row index
        col: Starting column index
        data_list: List of data items to write
        cell_format: Optional format object to apply to all cells
    """
    for i, data in enumerate(data_list):
        write_data(worksheet, row, col + i, data, cell_format)


def write_column(worksheet, row, col, data_list, cell_format=None):
    """
    Write a list of data vertically starting at the specified cell.
    
    Args:
        worksheet: Worksheet object
        row: Starting row index
        col: Starting column index
        data_list: List of data items to write
        cell_format: Optional format object to apply to all cells
    """
    for i, data in enumerate(data_list):
        write_data(worksheet, row + i, col, data, cell_format)


def write_2d_array(worksheet, start_row, start_col, data_2d, cell_format=None):
    """
    Write a 2D array of data starting at the specified cell.
    
    Args:
        worksheet: Worksheet object
        start_row: Starting row index
        start_col: Starting column index
        data_2d: 2D list of data items to write
        cell_format: Optional format object to apply to all cells
    """
    for row_idx, row_data in enumerate(data_2d):
        for col_idx, cell_data in enumerate(row_data):
            write_data(worksheet, start_row + row_idx, start_col + col_idx, cell_data, cell_format)


def add_header_format(workbook, **format_props):
    """
    Create a header cell format with common defaults that can be overridden.
    
    Args:
        workbook: Workbook object
        format_props: Dictionary of format properties to override defaults
        
    Returns:
        Format object
    """
    defaults = {
        'bold': True,
        'bg_color': '#4472C4',
        'font_color': 'white',
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    }
    defaults.update(format_props)
    return workbook.add_format(defaults)


def add_number_format(workbook, num_format, **format_props):
    """
    Create a number format with optional additional properties.
    
    Args:
        workbook: Workbook object
        num_format: Number format string (e.g., '#,##0.00')
        format_props: Additional format properties
        
    Returns:
        Format object
    """
    format_props = {'num_format': num_format}
    format_props.update(format_props)
    return workbook.add_format(format_props)


def add_date_format(workbook, date_format='yyyy-mm-dd', **format_props):
    """
    Create a date format with optional additional properties.
    
    Args:
        workbook: Workbook object
        date_format: Date format string
        format_props: Additional format properties
        
    Returns:
        Format object
    """
    format_props = {'num_format': date_format}
    return workbook.add_format(format_props)


def set_column_widths(worksheet, col_widths):
    """
    Set widths for multiple columns at once.
    
    Args:
        worksheet: Worksheet object
        col_widths: Dictionary of {column_index: width} pairs
                   or list of widths for consecutive columns starting at A
    """
    if isinstance(col_widths, dict):
        for col, width in col_widths.items():
            worksheet.set_column(col, col, width)
    else:
        for col, width in enumerate(col_widths):
            worksheet.set_column(col, col, width)


def add_autofilter(worksheet, first_row, first_col, last_row, last_col):
    """
    Add autofilter to a range of cells.
    
    Args:
        worksheet: Worksheet object
        first_row: First row of the range (0-based)
        first_col: First column of the range (0-based)
        last_row: Last row of the range (0-based)
        last_col: Last column of the range (0-based)
    """
    worksheet.autofilter(first_row, first_col, last_row, last_col)


def add_table(worksheet, first_row, first_col, last_row, last_col, options=None):
    """
    Add an Excel table to a range of cells.
    
    Args:
        worksheet: Worksheet object
        first_row: First row of the range (0-based)
        first_col: First column of the range (0-based)
        last_row: Last row of the range (0-based)
        last_col: Last column of the range (0-based)
        options: Dictionary of table options (name, style, etc.)
    """
    if options is None:
        options = {}
    options.update({
        'first_row': first_row,
        'first_col': first_col,
        'last_row': last_row,
        'last_col': last_col,
        'columns': [{'header': ''} for _ in range(first_col, last_col + 1)]
    })
    worksheet.add_table(**options)


def add_hyperlink(worksheet, row, col, url, text=None, tooltip=None, cell_format=None):
    """
    Add a hyperlink to a cell.
    
    Args:
        worksheet: Worksheet object
        row: Row index (0-based)
        col: Column index (0-based)
        url: URL to link to
        text: Optional display text (defaults to URL)
        tooltip: Optional tooltip text
        cell_format: Optional format object
    """
    if text is None:
        text = url
    worksheet.write_url(row, col, url, cell_format, string=text, tip=tooltip)


def add_data_validation(worksheet, first_row, first_col, last_row, last_col, options):
    """
    Add data validation to a range of cells.
    
    Args:
        worksheet: Worksheet object
        first_row: First row of the range (0-based)
        first_col: First column of the range (0-based)
        last_row: Last row of the range (0-based)
        last_col: Last column of the range (0-based)
        options: Dictionary of validation options
    """
    worksheet.data_validation(first_row, first_col, last_row, last_col, options)


def add_conditional_formatting(worksheet, first_row, first_col, last_row, last_col, options):
    """
    Add conditional formatting to a range of cells.
    
    Args:
        worksheet: Worksheet object
        first_row: First row of the range (0-based)
        first_col: First column of the range (0-based)
        last_row: Last row of the range (0-based)
        last_col: Last column of the range (0-based)
        options: Dictionary of conditional formatting options
    """
    worksheet.conditional_format(first_row, first_col, last_row, last_col, options)


def freeze_panes(worksheet, row=None, col=None):
    """
    Freeze panes at the specified row and/or column.
    
    Args:
        worksheet: Worksheet object
        row: Row to freeze above (1-based, None for no row freeze)
        col: Column to freeze left of (1-based, None for no column freeze)
    """
    if row is not None and col is not None:
        worksheet.freeze_panes(row, col)
    elif row is not None:
        worksheet.freeze_panes(row, 0)
    elif col is not None:
        worksheet.freeze_panes(0, col)


def save_workbook(workbook):
    """
    Close and save the workbook.
    
    Args:
        workbook: Workbook object to save
    """
    workbook.close()
```

## Example Usage

```python
from xlsxwriter_helpers import *

# Create a new workbook
workbook, worksheet = create_workbook('example.xlsx')

# Add formats
header_format = add_header_format(workbook)
date_format = add_date_format(workbook)
money_format = add_number_format(workbook, '$#,##0.00')

# Write headers
headers = ['Date', 'Product', 'Quantity', 'Price', 'Total']
write_row(worksheet, 0, 0, headers, header_format)

# Sample data
data = [
    [datetime(2023, 1, 1), 'Widget A', 5, 19.99, '=C2*D2'],
    [datetime(2023, 1, 2), 'Widget B', 3, 24.99, '=C3*D3'],
    [datetime(2023, 1, 3), 'Widget C', 2, 29.99, '=C4*D4'],
]

# Write data
write_2d_array(worksheet, 1, 0, data)

# Apply formats
worksheet.set_column(0, 0, 12, date_format)
worksheet.set_column(3, 4, 10, money_format)

# Add autofilter
add_autofilter(worksheet, 0, 0, len(data), len(headers)-1)

# Save the workbook
save_workbook(workbook)
```

This module provides a comprehensive set of helper functions that cover most common Excel operations while simplifying the xlsxwriter API. The functions handle common tasks like formatting, data writing, and worksheet configuration with sensible defaults.



# XLSXWriter Color Palette Helper

Here's a module that provides 20 distinct color/style combinations for cell formatting based on values, along with helper functions to apply them:

```python
"""
xlsxwriter_format_palette.py

Provides a palette of 20 distinct color/style combinations for cell formatting
based on value ranges or conditions.
"""

import xlsxwriter

def create_format_palette(workbook):
    """
    Create a dictionary of 20 distinct cell formats for value-based formatting.
    
    Args:
        workbook: xlsxwriter Workbook object
        
    Returns:
        Dictionary of format objects with keys 'style1' through 'style20'
    """
    formats = {
        # Gradient blues (cool colors)
        'style1': workbook.add_format({'bg_color': '#E6F2FF', 'font_color': '#003366', 'border': 1}),
        'style2': workbook.add_format({'bg_color': '#CCE5FF', 'font_color': '#002952', 'border': 1}),
        'style3': workbook.add_format({'bg_color': '#99CCFF', 'font_color': '#001F3F', 'border': 1}),
        'style4': workbook.add_format({'bg_color': '#66B2FF', 'font_color': '#00152B', 'border': 1}),
        'style5': workbook.add_format({'bg_color': '#3399FF', 'font_color': '#FFFFFF', 'border': 1}),
        
        # Gradient greens (growth colors)
        'style6': workbook.add_format({'bg_color': '#E6F7E6', 'font_color': '#004D00', 'border': 1}),
        'style7': workbook.add_format({'bg_color': '#CCEECC', 'font_color': '#003D00', 'border': 1}),
        'style8': workbook.add_format({'bg_color': '#99D699', 'font_color': '#002D00', 'border': 1}),
        'style9': workbook.add_format({'bg_color': '#66C266', 'font_color': '#001D00', 'border': 1}),
        'style10': workbook.add_format({'bg_color': '#33AD33', 'font_color': '#FFFFFF', 'border': 1}),
        
        # Gradient reds (warning colors)
        'style11': workbook.add_format({'bg_color': '#FFE6E6', 'font_color': '#800000', 'border': 1}),
        'style12': workbook.add_format({'bg_color': '#FFCCCC', 'font_color': '#660000', 'border': 1}),
        'style13': workbook.add_format({'bg_color': '#FF9999', 'font_color': '#4D0000', 'border': 1}),
        'style14': workbook.add_format({'bg_color': '#FF6666', 'font_color': '#330000', 'border': 1}),
        'style15': workbook.add_format({'bg_color': '#FF3333', 'font_color': '#FFFFFF', 'border': 1}),
        
        # Special styles
        'style16': workbook.add_format({
            'bg_color': '#FFF2CC', 
            'font_color': '#7F6000', 
            'border': 1,
            'font_italic': True
        }),
        'style17': workbook.add_format({
            'bg_color': '#FCE4D6', 
            'font_color': '#C65911', 
            'border': 1,
            'bold': True
        }),
        'style18': workbook.add_format({
            'bg_color': '#EDEDED', 
            'font_color': '#333333', 
            'border': 1,
            'font_name': 'Courier New'
        }),
        'style19': workbook.add_format({
            'bg_color': '#E2EFDA', 
            'font_color': '#548235', 
            'border': 1,
            'num_format': '#,##0.00'
        }),
        'style20': workbook.add_format({
            'bg_color': '#D9E1F2', 
            'font_color': '#2F5597', 
            'border': 1,
            'num_format': '$#,##0.00'
        })
    }
    return formats

def apply_value_based_formatting(worksheet, start_row, end_row, col, formats, rules):
    """
    Apply conditional formatting based on value ranges using the format palette.
    
    Args:
        worksheet: Worksheet object
        start_row: First row to format (0-based)
        end_row: Last row to format (0-based)
        col: Column to apply formatting to (0-based)
        formats: Dictionary of format objects from create_format_palette()
        rules: List of tuples with (condition, format_key) pairs
               Conditions can be:
               - (min, max): Value range (inclusive)
               - "==value": Exact value match
               - ">value": Greater than
               - "<value": Less than
               - "topN": Top N values
               - "bottomN": Bottom N values
    """
    for condition, format_key in rules:
        format_obj = formats[format_key]
        
        if isinstance(condition, tuple):
            # Range-based condition
            min_val, max_val = condition
            worksheet.conditional_format(
                start_row, col, end_row, col,
                {
                    'type': 'cell',
                    'criteria': 'between',
                    'minimum': min_val,
                    'maximum': max_val,
                    'format': format_obj
                }
            )
        elif isinstance(condition, str):
            if condition.startswith('=='):
                # Exact value match
                value = condition[2:]
                worksheet.conditional_format(
                    start_row, col, end_row, col,
                    {
                        'type': 'cell',
                        'criteria': 'equal to',
                        'value': value,
                        'format': format_obj
                    }
                )
            elif condition.startswith('>'):
                # Greater than
                value = condition[1:]
                worksheet.conditional_format(
                    start_row, col, end_row, col,
                    {
                        'type': 'cell',
                        'criteria': 'greater than',
                        'value': value,
                        'format': format_obj
                    }
                )
            elif condition.startswith('<'):
                # Less than
                value = condition[1:]
                worksheet.conditional_format(
                    start_row, col, end_row, col,
                    {
                        'type': 'cell',
                        'criteria': 'less than',
                        'value': value,
                        'format': format_obj
                    }
                )
            elif condition.startswith('top'):
                # Top N values
                n = int(condition[3:])
                worksheet.conditional_format(
                    start_row, col, end_row, col,
                    {
                        'type': 'top',
                        'value': n,
                        'format': format_obj
                    }
                )
            elif condition.startswith('bottom'):
                # Bottom N values
                n = int(condition[6:])
                worksheet.conditional_format(
                    start_row, col, end_row, col,
                    {
                        'type': 'bottom',
                        'value': n,
                        'format': format_obj
                    }
                )

def apply_text_based_formatting(worksheet, start_row, end_row, col, formats, rules):
    """
    Apply conditional formatting based on text content using the format palette.
    
    Args:
        worksheet: Worksheet object
        start_row: First row to format (0-based)
        end_row: Last row to format (0-based)
        col: Column to apply formatting to (0-based)
        formats: Dictionary of format objects from create_format_palette()
        rules: List of tuples with (text, format_key) pairs
               Text can be:
               - Exact text to match
               - "contains:text" for partial matches
               - "starts:text" for text starting with
               - "ends:text" for text ending with
    """
    for text, format_key in rules:
        format_obj = formats[format_key]
        
        if text.startswith('contains:'):
            search_text = text[9:]
            worksheet.conditional_format(
                start_row, col, end_row, col,
                {
                    'type': 'text',
                    'criteria': 'containing',
                    'value': search_text,
                    'format': format_obj
                }
            )
        elif text.startswith('starts:'):
            search_text = text[7:]
            worksheet.conditional_format(
                start_row, col, end_row, col,
                {
                    'type': 'text',
                    'criteria': 'begins with',
                    'value': search_text,
                    'format': format_obj
                }
            )
        elif text.startswith('ends:'):
            search_text = text[5:]
            worksheet.conditional_format(
                start_row, col, end_row, col,
                {
                    'type': 'text',
                    'criteria': 'ends with',
                    'value': search_text,
                    'format': format_obj
                }
            )
        else:
            # Exact text match
            worksheet.conditional_format(
                start_row, col, end_row, col,
                {
                    'type': 'text',
                    'criteria': 'equal to',
                    'value': text,
                    'format': format_obj
                }
            )
```

## Example Usage

```python
import xlsxwriter
from xlsxwriter_format_palette import create_format_palette, apply_value_based_formatting

# Create a workbook
workbook = xlsxwriter.Workbook('formatted_report.xlsx')
worksheet = workbook.add_worksheet()

# Create our format palette
formats = create_format_palette(workbook)

# Sample data - sales figures
headers = ['Region', 'Sales', 'Growth %']
data = [
    ['North', 125000, 12.5],
    ['South', 98000, 8.2],
    ['East', 156000, 15.8],
    ['West', 112000, 10.1],
    ['Central', 88000, 5.4],
]

# Write headers with style20 (blue with currency format)
worksheet.write_row(0, 0, headers, formats['style20'])

# Write data
for row_idx, row_data in enumerate(data, start=1):
    worksheet.write_row(row_idx, 0, row_data)

# Apply value-based formatting to Sales column (column B)
sales_rules = [
    ((0, 99999), 'style11'),  # Red gradient for sales < 100k
    ((100000, 124999), 'style1'),  # Light blue for 100k-125k
    ((125000, 150000), 'style6'),  # Light green for 125k-150k
    (">150000", 'style10'),  # Dark green for >150k
]
apply_value_based_formatting(worksheet, 1, 5, 1, formats, sales_rules)

# Apply value-based formatting to Growth % column (column C)
growth_rules = [
    ("<5", 'style15'),  # Dark red for growth <5%
    ((5, 9.9), 'style16'),  # Yellow warning for 5-9.9%
    (">=10", 'style9'),  # Green for >=10%
    ("top1", 'style5'),  # Bright blue for top value
]
apply_value_based_formatting(worksheet, 1, 5, 2, formats, growth_rules)

# Apply text-based formatting to Region column (column A)
region_rules = [
    ('North', 'style2'),
    ('South', 'style3'),
    ('East', 'style4'),
    ('West', 'style5'),
    ('Central', 'style1'),
]
apply_text_based_formatting(worksheet, 1, 5, 0, formats, region_rules)

# Set column widths
worksheet.set_column(0, 0, 15)  # Region
worksheet.set_column(1, 1, 12)  # Sales
worksheet.set_column(2, 2, 12)  # Growth %

workbook.close()
```

## Palette Description

The palette includes 20 distinct styles organized into:

1. **Cool Blues (style1-style5)**: 
   - Gradient from very light blue to bright blue
   - Good for neutral/normal values or information displays

2. **Growth Greens (style6-style10)**:
   - Gradient from light green to dark green
   - Ideal for positive metrics, growth indicators

3. **Warning Reds (style11-style15)**:
   - Gradient from light red to dark red
   - Use for negative values or warning conditions

4. **Special Styles (style16-style20)**:
   - style16: Yellow background with brown text (caution)
   - style17: Peach background with orange text (emphasis)
   - style18: Gray background with monospace font (code/data)
   - style19: Light green with built-in number format
   - style20: Light blue with currency format

Each style includes:
- Distinct background color
- Complementary text color
- Cell borders
- Additional formatting where appropriate (bold, italics, number formats)




# Pandas-XLSXWriter Helper Package

Here's a comprehensive helper package specifically designed to work with pandas DataFrames and the xlsxwriter module:

```python
"""
pandas_xlsxwriter_helpers.py

A collection of helper functions for exporting pandas DataFrames to Excel
with enhanced formatting using xlsxwriter.
"""

import pandas as pd
import xlsxwriter
from datetime import datetime

def dataframe_to_excel(df, file_path, sheet_name='Sheet1', index=True, 
                      header=True, autofilter=True, table_style=None,
                      column_formats=None, conditional_formats=None,
                      freeze_panes=None, hide_gridlines=True):
    """
    Export a pandas DataFrame to an Excel file with enhanced formatting options.
    
    Args:
        df: pandas DataFrame to export
        file_path: Output file path
        sheet_name: Name of the worksheet
        index: Write index (True/False)
        header: Write header (True/False)
        autofilter: Add autofilter to header row (True/False)
        table_style: Excel table style name (None for no table)
        column_formats: Dict of {column: format} for special formatting
        conditional_formats: Dict of {column: [formatting rules]} 
        freeze_panes: Tuple of (row, col) to freeze panes at (1-based)
        hide_gridlines: Hide gridlines in the worksheet (True/False)
    """
    # Create workbook and worksheet
    writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
    df.to_excel(writer, sheet_name=sheet_name, index=index, header=header)
    
    workbook = writer.book
    worksheet = writer.sheets[sheet_name]
    
    # Hide gridlines if requested
    if hide_gridlines:
        worksheet.hide_gridlines(2)  # 2 = hide all gridlines
    
    # Apply column formats if specified
    if column_formats:
        apply_column_formats(worksheet, workbook, df, column_formats, index)
    
    # Apply conditional formatting if specified
    if conditional_formats:
        apply_conditional_formatting(worksheet, workbook, df, conditional_formats, index)
    
    # Add autofilter if requested
    if autofilter and header:
        add_dataframe_autofilter(worksheet, df, index)
    
    # Convert to Excel table if style specified
    if table_style:
        convert_to_excel_table(worksheet, workbook, df, sheet_name, table_style, index)
    
    # Freeze panes if specified
    if freeze_panes:
        row, col = freeze_panes
        worksheet.freeze_panes(row, col)
    
    # Auto-adjust column widths
    autofit_dataframe_columns(worksheet, df, index)
    
    writer.close()

def apply_column_formats(worksheet, workbook, df, column_formats, has_index):
    """
    Apply specific formatting to DataFrame columns.
    
    Args:
        worksheet: Worksheet object
        workbook: Workbook object
        df: pandas DataFrame
        column_formats: Dict of {column: format_spec}
                       format_spec can be:
                       - Excel format string ('#,##0.00')
                       - Format type name ('currency', 'percent', 'date')
                       - Dict of format properties
        has_index: Whether the DataFrame index is included
    """
    # Create default format types
    format_types = {
        'currency': {'num_format': '$#,##0.00'},
        'percent': {'num_format': '0.00%'},
        'date': {'num_format': 'yyyy-mm-dd'},
        'datetime': {'num_format': 'yyyy-mm-dd hh:mm:ss'},
        'text': {'num_format': '@'},
        'integer': {'num_format': '#,##0'},
        'float': {'num_format': '#,##0.00'},
    }
    
    col_offset = 1 if has_index else 0
    
    for col, format_spec in column_formats.items():
        if isinstance(col, str):
            col_idx = df.columns.get_loc(col) + col_offset
        else:
            col_idx = col + col_offset
        
        if isinstance(format_spec, str):
            # Check if it's a predefined format type
            if format_spec in format_types:
                fmt = workbook.add_format(format_types[format_spec])
            else:
                # Treat as direct format string
                fmt = workbook.add_format({'num_format': format_spec})
        elif isinstance(format_spec, dict):
            fmt = workbook.add_format(format_spec)
        else:
            continue
        
        worksheet.set_column(col_idx, col_idx, None, fmt)

def apply_conditional_formatting(worksheet, workbook, df, conditional_formats, has_index):
    """
    Apply conditional formatting to DataFrame columns.
    
    Args:
        worksheet: Worksheet object
        workbook: Workbook object
        df: pandas DataFrame
        conditional_formats: Dict of {column: [formatting rules]}
                           Each rule is a dict with:
                           - 'type': 'cell', 'text', 'top', etc.
                           - 'criteria': 'greater than', 'between', etc.
                           - 'value': value or (min, max) for between
                           - 'format': format properties dict
        has_index: Whether the DataFrame index is included
    """
    col_offset = 1 if has_index else 0
    start_row = 1 if df.columns.name is None else 2
    
    for col, rules in conditional_formats.items():
        if isinstance(col, str):
            col_idx = df.columns.get_loc(col) + col_offset
        else:
            col_idx = col + col_offset
        
        for rule in rules:
            fmt = workbook.add_format(rule.get('format', {}))
            
            if rule['type'] == 'data_bar':
                # Data bar conditional formatting
                worksheet.conditional_format(
                    start_row, col_idx, start_row + len(df) - 1, col_idx,
                    {
                        'type': 'data_bar',
                        'bar_color': rule.get('bar_color', '#63C384'),
                        'bar_border_color': rule.get('border_color', '#63C384'),
                        'bar_negative_color': rule.get('negative_color', '#FF555A'),
                        'bar_negative_border_color': rule.get('negative_border_color', '#FF555A'),
                        'bar_axis_color': rule.get('axis_color', '#000000'),
                        'bar_direction': rule.get('direction', 'left'),
                        'bar_only': rule.get('bar_only', True)
                    }
                )
            else:
                # Standard conditional formatting
                options = {
                    'type': rule['type'],
                    'format': fmt
                }
                
                if 'criteria' in rule:
                    options['criteria'] = rule['criteria']
                
                if 'value' in rule:
                    if isinstance(rule['value'], (list, tuple)):
                        options['minimum'] = rule['value'][0]
                        options['maximum'] = rule['value'][1]
                    else:
                        options['value'] = rule['value']
                
                worksheet.conditional_format(
                    start_row, col_idx, start_row + len(df) - 1, col_idx,
                    options
                )

def add_dataframe_autofilter(worksheet, df, has_index):
    """
    Add autofilter to the DataFrame header row.
    
    Args:
        worksheet: Worksheet object
        df: pandas DataFrame
        has_index: Whether the DataFrame index is included
    """
    start_col = 1 if has_index else 0
    end_col = start_col + len(df.columns) - 1
    
    header_row = 0 if df.columns.name is None else 1
    end_row = header_row + len(df)
    
    worksheet.autofilter(header_row, start_col, end_row, end_col)

def convert_to_excel_table(worksheet, workbook, df, sheet_name, table_style, has_index):
    """
    Convert the DataFrame range to an Excel table.
    
    Args:
        worksheet: Worksheet object
        workbook: Workbook object
        df: pandas DataFrame
        sheet_name: Worksheet name
        table_style: Excel table style name
        has_index: Whether the DataFrame index is included
    """
    start_col = 1 if has_index else 0
    end_col = start_col + len(df.columns) - 1
    
    header_row = 0 if df.columns.name is None else 1
    end_row = header_row + len(df)
    
    # Create column headers list
    if has_index:
        headers = [''] + list(df.columns)
    else:
        headers = list(df.columns)
    
    # Add the table
    worksheet.add_table(
        header_row, start_col, end_row, end_col,
        {
            'name': f'Table_{sheet_name}',
            'style': table_style,
            'columns': [{'header': h} for h in headers]
        }
    )

def autofit_dataframe_columns(worksheet, df, has_index):
    """
    Auto-adjust column widths based on DataFrame content.
    
    Args:
        worksheet: Worksheet object
        df: pandas DataFrame
        has_index: Whether the DataFrame index is included
    """
    # Set width for index column if present
    if has_index:
        max_len = max((
            df.index.astype(str).map(len).max(),  # Index values
            len(str(df.index.name)) if df.index.name else 0  # Index name
        )
        worksheet.set_column(0, 0, min(max_len + 1, 50))
    
    # Set width for data columns
    for i, col in enumerate(df.columns):
        # Column name width
        col_name_len = len(str(col))
        
        # Content width (for first 100 rows to save time)
        sample_size = min(100, len(df))
        content_len = df[col].iloc[:sample_size].astype(str).map(len).max()
        
        # Use the larger of the two
        max_len = max(col_name_len, content_len)
        
        # Set column width with some padding
        col_idx = i + 1 if has_index else i
        worksheet.set_column(col_idx, col_idx, min(max_len + 2, 50))

def excel_report_from_dataframes(dataframes, file_path, sheet_names=None, 
                               table_styles=None, global_formats=None):
    """
    Create an Excel report from multiple DataFrames with consistent formatting.
    
    Args:
        dataframes: List of DataFrames or dict of {sheet_name: DataFrame}
        file_path: Output file path
        sheet_names: List of sheet names (if dataframes is a list)
        table_styles: List of table styles or single style for all sheets
        global_formats: Dict of {column: format} to apply to all sheets
    """
    if isinstance(dataframes, dict):
        sheet_names = list(dataframes.keys())
        dfs = list(dataframes.values())
    else:
        dfs = dataframes
        if sheet_names is None:
            sheet_names = [f'Sheet{i+1}' for i in range(len(dfs))]
    
    if isinstance(table_styles, str):
        table_styles = [table_styles] * len(dfs)
    elif table_styles is None:
        table_styles = [None] * len(dfs)
    
    writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
    workbook = writer.book
    
    # Apply date format to all worksheets
    date_format = workbook.add_format({'num_format': 'yyyy-mm-dd'})
    workbook.formats[0].set_num_format('yyyy-mm-dd')
    
    for df, sheet_name, table_style in zip(dfs, sheet_names, table_styles):
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        worksheet = writer.sheets[sheet_name]
        
        # Apply global formats if specified
        if global_formats:
            apply_column_formats(worksheet, workbook, df, global_formats, False)
        
        # Convert to table if style specified
        if table_style:
            convert_to_excel_table(worksheet, workbook, df, sheet_name, table_style, False)
        
        # Auto-fit columns
        autofit_dataframe_columns(worksheet, df, False)
    
    writer.close()
```

## Example Usage

```python
import pandas as pd
import numpy as np
from pandas_xlsxwriter_helpers import *

# Sample DataFrame
data = {
    'Date': pd.date_range('2023-01-01', periods=10),
    'Product': ['A', 'B', 'A', 'C', 'B', 'A', 'C', 'B', 'A', 'C'],
    'Region': ['North', 'South', 'East', 'West', 'North', 'South', 'East', 'West', 'North', 'South'],
    'Sales': np.random.randint(10000, 50000, 10),
    'Growth': np.random.uniform(-5, 20, 10),
    'Cost': np.random.uniform(0.1, 0.5, 10),
}

df = pd.DataFrame(data)

# Define column formats
column_formats = {
    'Date': 'date',
    'Sales': {'num_format': '$#,##0', 'bold': True},
    'Growth': {'num_format': '0.00%', 'align': 'center'},
    'Cost': {'num_format': '0.00%', 'font_color': 'red'},
}

# Define conditional formatting
conditional_formats = {
    'Sales': [
        {
            'type': 'data_bar',
            'bar_color': '#63C384',
            'negative_color': '#FF555A'
        }
    ],
    'Growth': [
        {
            'type': 'cell',
            'criteria': 'less than',
            'value': 0,
            'format': {'bg_color': '#FFC7CE', 'font_color': '#9C0006'}
        },
        {
            'type': 'cell',
            'criteria': 'greater than',
            'value': 0.1,
            'format': {'bg_color': '#C6EFCE', 'font_color': '#006100'}
        }
    ]
}

# Export with formatting
dataframe_to_excel(
    df,
    'sales_report.xlsx',
    sheet_name='Sales Data',
    index=False,
    table_style='Table Style Medium 9',
    column_formats=column_formats,
    conditional_formats=conditional_formats,
    freeze_panes=(1, 0)
)

# Example with multiple DataFrames
df1 = pd.DataFrame({'A': range(5), 'B': np.random.rand(5)})
df2 = pd.DataFrame({'X': ['a', 'b', 'c'], 'Y': [1.1, 2.2, 3.3]})

excel_report_from_dataframes(
    {'Summary': df1, 'Details': df2},
    'multi_sheet_report.xlsx',
    table_styles=['Table Style Light 1', 'Table Style Light 2'],
    global_formats={'B': 'percent', 'Y': '0.00'}
)
```

## Key Features

1. **DataFrame Export with Formatting**:
   - `dataframe_to_excel()` handles most common formatting needs in one call
   - Automatic column width adjustment
   - Option to convert to Excel tables with styles
   - Freeze panes and gridline control

2. **Column Formatting**:
   - Predefined format types ('currency', 'percent', 'date')
   - Custom number formats
   - Full control over font, alignment, colors

3. **Conditional Formatting**:
   - Data bars for visual comparisons
   - Color scales based on value ranges
   - Text-based formatting rules

4. **Multi-Sheet Reports**:
   - Consistent formatting across multiple sheets
   - Support for different table styles per sheet
   - Global formatting rules

5. **Pandas Integration**:
   - Works seamlessly with DataFrame index and columns
   - Handles different data types (dates, numbers, text)
   - Preserves DataFrame structure in Excel

This package provides a powerful yet simple interface for creating professional Excel reports from pandas DataFrames with minimal code.
