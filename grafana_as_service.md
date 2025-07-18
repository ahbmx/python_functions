# Creating a Grafana Service on RHEL 8

To run Grafana as a service on RHEL 8 when installed in `/opt/grafana-10.2.0`, follow these steps:

## 1. Create a systemd service file

Create a new service file with your preferred text editor (using `sudo`):

```bash
sudo vi /etc/systemd/system/grafana.service
```

Add the following content (adjust paths if needed):

```ini
[Unit]
Description=Grafana instance
Documentation=https://grafana.com/docs
After=network-online.target

[Service]
User=grafana
Group=grafana
Type=simple
ExecStart=/opt/grafana-10.2.0/bin/grafana-server \
          --config=/opt/grafana-10.2.0/conf/defaults.ini \
          --homepath=/opt/grafana-10.2.0
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

## 2. Create a dedicated Grafana user (recommended)

```bash
sudo useradd -r -s /sbin/nologin grafana
sudo chown -R grafana:grafana /opt/grafana-10.2.0
```

## 3. Reload systemd and enable the service

```bash
sudo systemctl daemon-reload
sudo systemctl enable grafana.service
sudo systemctl start grafana.service
```

## 4. Verify the service is running

```bash
sudo systemctl status grafana.service
```

## Optional configurations:

### If you need custom configurations:
1. Copy the default config:
   ```bash
   sudo cp /opt/grafana-10.2.0/conf/defaults.ini /opt/grafana-10.2.0/conf/custom.ini
   ```
2. Edit the custom.ini file
3. Update the service file to use your custom config

### To open firewall (if needed):
```bash
sudo firewall-cmd --add-port=3000/tcp --permanent
sudo firewall-cmd --reload
```

### To check logs:
```bash
journalctl -u grafana.service -f
```

After completing these steps, Grafana should be running as a service and start automatically on system boot. You can access it at `http://your-server-ip:3000`.
