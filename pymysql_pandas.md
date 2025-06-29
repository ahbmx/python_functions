Here's the updated module with centralized DB configuration and automatic connection handling without needing to pass credentials each time:

```python
import pandas as pd
import mysql.connector
from mysql.connector import Error
from functools import wraps

# Module-level DB Configuration (set these before using DB functions)
DB_CONFIG = {
    'host': None,
    'database': None,
    'user': None,
    'password': None
}

def configure_db(host, database, user, password):
    """
    Configure database connection parameters for the module
    :param host: Database host
    :param database: Database name
    :param user: Database username
    :param password: Database password
    """
    DB_CONFIG.update({
        'host': host,
        'database': database,
        'user': user,
        'password': password
    })

# Connection Handling Decorator
def with_auto_connection(func):
    """
    Decorator for automatic MySQL connection handling using module-level config
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if None in DB_CONFIG.values():
            raise ValueError("Database not configured. Call configure_db() first.")
            
        connection = None
        try:
            connection = create_mysql_connection(**DB_CONFIG)
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

# DataFrame Operations (same as before)
def drop_columns(df, columns_to_drop):
    return df.drop(columns=columns_to_drop, errors='ignore')

def reorder_columns(df, new_order):
    existing_cols = [col for col in new_order if col in df.columns]
    return df[existing_cols]

def rename_columns(df, column_mapping):
    return df.rename(columns=column_mapping)

def get_null_counts(df):
    return df.isnull().sum()

def drop_null_rows(df, columns=None):
    if columns:
        return df.dropna(subset=columns)
    return df.dropna()

def fill_null_values(df, fill_values):
    return df.fillna(fill_values)

def filter_rows(df, condition):
    return df[condition]

def add_column(df, column_name, value):
    df[column_name] = value
    return df

# MySQL Database Operations
def create_mysql_connection(host, database, user, password):
    try:
        return mysql.connector.connect(
            host=host,
            database=database,
            user=user,
            password=password
        )
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

@with_auto_connection
def execute_query(connection, query, params=None, fetch=False):
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
    cols = '*' if not columns else ', '.join(columns)
    query = f"SELECT {cols} FROM {table_name}"
    if where:
        query += f" WHERE {where}"
    if limit:
        query += f" LIMIT {limit}"
    return execute_query(connection, query, fetch=True)

@with_auto_connection
def write_to_sql_table(connection, df, table_name, if_exists='append', index=False):
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
    try:
        return execute_query(
            connection,
            "SHOW TABLES",
            fetch=True
        )
    except Error as e:
        print(f"Error getting table names: {e}")
        return None
```

### Key Improvements:

1. **Centralized DB Configuration**:
   - Added `DB_CONFIG` module-level dictionary
   - Added `configure_db()` function to set credentials once

2. **Simplified Decorator**:
   - Renamed to `with_auto_connection`
   - Uses module-level config automatically
   - Validates configuration before attempting connection

3. **Additional Features**:
   - Added `get_table_names()` function
   - Added `limit` parameter to `read_sql_table()`
   - Better return values for write operations (success/failure)

### Usage Example:

```python
# Configure the database once (typically at application startup)
configure_db(
    host='localhost',
    database='mydb',
    user='myuser',
    password='mypassword'
)

# All DB functions now work without connection parameters
df = read_sql_table(table_name='customers')

# Write operations are simpler too
success = write_to_sql_table(
    df=processed_data,
    table_name='processed_records',
    if_exists='append'
)

# Get list of tables in database
tables_df = get_table_names()
```

This implementation provides:
1. Single configuration point for DB credentials
2. Automatic connection management for all operations
3. Cleaner function signatures
4. Consistent error handling
5. Additional utility functions

The module maintains all the original functionality while making the API simpler to use in most common cases.
