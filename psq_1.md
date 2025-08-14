# PostgreSQL Database Creation Script

Here's a comprehensive script to create 6 databases with read-only and read-write users, along with schema setup and pg_hba.conf configuration instructions.

## Database Creation Script

```sql
-- Create databases and users for storage infrastructure
CREATE DATABASE storage_infra_db;
\c storage_infra_db
CREATE SCHEMA storage_infra_schema;
CREATE ROLE storage_infra_rw WITH LOGIN PASSWORD 'secure_password_rw';
CREATE ROLE storage_infra_ro WITH LOGIN PASSWORD 'secure_password_ro';
ALTER DATABASE storage_infra_db OWNER TO storage_infra_rw;
ALTER SCHEMA storage_infra_schema OWNER TO storage_infra_rw;
GRANT ALL PRIVILEGES ON DATABASE storage_infra_db TO storage_infra_rw;
GRANT ALL PRIVILEGES ON SCHEMA storage_infra_schema TO storage_infra_rw;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA storage_infra_schema TO storage_infra_rw;
ALTER ROLE storage_infra_rw SET search_path TO storage_infra_schema;
GRANT CONNECT ON DATABASE storage_infra_db TO storage_infra_ro;
GRANT USAGE ON SCHEMA storage_infra_schema TO storage_infra_ro;
GRANT SELECT ON ALL TABLES IN SCHEMA storage_infra_schema TO storage_infra_ro;
ALTER DEFAULT PRIVILEGES IN SCHEMA storage_infra_schema GRANT SELECT ON TABLES TO storage_infra_ro;

-- Create databases and users for NAS
CREATE DATABASE nas_db;
\c nas_db
CREATE SCHEMA nas_schema;
CREATE ROLE nas_rw WITH LOGIN PASSWORD 'secure_password_rw';
CREATE ROLE nas_ro WITH LOGIN PASSWORD 'secure_password_ro';
ALTER DATABASE nas_db OWNER TO nas_rw;
ALTER SCHEMA nas_schema OWNER TO nas_rw;
GRANT ALL PRIVILEGES ON DATABASE nas_db TO nas_rw;
GRANT ALL PRIVILEGES ON SCHEMA nas_schema TO nas_rw;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA nas_schema TO nas_rw;
ALTER ROLE nas_rw SET search_path TO nas_schema;
GRANT CONNECT ON DATABASE nas_db TO nas_ro;
GRANT USAGE ON SCHEMA nas_schema TO nas_ro;
GRANT SELECT ON ALL TABLES IN SCHEMA nas_schema TO nas_ro;
ALTER DEFAULT PRIVILEGES IN SCHEMA nas_schema GRANT SELECT ON TABLES TO nas_ro;

-- Create databases and users for SAN
CREATE DATABASE san_db;
\c san_db
CREATE SCHEMA san_schema;
CREATE ROLE san_rw WITH LOGIN PASSWORD 'secure_password_rw';
CREATE ROLE san_ro WITH LOGIN PASSWORD 'secure_password_ro';
ALTER DATABASE san_db OWNER TO san_rw;
ALTER SCHEMA san_schema OWNER TO san_rw;
GRANT ALL PRIVILEGES ON DATABASE san_db TO san_rw;
GRANT ALL PRIVILEGES ON SCHEMA san_schema TO san_rw;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA san_schema TO san_rw;
ALTER ROLE san_rw SET search_path TO san_schema;
GRANT CONNECT ON DATABASE san_db TO san_ro;
GRANT USAGE ON SCHEMA san_schema TO san_ro;
GRANT SELECT ON ALL TABLES IN SCHEMA san_schema TO san_ro;
ALTER DEFAULT PRIVILEGES IN SCHEMA san_schema GRANT SELECT ON TABLES TO san_ro;

-- Create databases and users for DPS
CREATE DATABASE dps_db;
\c dps_db
CREATE SCHEMA dps_schema;
CREATE ROLE dps_rw WITH LOGIN PASSWORD 'secure_password_rw';
CREATE ROLE dps_ro WITH LOGIN PASSWORD 'secure_password_ro';
ALTER DATABASE dps_db OWNER TO dps_rw;
ALTER SCHEMA dps_schema OWNER TO dps_rw;
GRANT ALL PRIVILEGES ON DATABASE dps_db TO dps_rw;
GRANT ALL PRIVILEGES ON SCHEMA dps_schema TO dps_rw;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA dps_schema TO dps_rw;
ALTER ROLE dps_rw SET search_path TO dps_schema;
GRANT CONNECT ON DATABASE dps_db TO dps_ro;
GRANT USAGE ON SCHEMA dps_schema TO dps_ro;
GRANT SELECT ON ALL TABLES IN SCHEMA dps_schema TO dps_ro;
ALTER DEFAULT PRIVILEGES IN SCHEMA dps_schema GRANT SELECT ON TABLES TO dps_ro;

-- Create databases and users for Grafana Production
CREATE DATABASE grafana_prod_db;
\c grafana_prod_db
CREATE SCHEMA grafana_prod_schema;
CREATE ROLE grafana_prod_rw WITH LOGIN PASSWORD 'secure_password_rw';
CREATE ROLE grafana_prod_ro WITH LOGIN PASSWORD 'secure_password_ro';
ALTER DATABASE grafana_prod_db OWNER TO grafana_prod_rw;
ALTER SCHEMA grafana_prod_schema OWNER TO grafana_prod_rw;
GRANT ALL PRIVILEGES ON DATABASE grafana_prod_db TO grafana_prod_rw;
GRANT ALL PRIVILEGES ON SCHEMA grafana_prod_schema TO grafana_prod_rw;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA grafana_prod_schema TO grafana_prod_rw;
ALTER ROLE grafana_prod_rw SET search_path TO grafana_prod_schema;
GRANT CONNECT ON DATABASE grafana_prod_db TO grafana_prod_ro;
GRANT USAGE ON SCHEMA grafana_prod_schema TO grafana_prod_ro;
GRANT SELECT ON ALL TABLES IN SCHEMA grafana_prod_schema TO grafana_prod_ro;
ALTER DEFAULT PRIVILEGES IN SCHEMA grafana_prod_schema GRANT SELECT ON TABLES TO grafana_prod_ro;

-- Create databases and users for Grafana DRP
CREATE DATABASE grafana_drp_db;
\c grafana_drp_db
CREATE SCHEMA grafana_drp_schema;
CREATE ROLE grafana_drp_rw WITH LOGIN PASSWORD 'secure_password_rw';
CREATE ROLE grafana_drp_ro WITH LOGIN PASSWORD 'secure_password_ro';
ALTER DATABASE grafana_drp_db OWNER TO grafana_drp_rw;
ALTER SCHEMA grafana_drp_schema OWNER TO grafana_drp_rw;
GRANT ALL PRIVILEGES ON DATABASE grafana_drp_db TO grafana_drp_rw;
GRANT ALL PRIVILEGES ON SCHEMA grafana_drp_schema TO grafana_drp_rw;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA grafana_drp_schema TO grafana_drp_rw;
ALTER ROLE grafana_drp_rw SET search_path TO grafana_drp_schema;
GRANT CONNECT ON DATABASE grafana_drp_db TO grafana_drp_ro;
GRANT USAGE ON SCHEMA grafana_drp_schema TO grafana_drp_ro;
GRANT SELECT ON ALL TABLES IN SCHEMA grafana_drp_schema TO grafana_drp_ro;
ALTER DEFAULT PRIVILEGES IN SCHEMA grafana_drp_schema GRANT SELECT ON TABLES TO grafana_drp_ro;

-- Create databases and users for Playground
CREATE DATABASE playground_db;
\c playground_db
CREATE SCHEMA playground_schema;
CREATE ROLE playground_rw WITH LOGIN PASSWORD 'secure_password_rw';
CREATE ROLE playground_ro WITH LOGIN PASSWORD 'secure_password_ro';
ALTER DATABASE playground_db OWNER TO playground_rw;
ALTER SCHEMA playground_schema OWNER TO playground_rw;
GRANT ALL PRIVILEGES ON DATABASE playground_db TO playground_rw;
GRANT ALL PRIVILEGES ON SCHEMA playground_schema TO playground_rw;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA playground_schema TO playground_rw;
ALTER ROLE playground_rw SET search_path TO playground_schema;
GRANT CONNECT ON DATABASE playground_db TO playground_ro;
GRANT USAGE ON SCHEMA playground_schema TO playground_ro;
GRANT SELECT ON ALL TABLES IN SCHEMA playground_schema TO playground_ro;
ALTER DEFAULT PRIVILEGES IN SCHEMA playground_schema GRANT SELECT ON TABLES TO playground_ro;
```

