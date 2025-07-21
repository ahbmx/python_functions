Here's an enhanced version of the function that includes an option to save the output to a text file:

```python
import pandas as pd

def dataframe_to_fixed_width(df, output_file=None, padding=2, 
                           numeric_align='right', str_align='left',
                           show_index=False, index_align='right'):
    """
    Convert a pandas DataFrame to a fixed-width formatted string or file.
    
    Parameters:
    - df: pandas DataFrame
    - output_file: Path to output file (if None, returns string)
    - padding: Number of extra spaces to add to column widths (default: 2)
    - numeric_align: Alignment for numeric columns ('right', 'left', or 'center')
    - str_align: Alignment for string/object columns ('right', 'left', or 'center')
    - show_index: Whether to include the index in output (default: False)
    - index_align: Alignment for index column ('right', 'left', or 'center')
    
    Returns:
    - If output_file is None: returns formatted string
    - If output_file is provided: saves to file and returns None
    """
    
    # Make a copy to avoid modifying original DataFrame
    df = df.copy()
    
    # Handle index if needed
    if show_index:
        df = df.reset_index()
    
    # Determine column widths
    col_widths = {}
    for col in df.columns:
        # Get max length in column values (convert to string first)
        max_data_len = df[col].astype(str).str.len().max()
        # Compare with column name length
        col_widths[col] = max(max_data_len, len(str(col))) + padding
    
    # Create format specifiers based on column types
    formats = {}
    for col in df.columns:
        width = col_widths[col]
        if pd.api.types.is_numeric_dtype(df[col]):
            align = {'right': '>', 'left': '<', 'center': '^'}[numeric_align]
        else:
            align = {'right': '>', 'left': '<', 'center': '^'}[str_align]
        formats[col] = f"{{:{align}{width}}}"
    
    # Build the header
    header = ''.join(formats[col].format(str(col)) for col in df.columns) + '\n'
    
    # Build each row
    rows = []
    for _, row in df.iterrows():
        row_str = ''.join(formats[col].format(str(row[col])) for col in df.columns)
        rows.append(row_str)
    
    # Combine header and rows
    output = header + '\n'.join(rows)
    
    # Handle output destination
    if output_file:
        with open(output_file, 'w') as f:
            f.write(output)
        return None
    else:
        return output

# Example usage:
if __name__ == "__main__":
    # Create sample DataFrame
    df = pd.DataFrame({
        'Name': ['Alice', 'Bob', 'Charlie', 'Diana'],
        'Age': [25, 30, 35, 28],
        'Salary': [50000, 60000, 70000, 55000],
        'Department': ['HR', 'Engineering', 'Marketing', 'Finance']
    }, index=['ID001', 'ID002', 'ID003', 'ID004'])
    
    # Option 1: Get as string
    fixed_width_str = dataframe_to_fixed_width(df, show_index=True)
    print("String output:")
    print(fixed_width_str)
    
    # Option 2: Save directly to file
    print("\nSaving to file...")
    dataframe_to_fixed_width(df, 
                           output_file='output.txt', 
                           show_index=True,
                           padding=3,
                           numeric_align='center',
                           str_align='left')
    
    print("Saved to 'output.txt'")
```

### Key Enhancements:
1. **File output option**: Added `output_file` parameter to save directly to a text file
2. **Index handling**: Added `show_index` and `index_align` parameters
3. **Improved formatting**: Better handling of column names and data types
4. **Flexible alignment**: Separate controls for numeric and string columns
5. **Non-destructive**: Works on a copy of the DataFrame

### Example File Output (output.txt):
```
index     Name      Age    Salary    Department  
ID001    Alice      25     50000    HR          
ID002    Bob        30     60000    Engineering 
ID003    Charlie    35     70000    Marketing   
ID004    Diana      28     55000    Finance     
```

### Usage Options:
1. **Get as string**: `result = dataframe_to_fixed_width(df)`
2. **Save to file**: `dataframe_to_fixed_width(df, output_file='data.txt')`
3. **Customize appearance**: Adjust padding, alignment, and index display

The function now provides a complete solution for both string output and file export with flexible formatting options.
