# Python Script with DVL Package and Helper Modules

Here's a comprehensive Python script structure with all the requested components:

## Directory Structure
```
your_project/
├── dvl/
│   ├── __init__.py
│   ├── functionHelper.py
│   ├── pmaxHelper.py
│   ├── brocadeHelper.py
│   ├── reportHelper.py
│   └── config.py
├── main_script.py
└── logs/
    └── app.log
```

## 1. config.py (Shared Variables)
```python
# dvl/config.py
import os
from pathlib import Path

# Shared variables available to all modules
# File paths
BASE_DIR = Path(__file__).parent.parent
LOG_DIR = BASE_DIR / 'logs'
DATA_DIR = BASE_DIR / 'data'
OUTPUT_DIR = BASE_DIR / 'output'

# Ensure directories exist
LOG_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Log file path
LOG_FILE = LOG_DIR / 'app.log'

# Configuration lists and dictionaries
PMAX_CONFIG = {
    'default_timeout': 30,
    'retry_attempts': 3
}

BROCADE_SETTINGS = {
    'ports': ['1/1', '1/2', '2/1'],
    'zoning_enabled': True
}

REPORT_COLUMNS = ['device', 'status', 'timestamp', 'details']

# Regular variables
DEFAULT_TIMEOUT = 60
MAX_RETRIES = 5
DEBUG_MODE = False

# You can add more shared variables here
```

## 2. __init__.py
```python
# dvl/__init__.py
from .config import *
from .functionHelper import setup_logging
from .pmaxHelper import PmaxHelper
from .brocadeHelper import BrocadeHelper
from .reportHelper import ReportHelper

__all__ = [
    'setup_logging',
    'PmaxHelper',
    'BrocadeHelper',
    'ReportHelper',
    'BASE_DIR',
    'LOG_DIR',
    'DATA_DIR',
    'OUTPUT_DIR',
    'LOG_FILE',
    'PMAX_CONFIG',
    'BROCADE_SETTINGS',
    'REPORT_COLUMNS',
    'DEFAULT_TIMEOUT',
    'MAX_RETRIES',
    'DEBUG_MODE'
]
```

## 3. functionHelper.py
```python
# dvl/functionHelper.py
import logging
import pandas as pd
from pathlib import Path
from typing import Optional, Union
from .config import LOG_FILE, DEBUG_MODE

def setup_logging(module_name: str, log_to_file: bool = True) -> logging.Logger:
    """
    Set up logging with module name included in the format.
    
    Args:
        module_name (str): Name of the module where logger is being set up
        log_to_file (bool): Whether to log to file (default: True)
    
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(module_name)
    logger.setLevel(logging.DEBUG if DEBUG_MODE else logging.INFO)
    
    # Clear existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    # File handler if requested
    if log_to_file:
        fh = logging.FileHandler(LOG_FILE)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    
    return logger

# Pandas-related helper functions
def read_data_file(file_path: Union[str, Path], logger: logging.Logger) -> pd.DataFrame:
    """
    Read data file with error handling.
    
    Args:
        file_path: Path to the data file
        logger: Logger instance for logging messages
    
    Returns:
        pd.DataFrame: Loaded dataframe
    """
    try:
        if str(file_path).endswith('.csv'):
            df = pd.read_csv(file_path)
        elif str(file_path).endswith('.xlsx'):
            df = pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file format")
            
        logger.info(f"Successfully loaded data from {file_path}")
        return df
    except Exception as e:
        logger.error(f"Failed to load data from {file_path}: {str(e)}")
        raise

def save_dataframe(df: pd.DataFrame, output_path: Union[str, Path], logger: logging.Logger) -> None:
    """
    Save dataframe to file with error handling.
    
    Args:
        df: DataFrame to save
        output_path: Path to save the file
        logger: Logger instance for logging messages
    """
    try:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if str(output_path).endswith('.csv'):
            df.to_csv(output_path, index=False)
        elif str(output_path).endswith('.xlsx'):
            df.to_excel(output_path, index=False)
        else:
            raise ValueError("Unsupported file format")
            
        logger.info(f"Successfully saved data to {output_path}")
    except Exception as e:
        logger.error(f"Failed to save data to {output_path}: {str(e)}")
        raise

# General helper functions
def validate_input(data: dict, required_fields: list, logger: logging.Logger) -> bool:
    """
    Validate input data contains all required fields.
    
    Args:
        data: Input data dictionary
        required_fields: List of required field names
        logger: Logger instance for logging messages
    
    Returns:
        bool: True if validation passes, False otherwise
    """
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        logger.warning(f"Missing required fields: {', '.join(missing_fields)}")
        return False
    return True
```