## pg_hba.conf Configuration

To allow connections from anywhere to both user types, you'll need to modify the PostgreSQL host-based authentication file (pg_hba.conf). Here's how:

1. Locate your pg_hba.conf file (typically in `/etc/postgresql/17/main/pg_hba.conf` or `/var/lib/pgsql/17/data/pg_hba.conf`)

2. Add these lines to the file (replace "17" with your actual PostgreSQL version if different):

```
# Allow all IPv4 connections with password
host    storage_infra_db    storage_infra_rw    0.0.0.0/0    scram-sha-256
host    storage_infra_db    storage_infra_ro    0.0.0.0/0    scram-sha-256

host    nas_db             nas_rw              0.0.0.0/0    scram-sha-256
host    nas_db             nas_ro              0.0.0.0/0    scram-sha-256

host    san_db             san_rw              0.0.0.0/0    scram-sha-256
host    san_db             san_ro              0.0.0.0/0    scram-sha-256

host    dps_db             dps_rw              0.0.0.0/0    scram-sha-256
host    dps_db             dps_ro              0.0.0.0/0    scram-sha-256

host    grafana_prod_db    grafana_prod_rw     0.0.0.0/0    scram-sha-256
host    grafana_prod_db    grafana_prod_ro     0.0.0.0/0    scram-sha-256

host    grafana_drp_db     grafana_drp_rw      0.0.0.0/0    scram-sha-256
host    grafana_drp_db     grafana_drp_ro      0.0.0.0/0    scram-sha-256

host    playground_db      playground_rw        0.0.0.0/0    scram-sha-256
host    playground_db      playground_ro        0.0.0.0/0    scram-sha-256

# Allow all IPv6 connections with password
host    storage_infra_db    storage_infra_rw    ::/0    scram-sha-256
host    storage_infra_db    storage_infra_ro    ::/0    scram-sha-256

host    nas_db             nas_rw              ::/0    scram-sha-256
host    nas_db             nas_ro              ::/0    scram-sha-256

host    san_db             san_rw              ::/0    scram-sha-256
host    san_db             san_ro              ::/0    scram-sha-256

host    dps_db             dps_rw              ::/0    scram-sha-256
host    dps_db             dps_ro              ::/0    scram-sha-256

host    grafana_prod_db    grafana_prod_rw     ::/0    scram-sha-256
host    grafana_prod_db    grafana_prod_ro     ::/0    scram-sha-256

host    grafana_drp_db     grafana_drp_rw      ::/0    scram-sha-256
host    grafana_drp_db     grafana_drp_ro      ::/0    scram-sha-256

host    playground_db      playground_rw        ::/0    scram-sha-256
host    playground_db      playground_ro        ::/0    scram-sha-256
```

3. After modifying pg_hba.conf, you'll need to reload PostgreSQL for the changes to take effect:

```bash
sudo systemctl reload postgresql@17-main

Reload PostgreSQL: SELECT pg_reload_conf();

```

## Important Security Notes

1. Replace 'secure_password_rw' and 'secure_password_ro' with strong, unique passwords for each user.

2. Allowing connections from anywhere (0.0.0.0/0) is a security risk. For production environments, consider restricting to specific IP ranges.

3. The ALTER DEFAULT PRIVILEGES commands ensure that future tables created will automatically have the correct permissions for read-only users.

4. You may also need to configure PostgreSQL's listen_addresses in postgresql.conf to accept remote connections.
