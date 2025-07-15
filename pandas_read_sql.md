# Pandas read_sql Example Functions

Here are several example functions demonstrating how to use pandas' `read_sql` function to retrieve data from databases:

## Basic Examples

### 1. Simple SQL Query with SQLAlchemy Connection

```python
import pandas as pd
from sqlalchemy import create_engine

def get_data_from_table(connection_string, table_name):
    """
    Read entire table into a DataFrame
    
    Args:
        connection_string (str): Database connection string
        table_name (str): Name of table to read
        
    Returns:
        pd.DataFrame: DataFrame containing table data
    """
    engine = create_engine(connection_string)
    query = f"SELECT * FROM {table_name}"
    return pd.read_sql(query, engine)
```

### 2. Parameterized Query with WHERE Clause

```python
def get_filtered_data(connection_string, table_name, filter_column, filter_value):
    """
    Read filtered data from a table
    
    Args:
        connection_string (str): Database connection string
        table_name (str): Name of table to read
        filter_column (str): Column to filter on
        filter_value: Value to filter for
        
    Returns:
        pd.DataFrame: Filtered DataFrame
    """
    engine = create_engine(connection_string)
    query = f"SELECT * FROM {table_name} WHERE {filter_column} = :value"
    return pd.read_sql(query, engine, params={'value': filter_value})
```

## Advanced Examples

### 3. Using Stored Procedure

```python
def call_stored_procedure(connection_string, procedure_name, params=None):
    """
    Call a stored procedure and return results
    
    Args:
        connection_string (str): Database connection string
        procedure_name (str): Name of stored procedure
        params (dict): Parameters to pass to procedure
        
    Returns:
        pd.DataFrame: Result set from procedure
    """
    engine = create_engine(connection_string)
    if params:
        placeholders = ', '.join([f':{p}' for p in params.keys()])
        query = f"EXEC {procedure_name} {placeholders}"
        return pd.read_sql(query, engine, params=params)
    else:
        query = f"EXEC {procedure_name}"
        return pd.read_sql(query, engine)
```

### 4. Chunked Reading for Large Datasets

```python
def read_large_table_in_chunks(connection_string, table_name, chunk_size=10000):
    """
    Read large table in chunks to conserve memory
    
    Args:
        connection_string (str): Database connection string
        table_name (str): Name of table to read
        chunk_size (int): Number of rows per chunk
        
    Yields:
        pd.DataFrame: Chunk of the table data
    """
    engine = create_engine(connection_string)
    query = f"SELECT * FROM {table_name}"
    
    for chunk in pd.read_sql(query, engine, chunksize=chunk_size):
        yield chunk
```

### 5. Join Multiple Tables

```python
def join_tables(connection_string, table1, table2, join_condition, columns=None):
    """
    Join two tables and return result
    
    Args:
        connection_string (str): Database connection string
        table1 (str): First table name
        table2 (str): Second table name
        join_condition (str): JOIN condition (e.g., "table1.id = table2.table1_id")
        columns (list): List of columns to select (None for all columns)
        
    Returns:
        pd.DataFrame: Joined data
    """
    engine = create_engine(connection_string)
    
    if columns:
        cols = ', '.join(columns)
    else:
        cols = f"{table1}.*, {table2}.*"
    
    query = f"""
    SELECT {cols}
    FROM {table1}
    JOIN {table2} ON {join_condition}
    """
    
    return pd.read_sql(query, engine)
```

## Usage Examples

```python
# Example usage with SQLite
sqlite_conn = "sqlite:///mydatabase.db"

# 1. Read entire table
df = get_data_from_table(sqlite_conn, "customers")

# 2. Read filtered data
df_active = get_filtered_data(sqlite_conn, "customers", "status", "active")

# 3. Call stored procedure (syntax varies by DBMS)
# df_results = call_stored_procedure(sqlite_conn, "sp_get_recent_orders", {'days': 30})

# 4. Process large table in chunks
for chunk in read_large_table_in_chunks(sqlite_conn, "transactions"):
    process_chunk(chunk)  # Your processing function

# 5. Join tables
df_joined = join_tables(
    sqlite_conn,
    "orders",
    "customers",
    "orders.customer_id = customers.id",
    columns=["orders.id", "orders.date", "customers.name", "orders.amount"]
)
```

## Connection String Examples

Different databases require different connection strings:

- **SQLite**: `sqlite:///path/to/database.db`
- **PostgreSQL**: `postgresql://username:password@localhost:5432/database`
- **MySQL**: `mysql://username:password@localhost:3306/database`
- **SQL Server**: `mssql+pyodbc://username:password@dsn_name`
- **Oracle**: `oracle://username:password@localhost:1521/sid`

Note: You may need to install additional database drivers (like psycopg2 for PostgreSQL, pymysql for MySQL, etc.).



# Python Pandas and MySQL Utilities

Here's a set of functions to help with your data analysis and MySQL database operations:

## 1. Functions to Analyze DataFrame Columns

```python
import pandas as pd
import numpy as np

def get_column_max_lengths(df):
    """
    Calculate maximum length of string values in each column.
    
    Args:
        df (pd.DataFrame): Input dataframe
    
    Returns:
        dict: Dictionary with column names as keys and max lengths as values
    """
    length_stats = {}
    
    for col in df.columns:
        if df[col].dtype == object:  # String columns
            max_len = df[col].astype(str).str.len().max()
            length_stats[col] = max_len if not np.isnan(max_len) else 0
        else:
            length_stats[col] = None  # Non-string columns
    
    return length_stats

def detect_column_dtypes(df):
    """
    Detect data types of each column in a DataFrame.
    
    Args:
        df (pd.DataFrame): Input dataframe
    
    Returns:
        dict: Dictionary with column names as keys and dtypes as values
    """
    return {col: str(df[col].dtype) for col in df.columns}

def analyze_dataframe(df):
    """
    Comprehensive analysis of dataframe columns including dtypes and max lengths.
    
    Args:
        df (pd.DataFrame): Input dataframe
    
    Returns:
        dict: Dictionary with analysis results for each column
    """
    analysis = {}
    
    dtypes = detect_column_dtypes(df)
    max_lengths = get_column_max_lengths(df)
    
    for col in df.columns:
        analysis[col] = {
            'dtype': dtypes[col],
            'max_length': max_lengths[col],
            'sample_value': df[col].iloc[0] if len(df) > 0 else None
        }
    
    return analysis
```

## 2. MySQL Index Creation Functions

```python
import pymysql
from sqlalchemy import create_engine

def create_mysql_index(connection_params, table_name, column_name, index_name=None, index_type='INDEX'):
    """
    Create an index on a MySQL table column.
    
    Args:
        connection_params (dict): Dictionary with connection parameters
                                (host, user, password, database)
        table_name (str): Name of the table
        column_name (str): Name of the column to index
        index_name (str, optional): Name of the index. Defaults to f"idx_{column_name}"
        index_type (str, optional): Type of index (INDEX, UNIQUE, FULLTEXT). Defaults to 'INDEX'
    """
    if index_name is None:
        index_name = f"idx_{column_name}"
    
    connection = pymysql.connect(**connection_params)
    
    try:
        with connection.cursor() as cursor:
            sql = f"CREATE {index_type} {index_name} ON {table_name} ({column_name})"
            cursor.execute(sql)
        connection.commit()
        print(f"Successfully created {index_type} '{index_name}' on {table_name}({column_name})")
    except Exception as e:
        print(f"Error creating index: {e}")
    finally:
        connection.close()

def create_mysql_indexes_from_df(connection_params, table_name, df, index_columns=None):
    """
    Create indexes based on a DataFrame's columns.
    
    Args:
        connection_params (dict): MySQL connection parameters
        table_name (str): Name of the table
        df (pd.DataFrame): DataFrame used to determine appropriate indexes
        index_columns (list, optional): List of columns to index. Defaults to all string columns.
    """
    if index_columns is None:
        # Default to indexing string columns
        index_columns = [col for col in df.columns if df[col].dtype == object]
    
    for col in index_columns:
        create_mysql_index(connection_params, table_name, col)

def get_mysql_connection_engine(connection_params):
    """
    Create a SQLAlchemy engine for MySQL connection.
    
    Args:
        connection_params (dict): Dictionary with connection parameters
                                (host, user, password, database)
    
    Returns:
        sqlalchemy.engine: SQLAlchemy engine object
    """
    connection_string = (
        f"mysql+pymysql://{connection_params['user']}:{connection_params['password']}"
        f"@{connection_params['host']}/{connection_params['database']}"
    )
    return create_engine(connection_string)
```

## Example Usage

```python
# Example DataFrame
data = {
    'name': ['Alice', 'Bob', 'Charlie', 'David'],
    'age': [25, 30, 35, 40],
    'email': ['alice@example.com', 'bob@example.com', 'charlie@example.com', 'david@example.com'],
    'registration_date': pd.to_datetime(['2020-01-01', '2019-05-15', '2021-03-22', '2018-11-10'])
}
df = pd.DataFrame(data)

# Analyze the DataFrame
analysis = analyze_dataframe(df)
print("DataFrame Analysis:")
for col, stats in analysis.items():
    print(f"{col}: {stats}")

# MySQL Connection Parameters (example)
mysql_params = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'your_database'
}

# Create indexes (assuming you have a table called 'users')
# create_mysql_indexes_from_df(mysql_params, 'users', df, index_columns=['name', 'email'])
```

These functions provide:
1. Analysis of your DataFrame columns (data types and maximum lengths)
2. Utilities to create indexes in MySQL based on your DataFrame structure
3. A SQLAlchemy engine creator for more advanced operations

Remember to handle your database credentials securely and adjust the functions as needed for your specific use case.



