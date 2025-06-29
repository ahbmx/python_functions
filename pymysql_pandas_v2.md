Here's the updated version with hardcoded DB configuration and automatic connection handling, eliminating the need for initialization:

```python
import pandas as pd
import mysql.connector
from mysql.connector import Error
from functools import wraps

# Hardcoded DB Configuration - modify these values directly in the module
DB_CONFIG = {
    'host': 'localhost',
    'database': 'mydatabase',
    'user': 'myuser',
    'password': 'mypassword'
}

# Connection Handling Decorator
def with_auto_connection(func):
    """
    Decorator for automatic MySQL connection handling using hardcoded config
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        connection = None
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            if connection is None:
                raise ValueError("Failed to establish database connection")
            
            # Pass connection as first argument if not already provided
            if 'connection' not in kwargs and not any(
                isinstance(arg, mysql.connector.connection.MySQLConnection) 
                for arg in args
            ):
                args = (connection,) + args
                
            return func(*args, **kwargs)
        except Error as e:
            print(f"Database error in {func.__name__}: {e}")
            return None
        finally:
            if connection and connection.is_connected():
                connection.close()
    return wrapper

# DataFrame Operations
def drop_columns(df, columns_to_drop):
    """Drop specified columns from DataFrame"""
    return df.drop(columns=columns_to_drop, errors='ignore')

def reorder_columns(df, new_order):
    """Reorder columns in DataFrame"""
    existing_cols = [col for col in new_order if col in df.columns]
    return df[existing_cols]

def rename_columns(df, column_mapping):
    """Rename columns in DataFrame"""
    return df.rename(columns=column_mapping)

def get_null_counts(df):
    """Get count of null values for each column"""
    return df.isnull().sum()

def drop_null_rows(df, columns=None):
    """Drop rows with null values"""
    if columns:
        return df.dropna(subset=columns)
    return df.dropna()

def fill_null_values(df, fill_values):
    """Fill null values with specified values"""
    return df.fillna(fill_values)

def filter_rows(df, condition):
    """Filter rows based on condition"""
    return df[condition]

def add_column(df, column_name, value):
    """Add a new column to DataFrame"""
    df[column_name] = value
    return df

# MySQL Database Operations
@with_auto_connection
def execute_query(connection, query, params=None, fetch=False):
    """Execute a SQL query"""
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute(query, params or ())
        
        if fetch:
            columns = [col[0] for col in cursor.description]
            data = cursor.fetchall()
            return pd.DataFrame(data, columns=columns)
        connection.commit()
        return None
    except Error as e:
        print(f"Error executing query: {e}")
        connection.rollback()
        return None
    finally:
        if cursor:
            cursor.close()

@with_auto_connection
def read_sql_table(connection, table_name, columns=None, where=None, limit=None):
    """Read a SQL table into a DataFrame"""
    cols = '*' if not columns else ', '.join(columns)
    query = f"SELECT {cols} FROM {table_name}"
    if where:
        query += f" WHERE {where}"
    if limit:
        query += f" LIMIT {limit}"
    return execute_query(connection, query, fetch=True)

@with_auto_connection
def write_to_sql_table(connection, df, table_name, if_exists='append', index=False):
    """Write DataFrame to SQL table"""
    try:
        df.to_sql(
            name=table_name,
            con=connection,
            if_exists=if_exists,
            index=index
        )
        connection.commit()
        return True
    except Error as e:
        print(f"Error writing to SQL table: {e}")
        connection.rollback()
        return False

@with_auto_connection
def get_table_names(connection):
    """Get list of tables in the database"""
    try:
        return execute_query(
            connection,
            "SHOW TABLES",
            fetch=True
        )
    except Error as e:
        print(f"Error getting table names: {e}")
        return None

@with_auto_connection
def table_exists(connection, table_name):
    """Check if a table exists in the database"""
    try:
        result = execute_query(
            connection,
            "SHOW TABLES LIKE %s",
            params=(table_name,),
            fetch=True
        )
        return len(result) > 0
    except Error as e:
        print(f"Error checking table existence: {e}")
        return False
```

### Key Features:

1. **Hardcoded DB Configuration**:
   - The `DB_CONFIG` dictionary contains the connection parameters directly in the module
   - Simply edit these values in the module file to match your database setup

2. **Simplified Usage**:
   - No need to call any configuration function
   - All database functions work immediately with the hardcoded settings

3. **Additional Utility Function**:
   - Added `table_exists()` function to check if a table exists

4. **Automatic Connection Management**:
   - The decorator handles all connection lifecycle operations
   - Every database function gets a fresh connection automatically

### Usage Example:

```python
# Simply import and use - no configuration needed
from db_helper import read_sql_table, write_to_sql_table

# Read data
customers = read_sql_table(table_name='customers', limit=100)

# Process data
customers = drop_columns(customers, ['temp_column'])
customers = fill_null_values(customers, {'address': 'Unknown'})

# Write data
write_to_sql_table(
    df=customers,
    table_name='processed_customers',
    if_exists='replace'
)

# Check if table exists
if table_exists('important_table'):
    print("Table exists!")
```

To change the database connection, simply modify the `DB_CONFIG` dictionary at the top of the module file. All database functions will automatically use the new connection settings.
