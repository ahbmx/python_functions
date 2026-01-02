Excellent choice — **UNLOGGED tables** are one of the biggest wins for bulk loads like this.

Below is the **full updated script**, with **UNLOGGED table support added**, while keeping:

✅ Parquet input
✅ COPY bulk load
✅ `synchronous_commit = OFF`
✅ Indexes after load
✅ Timing + throughput stats
✅ No deprecated pandas APIs

---

## ⚠️ Important note about UNLOGGED tables (read once)

* **Much faster inserts** (no WAL logging)
* **Data is lost if PostgreSQL crashes or restarts**
* Perfect for **ETL / rebuildable tables**
* You can later convert it to a logged table if needed

---

## ✅ Full ready-to-run script (UNLOGGED enabled)

```python
import pandas as pd
import psycopg2
from psycopg2 import sql
import tempfile
import os
import time
from pandas.api.types import (
    is_integer_dtype,
    is_float_dtype,
    is_bool_dtype,
    is_datetime64_any_dtype,
)

# ========================
# CONFIGURATION
# ========================
PARQUET_FILE = "big_file.parquet"
TABLE_NAME = "nbu_bpimagelist"
INDEX_COLUMNS = ["backup_id", "client_name"]

DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "your_dbname"
DB_USER = "your_user"
DB_PASSWORD = "your_password"

# ========================
# TIMER START
# ========================
overall_start = time.time()

# ========================
# 1️⃣ READ PARQUET
# ========================
print("Reading parquet file...")
read_start = time.time()
df = pd.read_parquet(PARQUET_FILE)
read_time = time.time() - read_start

row_count = len(df)
print(f"Loaded {row_count:,} rows in {read_time:.2f}s")

# ========================
# 2️⃣ MAP PANDAS → POSTGRES TYPES
# ========================
dtype_mapping = {}

for col, dt in df.dtypes.items():
    if is_integer_dtype(dt):
        dtype_mapping[col] = "BIGINT"
    elif is_float_dtype(dt):
        dtype_mapping[col] = "DOUBLE PRECISION"
    elif is_bool_dtype(dt):
        dtype_mapping[col] = "BOOLEAN"
    elif is_datetime64_any_dtype(dt):
        dtype_mapping[col] = "TIMESTAMP"
    elif isinstance(dt, pd.CategoricalDtype):
        dtype_mapping[col] = "TEXT"
    else:
        dtype_mapping[col] = "TEXT"

print("PostgreSQL column mapping:")
for k, v in dtype_mapping.items():
    print(f"  {k}: {v}")

# ========================
# 3️⃣ CONNECT TO POSTGRES
# ========================
conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)
cur = conn.cursor()

# ========================
# 4️⃣ PERFORMANCE TUNING
# ========================
print("Applying performance settings...")
cur.execute("SET synchronous_commit = OFF;")
conn.commit()

# ========================
# 5️⃣ DROP + CREATE UNLOGGED TABLE
# ========================
print("Dropping existing table (if any)...")
cur.execute(sql.SQL("DROP TABLE IF EXISTS {}").format(sql.Identifier(TABLE_NAME)))

columns_sql = ",\n".join(
    f"{col} {dtype_mapping[col]}" for col in df.columns
)

create_table_sql = f"""
CREATE UNLOGGED TABLE {TABLE_NAME} (
{columns_sql}
)
"""
cur.execute(create_table_sql)
conn.commit()
print("UNLOGGED table created.")

# ========================
# 6️⃣ COPY DATA (FASTEST)
# ========================
print("Preparing temporary CSV for COPY...")
with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as tmp:
    tmp_csv = tmp.name
    df.to_csv(tmp_csv, index=False)

print("Starting COPY...")
copy_start = time.time()

with open(tmp_csv, "r") as f:
    cur.copy_expert(
        f"COPY {TABLE_NAME} FROM STDIN WITH CSV HEADER",
        f
    )

conn.commit()
copy_time = time.time() - copy_start
os.remove(tmp_csv)

rows_per_sec = row_count / copy_time

print(f"COPY completed in {copy_time:.2f}s")
print(f"Throughput: {rows_per_sec:,.0f} rows/sec")

# ========================
# 7️⃣ CREATE INDEXES
# ========================
print("Creating indexes...")
index_start = time.time()

for col in INDEX_COLUMNS:
    cur.execute(
        sql.SQL("CREATE INDEX idx_{}_{} ON {} ({})").format(
            sql.Identifier(col),
            sql.Identifier(TABLE_NAME),
            sql.Identifier(TABLE_NAME),
            sql.Identifier(col),
        )
    )

conn.commit()
index_time = time.time() - index_start
print(f"Indexes created in {index_time:.2f}s")

# ========================
# 8️⃣ RESET SETTINGS
# ========================
cur.execute("SET synchronous_commit = ON;")
conn.commit()

# ========================
# 9️⃣ CLEANUP
# ========================
cur.close()
conn.close()

overall_time = time.time() - overall_start

print("\n===== LOAD SUMMARY =====")
print(f"Rows loaded      : {row_count:,}")
print(f"Read time        : {read_time:.2f}s")
print(f"COPY time        : {copy_time:.2f}s")
print(f"Index time       : {index_time:.2f}s")
print(f"Total time       : {overall_time:.2f}s")
print("========================")
print("✅ Done.")
```

---

## 🚀 Expected speed improvement

Compared to a normal logged table:

| Technique                  | Speed gain |
| -------------------------- | ---------- |
| COPY vs inserts            | ~10×       |
| `synchronous_commit = OFF` | ~1.5×      |
| **UNLOGGED table**         | **2–3×**   |
| Index after load           | ~2×        |

For **6 million rows**, this often means:
**single-digit seconds for COPY** on a decent server.

---

## 🔁 Optional next step (safe persistence)

If you want durability **after** loading:

```sql
ALTER TABLE nbu_bpimagelist SET LOGGED;
```

* Converts it to a normal table
* One-time WAL cost
* Keeps your fast load + safe long-term storage

---

If you want next-level performance, I can also:

* Remove the temp CSV and **stream Parquet → COPY**
* Use **UNLOGGED + parallel indexes**
* Partition the table by date or client
* Add VACUUM/ANALYZE tuning

Just tell me 👍
