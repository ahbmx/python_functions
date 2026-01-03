Below is a **clean, reusable set of helper functions** for interacting with PostgreSQL using **SQLAlchemy (2.0 style)** and **pandas**.
You can drop this into a module like `db_utils.py`.

> Assumes: `sqlalchemy>=1.4`, `psycopg2`, `pandas`

---

## 1. Engine & connection helpers

```python
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
import pandas as pd
from typing import Optional, Iterable, Dict, Any
```

```python
def create_db_engine(
    url: str,
    echo: bool = False,
    pool_size: int = 5,
    max_overflow: int = 10,
) -> Engine:
    """
    Create a SQLAlchemy engine.
    """
    return create_engine(
        url,
        echo=echo,
        pool_size=pool_size,
        max_overflow=max_overflow,
        future=True,
    )
```

---

## 2. Create / drop tables

```python
def create_table(engine: Engine, ddl_sql: str) -> None:
    """
    Create a table using a DDL SQL statement.
    """
    with engine.begin() as conn:
        conn.execute(text(ddl_sql))
```

```python
def drop_table(engine: Engine, table_name: str, cascade: bool = False) -> None:
    sql = f"DROP TABLE IF EXISTS {table_name}"
    if cascade:
        sql += " CASCADE"

    with engine.begin() as conn:
        conn.execute(text(sql))
```

---

## 3. Run arbitrary queries (SELECT / INSERT / UPDATE / DELETE)

```python
def run_query(
    engine: Engine,
    sql: str,
    params: Optional[Dict[str, Any]] = None,
):
    """
    Run any SQL query and return the SQLAlchemy Result.
    """
    with engine.begin() as conn:
        return conn.execute(text(sql), params or {})
```

---

## 4. Build pandas DataFrames from queries

### Best method (recommended)

```python
def query_to_dataframe(
    engine: Engine,
    sql: str,
    params: Optional[Dict[str, Any]] = None,
) -> pd.DataFrame:
    """
    Execute a SELECT query and return a DataFrame.
    """
    with engine.connect() as conn:
        result = conn.execute(text(sql), params or {})
        return pd.DataFrame(result.mappings().all())
```

### Chunked (for large tables)

```python
def query_to_dataframe_chunks(
    engine: Engine,
    sql: str,
    chunksize: int = 10_000,
) -> Iterable[pd.DataFrame]:
    """
    Yield DataFrames in chunks.
    """
    yield from pd.read_sql(sql, engine, chunksize=chunksize)
```

---

## 5. Create indexes

```python
def create_index(
    engine: Engine,
    index_name: str,
    table_name: str,
    columns: list[str],
    unique: bool = False,
) -> None:
    cols = ", ".join(columns)
    unique_sql = "UNIQUE " if unique else ""

    sql = f"""
    CREATE {unique_sql}INDEX IF NOT EXISTS {index_name}
    ON {table_name} ({cols})
    """

    with engine.begin() as conn:
        conn.execute(text(sql))
```

---

## 6. Update values (safe + parameterized)

```python
def update_rows(
    engine: Engine,
    table_name: str,
    set_clause: str,
    where_clause: str,
    params: Dict[str, Any],
) -> int:
    """
    Update rows and return affected row count.

    Example:
    set_clause="status = :status"
    where_clause="id = :id"
    """
    sql = f"""
    UPDATE {table_name}
    SET {set_clause}
    WHERE {where_clause}
    """

    with engine.begin() as conn:
        result = conn.execute(text(sql), params)
        return result.rowcount
```

---

## 7. Upload a pandas DataFrame to Postgres

```python
def upload_dataframe(
    df: pd.DataFrame,
    engine: Engine,
    table_name: str,
    schema: Optional[str] = None,
    if_exists: str = "append",  # 'fail', 'replace', 'append'
    index: bool = False,
    chunksize: int = 5_000,
) -> None:
    df.to_sql(
        table_name,
        engine,
        schema=schema,
        if_exists=if_exists,
        index=index,
        chunksize=chunksize,
        method="multi",
    )
```

---

## 8. Delete rows

```python
def delete_rows(
    engine: Engine,
    table_name: str,
    where_clause: str,
    params: Dict[str, Any],
) -> int:
    sql = f"DELETE FROM {table_name} WHERE {where_clause}"

    with engine.begin() as conn:
        result = conn.execute(text(sql), params)
        return result.rowcount
```

---

## 9. Example usage

```python
engine = create_db_engine(
    "postgresql+psycopg2://user:password@localhost:5432/mydb"
)

create_table(engine, """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name TEXT,
    age INT
)
""")

df = query_to_dataframe(engine, "SELECT * FROM users")

update_rows(
    engine,
    table_name="users",
    set_clause="age = :age",
    where_clause="name = :name",
    params={"age": 18, "name": "Alice"},
)
```

---

## Design principles used

* ✅ SQLAlchemy 2.0–compatible
* ✅ Connection pooling
* ✅ Safe parameter binding
* ✅ pandas-friendly
* ✅ Works for small scripts *and* production code

---

If you want, I can:

* Convert this into a **class-based DB client**
* Add **async (asyncpg + SQLAlchemy async)**
* Add **bulk upserts**
* Add **schema reflection**
* Add **migrations-style helpers**

Just tell me what you’re building.
