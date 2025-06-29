Yes! We can automate connection handling using **context managers** (`with` statements) or **decorators** to avoid manually opening/closing connections. Here are improved versions of both modules with **auto-connection handling**:

---

# **1. `pymysql_functions.py` (Auto-Connection Handling)**
```python
import pymysql
from sqlalchemy import create_engine
import pandas as pd
from typing import List, Dict, Union, Optional, Callable
from functools import wraps

# --- Connection Handling ---
def get_pymysql_engine(host: str, user: str, password: str, database: str):
    """Returns a SQLAlchemy engine for Pandas."""
    return create_engine(f"mysql+pymysql://{user}:{password}@{host}/{database}")

def with_pymysql_connection(func: Callable):
    """Decorator to automatically handle PyMySQL connections."""
    @wraps(func)
    def wrapper(host: str, user: str, password: str, database: str, *args, **kwargs):
        conn = pymysql.connect(host=host, user=user, password=password, database=database)
        try:
            result = func(conn, *args, **kwargs)
            conn.commit()
            return result
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    return wrapper

# --- Table Operations ---
@with_pymysql_connection
def create_table(conn, table_name: str, columns: Dict[str, str], primary_key: Optional[str] = None):
    """Creates a table. Example: {'id': 'INT', 'name': 'VARCHAR(50)'}"""
    columns_sql = ", ".join([f"{col} {dtype}" for col, dtype in columns.items()])
    if primary_key:
        columns_sql += f", PRIMARY KEY ({primary_key})"
    with conn.cursor() as cursor:
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql})")

@with_pymysql_connection
def drop_table(conn, table_name: str):
    """Drops a table if it exists."""
    with conn.cursor() as cursor:
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

# --- Query Execution ---
@with_pymysql_connection
def run_query(conn, query: str, params: Optional[tuple] = None):
    """Executes INSERT/UPDATE/DELETE queries."""
    with conn.cursor() as cursor:
        cursor.execute(query, params)

@with_pymysql_connection
def read_query(conn, query: str, params: Optional[tuple] = None) -> List[tuple]:
    """Returns query results as a list of tuples."""
    with conn.cursor() as cursor:
        cursor.execute(query, params)
        return cursor.fetchall()

@with_pymysql_connection
def read_query_dict(conn, query: str, params: Optional[tuple] = None) -> List[dict]:
    """Returns query results as a list of dictionaries."""
    with conn.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute(query, params)
        return cursor.fetchall()

def read_query_dataframe(engine, query: str) -> pd.DataFrame:
    """Returns query results as a Pandas DataFrame."""
    return pd.read_sql(query, engine)

# --- Indexes & Keys ---
@with_pymysql_connection
def create_index(conn, table_name: str, index_name: str, columns: Union[str, List[str]]):
    """Creates an index. Example: create_index(..., 'idx_name', ['col1', 'col2'])"""
    if isinstance(columns, list):
        columns = ", ".join(columns)
    run_query(conn, f"CREATE INDEX {index_name} ON {table_name} ({columns})")

@with_pymysql_connection
def add_foreign_key(conn, table: str, column: str, ref_table: str, ref_column: str, constraint_name: Optional[str] = None):
    """Adds a foreign key constraint."""
    constraint = f"CONSTRAINT {constraint_name}" if constraint_name else ""
    run_query(conn, f"ALTER TABLE {table} ADD {constraint} FOREIGN KEY ({column}) REFERENCES {ref_table}({ref_column})")
```

---