## 4. pmaxHelper.py
```python
# dvl/pmaxHelper.py
import logging
from typing import Optional, Dict, Any
from .functionHelper import setup_logging
from .config import PMAX_CONFIG, DEFAULT_TIMEOUT, MAX_RETRIES

class PmaxHelper:
    def __init__(self, log_to_file: bool = True):
        self.logger = setup_logging('dvl.pmaxHelper', log_to_file)
        self.config = PMAX_CONFIG
        self.timeout = DEFAULT_TIMEOUT
        self.max_retries = MAX_RETRIES
        self.logger.info("PmaxHelper initialized")
    
    def connect(self, connection_params: Dict[str, Any]) -> bool:
        """
        Connect to Pmax device.
        
        Args:
            connection_params: Dictionary containing connection parameters
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        self.logger.debug(f"Attempting to connect with params: {connection_params}")
        try:
            # Simulate connection logic
            if 'host' not in connection_params:
                raise ValueError("Missing host parameter")
            
            self.logger.info("Successfully connected to Pmax device")
            return True
        except Exception as e:
            self.logger.error(f"Connection failed: {str(e)}")
            return False
    
    def get_device_info(self, device_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a Pmax device.
        
        Args:
            device_id: ID of the device to query
        
        Returns:
            Optional dictionary containing device info, None if failed
        """
        self.logger.debug(f"Getting info for device {device_id}")
        try:
            # Simulate getting device info
            if not device_id:
                raise ValueError("Device ID cannot be empty")
            
            info = {
                'id': device_id,
                'status': 'online',
                'capacity': '10TB',
                'ports': 4
            }
            self.logger.info(f"Retrieved info for device {device_id}")
            return info
        except Exception as e:
            self.logger.error(f"Failed to get device info: {str(e)}")
            return None
```

## 5. brocadeHelper.py
```python
# dvl/brocadeHelper.py
import logging
from typing import Optional, Dict, Any, List
from .functionHelper import setup_logging
from .config import BROCADE_SETTINGS, DEFAULT_TIMEOUT

class BrocadeHelper:
    def __init__(self, log_to_file: bool = True):
        self.logger = setup_logging('dvl.brocadeHelper', log_to_file)
        self.settings = BROCADE_SETTINGS
        self.timeout = DEFAULT_TIMEOUT
        self.logger.info("BrocadeHelper initialized")
    
    def get_port_status(self, port_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of a Brocade port.
        
        Args:
            port_id: ID of the port to check
        
        Returns:
            Optional dictionary containing port status, None if failed
        """
        self.logger.debug(f"Checking status for port {port_id}")
        try:
            if port_id not in self.settings['ports']:
                raise ValueError(f"Port {port_id} not configured")
            
            status = {
                'port': port_id,
                'status': 'active',
                'speed': '16Gbps',
                'connected': True
            }
            self.logger.info(f"Retrieved status for port {port_id}")
            return status
        except Exception as e:
            self.logger.error(f"Failed to get port status: {str(e)}")
            return None
    
    def get_all_zones(self) -> List[Dict[str, Any]]:
        """
        Get all zones from Brocade switch.
        
        Returns:
            List of zone dictionaries
        """
        self.logger.debug("Getting all zones")
        try:
            # Simulate getting zones
            zones = [
                {'name': 'zone1', 'members': ['host1', 'storage1']},
                {'name': 'zone2', 'members': ['host2', 'storage2']}
            ]
            self.logger.info(f"Retrieved {len(zones)} zones")
            return zones
        except Exception as e:
            self.logger.error(f"Failed to get zones: {str(e)}")
            return []
```

