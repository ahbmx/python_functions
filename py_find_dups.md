Here's the enhanced Python script with Excel export functionality using XlsxWriter:

```python
#!/usr/bin/env python3
"""
Duplicate File Finder with Excel Export
Finds duplicate files across multiple directories recursively
"""

import os
import sys
import hashlib
import argparse
from collections import defaultdict
from datetime import datetime
from typing import List, Dict, Set
try:
    import xlsxwriter
except ImportError:
    print("Error: xlsxwriter library is required for Excel export.")
    print("Install it with: pip install XlsxWriter")
    sys.exit(1)

def get_file_hash(filepath: str, chunk_size: int = 8192) -> str:
    """Calculate MD5 hash of a file"""
    hash_md5 = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except (IOError, OSError) as e:
        print(f"Error reading file {filepath}: {e}")
        return None

def get_file_info(filepath: str) -> dict:
    """Get detailed file information"""
    try:
        stat = os.stat(filepath)
        return {
            'size': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'created': datetime.fromtimestamp(stat.st_ctime),
            'path': filepath,
            'filename': os.path.basename(filepath),
            'directory': os.path.dirname(filepath)
        }
    except (OSError, PermissionError) as e:
        print(f"Error getting file info for {filepath}: {e}")
        return None

def find_duplicates(paths: List[str], min_size: int = 1) -> Dict[str, List[dict]]:
    """
    Find duplicate files in given paths recursively
    
    Args:
        paths: List of directory paths to search
        min_size: Minimum file size in bytes to consider (default: 1 byte)
    
    Returns:
        Dictionary with file hashes as keys and lists of file info dictionaries as values
    """
    file_hashes = defaultdict(list)
    files_processed = 0
    
    for search_path in paths:
        if not os.path.exists(search_path):
            print(f"Warning: Path '{search_path}' does not exist, skipping...")
            continue
            
        print(f"Scanning: {search_path}")
        
        for root, dirs, files in os.walk(search_path):
            for file in files:
                file_path = os.path.join(root, file)
                
                try:
                    # Skip if file is too small
                    file_size = os.path.getsize(file_path)
                    if file_size < min_size:
                        continue
                    
                    # Skip symlinks and special files
                    if not os.path.isfile(file_path):
                        continue
                        
                    files_processed += 1
                    if files_processed % 1000 == 0:
                        print(f"Processed {files_processed} files...")
                    
                    file_hash = get_file_hash(file_path)
                    if file_hash:
                        file_info = get_file_info(file_path)
                        if file_info:
                            file_hashes[file_hash].append(file_info)
                        
                except (OSError, PermissionError) as e:
                    print(f"Error accessing {file_path}: {e}")
                    continue
    
    # Only return hashes with multiple files (duplicates)
    duplicates = {h: files for h, files in file_hashes.items() if len(files) > 1}
    return duplicates

def format_size(size_bytes: int) -> str:
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def display_duplicates(duplicates: Dict[str, List[dict]], show_size: bool = True):
    """Display duplicate files in a readable format"""
    if not duplicates:
        print("No duplicate files found!")
        return
    
    total_duplicates = 0
    total_wasted = 0
    
    print("\n" + "="*80)
    print("DUPLICATE FILES FOUND")
    print("="*80)
    
    for i, (file_hash, file_infos) in enumerate(duplicates.items(), 1):
        # Get file size of first file in the group
        file_size = file_infos[0]['size']
        wasted_space = file_size * (len(file_infos) - 1)
        total_wasted += wasted_space
        total_duplicates += len(file_infos) - 1
        
        print(f"\nGroup {i}: {format_size(file_size)} each")
        if show_size:
            print(f"Hash: {file_hash[:16]}...")
        print(f"Wasted space: {format_size(wasted_space)}")
        print("-" * 40)
        
        for j, info in enumerate(file_infos, 1):
            print(f"{j}. {info['path']}")
    
    print("\n" + "="*80)
    print(f"SUMMARY:")
    print(f"Total duplicate groups: {len(duplicates)}")
    print(f"Total duplicate files: {total_duplicates}")
    print(f"Total wasted space: {format_size(total_wasted)}")
    print("="*80)

def export_to_excel(duplicates: Dict[str, List[dict]], output_file: str):
    """Export duplicate files report to Excel using XlsxWriter"""
    if not duplicates:
        print("No duplicates to export!")
        return
    
    # Create workbook and worksheets
    workbook = xlsxwriter.Workbook(output_file)
    
    # Summary worksheet
    summary_ws = workbook.add_worksheet('Summary')
    summary_ws.set_tab_color('#FF9900')
    
    # Detailed worksheet
    details_ws = workbook.add_worksheet('Duplicate Files')
    details_ws.set_tab_color('#FF0000')
    
    # Format styles
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#366092',
        'font_color': 'white',
        'border': 1,
        'align': 'center',
        'valign': 'vcenter'
    })
    
    number_format = workbook.add_format({'num_format': '#,##0'})
    size_format = workbook.add_format({'num_format': '#,##0" KB"'})
    date_format = workbook.add_format({'num_format': 'yyyy-mm-dd hh:mm:ss'})
    
    # Write summary data
    summary_headers = ['Metric', 'Value']
    summary_data = [
        ['Total Duplicate Groups', len(duplicates)],
        ['Total Duplicate Files', sum(len(files) - 1 for files in duplicates.values())],
        ['Total Wasted Space (bytes)', sum(files[0]['size'] * (len(files) - 1) for files in duplicates.values())],
        ['Scan Date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
    ]
    
    for col, header in enumerate(summary_headers):
        summary_ws.write(0, col, header, header_format)
    
    for row, (metric, value) in enumerate(summary_data, 1):
        summary_ws.write(row, 0, metric)
        if isinstance(value, (int, float)):
            summary_ws.write(row, 1, value, number_format)
        else:
            summary_ws.write(row, 1, value)
    
    summary_ws.set_column('A:A', 25)
    summary_ws.set_column('B:B', 20)
    
    # Write detailed data
    details_headers = [
        'Group ID', 'File Hash', 'File Name', 'File Size (KB)', 
        'File Path', 'Directory', 'Modified Date', 'Created Date'
    ]
    
    for col, header in enumerate(details_headers):
        details_ws.write(0, col, header, header_format)
    
    row = 1
    for group_id, (file_hash, file_infos) in enumerate(duplicates.items(), 1):
        for file_info in file_infos:
            details_ws.write(row, 0, group_id)
            details_ws.write(row, 1, file_hash)
            details_ws.write(row, 2, file_info['filename'])
            details_ws.write(row, 3, file_info['size'] / 1024, size_format)
            details_ws.write(row, 4, file_info['path'])
            details_ws.write(row, 5, file_info['directory'])
            details_ws.write(row, 6, file_info['modified'], date_format)
            details_ws.write(row, 7, file_info['created'], date_format)
            row += 1
    
    # Set column widths
    details_ws.set_column('A:A', 10)  # Group ID
    details_ws.set_column('B:B', 20)  # File Hash
    details_ws.set_column('C:C', 30)  # File Name
    details_ws.set_column('D:D', 15)  # File Size
    details_ws.set_column('E:E', 50)  # File Path
    details_ws.set_column('F:F', 40)  # Directory
    details_ws.set_column('G:H', 20)  # Dates
    
    # Add autofilter
    details_ws.autofilter(0, 0, row, len(details_headers) - 1)
    
    # Add chart to summary
    chart = workbook.add_chart({'type': 'column'})
    
    chart.add_series({
        'name': 'Duplicate Groups',
        'categories': '=Summary!$A$2:$A$4',
        'values': '=Summary!$B$2:$B$4',
    })
    
    chart.set_title({'name': 'Duplicate Files Summary'})
    chart.set_x_axis({'name': 'Metrics'})
    chart.set_y_axis({'name': 'Count'})
    
    summary_ws.insert_chart('E2', chart)
    
    workbook.close()
    print(f"Excel report saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(
        description="Find duplicate files across multiple directories recursively",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/dir1 /path/to/dir2
  %(prog)s ~/Documents ~/Pictures --min-size 1048576
  %(prog)s . --export report.xlsx
  %(prog)s /path/to/search --quiet --export duplicates.xlsx
        """
    )
    
    parser.add_argument(
        "paths",
        nargs="+",
        help="Directories to search for duplicates"
    )
    
    parser.add_argument(
        "--min-size",
        type=int,
        default=1,
        help="Minimum file size in bytes (default: 1)"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress output"
    )
    
    parser.add_argument(
        "--no-size",
        action="store_true",
        help="Don't show file sizes in output"
    )
    
    parser.add_argument(
        "--export",
        metavar="FILENAME",
        help="Export results to Excel file (e.g., --export report.xlsx)"
    )
    
    args = parser.parse_args()
    
    if not args.quiet:
        print("Starting duplicate file search...")
        print(f"Searching in: {', '.join(args.paths)}")
        if args.min_size > 1:
            print(f"Minimum file size: {format_size(args.min_size)}")
    
    duplicates = find_duplicates(args.paths, args.min_size)
    
    if not args.quiet:
        display_duplicates(duplicates, not args.no_size)
    else:
        # Quiet mode: just output file paths for scripting
        for file_infos in duplicates.values():
            for info in file_infos:
                print(info['path'])
    
    # Export to Excel if requested
    if args.export:
        if not args.quiet:
            print(f"\nExporting results to Excel file: {args.export}")
        export_to_excel(duplicates, args.export)
        
        if not args.quiet:
            print("Export completed successfully!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
```