# **2. `mysqlconnector_functions.py` (Auto-Connection Handling)**
```python
import mysql.connector
from sqlalchemy import create_engine
import pandas as pd
from typing import List, Dict, Union, Optional, Callable
from functools import wraps

# --- Connection Handling ---
def get_mysql_connector_engine(host: str, user: str, password: str, database: str):
    """Returns a SQLAlchemy engine for Pandas."""
    return create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}/{database}")

def with_mysql_connector_connection(func: Callable):
    """Decorator to automatically handle mysql.connector connections."""
    @wraps(func)
    def wrapper(host: str, user: str, password: str, database: str, *args, **kwargs):
        conn = mysql.connector.connect(host=host, user=user, password=password, database=database)
        try:
            result = func(conn, *args, **kwargs)
            conn.commit()
            return result
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    return wrapper

# --- Table Operations ---
@with_mysql_connector_connection
def create_table(conn, table_name: str, columns: Dict[str, str], primary_key: Optional[str] = None):
    """Creates a table."""
    columns_sql = ", ".join([f"{col} {dtype}" for col, dtype in columns.items()])
    if primary_key:
        columns_sql += f", PRIMARY KEY ({primary_key})"
    with conn.cursor() as cursor:
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql})")

@with_mysql_connector_connection
def drop_table(conn, table_name: str):
    """Drops a table if it exists."""
    with conn.cursor() as cursor:
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

# --- Query Execution ---
@with_mysql_connector_connection
def run_query(conn, query: str, params: Optional[tuple] = None):
    """Executes INSERT/UPDATE/DELETE queries."""
    with conn.cursor() as cursor:
        cursor.execute(query, params)

@with_mysql_connector_connection
def read_query(conn, query: str, params: Optional[tuple] = None) -> List[tuple]:
    """Returns query results as a list of tuples."""
    with conn.cursor() as cursor:
        cursor.execute(query, params)
        return cursor.fetchall()

@with_mysql_connector_connection
def read_query_dict(conn, query: str, params: Optional[tuple] = None) -> List[dict]:
    """Returns query results as a list of dictionaries."""
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute(query, params)
        return cursor.fetchall()

def read_query_dataframe(engine, query: str) -> pd.DataFrame:
    """Returns query results as a Pandas DataFrame."""
    return pd.read_sql(query, engine)

# --- Indexes & Keys ---
@with_mysql_connector_connection
def create_index(conn, table_name: str, index_name: str, columns: Union[str, List[str]]):
    """Creates an index on specified columns."""
    if isinstance(columns, list):
        columns = ", ".join(columns)
    run_query(conn, f"CREATE INDEX {index_name} ON {table_name} ({columns})")

@with_mysql_connector_connection
def add_foreign_key(conn, table: str, column: str, ref_table: str, ref_column: str, constraint_name: Optional[str] = None):
    """Adds a foreign key constraint."""
    constraint = f"CONSTRAINT {constraint_name}" if constraint_name else ""
    run_query(conn, f"ALTER TABLE {table} ADD {constraint} FOREIGN KEY ({column}) REFERENCES {ref_table}({ref_column})")
```

---

# **Usage Examples**
### **1. PyMySQL (No Manual Connection Handling!)**
```python
import pymysql_functions as pymysql

# Configure once
DB_CONFIG = {
    "host": "localhost",
    "user": "your_user",
    "password": "your_password",
    "database": "your_db"
}

# Auto-connection example (no conn.close() needed!)
pymysql.create_table(**DB_CONFIG, 
    table_name="users",
    columns={"id": "INT AUTO_INCREMENT", "name": "VARCHAR(50)"},
    primary_key="id"
)

# Insert data
pymysql.run_query(**DB_CONFIG, 
    query="INSERT INTO users (name) VALUES ('Alice')"
)

# Fetch results
users = pymysql.read_query_dict(**DB_CONFIG, 
    query="SELECT * FROM users"
)
print(users)
```

### **2. MySQL Connector (Same Clean Syntax)**
```python
import mysqlconnector_functions as mysql

DB_CONFIG = {
    "host": "localhost",
    "user": "your_user",
    "password": "your_password",
    "database": "your_db"
}

# All functions auto-handle connections!
mysql.create_table(**DB_CONFIG,
    table_name="products",
    columns={"id": "INT AUTO_INCREMENT", "name": "TEXT"},
    primary_key="id"
)

# Pandas integration
engine = mysql.get_mysql_connector_engine(**DB_CONFIG)
df = mysql.read_query_dataframe(engine, "SELECT * FROM products")
```

---

# **Key Improvements**
1. **No Manual Connection Handling**  
   - Decorators (`@with_*_connection`) automatically manage:  
     - Connection opening/closing  
     - Commits on success  
     - Rollbacks on errors  

2. **Cleaner API**  
   - Pass database credentials once (e.g., `**DB_CONFIG`)  
   - No more `conn` clutter in your business logic  

3. **Safety**  
   - Guaranteed connection cleanup (even if errors occur)  

4. **Unified Workflow**  
   - Both modules work identically (just switch the import)  

Choose either module based on your preferred driver! 🚀
