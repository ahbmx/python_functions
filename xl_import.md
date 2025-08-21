Here's the enhanced advanced script using XlsxWriter as the primary engine:

```python
import pandas as pd
import os
import glob
from pathlib import Path
import xlsxwriter
import warnings
warnings.filterwarnings('ignore')

class AdvancedExcelImporter:
    def __init__(self):
        self.dataframes = {}
        self.file_info = {}
    
    def detect_engine(self, file_path):
        """Detect the appropriate engine for the Excel file with preference for XlsxWriter"""
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.xlsx':
            try:
                # Try XlsxWriter first for .xlsx files
                return 'xlsxwriter'
            except:
                # Fallback to openpyxl if XlsxWriter fails
                return 'openpyxl'
        elif file_ext == '.xls':
            return 'xlrd'  # Older Excel format
        elif file_ext == '.xlsm':
            return 'openpyxl'  # Macro-enabled files
        else:
            return 'xlsxwriter'  # Default to XlsxWriter
    
    def get_sheet_names(self, file_path):
        """Get all sheet names from an Excel file using XlsxWriter when possible"""
        try:
            engine = self.detect_engine(file_path)
            with pd.ExcelFile(file_path, engine=engine) as xl:
                return xl.sheet_names
        except Exception as e:
            print(f"Error getting sheet names for {file_path}: {e}")
            return []
    
    def import_single_file(self, file_path, sheet_name=0, engine='xlsxwriter', **kwargs):
        """Import a single Excel file or specific sheet using XlsxWriter"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File {file_path} not found")
            
            # Force XlsxWriter engine
            kwargs['engine'] = engine
            
            print(f"Importing {file_path} using {engine} engine...")
            
            df = pd.read_excel(file_path, sheet_name=sheet_name, **kwargs)
            filename = os.path.basename(file_path)
            
            # Create a unique key
            if isinstance(sheet_name, (int, type(None))):
                sheet_key = f"Sheet_{sheet_name if sheet_name is not None else 0}"
            else:
                sheet_key = sheet_name
            
            key = f"{filename}_{sheet_key}"
            self.dataframes[key] = df
            
            # Store file info
            self.file_info[key] = {
                'file_path': file_path,
                'sheet_name': sheet_name,
                'engine_used': engine,
                'shape': df.shape,
                'columns': list(df.columns),
                'dtypes': df.dtypes.to_dict(),
                'import_time': pd.Timestamp.now()
            }
            
            print(f"✓ Successfully imported {key} - Shape: {df.shape}")
            return df
            
        except Exception as e:
            print(f"❌ Error importing {file_path} with {engine}: {e}")
            print("Trying fallback engine...")
            
            # Fallback to openpyxl if XlsxWriter fails
            if engine == 'xlsxwriter':
                return self.import_single_file(file_path, sheet_name, engine='openpyxl', **kwargs)
            return None
    
    def import_multiple_files(self, folder_path, pattern="*.xlsx", engine='xlsxwriter', **kwargs):
        """Import multiple Excel files from a folder using specified engine"""
        try:
            files = glob.glob(os.path.join(folder_path, pattern))
            if not files:
                print(f"No files found matching pattern: {pattern}")
                return {}
            
            results = {}
            for file_path in files:
                df = self.import_single_file(file_path, engine=engine, **kwargs)
                if df is not None:
                    results[os.path.basename(file_path)] = df
            
            return results
        except Exception as e:
            print(f"Error importing files from {folder_path}: {e}")
            return {}
    
    def import_all_sheets(self, file_path, engine='xlsxwriter', **kwargs):
        """Import all sheets from an Excel file using XlsxWriter"""
        try:
            # Force XlsxWriter engine
            kwargs['engine'] = engine
            
            print(f"Importing all sheets from {file_path} using {engine} engine...")
            
            # Read all sheets into a dictionary of DataFrames
            sheets_dict = pd.read_excel(file_path, sheet_name=None, **kwargs)
            filename = os.path.basename(file_path)
            
            for sheet_name, df in sheets_dict.items():
                key = f"{filename}_{sheet_name}"
                self.dataframes[key] = df
                
                # Store file info
                self.file_info[key] = {
                    'file_path': file_path,
                    'sheet_name': sheet_name,
                    'engine_used': engine,
                    'shape': df.shape,
                    'columns': list(df.columns),
                    'dtypes': df.dtypes.to_dict(),
                    'import_time': pd.Timestamp.now()
                }
                
                print(f"✓ Sheet '{sheet_name}': {df.shape}")
            
            return sheets_dict
            
        except Exception as e:
            print(f"❌ Error importing sheets from {file_path} with {engine}: {e}")
            print("Trying fallback engine...")
            
            # Fallback to openpyxl if XlsxWriter fails
            if engine == 'xlsxwriter':
                return self.import_all_sheets(file_path, engine='openpyxl', **kwargs)
            return {}
    
    def export_to_excel(self, df, output_path, sheet_name='Sheet1', engine='xlsxwriter', **kwargs):
        """Export DataFrame to Excel using XlsxWriter"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with pd.ExcelWriter(output_path, engine=engine, **kwargs) as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            print(f"✓ Successfully exported to {output_path} using {engine}")
            return True
        except Exception as e:
            print(f"❌ Error exporting to {output_path}: {e}")
            return False
    
    def get_dataframe(self, key):
        """Get a specific DataFrame by key"""
        return self.dataframes.get(key)
    
    def list_dataframes(self):
        """List all imported DataFrames"""
        return list(self.dataframes.keys())
    
    def get_file_info(self, key=None):
        """Get information about imported files"""
        if key:
            return self.file_info.get(key)
        return self.file_info
    
    def display_summary(self):
        """Display summary of all imported data"""
        print("\n" + "="*60)
        print("EXCEL IMPORT SUMMARY")
        print("="*60)
        
        if not self.dataframes:
            print("No data imported yet.")
            return
        
        for key, info in self.file_info.items():
            print(f"\n📁 {key}")
            print(f"   File: {info['file_path']}")
            print(f"   Sheet: {info['sheet_name']}")
            print(f"   Engine: {info['engine_used']}")
            print(f"   Shape: {info['shape']}")
            print(f"   Columns: {len(info['columns'])}")
            print(f"   Imported: {info['import_time']}")

# Example usage and demonstration
def main():
    # Initialize the importer
    importer = AdvancedExcelImporter()
    
    # Example 1: Import single file with XlsxWriter
    print("=== Importing Single File with XlsxWriter ===")
    df_single = importer.import_single_file(
        "data/sample.xlsx",
        sheet_name=0,
        engine='xlsxwriter',  # Force XlsxWriter
        header=0,
        na_values=["NA", "N/A", ""]
    )
    
    if df_single is not None:
        print(f"\nDataFrame Info:")
        print(df_single.info())
        print(f"\nFirst 3 rows:")
        print(df_single.head(3))
    
    # Example 2: Import all sheets with XlsxWriter
    print("\n=== Importing All Sheets with XlsxWriter ===")
    sheets_dict = importer.import_all_sheets(
        "data/multi_sheet.xlsx",
        engine='xlsxwriter'
    )
    
    # Example 3: Import multiple files
    print("\n=== Importing Multiple Files ===")
    folder_data = importer.import_multiple_files(
        "data/",
        pattern="*.xlsx",
        engine='xlsxwriter'
    )
    
    # Display summary
    importer.display_summary()
    
    # Example 4: Export to Excel using XlsxWriter
    print("\n=== Exporting DataFrame using XlsxWriter ===")
    if importer.list_dataframes():
        sample_key = importer.list_dataframes()[0]
        sample_df = importer.get_dataframe(sample_key)
        
        success = importer.export_to_excel(
            sample_df,
            "output/exported_data.xlsx",
            sheet_name='Exported_Data',
            engine='xlsxwriter'
        )
        
        if success:
            print("Export completed successfully!")

if __name__ == "__main__":
    # Create sample data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    
    main()
```

## Installation Requirements

First, install the required packages:

```bash
pip install pandas xlsxwriter openpyxl xlrd
```

## Key Features:

1. **XlsxWriter as Primary Engine**: Forces XlsxWriter for all operations
2. **Automatic Fallback**: Falls back to openpyxl if XlsxWriter fails
3. **Comprehensive Error Handling**: Robust error handling with detailed messages
4. **File Information Tracking**: Keeps metadata about imported files
5. **Export Functionality**: Includes export to Excel using XlsxWriter
6. **Multiple File Support**: Handles single files, multiple files, and all sheets
7. **Summary Reporting**: Detailed summary of imported data

## Usage Examples:

```python
# Initialize
importer = AdvancedExcelImporter()

# Import single file with XlsxWriter
df = importer.import_single_file("file.xlsx", engine='xlsxwriter')

# Import all sheets
sheets = importer.import_all_sheets("file.xlsx", engine='xlsxwriter')

# Import multiple files
files = importer.import_multiple_files("folder/", engine='xlsxwriter')

# Export data
importer.export_to_excel(df, "output.xlsx", engine='xlsxwriter')
```

The script will automatically use XlsxWriter as the primary engine and provide fallback options if needed.
