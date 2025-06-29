Here are the simplified versions of both modules **without typing** and with **hardcoded credentials**. Just replace the placeholder values (`your_username`, `your_password`, etc.) with your actual database credentials.

---

# **1. `pymysql_helpers.py` (PyMySQL with Hardcoded Credentials)**
```python
import pymysql
from sqlalchemy import create_engine
import pandas as pd
from functools import wraps

# Hardcoded credentials (REPLACE THESE!)
HOST = "localhost"
USER = "your_username"
PASSWORD = "your_password"
DATABASE = "your_database"

# SQLAlchemy engine for Pandas
engine = create_engine(f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}/{DATABASE}")

# Decorator to auto-handle connections
def with_connection(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        conn = pymysql.connect(host=HOST, user=USER, password=PASSWORD, database=DATABASE)
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
@with_connection
def create_table(conn, table_name, columns, primary_key=None):
    columns_sql = ", ".join([f"{col} {dtype}" for col, dtype in columns.items()])
    if primary_key:
        columns_sql += f", PRIMARY KEY ({primary_key})"
    with conn.cursor() as cursor:
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql})")

@with_connection
def drop_table(conn, table_name):
    with conn.cursor() as cursor:
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

# --- Query Execution ---
@with_connection
def run_query(conn, query, params=None):
    with conn.cursor() as cursor:
        cursor.execute(query, params)

@with_connection
def read_query(conn, query, params=None):
    with conn.cursor() as cursor:
        cursor.execute(query, params)
        return cursor.fetchall()

@with_connection
def read_query_dict(conn, query, params=None):
    with conn.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute(query, params)
        return cursor.fetchall()

def read_query_dataframe(query):
    return pd.read_sql(query, engine)

# --- Indexes & Keys ---
@with_connection
def create_index(conn, table_name, index_name, columns):
    if isinstance(columns, list):
        columns = ", ".join(columns)
    run_query(conn, f"CREATE INDEX {index_name} ON {table_name} ({columns})")

@with_connection
def add_foreign_key(conn, table, column, ref_table, ref_column, constraint_name=None):
    constraint = f"CONSTRAINT {constraint_name}" if constraint_name else ""
    run_query(conn, f"ALTER TABLE {table} ADD {constraint} FOREIGN KEY ({column}) REFERENCES {ref_table}({ref_column})")
```

---

# **2. `mysqlconnector_helpers.py` (MySQL Connector with Hardcoded Credentials)**
```python
import mysql.connector
from sqlalchemy import create_engine
import pandas as pd
from functools import wraps

# Hardcoded credentials (REPLACE THESE!)
HOST = "localhost"
USER = "your_username"
PASSWORD = "your_password"
DATABASE = "your_database"

# SQLAlchemy engine for Pandas
engine = create_engine(f"mysql+mysqlconnector://{USER}:{PASSWORD}@{HOST}/{DATABASE}")

# Decorator to auto-handle connections
def with_connection(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        conn = mysql.connector.connect(host=HOST, user=USER, password=PASSWORD, database=DATABASE)
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
@with_connection
def create_table(conn, table_name, columns, primary_key=None):
    columns_sql = ", ".join([f"{col} {dtype}" for col, dtype in columns.items()])
    if primary_key:
        columns_sql += f", PRIMARY KEY ({primary_key})"
    with conn.cursor() as cursor:
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql})")

@with_connection
def drop_table(conn, table_name):
    with conn.cursor() as cursor:
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

# --- Query Execution ---
@with_connection
def run_query(conn, query, params=None):
    with conn.cursor() as cursor:
        cursor.execute(query, params)

@with_connection
def read_query(conn, query, params=None):
    with conn.cursor() as cursor:
        cursor.execute(query, params)
        return cursor.fetchall()

@with_connection
def read_query_dict(conn, query, params=None):
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute(query, params)
        return cursor.fetchall()

def read_query_dataframe(query):
    return pd.read_sql(query, engine)

# --- Indexes & Keys ---
@with_connection
def create_index(conn, table_name, index_name, columns):
    if isinstance(columns, list):
        columns = ", ".join(columns)
    run_query(conn, f"CREATE INDEX {index_name} ON {table_name} ({columns})")

@with_connection
def add_foreign_key(conn, table, column, ref_table, ref_column, constraint_name=None):
    constraint = f"CONSTRAINT {constraint_name}" if constraint_name else ""
    run_query(conn, f"ALTER TABLE {table} ADD {constraint} FOREIGN KEY ({column}) REFERENCES {ref_table}({ref_column})")
```

---

# **Usage Examples**
### **1. PyMySQL (No Credentials Needed in Calls!)**
```python
import pymysql_helpers as db

# Create a table
db.create_table(
    table_name="users",
    columns={"id": "INT AUTO_INCREMENT", "name": "VARCHAR(50)"},
    primary_key="id"
)

# Insert data
db.run_query("INSERT INTO users (name) VALUES ('Alice')")

# Fetch data
users = db.read_query_dict("SELECT * FROM users")
print(users)

# Pandas DataFrame
df = db.read_query_dataframe("SELECT * FROM users")
print(df)
```

### **2. MySQL Connector (Identical API)**
```python
import mysqlconnector_helpers as db

# All functions work the same way!
db.create_table(
    table_name="products",
    columns={"id": "INT AUTO_INCREMENT", "name": "TEXT"},
    primary_key="id"
)

df = db.read_query_dataframe("SELECT * FROM products")
```

---

# **Key Features**
1. **No Credentials in Function Calls**  
   - Credentials are hardcoded at the top of each module.  

2. **Auto-Connection Handling**  
   - Decorators manage connections (open/close/commit/rollback).  

3. **Simplified API**  
   - No `conn` or `engine` passing required.  

4. **Drop-in Replacement**  
   - Switch between PyMySQL and MySQL Connector by changing the import.  

5. **No `typing` Module**  
   - Removed all type hints for compatibility with older Python versions.  

Replace the credentials at the top of each file, and you’re ready to go! 🚀