## Features Added:

1. **Excel Export with XlsxWriter**: Creates a comprehensive Excel report with:
   - Summary worksheet with statistics
   - Detailed worksheet with all duplicate files
   - Formatted headers and columns
   - Automatic column sizing
   - Date and number formatting
   - Color-coded worksheet tabs
   - Autofilter for easy data manipulation
   - Charts for visual representation

2. **Enhanced File Information**: Collects additional metadata:
   - File size
   - Modification date
   - Creation date
   - File name and directory paths

3. **Command Line Option**: `--export filename.xlsx` to export results

## Installation:

```bash
pip install XlsxWriter
```

## Usage Examples:

```bash
# Basic usage with Excel export
python duplicate_finder.py /path/to/dir1 /path/to/dir2 --export report.xlsx

# With minimum file size and export
python duplicate_finder.py ~/Documents ~/Pictures --min-size 1048576 --export duplicates.xlsx

# Quiet mode with export (for scripting)
python duplicate_finder.py /path/to/search --quiet --export output.xlsx
```

## Excel Report Includes:

- **Summary Sheet**: Total groups, files, wasted space, scan date
- **Duplicate Files Sheet**: Detailed list of all duplicate files with metadata
- **Formatted Columns**: Proper number, date, and size formatting
- **Autofilter**: Easy filtering and sorting of results
- **Chart**: Visual representation of summary statistics

The Excel export provides a professional, formatted report that's easy to analyze and share with others.