# Enhanced Data Type Detection for SQLAlchemy Insertion

Here's an improved version that detects Pandas dtypes and maps them to appropriate SQLAlchemy types for database insertion:

```python
import pandas as pd
import numpy as np
from sqlalchemy import types as sa_types

def detect_sqlalchemy_dtype(series):
    """
    Detect the appropriate SQLAlchemy data type for a pandas Series.
    
    Args:
        series (pd.Series): Input pandas Series
        
    Returns:
        sqlalchemy.types: Corresponding SQLAlchemy data type
    """
    dtype = series.dtype
    
    # Handle nullable integer types (pandas Int64, Int32, etc.)
    if pd.api.types.is_integer_dtype(dtype):
        if series.isna().any():  # Contains nulls
            if series.max() < 2**31 and series.min() > -2**31-1:
                return sa_types.Integer()
            return sa_types.BigInteger()
        else:
            if series.max() < 2**31 and series.min() > -2**31-1:
                return sa_types.Integer()
            return sa_types.BigInteger()
    
    # Handle floating point numbers
    elif pd.api.types.is_float_dtype(dtype):
        return sa_types.Float()
    
    # Handle boolean types
    elif pd.api.types.is_bool_dtype(dtype):
        return sa_types.Boolean()
    
    # Handle datetime types
    elif pd.api.types.is_datetime64_any_dtype(dtype):
        return sa_types.DateTime()
    
    # Handle date types (without time)
    elif pd.api.types.is_datetime64_dtype(dtype) and not pd.api.types.is_datetime64_ns_dtype(dtype):
        return sa_types.Date()
    
    # Handle timedelta types
    elif pd.api.types.is_timedelta64_dtype(dtype):
        return sa_types.Interval()
    
    # Handle string/object types
    elif pd.api.types.is_string_dtype(dtype) or pd.api.types.is_object_dtype(dtype):
        max_len = series.astype(str).str.len().max()
        if pd.isna(max_len):
            max_len = 255  # Default length if no data
        return sa_types.String(length=int(max_len))
    
    # Handle categorical types
    elif pd.api.types.is_categorical_dtype(dtype):
        return sa_types.String(length=series.astype(str).str.len().max())
    
    # Default case
    return sa_types.Text()

def get_sqlalchemy_schema(df):
    """
    Generate a SQLAlchemy schema representation for a DataFrame.
    
    Args:
        df (pd.DataFrame): Input DataFrame
        
    Returns:
        dict: Dictionary mapping column names to SQLAlchemy types
    """
    return {col: detect_sqlalchemy_dtype(df[col]) for col in df.columns}

def dataframe_to_sql(df, table_name, engine, if_exists='fail', index=False, dtype=None):
    """
    Enhanced DataFrame.to_sql with automatic dtype detection.
    
    Args:
        df (pd.DataFrame): DataFrame to store
        table_name (str): Target table name
        engine (sqlalchemy.engine): Database engine
        if_exists (str): Behavior when table exists ('fail', 'replace', 'append')
        index (bool): Whether to write index
        dtype (dict, optional): Manual type specification overrides
    """
    if dtype is None:
        dtype = get_sqlalchemy_schema(df)
    
    df.to_sql(
        table_name,
        engine,
        if_exists=if_exists,
        index=index,
        dtype=dtype
    )
```

## Example Usage

```python
from sqlalchemy import create_engine

# Create example DataFrame with various data types
data = {
    'id': pd.Series([1, 2, 3], dtype='Int64'),  # Nullable integer
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35],
    'price': [19.99, 29.99, 39.99],
    'is_active': [True, False, True],
    'created_at': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03']),
    'description': ['Short', 'Medium text', 'Very long description text'],
    'category': pd.Categorical(['A', 'B', 'A'])
}
df = pd.DataFrame(data)

# Detect SQLAlchemy types
schema = get_sqlalchemy_schema(df)
for col, dtype in schema.items():
    print(f"{col}: {dtype}")

# Connect to database (example)
# engine = create_engine('mysql+pymysql://user:password@localhost/dbname')

# Write to database with automatic type detection
# dataframe_to_sql(df, 'my_table', engine, if_exists='replace')
```

## Key Features:

1. **Comprehensive Type Mapping**:
   - Handles nullable integers (pandas `Int64`)
   - Properly detects datetime vs date types
   - Manages string lengths based on actual data
   - Supports categorical types

2. **Enhanced to_sql Function**:
   - Wrapper around pandas' `to_sql` with automatic type detection
   - Still allows manual type overrides

3. **Practical Output**:
   - Returns SQLAlchemy types ready for database operations
   - Can be used directly with `to_sql` or for table creation

4. **Edge Case Handling**:
   - Empty/missing values don't break type detection
   - Automatic fallbacks for unknown types

This solution will help ensure your data is stored in the database with the most appropriate types while maintaining data integrity.
