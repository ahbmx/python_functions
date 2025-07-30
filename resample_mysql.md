Here are the MySQL queries you'll need for your Grafana dashboard, optimized for each visualization type:

### 1. **Candlestick Chart (Daily/Weekly/Monthly Capacity Trends)**
```sql
-- Daily candlestick
SELECT 
    sid,
    DATE(tstamp) AS time,
    MIN(subscribed_capacity_tb) AS low,
    MAX(subscribed_capacity_tb) AS high,
    SUBSTRING_INDEX(GROUP_CONCAT(subscribed_capacity_tb ORDER BY tstamp), ',', 1) AS open,
    SUBSTRING_INDEX(GROUP_CONCAT(subscribed_capacity_tb ORDER BY tstamp DESC), ',', 1) AS close,
    SUM(CASE WHEN daily_change > 0 THEN daily_change ELSE 0 END) AS provisioned,
    SUM(CASE WHEN daily_change < 0 THEN ABS(daily_change) ELSE 0 END) AS recovered
FROM storage_metrics
WHERE sid = '${storage_id}'
  AND tstamp BETWEEN ${__timeFrom()} AND ${__timeTo()}
  AND is_projection = 0
GROUP BY sid, DATE(tstamp);

-- Weekly version (use with Grafana's week grouping)
SELECT 
    sid,
    DATE_SUB(DATE(tstamp), INTERVAL WEEKDAY(tstamp) DAY) AS week_start,
    MIN(subscribed_capacity_tb) AS low,
    MAX(subscribed_capacity_tb) AS high,
    SUBSTRING_INDEX(GROUP_CONCAT(subscribed_capacity_tb ORDER BY tstamp), ',', 1) AS open,
    SUBSTRING_INDEX(GROUP_CONCAT(subscribed_capacity_tb ORDER BY tstamp DESC), ',', 1) AS close
FROM storage_metrics
WHERE sid = '${storage_id}'
GROUP BY sid, YEAR(tstamp), WEEK(tstamp);
```

### 2. **Usage vs Capacity Projection**
```sql
-- Actual vs Projected Usage
SELECT 
    time,
    sid,
    used_cap,
    base_projection,
    subscribed_capacity_tb,
    usable_capacity,
    is_projection,
    provision_notes
FROM storage_metrics
WHERE sid = '${storage_id}'
  AND time BETWEEN ${__timeFrom()} AND DATE_ADD(${__timeTo()}, INTERVAL ${projection_days} DAY)
ORDER BY time;
```

### 3. **Provision/Recovery Heatmap**
```sql
-- Daily Provision/Recovery Heatmap
SELECT 
    sid,
    DATE(tstamp) AS time,
    SUM(provisioned) AS provisioned_tb,
    SUM(recovered) AS recovered_tb
FROM storage_metrics
WHERE tstamp BETWEEN ${__timeFrom()} AND ${__timeTo()}
GROUP BY sid, DATE(tstamp);

-- Weekly Aggregated Version
SELECT 
    sid,
    YEAR(tstamp) AS year,
    WEEK(tstamp) AS week,
    SUM(provisioned) AS provisioned_tb,
    SUM(recovered) AS recovered_tb
FROM storage_metrics
GROUP BY sid, YEAR(tstamp), WEEK(tstamp);
```

### 4. **Future Provisions Calendar**
```sql
-- Scheduled Provisions
SELECT 
    time AS start_time,
    DATE_ADD(time, INTERVAL 1 DAY) AS end_time,
    sid,
    CONCAT(provision_notes, ' (', ROUND(provision_impact,2), 'TB)') AS text,
    CASE 
        WHEN provision_impact > 0 THEN '#7EB26D' 
        ELSE '#EAB839' 
    END AS color
FROM storage_metrics
WHERE provision_notes != ''
  AND time > NOW()
ORDER BY time;
```

### 5. **Capacity Health Status**
```sql
-- Current Utilization
SELECT 
    sid,
    usable_capacity,
    used_cap,
    ROUND((used_cap/usable_capacity)*100, 2) AS utilization_pct,
    CASE 
        WHEN (used_cap/usable_capacity) < 0.7 THEN 'OK'
        WHEN (used_cap/usable_capacity) < 0.9 THEN 'WARNING'
        ELSE 'CRITICAL'
    END AS status
FROM storage_metrics
WHERE sid = '${storage_id}'
  AND is_projection = 0
  AND time = (SELECT MAX(time) FROM storage_metrics WHERE sid = '${storage_id}');

-- Projected Days Until Full
WITH projection AS (
    SELECT 
        time,
        used_cap,
        usable_capacity
    FROM storage_metrics
    WHERE sid = '${storage_id}'
      AND is_projection = 1
      AND time > NOW()
    ORDER BY time
    LIMIT 30
)
SELECT 
    MIN(DATEDIFF(time, NOW())) AS days_until_full
FROM projection
WHERE used_cap >= usable_capacity;
```

### 6. **Alert Queries**
```sql
-- 90% Capacity Alert
SELECT 
    time,
    sid,
    used_cap,
    usable_capacity,
    (used_cap/usable_capacity)*100 AS utilization_pct
FROM storage_metrics
WHERE (used_cap/usable_capacity) > 0.9
  AND is_projection = 0
ORDER BY time DESC
LIMIT 1;

-- Future Provision Impact Alert
SELECT 
    time,
    sid,
    provision_impact
FROM storage_metrics
WHERE provision_impact > 500  -- Large provision threshold
  AND time > NOW()
ORDER BY time;
```

### Optimization Tips:

1. **Indexing Recommendations**:
   ```sql
   CREATE INDEX idx_storage_metrics_sid_time ON storage_metrics(sid, time);
   CREATE INDEX idx_storage_metrics_projection ON storage_metrics(is_projection, time);
   ```

2. **Grafana Variables**:
   ```sql
   -- For $storage_id variable
   SELECT DISTINCT sid FROM storage_metrics ORDER BY sid;
   
   -- For $projection_days variable
   SELECT 30 AS days UNION SELECT 60 UNION SELECT 90;
   ```

3. **Time Range Macros**:
   - Use `${__timeFrom()}` and `${__timeTo()}` for dashboard time ranges
   - For projections: `DATE_ADD(${__timeTo()}, INTERVAL ${projection_days} DAY)`

4. **Caching**:
   ```sql
   -- Daily pre-aggregation
   CREATE TABLE daily_aggregates AS
   SELECT 
       sid,
       DATE(tstamp) AS day,
       AVG(used_cap) AS avg_used_cap,
       SUM(provisioned) AS total_provisioned
   FROM storage_metrics
   GROUP BY sid, DATE(tstamp);
   ```

These queries are designed to work with Grafana's time range variables and template variables while providing optimal performance for your dashboard visualizations.
