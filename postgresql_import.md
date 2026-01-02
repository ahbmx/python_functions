Perfect! Let’s make a **full plug-and-play Python script** that will:

1. Read your **Parquet file** efficiently.
2. Automatically infer **column types** and map them to PostgreSQL types.
3. Handle **dates** and **booleans** correctly.
4. Drop and recreate the table `nbu_bpimagelist`.
5. Bulk insert all **6 million rows** using **COPY**.
6. Add indexes on `backup_id` and `client_name`.

Here’s the complete ready-to-run script:

```python
import pandas as pd
import psycopg2
from psycopg2 import sql
import tempfile
import os

# ========================
# CONFIGURATION
# ========================
PARQUET_FILE = "big_file.parquet"  # Your parquet file
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "your_dbname"
DB_USER = "your_user"
DB_PASSWORD = "your_password"
TABLE_NAME = "nbu_bpimagelist"
INDEX_COLUMNS = ["backup_id", "client_name"]

# ========================
# 1️⃣ READ PARQUET
# ========================
print("Reading parquet file...")
df = pd.read_parquet(PARQUET_FILE)
print(f"Dataframe loaded: {df.shape[0]} rows, {df.shape[1]} columns")

# ========================
# 2️⃣ MAP PANDAS DTYPE → POSTGRES TYPE
# ========================
dtype_mapping = {}
for col, dt in df.dtypes.items():
    if pd.api.types.is_integer_dtype(dt):
        dtype_mapping[col] = "BIGINT"
    elif pd.api.types.is_float_dtype(dt):
        dtype_mapping[col] = "DOUBLE PRECISION"
    elif pd.api.types.is_bool_dtype(dt):
        dtype_mapping[col] = "BOOLEAN"
    elif pd.api.types.is_datetime64_any_dtype(dt):
        dtype_mapping[col] = "TIMESTAMP"
    elif pd.api.types.is_categorical_dtype(dt) or pd.api.types.is_object_dtype(dt):
        dtype_mapping[col] = "TEXT"
    else:
        dtype_mapping[col] = "TEXT"

print("Column types mapped to PostgreSQL:")
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
# 4️⃣ DROP TABLE IF EXISTS
# ========================
cur.execute(sql.SQL("DROP TABLE IF EXISTS {}").format(sql.Identifier(TABLE_NAME)))
conn.commit()
print(f"Table {TABLE_NAME} dropped if existed.")

# ========================
# 5️⃣ CREATE TABLE
# ========================
columns_sql = ",\n".join([f"{col} {dtype_mapping[col]}" for col in df.columns])
create_table_query = f"CREATE TABLE {TABLE_NAME} (\n{columns_sql}\n)"
cur.execute(create_table_query)
conn.commit()
print(f"Table {TABLE_NAME} created.")

# ========================
# 6️⃣ BULK COPY USING TEMP CSV
# ========================
# COPY is faster than to_sql
print("Saving temporary CSV for COPY...")
with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as tmpfile:
    tmp_csv = tmpfile.name
    df.to_csv(tmp_csv, index=False)

print("Copying data into PostgreSQL...")
with open(tmp_csv, "r") as f:
    cur.copy_expert(f"COPY {TABLE_NAME} FROM STDIN WITH CSV HEADER", f)
conn.commit()
print("Data copied successfully.")

# Delete temporary CSV
os.remove(tmp_csv)

# ========================
# 7️⃣ CREATE INDEXES
# ========================
for col in INDEX_COLUMNS:
    cur.execute(sql.SQL("CREATE INDEX idx_{}_{} ON {} ({})").format(
        sql.Identifier(col),
        sql.Identifier(TABLE_NAME),
        sql.Identifier(TABLE_NAME),
        sql.Identifier(col)
    ))
conn.commit()
print(f"Indexes created on: {', '.join(INDEX_COLUMNS)}")

# ========================
# 8️⃣ CLOSE CONNECTION
# ========================
cur.close()
conn.close()
print("PostgreSQL connection closed. ✅ All done!")
```

---

### **Features of this script**

* Reads **Parquet** directly → no huge memory overhead compared to CSV.
* Automatically maps **pandas types → PostgreSQL types**, including integers, floats, booleans, datetimes, and text.
* Uses **COPY** via a temporary CSV → fastest way to load 6M rows.
* Drops the table if it exists, creates a new one.
* Adds **indexes** on `backup_id` and `client_name` after insert.
* Fully plug-and-play; just update **DB credentials** and file paths.

---

If you want, I can also add **optional progress logging** so you can see how many rows are being processed during the COPY — useful for very large datasets.

Do you want me to add that?
