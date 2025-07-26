Here's an updated version of the script that removes the interactive configuration and adds a `-f` (force) flag to control table replacement behavior:

```python
import argparse
import pandas as pd
import os
from sqlalchemy import create_engine

def upload_excel_to_db(file_path, db_type, table_name, db_config, force=False):
    """
    Upload an Excel file to the specified database table.
    
    Args:
        file_path (str): Path to the Excel file
        db_type (str): Type of database (mysql, postgresql, mssql)
        table_name (str): Name of the table to create/append to
        db_config (dict): Database connection parameters
        force (bool): If True, replace existing table; if False, fail if table exists
    """
    try:
        # Read Excel file
        df = pd.read_excel(file_path)
        print(f"Successfully read Excel file with {len(df)} rows")
        
        # Create database connection string based on type
        if db_type == 'mysql':
            conn_str = f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
        elif db_type == 'postgresql':
            conn_str = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
        elif db_type == 'mssql':
            conn_str = f"mssql+pyodbc://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}?driver=ODBC+Driver+17+for+SQL+Server"
        else:
            raise ValueError("Unsupported database type")
            
        # Create SQLAlchemy engine
        engine = create_engine(conn_str)
        print(f"Connected to {db_type} database")
        
        # Determine if_exists parameter based on force flag
        if_exists = 'replace' if force else 'fail'
        
        # Upload data to database
        df.to_sql(table_name, engine, if_exists=if_exists, index=False)
        print(f"Successfully uploaded data to table '{table_name}'")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Upload Excel file to a database table.')
    parser.add_argument('file', help='Path to the Excel file to upload')
    parser.add_argument('--db', required=True, choices=['mysql', 'postgresql', 'mssql'], 
                       help='Database type (mysql, postgresql, mssql)')
    parser.add_argument('--table', required=True, help='Name of the table to create/append to')
    parser.add_argument('--host', required=True, help='Database host')
    parser.add_argument('--port', required=True, help='Database port')
    parser.add_argument('--database', required=True, help='Database name')
    parser.add_argument('--user', required=True, help='Database username')
    parser.add_argument('--password', required=True, help='Database password')
    parser.add_argument('-f', '--force', action='store_true', 
                       help='Force replace table if it exists (default: fail if exists)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Verify file exists
    if not os.path.isfile(args.file):
        print(f"Error: File '{args.file}' not found")
        return
    
    # Prepare database configuration
    db_config = {
        'host': args.host,
        'port': args.port,
        'database': args.database,
        'user': args.user,
        'password': args.password
    }
    
    # Upload the file
    upload_excel_to_db(args.file, args.db, args.table, db_config, args.force)

if __name__ == '__main__':
    main()
```

## Usage Examples

1. **MySQL example (fail if table exists)**:
```bash
python upload_excel.py data.xlsx --db mysql --table my_table \
--host localhost --port 3306 --database mydb \
--user root --password secret
```

2. **PostgreSQL example (force replace table)**:
```bash
python upload_excel.py data.xlsx --db postgresql --table my_table \
--host localhost --port 5432 --database mydb \
--user postgres --password secret -f
```

3. **MS SQL Server example (fail if table exists)**:
```bash
python upload_excel.py data.xlsx --db mssql --table my_table \
--host localhost --port 1433 --database mydb \
--user sa --password "complex@password123"
```

## Key Changes:

1. **Removed interactive mode** - All database credentials must now be provided as command-line arguments
2. **Added `-f/--force` flag**:
   - When present: Will replace existing table (`if_exists='replace'`)
   - When absent: Will fail if table exists (`if_exists='fail'`)
3. **Required database parameters**:
   - `--host`: Database server host
   - `--port`: Database server port
   - `--database`: Database name
   - `--user`: Database username
   - `--password`: Database password

For security reasons, you might want to:
1. Use environment variables for sensitive credentials instead of command-line arguments
2. Or read from a configuration file
3. Or prompt for the password interactively while keeping other parameters as arguments
