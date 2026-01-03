Perfect! Here’s a **step-by-step plan** to get this working with your PostgreSQL database:

---

## **Step 1: Create the materialized view**

Run this query **once** in your database:

```sql
CREATE MATERIALIZED VIEW nbu_bp_summary AS
SELECT
    month_series.year_month,
    COALESCE(b.backup_count, 0) AS backup_count,
    COALESCE(e.expiration_count, 0) AS expiration_count
FROM (
    SELECT TO_CHAR(month::date, 'YYYY-MM') AS year_month
    FROM generate_series(
        (SELECT MIN(backup_date) FROM nbu_bpimagelist),
        (SELECT MAX(GREATEST(backup_date, expiration_date)) FROM nbu_bpimagelist),
        '1 month'::interval
    ) AS month
) AS month_series
LEFT JOIN (
    SELECT TO_CHAR(backup_date, 'YYYY-MM') AS backup_year_month,
           COUNT(*) AS backup_count
    FROM nbu_bpimagelist
    GROUP BY TO_CHAR(backup_date, 'YYYY-MM')
) AS b
ON month_series.year_month = b.backup_year_month
LEFT JOIN (
    SELECT TO_CHAR(expiration_date, 'YYYY-MM') AS expiration_year_month,
           COUNT(*) AS expiration_count
    FROM nbu_bpimagelist
    GROUP BY TO_CHAR(expiration_date, 'YYYY-MM')
) AS e
ON month_series.year_month = e.expiration_year_month
ORDER BY month_series.year_month;
```

✅ This will create the `nbu_bp_summary` materialized view.

---

## **Step 2: Schedule daily refresh**

After your daily data update, refresh the materialized view:

```sql
REFRESH MATERIALIZED VIEW nbu_bp_summary;
```

* You can run this manually for now.
* Later, you can schedule it using **cron**, **pg_cron**, or your ETL tool.

---

## **Step 3: Query the summary**

Example queries:

```sql
-- Show all months
SELECT * FROM nbu_bp_summary ORDER BY year_month;

-- Show recent months
SELECT * FROM nbu_bp_summary
WHERE year_month >= '2025-01'
ORDER BY year_month;
```

* Columns:

  * `year_month` → e.g., `2026-01`
  * `backup_count` → backups that month
  * `expiration_count` → expirations that month

---

## **Step 4: Optional performance boost**

Add indexes on your main table if summaries become slower:

```sql
CREATE INDEX idx_backup_date ON nbu_bpimagelist (backup_date);
CREATE INDEX idx_expiration_date ON nbu_bpimagelist (expiration_date);
```

* Only needed if your table grows much larger in the future.

---

That’s it — once this is set up, **queries are instant** and the summary is updated daily.

If you want, I can also **write a minimal script you can run each night** to refresh the view automatically. This would be a 3–5 line solution you can plug into your nightly ETL.

Do you want me to do that?
