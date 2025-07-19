# Enhanced PyU4V Report Export with Pagination

Here's a complete solution to run your `daily_data` and `yearly_data` reports, export them as CSV files, with pagination support for large reports:

```python
from PyU4V import U4VConn
import csv
from datetime import datetime

class ReportExporter:
    def __init__(self, username, password, server_ip, port='8443'):
        """Initialize the Unisphere connection"""
        self.conn = U4VConn(
            username=username,
            password=password,
            server_ip=server_ip,
            port=port,
            verify=False  # Set to True if using valid SSL cert
        )
        self.perf = self.conn.performance

    def export_report(self, report_name, page_size=1000):
        """
        Export a report to CSV with pagination support
        :param report_name: Name of the saved report
        :param page_size: Number of records per page (adjust based on performance)
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"{report_name}_{timestamp}.csv"
        
        print(f"Exporting report '{report_name}' to {output_file}...")
        
        # Get the first page of results
        current_page = 0
        more_pages = True
        first_page = True
        
        with open(output_file, 'w', newline='') as csvfile:
            writer = None
            
            while more_pages:
                current_page += 1
                print(f"Processing page {current_page}...")
                
                # Get paginated results
                report_data = self.perf.get_report_results(
                    report_name, 
                    start_page=current_page, 
                    page_size=page_size
                )
                
                if not report_data:
                    more_pages = False
                    break
                
                # Initialize CSV writer and write headers on first page
                if first_page and report_data:
                    writer = csv.DictWriter(csvfile, fieldnames=report_data[0].keys())
                    writer.writeheader()
                    first_page = False
                
                # Write data rows
                for row in report_data:
                    writer.writerow(row)
                
                # Check if we've reached the end (page smaller than page size)
                if len(report_data) < page_size:
                    more_pages = False
        
        print(f"Successfully exported {report_name} to {output_file}")
        return output_file

    def close(self):
        """Close the Unisphere connection"""
        self.conn.close_session()

# Example usage
if __name__ == "__main__":
    # Initialize exporter
    exporter = ReportExporter(
        username='your_username',
        password='your_password',
        server_ip='unisphere_server_ip'
    )
    
    try:
        # Export both reports
        daily_report = exporter.export_report('daily_data')
        yearly_report = exporter.export_report('yearly_data', page_size=500)  # Smaller page size for large reports
        
        print(f"\nReports exported successfully:")
        print(f"- Daily report: {daily_report}")
        print(f"- Yearly report: {yearly_report}")
    except Exception as e:
        print(f"Error exporting reports: {str(e)}")
    finally:
        exporter.close()
```

## Key Features:

1. **Pagination Support**:
   - Processes reports in chunks (configurable page size)
   - Automatically detects when all data has been retrieved
   - Adjust page_size parameter based on report size and performance needs

2. **Automatic Filenaming**:
   - Includes timestamp in filenames (e.g., `daily_data_20230719_143022.csv`)
   - Prevents overwriting previous exports

3. **Proper CSV Handling**:
   - Uses Python's csv module for proper CSV formatting
   - Handles header row automatically

4. **Error Handling**:
   - Wrapped in try-except block
   - Ensures connection is properly closed

5. **Flexible Configuration**:
   - Can adjust page_size per report (smaller for large yearly reports)
   - Easy to add more reports

## Usage Tips:

1. For very large reports (like yearly_data), use a smaller page_size (e.g., 500) to avoid memory issues.

2. Monitor performance - if exports are slow, try adjusting the page_size up or down.

3. Add error handling for specific cases like invalid report names or authentication failures.

4. Consider adding a progress bar for large reports (e.g., using tqdm library).

Would you like me to add any additional features to this implementation?
