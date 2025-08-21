Here's a Python script to import Excel files into pandas DataFrames with several options:

## Basic Script

```python
import pandas as pd
import os
from pathlib import Path

def import_excel_to_dataframe(file_path, sheet_name=0, **kwargs):
    """
    Import Excel file into pandas DataFrame
    
    Parameters:
    file_path (str): Path to the Excel file
    sheet_name (str/int): Sheet name or index (default: 0)
    **kwargs: Additional pandas read_excel parameters
    
    Returns:
    pandas.DataFrame or dict of DataFrames
    """
    try:
        # Read the Excel file
        df = pd.read_excel(file_path, sheet_name=sheet_name, **kwargs)
        return df
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None

# Example usage
if __name__ == "__main__":
    # Single file import
    file_path = "your_file.xlsx"
    df = import_excel_to_dataframe(file_path)
    
    if df is not None:
        print(f"Successfully imported {file_path}")
        print(f"Shape: {df.shape}")
        print("First few rows:")
        print(df.head())
```

## Advanced Script with Multiple Options

```python
import pandas as pd
import os
import glob
from pathlib import Path

class ExcelImporter:
    def __init__(self):
        self.dataframes = {}
    
    def import_single_file(self, file_path, **kwargs):
        """Import a single Excel file"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File {file_path} not found")
            
            df = pd.read_excel(file_path, **kwargs)
            filename = os.path.basename(file_path)
            self.dataframes[filename] = df
            return df
        except Exception as e:
            print(f"Error importing {file_path}: {e}")
            return None
    
    def import_multiple_files(self, folder_path, pattern="*.xlsx", **kwargs):
        """Import multiple Excel files from a folder"""
        try:
            files = glob.glob(os.path.join(folder_path, pattern))
            if not files:
                print(f"No files found matching pattern: {pattern}")
                return {}
            
            for file_path in files:
                df = self.import_single_file(file_path, **kwargs)
                if df is not None:
                    print(f"Imported: {os.path.basename(file_path)} - Shape: {df.shape}")
            
            return self.dataframes
        except Exception as e:
            print(f"Error importing files from {folder_path}: {e}")
            return {}
    
    def import_all_sheets(self, file_path, **kwargs):
        """Import all sheets from an Excel file"""
        try:
            # Read all sheets into a dictionary of DataFrames
            sheets_dict = pd.read_excel(file_path, sheet_name=None, **kwargs)
            filename = os.path.basename(file_path)
            
            for sheet_name, df in sheets_dict.items():
                key = f"{filename}_{sheet_name}"
                self.dataframes[key] = df
            
            return sheets_dict
        except Exception as e:
            print(f"Error importing sheets from {file_path}: {e}")
            return {}
    
    def get_dataframe(self, key):
        """Get a specific DataFrame by key"""
        return self.dataframes.get(key)
    
    def list_dataframes(self):
        """List all imported DataFrames"""
        return list(self.dataframes.keys())

# Example usage and demonstration
def main():
    # Initialize the importer
    importer = ExcelImporter()
    
    # Example 1: Import single file
    print("=== Importing Single File ===")
    df_single = importer.import_single_file(
        "data/sample.xlsx",
        sheet_name=0,  # or sheet name "Sheet1"
        header=0,      # use first row as header
        na_values=["NA", "N/A", ""]  # treat these as NaN
    )
    
    if df_single is not None:
        print(f"Single file imported successfully!")
        print(f"Shape: {df_single.shape}")
        print(f"Columns: {list(df_single.columns)}")
        print("\nFirst 5 rows:")
        print(df_single.head())
    
    # Example 2: Import all sheets from a file
    print("\n=== Importing All Sheets ===")
    sheets_dict = importer.import_all_sheets("data/multi_sheet.xlsx")
    for sheet_name, df in sheets_dict.items():
        print(f"Sheet '{sheet_name}': {df.shape}")
    
    # Example 3: Import multiple files from folder
    print("\n=== Importing Multiple Files ===")
    folder_data = importer.import_multiple_files(
        "data/",
        pattern="*.xlsx",
        header=0
    )
    
    # List all imported dataframes
    print(f"\nAll imported DataFrames: {importer.list_dataframes()}")
    
    # Access a specific dataframe
    if importer.list_dataframes():
        sample_df = importer.get_dataframe(importer.list_dataframes()[0])
        if sample_df is not None:
            print(f"\nSample DataFrame info:")
            print(sample_df.info())

if __name__ == "__main__":
    main()
```

## Simple One-Liner Import

```python
import pandas as pd

# Most basic import
df = pd.read_excel('your_file.xlsx')

# With common parameters
df = pd.read_excel(
    'your_file.xlsx',
    sheet_name='Sheet1',    # or sheet index 0
    header=0,               # row to use as column names
    index_col=0,            # column to use as row index
    usecols='A:C,E:G',      # specific columns to read
    na_values=['NA', ''],   # values to treat as NaN
    dtype={'column_name': str}  # specify data types
)

print(df.head())
```

## Installation Requirements

First, install the required packages:

```bash
pip install pandas openpyxl xlrd
```

- `pandas`: Data analysis library
- `openpyxl`: For reading .xlsx files (Excel 2007+)
- `xlrd`: For reading .xls files (Excel 2003-)

## Common Parameters for read_excel()

```python
# Common useful parameters:
pd.read_excel(
    file_path,
    sheet_name=0,           # Sheet name or index
    header=0,               # Row number for headers
    names=['col1', 'col2'], # Custom column names
    index_col=0,            # Column to use as index
    usecols='A:C,E:G',      # Columns to read
    skiprows=3,             # Rows to skip at start
    nrows=100,              # Number of rows to read
    dtype={'col1': str},    # Data types
    na_values=['', 'NA'],   # Values to treat as NaN
    engine='openpyxl'       # Engine to use
)
```

Choose the script version that best fits your needs. The advanced class-based approach provides the most flexibility for handling multiple files and sheets.