## 6. reportHelper.py
```python
# dvl/reportHelper.py
import logging
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional
from .functionHelper import setup_logging, save_dataframe
from .config import REPORT_COLUMNS, OUTPUT_DIR

class ReportHelper:
    def __init__(self, log_to_file: bool = True):
        self.logger = setup_logging('dvl.reportHelper', log_to_file)
        self.default_columns = REPORT_COLUMNS
        self.output_dir = OUTPUT_DIR
        self.logger.info("ReportHelper initialized")
    
    def generate_report(self, data: List[Dict[str, Any]], 
                       report_name: str = "report",
                       columns: Optional[List[str]] = None) -> Path:
        """
        Generate a report from the provided data.
        
        Args:
            data: List of dictionaries containing report data
            report_name: Base name for the report file
            columns: Optional list of columns to include (uses default if None)
        
        Returns:
            Path to the generated report file
        """
        self.logger.debug(f"Generating report '{report_name}' with {len(data)} entries")
        try:
            # Use provided columns or default ones
            columns = columns or self.default_columns
            
            # Create DataFrame
            df = pd.DataFrame(data, columns=columns)
            
            # Generate output path
            output_path = self.output_dir / f"{report_name}.xlsx"
            
            # Save the report
            save_dataframe(df, output_path, self.logger)
            
            self.logger.info(f"Report successfully generated at {output_path}")
            return output_path
        except Exception as e:
            self.logger.error(f"Failed to generate report: {str(e)}")
            raise
    
    def merge_reports(self, report_paths: List[Path], 
                     output_name: str = "merged_report") -> Path:
        """
        Merge multiple reports into one.
        
        Args:
            report_paths: List of paths to reports to merge
            output_name: Base name for the merged report file
        
        Returns:
            Path to the merged report file
        """
        self.logger.debug(f"Merging {len(report_paths)} reports")
        try:
            dfs = []
            for path in report_paths:
                if path.suffix == '.csv':
                    df = pd.read_csv(path)
                elif path.suffix == '.xlsx':
                    df = pd.read_excel(path)
                else:
                    raise ValueError(f"Unsupported file format: {path.suffix}")
                dfs.append(df)
            
            merged_df = pd.concat(dfs, ignore_index=True)
            
            output_path = self.output_dir / f"{output_name}.xlsx"
            save_dataframe(merged_df, output_path, self.logger)
            
            self.logger.info(f"Merged report successfully generated at {output_path}")
            return output_path
        except Exception as e:
            self.logger.error(f"Failed to merge reports: {str(e)}")
            raise
```

## 7. main_script.py
```python
#!/usr/bin/env python3
"""
Main script demonstrating usage of the DVL package and helper modules.
"""
from dvl import (
    PmaxHelper, 
    BrocadeHelper, 
    ReportHelper,
    setup_logging,
    LOG_FILE,
    PMAX_CONFIG,
    BROCADE_SETTINGS,
    REPORT_COLUMNS,
    DEFAULT_TIMEOUT,
    MAX_RETRIES,
    DEBUG_MODE
)

def main():
    # Set up main script logging
    logger = setup_logging('main_script', log_to_file=True)
    
    logger.info("Starting main script execution")
    logger.debug(f"Configuration: timeout={DEFAULT_TIMEOUT}, retries={MAX_RETRIES}")
    logger.debug(f"PMax config: {PMAX_CONFIG}")
    logger.debug(f"Brocade settings: {BROCADE_SETTINGS}")
    
    # Initialize helpers
    pmax = PmaxHelper()
    brocade = BrocadeHelper()
    report = ReportHelper()
    
    # Demonstrate PMax functionality
    pmax.connect({'host': 'pmax1.example.com', 'user': 'admin'})
    device_info = pmax.get_device_info('pmax-001')
    logger.info(f"Device info: {device_info}")
    
    # Demonstrate Brocade functionality
    port_status = brocade.get_port_status('1/1')
    logger.info(f"Port status: {port_status}")
    zones = brocade.get_all_zones()
    logger.info(f"Found {len(zones)} zones")
    
    # Generate a report
    report_data = [
        {'device': 'pmax-001', 'status': 'online', 'timestamp': '2023-01-01', 'details': 'Normal operation'},
        {'device': 'brocade-1', 'status': 'active', 'timestamp': '2023-01-01', 'details': 'Port 1/1 active'}
    ]
    report_path = report.generate_report(report_data, report_name='device_status')
    logger.info(f"Report generated at: {report_path}")
    
    logger.info("Main script execution completed")

if __name__ == '__main__':
    main()
```

## Key Features:

1. **Shared Configuration**:
   - All modules can access shared variables from `config.py`
   - Includes file paths, dictionaries, lists, and regular variables

2. **Comprehensive Logging**:
   - Logger includes module name in format
   - Configurable file logging
   - Consistent logging across all modules

3. **Helper Modules**:
   - `functionHelper`: Core utilities and pandas functions
   - `pmaxHelper`: PMax-specific functionality
   - `brocadeHelper`: Brocade-specific functionality
   - `reportHelper`: Reporting and data export functionality

