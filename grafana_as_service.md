# Setting Up Grafana as a Service on RHEL 8.10

To run Grafana as a service on your Red Hat Enterprise Linux 8.10 server, follow these steps:

## 1. Create a Systemd Service File

Create a new service file for Grafana:

```bash
sudo vi /etc/systemd/system/grafana.service
```

Add the following content, adjusting paths as needed:

```ini
[Unit]
Description=Grafana
After=network.target

[Service]
Type=simple
User=grafana
Group=grafana
ExecStart=/opt/grafana-v12.0.2/bin/grafana-server \
          --config=/opt/grafana-v12.0.2/conf/custom.ini \
          --homepath=/opt/grafana-v12.0.2
WorkingDirectory=/opt/grafana-v12.0.2
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## 2. Create Grafana User

Create a dedicated user for Grafana:

```bash
sudo useradd -r -s /bin/false grafana
sudo chown -R grafana:grafana /opt/grafana-v12.0.2
```

## 3. Reload Systemd and Start Grafana

```bash
sudo systemctl daemon-reload
sudo systemctl start grafana
sudo systemctl enable grafana
```

## 4. Verify the Service

Check the status of the service:

```bash
sudo systemctl status grafana
```

View logs if needed:

```bash
journalctl -u grafana -f
```

## 5. (Optional) Firewall Configuration

If you need to access Grafana from another machine:

```bash
sudo firewall-cmd --add-port=3000/tcp --permanent
sudo firewall-cmd --reload
```

## Additional Notes

1. Make sure your `custom.ini` file has the appropriate configurations for your environment.

2. If you want to use the default Grafana port (3000), ensure it's not being used by another service.

3. For production environments, consider:
   - Setting up a reverse proxy (Nginx/Apache)
   - Configuring SSL/TLS
   - Setting up proper database configuration in custom.ini

4. The Grafana web interface should now be accessible at `http://your-server-ip:3000`
