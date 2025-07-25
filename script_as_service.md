I'll update the logging configuration to use rotating logs with a 7-day retention period in the format `%Y_%m_%d_capacity.log`. Here's the modified version:

## Updated Python Script with Rotating Logs (/opt/Storage/capacity.py)

```python
#!/usr/bin/env python3

import time
import schedule
import logging
from logging.handlers import TimedRotatingFileHandler
import signal
from datetime import datetime
import threading
import os

# Global flag for graceful shutdown
running = True

def setup_logging():
    """Configure logging with daily rotation and 7-day retention"""
    log_dir = "/var/log/capacity_monitor"
    log_file = os.path.join(log_dir, "capacity.log")
    
    # Create log directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Create timed rotating file handler
    file_handler = TimedRotatingFileHandler(
        log_file,
        when="midnight",
        interval=1,
        backupCount=7,
        encoding='utf-8'
    )
    file_handler.suffix = "%Y_%m_%d_capacity.log"
    file_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(file_handler)
    
    return logger

logger = setup_logging()

def daily_task():
    """Function to run once per day at midnight"""
    logger.info("Running daily task")
    # Add your daily task logic here
    print("Daily task executed at", datetime.now())

def hourly_task():
    """Function to run at the top of every hour"""
    logger.info("Running hourly task")
    # Add your hourly task logic here
    print("Hourly task executed at", datetime.now())

def twenty_minute_task():
    """Function to run every 20 minutes"""
    logger.info("Running 20-minute task")
    # Add your 20-minute task logic here
    print("20-minute task executed at", datetime.now())

def signal_handler(signum, frame):
    """Handle signals for graceful shutdown"""
    global running
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    running = False

def run_threaded(job_func):
    """Run jobs in a separate thread to prevent overlapping"""
    job_thread = threading.Thread(target=job_func)
    job_thread.start()

def setup_scheduler():
    """Configure the schedule jobs"""
    # Daily at midnight
    schedule.every().day.at("00:00").do(run_threaded, daily_task)
    
    # Every hour at :00
    schedule.every().hour.at(":00").do(run_threaded, hourly_task)
    
    # Every 20 minutes
    schedule.every(20).minutes.do(run_threaded, twenty_minute_task)

    logger.info("Scheduler configured with:")
    for job in schedule.jobs:
        logger.info(f" - {job}")

def main():
    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    logger.info("Starting capacity monitoring service")
    
    # Setup the scheduled jobs
    setup_scheduler()
    
    try:
        while running:
            schedule.run_pending()
            time.sleep(1)
    except Exception as e:
        logger.error(f"Error in main loop: {str(e)}", exc_info=True)
    finally:
        logger.info("Service stopped")

if __name__ == "__main__":
    main()
```

## Key Changes Made:

1. **New Logging Configuration**:
   - Created a dedicated `setup_logging()` function
   - Using `TimedRotatingFileHandler` for daily log rotation
   - Logs will be stored in `/var/log/capacity_monitor/`
   - Main log file will always be `capacity.log`
   - Rotated files will have names like `2023_11_15_capacity.log`

2. **Log Retention**:
   - `backupCount=7` keeps 7 days worth of logs
   - Oldest logs beyond 7 days will be automatically deleted

3. **Directory Creation**:
   - Automatically creates the log directory if it doesn't exist

4. **Improved Log Management**:
   - Better organized log files
   - Easier to find logs for specific dates
   - Automatic cleanup of old logs

## Systemd Service File Update

sudo nano /etc/systemd/system/capacity-monitor.service
sudo systemctl daemon-reload
sudo systemctl enable capacity-monitor.service
sudo systemctl start capacity-monitor.service


sudo systemctl status capacity-monitor.service
journalctl -u capacity-monitor.service -f

sudo pip3 install schedule

You might want to update your systemd service file to ensure proper log directory permissions:

```ini
[Unit]
Description=Storage Capacity Monitoring Service
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/bin/python3 /opt/Storage/capacity.py
Restart=on-failure
RestartSec=5s
# Remove StandardOutput and StandardError since we're handling logs in the script
WorkingDirectory=/opt/Storage
# Ensure log directory has proper permissions
ExecStartPre=/bin/mkdir -p /var/log/capacity_monitor
ExecStartPre=/bin/chown root:root /var/log/capacity_monitor
ExecStartPre=/bin/chmod 755 /var/log/capacity_monitor

[Install]
WantedBy=multi-user.target
```

## Verification

After implementing these changes:
1. Check that logs are being created properly:
   ```bash
   ls -la /var/log/capacity_monitor/
   ```
2. Verify new logs are created daily with the correct naming pattern
3. Confirm that only 7 days of logs are retained
4. Check log contents:
   ```bash
   tail -f /var/log/capacity_monitor/capacity.log
   ```