4. **Error Handling**:
   - Comprehensive error handling with logging
   - Consistent pattern across all functions

5. **Type Hints**:
   - Uses Python type hints for better code clarity

6. **File Management**:
   - Uses `pathlib` for cross-platform path handling
   - Automatic directory creation

To use this package, you would:
1. Create the directory structure
2. Add all the Python files
3. Run `main_script.py` or import the modules as needed


To create multiple directories defined in `config.py` using a function in `functionHelper.py`, here's how you should implement it:

## 1. First, update `config.py` to separate directory definitions

```python
# dvl/config.py
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Directory definitions (without creation)
DIRECTORIES = {
    'LOG_DIR': BASE_DIR / 'logs',
    'DATA_DIR': BASE_DIR / 'data',
    'OUTPUT_DIR': BASE_DIR / 'output',
    'REPORTS_DIR': BASE_DIR / 'reports',
    'TEMP_DIR': BASE_DIR / 'temp'
}

# Other existing configuration remains the same...
LOG_FILE = DIRECTORIES['LOG_DIR'] / 'app.log'
PMAX_CONFIG = {...}
# etc...
```

## 2. Add the directory creation function to `functionHelper.py`

```python
# dvl/functionHelper.py
import logging
from pathlib import Path
from typing import Dict, Union
from .config import DIRECTORIES

def create_directories(logger: logging.Logger = None) -> Dict[str, Path]:
    """
    Create all directories defined in config.DIRECTORIES
    
    Args:
        logger: Optional logger instance for logging creation results
    
    Returns:
        Dictionary of created directory paths
    """
    created_dirs = {}
    
    for name, path in DIRECTORIES.items():
        try:
            path.mkdir(parents=True, exist_ok=True)
            created_dirs[name] = path
            if logger:
                logger.debug(f"Directory {name} created/verified at {path}")
        except Exception as e:
            if logger:
                logger.error(f"Failed to create directory {name} at {path}: {str(e)}")
            created_dirs[name] = None
    
    return created_dirs
```

## 3. Update `__init__.py` to expose the new function

```python
# dvl/__init__.py
from .config import *
from .functionHelper import setup_logging, create_directories
# ... other imports ...

__all__ = [
    'setup_logging',
    'create_directories',
    # ... rest of your exports ...
]
```

## 4. Usage Examples

### Option 1: Use during package initialization
Add to your `__init__.py`:

```python
# Initialize directories when package is imported
_logger = setup_logging('dvl.init')
create_directories(_logger)
```

### Option 2: Explicit call from main script
In your `main_script.py`:

```python
from dvl import create_directories, setup_logging

logger = setup_logging('main_script')
create_directories(logger)
```

### Option 3: Use with existing helper initialization
In your helper classes (like `PmaxHelper.__init__`):

```python
def __init__(self, log_to_file: bool = True):
    self.logger = setup_logging('dvl.pmaxHelper', log_to_file)
    create_directories(self.logger)  # Ensure directories exist
    # ... rest of initialization ...
```

## Key Features of This Implementation:

1. **Separation of Concerns**:
   - `config.py` defines what directories should exist
   - `functionHelper.py` handles the actual creation

2. **Robust Error Handling**:
   - Continues if one directory fails
   - Provides detailed logging

3. **Flexible Usage**:
   - Can be called automatically or explicitly
   - Works with or without logging

4. **Parent Directory Creation**:
   - Uses `parents=True` to create entire paths
   - `exist_ok=True` prevents errors if directories exist

5. **Reporting**:
   - Returns dictionary showing which directories were created
   - None values indicate failures

## Alternative Implementation (More Functional Style)

If you prefer a more functional approach, you could modify `functionHelper.py` like this:

```python
def ensure_directory_exists(path: Union[str, Path], logger: logging.Logger = None) -> bool:
    """Ensure a single directory exists"""
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        if logger:
            logger.debug(f"Directory verified at {path}")
        return True
    except Exception as e:
        if logger:
            logger.error(f"Directory creation failed for {path}: {str(e)}")
        return False

def initialize_workspace(logger: logging.Logger = None) -> None:
    """Create all required directories"""
    for name, path in DIRECTORIES.items():
        success = ensure_directory_exists(path, logger)
        if not success and logger:
            logger.warning(f"Critical directory {name} could not be created")
```

This alternative gives you more granular control but requires more explicit calls. Choose whichever approach better fits your use case.

The logging will automatically include the module name in each log message and can be configured to log to both console and file.
