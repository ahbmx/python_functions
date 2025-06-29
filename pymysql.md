Below are two Python packages (`mysql_pymysql_helper` and `mysql_connector_helper`) that provide helper functions for **PyMySQL** and **mysql.connector**, respectively. Each package includes methods for:  
✅ **Creating & dropping tables**  
✅ **Running queries (INSERT/UPDATE/DELETE)**  
✅ **Reading queries (SELECT → list/dict/DataFrame)**  
✅ **Creating indexes & keys**  

---

# **1. `mysql_pymysql_helper` (PyMySQL Helper)**
### **Installation**
```bash
pip install pymysql sqlalchemy pandas
```

### **Package Code (`mysql_pymysql_helper.py`)**
```python
import pymysql
from sqlalchemy import create_engine
import pandas as pd
from typing import List, Dict, Union, Optional

class PyMySQLHelper:
    def __init__(self, host: str, user: str, password: str, database: str):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}/{database}")

    def _get_connection(self):
        return pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )

    # --- Table Operations ---
    def create_table(self, table_name: str, columns: Dict[str, str], primary_key: Optional[str] = None):
        """
        Creates a new table.
        
        Args:
            table_name (str): Name of the table.
            columns (Dict[str, str]): Dictionary of column names and types (e.g., {"id": "INT", "name": "VARCHAR(50)"}).
            primary_key (Optional[str]): Primary key column (if any).
        """
        columns_sql = ", ".join([f"{col} {dtype}" for col, dtype in columns.items()])
        if primary_key:
            columns_sql += f", PRIMARY KEY ({primary_key})"
        
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql})"
        self.run_query(query)

    def drop_table(self, table_name: str):
        """Drops a table if it exists."""
        self.run_query(f"DROP TABLE IF EXISTS {table_name}")

    # --- Query Execution ---
    def run_query(self, query: str, params: Optional[tuple] = None) -> None:
        """Executes a query (INSERT/UPDATE/DELETE)."""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                conn.commit()

    def read_query(self, query: str, params: Optional[tuple] = None) -> List[tuple]:
        """Returns query results as a list of tuples."""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()

    def read_query_dict(self, query: str, params: Optional[tuple] = None) -> List[dict]:
        """Returns query results as a list of dictionaries."""
        with self._get_connection() as conn:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()

    def read_query_dataframe(self, query: str) -> pd.DataFrame:
        """Returns query results as a Pandas DataFrame."""
        return pd.read_sql(query, self.engine)

    # --- Indexes & Keys ---
    def create_index(self, table_name: str, index_name: str, columns: Union[str, List[str]]):
        """Creates an index on a table."""
        if isinstance(columns, list):
            columns = ", ".join(columns)
        self.run_query(f"CREATE INDEX {index_name} ON {table_name} ({columns})")

    def add_foreign_key(self, table: str, column: str, ref_table: str, ref_column: str, constraint_name: Optional[str] = None):
        """Adds a foreign key constraint."""
        constraint = f"CONSTRAINT {constraint_name}" if constraint_name else ""
        query = f"ALTER TABLE {table} ADD {constraint} FOREIGN KEY ({column}) REFERENCES {ref_table}({ref_column})"
        self.run_query(query)
```

---

# **2. `mysql_connector_helper` (MySQL Connector Helper)**
### **Installation**
```bash
pip install mysql-connector-python sqlalchemy pandas
```

### **Package Code (`mysql_connector_helper.py`)**
```python
import mysql.connector
from sqlalchemy import create_engine
import pandas as pd
from typing import List, Dict, Union, Optional

class MySQLConnectorHelper:
    def __init__(self, host: str, user: str, password: str, database: str):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}/{database}")

    def _get_connection(self):
        return mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )

    # --- Table Operations ---
    def create_table(self, table_name: str, columns: Dict[str, str], primary_key: Optional[str] = None):
        """Creates a new table."""
        columns_sql = ", ".join([f"{col} {dtype}" for col, dtype in columns.items()])
        if primary_key:
            columns_sql += f", PRIMARY KEY ({primary_key})"
        
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql})"
        self.run_query(query)

    def drop_table(self, table_name: str):
        """Drops a table if it exists."""
        self.run_query(f"DROP TABLE IF EXISTS {table_name}")

    # --- Query Execution ---
    def run_query(self, query: str, params: Optional[tuple] = None) -> None:
        """Executes a query (INSERT/UPDATE/DELETE)."""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                conn.commit()

    def read_query(self, query: str, params: Optional[tuple] = None) -> List[tuple]:
        """Returns query results as a list of tuples."""
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()

    def read_query_dict(self, query: str, params: Optional[tuple] = None) -> List[dict]:
        """Returns query results as a list of dictionaries."""
        with self._get_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()

    def read_query_dataframe(self, query: str) -> pd.DataFrame:
        """Returns query results as a Pandas DataFrame."""
        return pd.read_sql(query, self.engine)

    # --- Indexes & Keys ---
    def create_index(self, table_name: str, index_name: str, columns: Union[str, List[str]]):
        """Creates an index on a table."""
        if isinstance(columns, list):
            columns = ", ".join(columns)
        self.run_query(f"CREATE INDEX {index_name} ON {table_name} ({columns})")

    def add_foreign_key(self, table: str, column: str, ref_table: str, ref_column: str, constraint_name: Optional[str] = None):
        """Adds a foreign key constraint."""
        constraint = f"CONSTRAINT {constraint_name}" if constraint_name else ""
        query = f"ALTER TABLE {table} ADD {constraint} FOREIGN KEY ({column}) REFERENCES {ref_table}({ref_column})"
        self.run_query(query)
```

---

# **Usage Examples**
### **1. Using `PyMySQLHelper`**
```python
from mysql_pymysql_helper import PyMySQLHelper

# Initialize helper
helper = PyMySQLHelper("localhost", "user", "password", "test_db")

# Create a table
helper.create_table(
    table_name="users",
    columns={"id": "INT AUTO_INCREMENT", "name": "VARCHAR(50)", "age": "INT"},
    primary_key="id"
)

# Insert data
helper.run_query("INSERT INTO users (name, age) VALUES ('Alice', 30)")

# Read data
users = helper.read_query_dict("SELECT * FROM users")
print(users)

# Read into DataFrame
df = helper.read_query_dataframe("SELECT * FROM users")
print(df)
```

### **2. Using `MySQLConnectorHelper`**
```python
from mysql_connector_helper import MySQLConnectorHelper

# Initialize helper
helper = MySQLConnectorHelper("localhost", "user", "password", "test_db")

# Create a table
helper.create_table(
    table_name="products",
    columns={"id": "INT AUTO_INCREMENT", "name": "VARCHAR(100)", "price": "FLOAT"},
    primary_key="id"
)

# Add an index
helper.create_index("products", "idx_price", "price")

# Read into DataFrame
df = helper.read_query_dataframe("SELECT * FROM products")
print(df)
```

---

# **Key Features**
| Feature | `PyMySQLHelper` | `MySQLConnectorHelper` |
|---------|----------------|----------------------|
| **Raw SQL Execution** | ✅ | ✅ |
| **Pandas Integration** | ✅ | ✅ |
| **Dictionary Results** | ✅ | ✅ |
| **Index & Foreign Key Support** | ✅ | ✅ |
| **Performance** | Good (Pure Python) | Better (C-optimized) |

Choose the one that fits your project! 🚀
