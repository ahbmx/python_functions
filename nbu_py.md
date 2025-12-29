Here's the complete NetBackup observability script converted to Python without using classes:

```python
#!/usr/bin/env python3
"""
NetBackup 9.1 Environment Observability & Capacity Script
Run from Linux Media Server
Version: 3.0 - Comprehensive Environment Summary
"""

import os
import sys
import subprocess
import json
import csv
import re
from datetime import datetime, timedelta
import time
import shutil
import logging
from collections import defaultdict, Counter
import math

# Configuration
OUTPUT_DIR = "/tmp/netbackup_monitor"
LOG_FILE = "/var/log/nb_environment_monitor.log"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
REPORT_FILE = f"{OUTPUT_DIR}/nb_env_report_{TIMESTAMP}.txt"
JSON_FILE = f"{OUTPUT_DIR}/nb_env_metrics_{TIMESTAMP}.json"
ALERT_FILE = f"{OUTPUT_DIR}/nb_alerts_{TIMESTAMP}.txt"

# NetBackup paths
NB_BIN = "/usr/openv/netbackup/bin/admincmd"
NB_BIN_BIN = "/usr/openv/netbackup/bin"

# Global variables
total_alerts = 0
overall_status = "UNKNOWN"
failed_jobs_temp = ""
jobs_raw_file = ""
metrics_data = {}
command_summary = []

# Setup logging
def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )

def log_message(message):
    """Log a message"""
    logging.info(message)

def run_command(cmd, description=""):
    """
    Run a shell command and return output
    Also record command for summary
    """
    global command_summary
    
    if description:
        command_summary.append(f"{description}: {cmd}")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        log_message(f"Command timed out: {cmd}")
        return ""
    except Exception as e:
        log_message(f"Error running command {cmd}: {e}")
        return ""

def create_output_dir():
    """Create output directory if it doesn't exist"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

def init_json():
    """Initialize JSON file"""
    global metrics_data
    metrics_data = {
        "timestamp": TIMESTAMP,
        "environment": "NetBackup 9.1",
        "monitoring_server": run_command("hostname", "Get hostname"),
        "metrics": {}
    }

def add_json_metric(metric_type, metric_name, value, unit, status, details=""):
    """Add a metric to JSON data"""
    metric_key = f"{metric_type}_{metric_name}"
    metrics_data["metrics"][metric_key] = {
        "value": str(value),
        "unit": unit,
        "status": status,
        "details": details
    }

def finalize_json():
    """Finalize and write JSON file"""
    metrics_data["summary"] = {
        "total_alerts": total_alerts,
        "status": overall_status
    }
    
    with open(JSON_FILE, 'w') as f:
        json.dump(metrics_data, f, indent=2)

def get_status_description(status_code):
    """Get description for NetBackup status code"""
    status_descriptions = {
        "0": "Success",
        "1": "Job started but did not complete",
        "2": "Backup suspended",
        "3": "Backup in progress",
        "4": "Restore in progress",
        "5": "Verify in progress",
        "6": "Archive in progress",
        "7": "Import in progress",
        "8": "Catalog backup in progress",
        "9": "Duplicate in progress",
        "10": "Snapshot in progress",
        "11": "Backup done with warnings",
        "12": "Backup canceled by user",
        "13": "Backup canceled by policy",
        "14": "Backup deferred",
        "15": "Backup queued",
        "23": "Client write failed",
        "25": "Client connection failed",
        "40": "Media write failed",
        "41": "Media read failed",
        "42": "Media not available",
        "82": "Backup window expired",
        "84": "Policy disabled",
        "96": "Client resource unavailable",
        "155": "Storage unit full",
        "191": "Client not found or not responding",
        "203": "Disk pool out of space"
    }
    
    return status_descriptions.get(str(status_code), f"Unknown error (code: {status_code})")

def check_environment_status(report_file):
    """Check NetBackup environment status"""
    log_message("Checking NetBackup environment status...")
    
    with open(report_file, 'a') as f:
        f.write("=== NETBACKUP ENVIRONMENT OVERVIEW ===\n")
    
    # Get NetBackup version
    version_output = run_command(f"{NB_BIN}/bpgetconfig", "Get NetBackup version")
    if version_output:
        version_line = ""
        for line in version_output.split('\n'):
            if 'version' in line.lower():
                version_line = line.strip()
                break
        
        with open(report_file, 'a') as f:
            f.write(f"NetBackup Version: {version_line}\n")
    
    # Get master server name
    bpconf_path = "/usr/openv/netbackup/bp.conf"
    master_server = "NOT FOUND"
    if os.path.exists(bpconf_path):
        with open(bpconf_path, 'r') as conf_file:
            for line in conf_file:
                if 'server' in line.lower():
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        master_server = parts[1]
                    break
    
    with open(report_file, 'a') as f:
        f.write(f"Master Server: {master_server}\n\n")
    
    # Get list of media servers
    with open(report_file, 'a') as f:
        f.write("=== MEDIA SERVERS ===\n")
    
    media_servers = run_command(f"{NB_BIN}/nbgetconfig -L -m", "Get media servers list")
    if media_servers:
        media_server_count = 0
        for line in media_servers.split('\n'):
            if 'Media Server' in line:
                media_server_count += 1
                with open(report_file, 'a') as f:
                    f.write(f"{line}\n")
        
        add_json_metric("servers", "media_server_count", media_server_count, "count", "info")
    
    with open(report_file, 'a') as f:
        f.write("\n")

def summarize_policies_detailed(report_file):
    """Summarize all policies with details"""
    log_message("Generating detailed policy summary...")
    
    with open(report_file, 'a') as f:
        f.write("=== DETAILED POLICY SUMMARY ===\n")
    
    if os.path.exists(f"{NB_BIN}/bppllist"):
        # Create policy summary file
        policy_summary_file = f"{OUTPUT_DIR}/policy_summary_{TIMESTAMP}.csv"
        policy_detail_file = f"{OUTPUT_DIR}/policy_details_{TIMESTAMP}.txt"
        
        with open(policy_summary_file, 'w') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["policy_name", "policy_type", "active_status", "client_count", 
                               "schedule_count", "retention_days", "last_backup"])
        
        with open(policy_detail_file, 'w') as detail_file:
            detail_file.write("POLICY DETAILS:\n")
            detail_file.write("================\n")
        
        # Get all policies
        policies_output = run_command(f"{NB_BIN}/bppllist", "List all policies")
        policy_list = []
        for line in policies_output.split('\n'):
            if 'Policy Name:' in line:
                parts = line.split()
                if len(parts) >= 3:
                    policy_list.append(parts[2])
        
        total_policies = len(policy_list)
        
        with open(report_file, 'a') as f:
            f.write(f"Total Policies: {total_policies}\n\n")
        
        policy_count = 0
        for policy in policy_list:
            policy_count += 1
            log_message(f"Processing policy {policy_count}/{total_policies}: {policy}")
            
            # Get policy details
            policy_details = run_command(f"{NB_BIN}/bppllist {policy} -L", f"Get details for policy {policy}")
            
            # Extract information
            policy_type = "Unknown"
            active_status = "Unknown"
            client_count = 0
            schedule_count = 0
            retention_days = "N/A"
            last_backup = "Unknown"
            schedule_list = []
            
            for line in policy_details.split('\n'):
                if 'Policy Type:' in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        policy_type = parts[2]
                elif 'Active:' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        active_status = parts[1]
                elif 'Client Name:' in line:
                    client_count += 1
                elif 'Schedule Name:' in line:
                    schedule_count += 1
                    parts = line.split()
                    if len(parts) >= 3:
                        schedule_list.append(parts[2])
                elif 'retention' in line.lower() and ('level' in line.lower() or 'period' in line.lower()):
                    # Extract numbers from retention line
                    numbers = re.findall(r'\d+', line)
                    if numbers:
                        retention_days = numbers[-1]
            
            # Get last backup time
            jobs_output = run_command(f"{NB_BIN_BIN}/bpdbjobs -report -most_columns", "Get job history for last backup")
            if jobs_output:
                for line in jobs_output.split('\n'):
                    if policy in line and ',done,0,' in line:
                        parts = line.split(',')
                        if parts:
                            last_backup = parts[0]
            
            # Write to CSV
            with open(policy_summary_file, 'a') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow([policy, policy_type, active_status, client_count, 
                                   schedule_count, retention_days, last_backup])
            
            # Write detailed info to text file
            with open(policy_detail_file, 'a') as detail_file:
                detail_file.write(f"\nPolicy: {policy}\n")
                detail_file.write(f"  Type: {policy_type}\n")
                detail_file.write(f"  Status: {active_status}\n")
                detail_file.write(f"  Clients: {client_count}\n")
                detail_file.write(f"  Schedules: {schedule_count}\n")
                detail_file.write(f"  Retention: {retention_days} days\n")
                detail_file.write(f"  Last Backup: {last_backup}\n")
                
                if schedule_list:
                    detail_file.write(f"  Schedule Names: {'; '.join(schedule_list)}\n")
            
            # Add summary to main report for top policies
            if policy_count <= 10:
                with open(report_file, 'a') as f:
                    f.write(f"{policy}: {policy_type}, Clients: {client_count}, Active: {active_status}\n")
        
        # Add summary metrics
        active_policies_output = run_command(f"{NB_BIN}/bppllist -U", "List active policies")
        active_policy_count = 0
        for line in active_policies_output.split('\n'):
            if 'Policy Name:' in line:
                active_policy_count += 1
        
        inactive_policy_count = total_policies - active_policy_count
        
        with open(report_file, 'a') as f:
            f.write(f"\nPolicy Statistics:\n")
            f.write(f"  Total Policies: {total_policies}\n")
            f.write(f"  Active Policies: {active_policy_count}\n")
            f.write(f"  Inactive Policies: {inactive_policy_count}\n\n")
        
        # Policy type breakdown
        policy_types = Counter()
        for policy in policy_list:
            policy_details = run_command(f"{NB_BIN}/bppllist {policy} -L", f"Get policy type for {policy}")
            for line in policy_details.split('\n'):
                if 'Policy Type:' in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        policy_types[parts[2]] += 1
        
        with open(report_file, 'a') as f:
            f.write("Policy Type Distribution:\n")
            for ptype, count in sorted(policy_types.items(), key=lambda x: x[1], reverse=True):
                f.write(f"  {ptype}: {count}\n")
        
        # Add to JSON metrics
        add_json_metric("policies", "total_count", total_policies, "count", "info")
        add_json_metric("policies", "active_count", active_policy_count, "count", "info")
        add_json_metric("policies", "inactive_count", inactive_policy_count, "count", "warning")
        
        with open(report_file, 'a') as f:
            f.write(f"\nDetailed policy information saved to:\n")
            f.write(f"  - {policy_summary_file} (CSV)\n")
            f.write(f"  - {policy_detail_file} (Detailed text)\n\n")
    else:
        with open(report_file, 'a') as f:
            f.write("bppllist command not available.\n\n")

def summarize_clients_detailed(report_file):
    """Summarize all clients with data consumption"""
    log_message("Generating detailed client summary with data consumption...")
    
    with open(report_file, 'a') as f:
        f.write("=== DETAILED CLIENT SUMMARY ===\n")
    
    # Create client summary files
    client_summary_file = f"{OUTPUT_DIR}/client_summary_{TIMESTAMP}.csv"
    client_consumption_file = f"{OUTPUT_DIR}/client_consumption_{TIMESTAMP}.csv"
    
    with open(client_summary_file, 'w') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["client_name", "policy_count", "last_backup", "backup_status", "estimated_data_gb"])
    
    with open(client_consumption_file, 'w') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["client_name", "policy", "last_backup_size_gb", "total_backups_7d", "retention_days"])
    
    if os.path.exists(f"{NB_BIN}/bpgetconfig"):
        # Get all clients
        clients_output = run_command(f"{NB_BIN}/bpgetconfig -L", "List all configured clients")
        client_list = []
        for line in clients_output.split('\n'):
            if 'Client Name:' in line:
                parts = line.split()
                if len(parts) >= 3:
                    client_list.append(parts[2])
        
        total_clients = len(client_list)
        
        with open(report_file, 'a') as f:
            f.write(f"Total Configured Clients: {total_clients}\n\n")
        
        # Initialize dictionaries for tracking
        client_policy_count = defaultdict(int)
        client_last_backup = {}
        client_status = {}
        client_data_estimate = {}
        
        # Get client info from policies
        if os.path.exists(f"{NB_BIN}/bppllist"):
            policies_output = run_command(f"{NB_BIN}/bppllist", "List policies for client analysis")
            policy_list = []
            for line in policies_output.split('\n'):
                if 'Policy Name:' in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        policy_list.append(parts[2])
            
            for policy in policy_list:
                policy_details = run_command(f"{NB_BIN}/bppllist {policy} -L", f"Get clients for policy {policy}")
                for line in policy_details.split('\n'):
                    if 'Client Name:' in line:
                        parts = line.split()
                        if len(parts) >= 3:
                            client = parts[2]
                            client_policy_count[client] += 1
        
        # Estimate data consumption from recent backups
        if os.path.exists(f"{NB_BIN_BIN}/bpdbjobs"):
            log_message("Analyzing backup history for data consumption...")
            
            # Get job data
            jobs_output = run_command(f"{NB_BIN_BIN}/bpdbjobs -report -most_columns", "Get job data for consumption analysis")
            job_lines = [line for line in jobs_output.split('\n') if ',done,0,' in line]
            
            for client in client_list:
                client_jobs = [line for line in job_lines if f",{client}," in line]
                
                if client_jobs:
                    recent_count = len(client_jobs)
                    
                    # Estimate average backup size
                    total_size_est = 0.0
                    size_samples = 0
                    
                    for job in client_jobs:
                        parts = job.split(',')
                        if len(parts) >= 8:
                            size_field = parts[-2]  # Second to last field often contains size
                            # Extract numeric value
                            size_match = re.search(r'(\d+\.?\d*)', size_field)
                            if size_match:
                                size_value = float(size_match.group(1))
                                # Determine unit and convert to GB
                                if 'KB' in size_field.upper():
                                    size_gb = size_value / 1048576
                                elif 'MB' in size_field.upper():
                                    size_gb = size_value / 1024
                                elif 'TB' in size_field.upper():
                                    size_gb = size_value * 1024
                                else:
                                    size_gb = size_value  # Assume GB
                                
                                total_size_est += size_gb
                                size_samples += 1
                    
                    # Calculate average if we have samples
                    if size_samples > 0:
                        avg_size = total_size_est / size_samples
                        client_data_estimate[client] = round(avg_size, 2)
                    else:
                        client_data_estimate[client] = 0
                    
                    # Get last backup time
                    last_job = client_jobs[-1]
                    last_backup = last_job.split(',')[0] if last_job else "Never"
                    client_last_backup[client] = last_backup
                    
                    # Determine backup status
                    today = datetime.now().strftime("%Y-%m-%d")
                    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                    
                    if today in last_backup:
                        client_status[client] = "Backed up today"
                    elif yesterday in last_backup:
                        client_status[client] = "Backed up yesterday"
                    elif last_backup != "Never":
                        try:
                            backup_date = datetime.strptime(last_backup[:10], "%Y-%m-%d")
                            days_old = (datetime.now() - backup_date).days
                            if days_old > 7:
                                client_status[client] = "Old (>7 days)"
                            else:
                                client_status[client] = "Recent"
                        except:
                            client_status[client] = "Recent"
                    else:
                        client_status[client] = "Never backed up"
                else:
                    client_data_estimate[client] = 0
                    client_last_backup[client] = "Never"
                    client_status[client] = "No backups found"
        
        # Write client summaries
        with open(report_file, 'a') as f:
            f.write("Top 20 Clients by Estimated Data Consumption:\n")
            f.write("==============================================\n")
        
        # Sort clients by estimated data size
        sorted_clients = sorted(client_data_estimate.items(), key=lambda x: x[1], reverse=True)
        
        client_count = 0
        total_estimated_data = 0.0
        
        for client, data_estimate in sorted_clients:
            client_count += 1
            
            policy_count = client_policy_count.get(client, 0)
            last_backup = client_last_backup.get(client, "Unknown")
            status = client_status.get(client, "Unknown")
            
            # Write to CSV
            with open(client_summary_file, 'a') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow([client, policy_count, last_backup, status, data_estimate])
            
            # Show top 20 in report
            if client_count <= 20:
                with open(report_file, 'a') as f:
                    f.write(f"{client}: {data_estimate} GB, Policies: {policy_count}, Last: {last_backup}\n")
            
            # Add to JSON metrics for top clients
            if client_count <= 10:
                if data_estimate > 100:
                    status_level = "large"
                elif data_estimate > 10:
                    status_level = "medium"
                else:
                    status_level = "small"
                
                metric_name = client.replace('.', '_').replace('-', '_')
                add_json_metric("clients", f"{metric_name}_data_gb", data_estimate, "GB", status_level)
            
            total_estimated_data += data_estimate
        
        # Calculate totals
        avg_per_client = total_estimated_data / total_clients if total_clients > 0 else 0
        
        with open(report_file, 'a') as f:
            f.write(f"\nClient Summary Statistics:\n")
            f.write(f"  Total Clients: {total_clients}\n")
            f.write(f"  Total Estimated Backup Data: {total_estimated_data:.2f} GB\n")
            f.write(f"  Average per Client: {avg_per_client:.2f} GB\n")
        
        add_json_metric("consumption", "total_estimated_gb", round(total_estimated_data, 2), "GB", "info")
        add_json_metric("consumption", "avg_per_client_gb", round(avg_per_client, 2), "GB", "info")
        
    else:
        with open(report_file, 'a') as f:
            f.write("bpgetconfig command not available.\n")
    
    with open(report_file, 'a') as f:
        f.write("\n")

def summarize_schedules_retention(report_file):
    """Summarize schedules and retention"""
    log_message("Generating schedule and retention summary...")
    
    with open(report_file, 'a') as f:
        f.write("=== SCHEDULE AND RETENTION SUMMARY ===\n")
    
    if os.path.exists(f"{NB_BIN}/bppllist"):
        # Create schedule summary files
        schedule_summary_file = f"{OUTPUT_DIR}/schedule_summary_{TIMESTAMP}.csv"
        retention_summary_file = f"{OUTPUT_DIR}/retention_summary_{TIMESTAMP}.csv"
        
        with open(schedule_summary_file, 'w') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["policy_name", "schedule_name", "frequency", "start_time", 
                               "window_duration", "retention_level", "retention_days"])
        
        with open(retention_summary_file, 'w') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["retention_level", "policy_count", "min_days", "max_days", "avg_days"])
        
        # Get all policies
        policies_output = run_command(f"{NB_BIN}/bppllist", "List policies for schedule analysis")
        policy_list = []
        for line in policies_output.split('\n'):
            if 'Policy Name:' in line:
                parts = line.split()
                if len(parts) >= 3:
                    policy_list.append(parts[2])
        
        # Track retention levels
        retention_levels = defaultdict(int)
        retention_min = {}
        retention_max = {}
        retention_sum = defaultdict(int)
        retention_count = defaultdict(int)
        
        schedule_count = 0
        
        for policy in policy_list:
            policy_details = run_command(f"{NB_BIN}/bppllist {policy} -L", f"Get schedule details for policy {policy}")
            
            lines = policy_details.split('\n')
            i = 0
            while i < len(lines):
                line = lines[i]
                if 'Schedule Name:' in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        schedule_name = parts[2]
                        
                        # Look for related information
                        frequency = ""
                        start_time = ""
                        window_duration = ""
                        retention_level = ""
                        retention_days = "0"
                        
                        # Check next few lines for schedule details
                        for j in range(i+1, min(i+10, len(lines))):
                            next_line = lines[j]
                            if 'Frequency:' in next_line:
                                freq_parts = next_line.split()
                                if len(freq_parts) >= 2:
                                    frequency = freq_parts[1]
                            elif 'Start Window:' in next_line:
                                start_parts = next_line.split()
                                if len(start_parts) >= 3:
                                    start_time = start_parts[2]
                            elif 'Length:' in next_line:
                                length_parts = next_line.split()
                                if len(length_parts) >= 2:
                                    window_duration = length_parts[1]
                            elif 'Retention Level:' in next_line:
                                ret_parts = next_line.split()
                                if len(ret_parts) >= 3:
                                    retention_level = ret_parts[2]
                            elif 'Retention Period:' in next_line:
                                period_parts = next_line.split()
                                if len(period_parts) >= 3:
                                    # Extract numbers
                                    numbers = re.findall(r'\d+', period_parts[2])
                                    if numbers:
                                        retention_days = numbers[0]
                        
                        schedule_count += 1
                        
                        # Write to CSV
                        with open(schedule_summary_file, 'a') as csv_file:
                            csv_writer = csv.writer(csv_file)
                            csv_writer.writerow([policy, schedule_name, frequency, start_time, 
                                               window_duration, retention_level, retention_days])
                        
                        # Track retention statistics
                        if retention_level and retention_days != "0":
                            retention_days_int = int(retention_days)
                            retention_levels[retention_level] += 1
                            
                            if retention_level not in retention_min:
                                retention_min[retention_level] = retention_days_int
                                retention_max[retention_level] = retention_days_int
                                retention_sum[retention_level] = retention_days_int
                                retention_count[retention_level] = 1
                            else:
                                if retention_days_int < retention_min[retention_level]:
                                    retention_min[retention_level] = retention_days_int
                                if retention_days_int > retention_max[retention_level]:
                                    retention_max[retention_level] = retention_days_int
                                
                                retention_sum[retention_level] += retention_days_int
                                retention_count[retention_level] += 1
                
                i += 1
        
        # Write retention summary
        with open(report_file, 'a') as f:
            f.write(f"\nSchedule Statistics:\n")
            f.write(f"  Total Schedules: {schedule_count}\n\n")
            f.write("Retention Level Summary:\n")
            f.write("========================\n")
        
        for level in sorted(retention_levels.keys()):
            count = retention_levels[level]
            min_days = retention_min.get(level, 0)
            max_days = retention_max.get(level, 0)
            total_sum = retention_sum.get(level, 0)
            avg_days = total_sum // count if count > 0 else 0
            
            with open(report_file, 'a') as f:
                f.write(f"{level}: {count} policies, Range: {min_days}-{max_days} days, Average: {avg_days} days\n")
            
            # Write to CSV
            with open(retention_summary_file, 'a') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow([level, count, min_days, max_days, avg_days])
            
            # Add to JSON
            add_json_metric("retention", f"{level}_avg_days", avg_days, "days", "info")
        
        # Show schedule frequency distribution
        if os.path.exists(schedule_summary_file):
            frequencies = Counter()
            with open(schedule_summary_file, 'r') as csv_file:
                reader = csv.reader(csv_file)
                next(reader)  # Skip header
                for row in reader:
                    if len(row) >= 3:
                        frequencies[row[2]] += 1
            
            with open(report_file, 'a') as f:
                f.write(f"\nSchedule Frequency Distribution:\n")
                f.write("================================\n")
                for freq, count in sorted(frequencies.items(), key=lambda x: x[1], reverse=True):
                    f.write(f"{freq}: {count} schedules\n")
                    add_json_metric("schedules", f"{freq}_count", count, "count", "info")
        
        with open(report_file, 'a') as f:
            f.write(f"\nDetailed schedule information saved to:\n")
            f.write(f"  - {schedule_summary_file}\n")
            f.write(f"  - {retention_summary_file}\n\n")
        
        add_json_metric("schedules", "total_count", schedule_count, "count", "info")
        
    else:
        with open(report_file, 'a') as f:
            f.write("bppllist command not available.\n\n")

def check_slp(report_file):
    """Check Storage Lifecycle Policies"""
    log_message("Checking Storage Lifecycle Policies...")
    
    with open(report_file, 'a') as f:
        f.write("=== STORAGE LIFECYCLE POLICIES ===\n")
    
    if os.path.exists(f"{NB_BIN}/nbgetconfig"):
        slp_output = run_command(f"{NB_BIN}/nbgetconfig -listSchedules", "Get SLP schedules")
        slp_count = 0
        slp_lines = []
        
        for line in slp_output.split('\n'):
            if 'SLP Name:' in line:
                slp_count += 1
                slp_lines.append(line)
        
        with open(report_file, 'a') as f:
            f.write(f"Total SLP Schedules: {slp_count}\n")
        
        add_json_metric("slp", "total_schedules", slp_count, "count", "info")
        
        if slp_count > 0:
            with open(report_file, 'a') as f:
                f.write(f"\nSLP Status:\n")
                for line in slp_lines:
                    f.write(f"{line}\n")
    
    with open(report_file, 'a') as f:
        f.write("\n")

def check_jobs_enhanced(report_file):
    """Enhanced check jobs function with failure analysis"""
    global jobs_raw_file
    
    log_message("Checking backup jobs...")
    
    with open(report_file, 'a') as f:
        f.write("=== BACKUP JOB STATUS ===\n")
    
    if os.path.exists(f"{NB_BIN_BIN}/bpdbjobs"):
        # Create a more comprehensive jobs report
        jobs_report_file = f"{OUTPUT_DIR}/jobs_report_{TIMESTAMP}.csv"
        
        # Get jobs from last 7 days
        jobs_output = run_command(f"{NB_BIN_BIN}/bpdbjobs -report -most_columns", "Get job report for analysis")
        job_lines = [line for line in jobs_output.split('\n') if ',active' in line or ',done' in line]
        
        # Save raw jobs
        jobs_raw_file = f"{jobs_report_file}.raw"
        with open(jobs_raw_file, 'w') as f:
            f.write('\n'.join(job_lines))
        
        # Process the report
        total_jobs = len(job_lines)
        success_jobs = len([line for line in job_lines if ',done,0,' in line])
        failed_jobs = len([line for line in job_lines if ',done,1,' in line])
        active_jobs = len([line for line in job_lines if ',active,' in line])
        
        with open(report_file, 'a') as f:
            f.write("Job Statistics (last 7 days):\n")
            f.write(f"  Total jobs: {total_jobs}\n")
            f.write(f"  Successful: {success_jobs}\n")
            f.write(f"  Failed: {failed_jobs}\n")
            f.write(f"  Active: {active_jobs}\n")
        
        # Calculate success rate
        if total_jobs > 0:
            completed_jobs = success_jobs + failed_jobs
            if completed_jobs > 0:
                success_rate = (success_jobs * 100) // completed_jobs
                
                with open(report_file, 'a') as f:
                    f.write(f"  Success Rate: {success_rate}%\n")
                
                if success_rate < 90:
                    status = "critical"
                    with open(ALERT_FILE, 'a') as alert_file:
                        alert_file.write("ALERT: Success rate below 90%\n")
                elif success_rate < 95:
                    status = "warning"
                else:
                    status = "healthy"
                
                add_json_metric("jobs", "success_rate", success_rate, "percent", status)
        
        add_json_metric("jobs", "total_7d", total_jobs, "count", "info")
        add_json_metric("jobs", "failed_7d", failed_jobs, "count", "warning")
        add_json_metric("jobs", "active_now", active_jobs, "count", "info")
        
        # Create jobs CSV for detailed analysis
        with open(jobs_report_file, 'w') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["job_id", "policy", "client", "status", "start_time", "end_time", "status_code", "size_mb"])
            
            # Add completed jobs
            completed_job_lines = [line for line in job_lines if ',done,' in line][:100]
            for job_line in completed_job_lines:
                parts = job_line.split(',')
                if len(parts) >= 8:
                    csv_writer.writerow(parts[:8])
        
        with open(report_file, 'a') as f:
            f.write(f"\nDetailed job report saved to: {jobs_report_file}\n\n")
        
    else:
        with open(report_file, 'a') as f:
            f.write("bpdbjobs command not available or not executable.\n\n")
        jobs_raw_file = ""

def analyze_failed_status_codes(report_file):
    """Analyze failed backup status codes"""
    global failed_jobs_temp
    
    log_message("Analyzing failed backup status codes...")
    
    with open(report_file, 'a') as f:
        f.write("=== FAILED BACKUP STATUS CODE ANALYSIS ===\n")
    
    if os.path.exists(f"{NB_BIN_BIN}/bpdbjobs"):
        # Create temporary file for failed jobs analysis
        failed_jobs_file = f"{OUTPUT_DIR}/failed_jobs_{TIMESTAMP}.tmp"
        
        # Get failed jobs from last 7 days
        jobs_output = run_command(f"{NB_BIN_BIN}/bpdbjobs -report -most_columns", "Get failed jobs for analysis")
        failed_job_lines = [line for line in jobs_output.split('\n') if ',done,1,' in line and ',Catalog,' not in line]
        
        # Save failed jobs
        with open(failed_jobs_file, 'w') as f:
            f.write('\n'.join(failed_job_lines))
        
        total_failed = len(failed_job_lines)
        
        if total_failed == 0:
            with open(report_file, 'a') as f:
                f.write("No failed backups found in the last 7 days.\n")
            add_json_metric("failures", "total_failed", 0, "count", "healthy")
            
            # Clean up
            if os.path.exists(failed_jobs_file):
                os.remove(failed_jobs_file)
            
            with open(report_file, 'a') as f:
                f.write("\n")
            return
        
        with open(report_file, 'a') as f:
            f.write(f"Total failed backups (7 days): {total_failed}\n")
        
        add_json_metric("failures", "total_failed", total_failed, "count", "warning")
        
        # Analyze status codes
        status_codes = Counter()
        for line in failed_job_lines:
            parts = line.split(',')
            if len(parts) >= 7:
                status_codes[parts[6]] += 1
        
        with open(report_file, 'a') as f:
            f.write("\nTop 10 Status Codes:\n")
            f.write("=====================\n")
        
        # Create detailed status code breakdown file
        status_codes_file = f"{OUTPUT_DIR}/status_codes_{TIMESTAMP}.csv"
        with open(status_codes_file, 'w') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["status_code", "count", "description", "percentage"])
            
            for code, count in status_codes.most_common(10):
                description = get_status_description(code)
                percentage = (count * 100) // total_failed
                
                with open(report_file, 'a') as f:
                    f.write(f"Status {code} ({description}): {count} failures ({percentage}%)\n")
                
                csv_writer.writerow([code, count, description, percentage])
                add_json_metric("status_codes", f"code_{code}", count, "count", "error", description)
        
        with open(report_file, 'a') as f:
            f.write(f"\nDetailed status code analysis saved to: {status_codes_file}\n")
        
        # Keep the failed jobs file for client analysis
        failed_jobs_temp = failed_jobs_file
        
    else:
        with open(report_file, 'a') as f:
            f.write("bpdbjobs command not available or not executable.\n\n")
        failed_jobs_temp = ""

def identify_problem_clients(report_file):
    """Identify clients with most errors"""
    log_message("Identifying clients with most errors...")
    
    with open(report_file, 'a') as f:
        f.write("=== CLIENTS WITH MOST BACKUP ERRORS ===\n")
    
    if not failed_jobs_temp or not os.path.exists(failed_jobs_temp):
        with open(report_file, 'a') as f:
            f.write("No failed jobs data available for analysis.\n\n")
        return
    
    # Read failed jobs
    with open(failed_jobs_temp, 'r') as f:
        failed_job_lines = f.read().splitlines()
    
    total_failed = len(failed_job_lines)
    
    with open(report_file, 'a') as f:
        f.write(f"Analyzing {total_failed} failed backups...\n\n")
    
    # Extract client names from failed jobs
    client_errors_file = f"{OUTPUT_DIR}/client_errors_{TIMESTAMP}.csv"
    
    client_counts = Counter()
    for line in failed_job_lines:
        parts = line.split(',')
        # Try different positions for client name
        for i in range(2, min(6, len(parts))):
            potential_client = parts[i]
            # Skip if it looks like a number or timestamp
            if (not re.match(r'^\d+$', potential_client) and 
                not re.match(r'^\d{4}-\d{2}-\d{2}', potential_client) and
                len(potential_client) > 1):
                client_counts[potential_client] += 1
                break
    
    total_problem_clients = len(client_counts)
    
    with open(report_file, 'a') as f:
        f.write("Top 10 Problem Clients (last 7 days):\n")
        f.write("======================================\n")
    
    # Create CSV
    with open(client_errors_file, 'w') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["client_name", "failure_count", "percentage_of_total_failures"])
        
        for client, count in client_counts.most_common(10):
            percentage = (count * 100) // total_failed if total_failed > 0 else 0
            
            # Clean up client name
            client_clean = client.strip().replace('"', '')
            if not client_clean:
                client_clean = "UNKNOWN"
            
            with open(report_file, 'a') as f:
                f.write(f"{client_clean}: {count} failures ({percentage}% of total failures)\n")
            
            csv_writer.writerow([client_clean, count, percentage])
            
            # Add to JSON metrics
            if percentage > 10:
                status = "critical"
            elif percentage > 5:
                status = "warning"
            else:
                status = "error"
            
            metric_name = client_clean.replace('.', '_').replace('-', '_')
            add_json_metric("problem_clients", metric_name, count, "count", status, f"{percentage}% of failures")
    
    # Check for chronic failures
    with open(report_file, 'a') as f:
        f.write("\nChronic Failure Analysis:\n")
        f.write("=========================\n")
    
    # Create daily failure pattern analysis (simplified)
    chronic_failures_file = f"{OUTPUT_DIR}/chronic_failures_{TIMESTAMP}.csv"
    with open(chronic_failures_file, 'w') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["client_name", "failure_count", "days_with_failures", "avg_failures_per_day"])
        
        for client, count in client_counts.most_common(5):
            client_clean = client.strip().replace('"', '')
            if not client_clean:
                client_clean = "UNKNOWN"
            
            # Estimate days with failures
            if count > 3:
                days = max(1, count // 2)
                avg = count // days
                
                with open(report_file, 'a') as f:
                    f.write(f"{client_clean}: Failed approximately {days} days ({count} total failures)\n")
                
                csv_writer.writerow([client_clean, count, days, avg])
    
    # Add summary metrics
    top_3_failures = sum(count for _, count in client_counts.most_common(3))
    top_3_percentage = (top_3_failures * 100) // total_failed if total_failed > 0 else 0
    
    with open(report_file, 'a') as f:
        f.write(f"\nSummary:\n")
        f.write(f"--------\n")
        f.write(f"Total clients with failures: {total_problem_clients}\n")
        f.write(f"Top 3 clients account for: {top_3_percentage}% of all failures\n")
        
        if top_3_percentage > 50:
            f.write("WARNING: Failures are highly concentrated in few clients!\n")
            add_json_metric("failures", "concentration", top_3_percentage, "percent", "warning", 
                          f"Top 3 clients cause {top_3_percentage}% of failures")
    
    with open(report_file, 'a') as f:
        f.write(f"\nDetailed client error analysis saved to:\n")
        f.write(f"  - {client_errors_file}\n")
        f.write(f"  - {chronic_failures_file}\n\n")

def check_tape_environment(report_file):
    """Check tape environment"""
    log_message("Checking tape environment...")
    
    with open(report_file, 'a') as f:
        f.write("=== TAPE ENVIRONMENT ===\n")
    
    # Check from media server perspective
    if os.path.exists("/usr/openv/volmgr/bin/tpconfig"):
        # Get tape drives
        tpconfig_output = run_command("/usr/openv/volmgr/bin/tpconfig -l", "Get tape configuration")
        tape_drives = tpconfig_output.count("Drive Number")
        robots = tpconfig_output.count("Robot")
        
        with open(report_file, 'a') as f:
            f.write(f"Tape Drives (local): {tape_drives}\n")
            f.write(f"Robots (local): {robots}\n\n")
        
        add_json_metric("tape", "local_drives", tape_drives, "count", "info")
        add_json_metric("tape", "local_robots", robots, "count", "info")
        
        # Check drive status
        with open(report_file, 'a') as f:
            f.write("Tape Drive Status:\n")
            for line in tpconfig_output.split('\n'):
                if "Drive Number" in line or "Robot" in line:
                    f.write(f"{line}\n")
    
    # Check disk pools
    if os.path.exists("/usr/openv/volmgr/bin/vmquery"):
        vmquery_output = run_command("/usr/openv/volmgr/bin/vmquery -d", "Get disk pool information")
        
        with open(report_file, 'a') as f:
            f.write("\nDisk Pools:\n")
            lines = vmquery_output.split('\n')[:20]
            for line in lines:
                f.write(f"{line}\n")
    
    with open(report_file, 'a') as f:
        f.write("\n")

def check_catalog_backup(report_file):
    """Check catalog backup status"""
    log_message("Checking catalog backups...")
    
    with open(report_file, 'a') as f:
        f.write("=== CATALOG BACKUPS ===\n")
    
    if os.path.exists(f"{NB_BIN}/bpcatlist"):
        # Get last catalog backup
        catalog_output = run_command(f"{NB_BIN}/bpcatlist -l", "Get catalog backup list")
        last_catalog = "NOT FOUND"
        
        for line in catalog_output.split('\n'):
            if 'Backup ID' in line:
                last_catalog = line.strip()
                break
        
        with open(report_file, 'a') as f:
            f.write(f"Last Catalog Backup: {last_catalog}\n")
        
        if "NOT FOUND" not in last_catalog:
            # Extract date from backup info
            date_match = re.search(r'(\d{2}/\d{2}/\d{4})', last_catalog)
            if date_match:
                backup_date_str = date_match.group(1)
                try:
                    backup_date = datetime.strptime(backup_date_str, "%m/%d/%Y")
                    days_old = (datetime.now() - backup_date).days
                    
                    with open(report_file, 'a') as f:
                        f.write(f"Age: {days_old} days\n")
                    
                    if days_old > 7:
                        status = "critical"
                        with open(ALERT_FILE, 'a') as alert_file:
                            alert_file.write("ALERT: Catalog backup older than 7 days\n")
                    elif days_old > 3:
                        status = "warning"
                    else:
                        status = "healthy"
                    
                    add_json_metric("catalog", "backup_age_days", days_old, "days", status)
                except:
                    pass
    
    with open(report_file, 'a') as f:
        f.write("\n")

def check_license(report_file):
    """Check license status"""
    log_message("Checking license status...")
    
    with open(report_file, 'a') as f:
        f.write("=== LICENSE INFORMATION ===\n")
    
    if os.path.exists(f"{NB_BIN}/nbgetconfig"):
        license_output = run_command(f"{NB_BIN}/nbgetconfig -L -license", "Get license information")
        
        with open(report_file, 'a') as f:
            lines = license_output.split('\n')[:30]
            for line in lines:
                f.write(f"{line}\n")
        
        # Check for expired licenses
        expired_count = 0
        for line in license_output.split('\n'):
            if 'expired' in line.lower() or 'invalid' in line.lower():
                expired_count += 1
        
        if expired_count > 0:
            with open(report_file, 'a') as f:
                f.write(f"\nALERT: Found {expired_count} expired/invalid licenses\n")
            
            with open(ALERT_FILE, 'a') as alert_file:
                alert_file.write(f"ALERT: Found {expired_count} expired/invalid licenses\n")
            
            add_json_metric("license", "expired_count", expired_count, "count", "critical")
    
    with open(report_file, 'a') as f:
        f.write("\n")

def generate_capacity_forecast(report_file):
    """Generate capacity forecast based on consumption"""
    log_message("Generating capacity forecast...")
    
    with open(report_file, 'a') as f:
        f.write("=== CAPACITY FORECAST ===\n")
    
    # Create forecast file
    forecast_file = f"{OUTPUT_DIR}/capacity_forecast_{TIMESTAMP}.csv"
    
    with open(forecast_file, 'w') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["forecast_period", "estimated_growth_gb", "total_required_gb", "growth_rate_percent"])
    
    # Get current estimated total
    current_estimate = 1000.0  # Default estimate
    
    client_summary_file = f"{OUTPUT_DIR}/client_summary_{TIMESTAMP}.csv"
    if os.path.exists(client_summary_file):
        total_data = 0.0
        with open(client_summary_file, 'r') as csv_file:
            reader = csv.reader(csv_file)
            next(reader)  # Skip header
            for row in reader:
                if len(row) >= 5:
                    try:
                        total_data += float(row[4])
                    except:
                        pass
        
        if total_data > 0:
            current_estimate = total_data
    
    # Calculate forecast (simplified - 5% monthly growth)
    monthly_growth = 5
    
    with open(report_file, 'a') as f:
        f.write(f"Current Estimated Backup Data: {current_estimate:.2f} GB\n")
        f.write(f"Assumed Monthly Growth Rate: {monthly_growth}%\n\n")
        f.write("Capacity Forecast:\n")
        f.write("==================\n")
    
    for months in [1, 3, 6, 12]:
        growth_factor = 1 + (monthly_growth / 100 * months)
        forecast_total = current_estimate * growth_factor
        growth_amount = forecast_total - current_estimate
        
        with open(report_file, 'a') as f:
            f.write(f"{months} month(s): {forecast_total:.2f} GB (Increase: {growth_amount:.2f} GB)\n")
        
        with open(forecast_file, 'a') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([f"{months} month(s)", f"{growth_amount:.2f}", f"{forecast_total:.2f}", monthly_growth])
        
        # Add to JSON
        add_json_metric("forecast", f"{months}_month_gb", round(forecast_total, 2), "GB", "info")
    
    # Add recommendations
    with open(report_file, 'a') as f:
        f.write("\nRecommendations:\n")
        f.write("================\n")
        
        if current_estimate > 10000:
            f.write("✓ Consider implementing deduplication\n")
            f.write("✓ Review retention policies for optimization\n")
            f.write("✓ Plan for storage expansion\n")
        elif current_estimate > 5000:
            f.write("✓ Monitor growth trends monthly\n")
            f.write("✓ Consider archive tier for older backups\n")
        else:
            f.write("✓ Current capacity appears sufficient\n")
            f.write("✓ Continue regular monitoring\n")
        
        f.write(f"\nForecast data saved to: {forecast_file}\n\n")

def generate_summary(report_file):
    """Generate summary and alerts"""
    global total_alerts, overall_status
    
    log_message("Generating summary...")
    
    with open(report_file, 'a') as f:
        f.write("=== ENVIRONMENT SUMMARY ===\n")
        f.write(f"Report Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Monitoring Server: {run_command('hostname', 'Get hostname for summary')}\n")
    
    # Check for alerts
    if os.path.exists(ALERT_FILE):
        with open(ALERT_FILE, 'r') as alert_file:
            alerts = alert_file.readlines()
            total_alerts = len(alerts)
        
        if total_alerts > 0:
            overall_status = "CRITICAL"
            with open(report_file, 'a') as f:
                f.write(f"\nALERTS FOUND: {total_alerts}\n")
                f.write("=======================\n")
                for alert in alerts:
                    f.write(alert)
    else:
        overall_status = "HEALTHY"
        with open(report_file, 'a') as f:
            f.write("\nNo critical alerts found.\n")

def generate_command_summary():
    """Generate command summary"""
    cmd_summary_file = f"{OUTPUT_DIR}/command_summary_{TIMESTAMP}.txt"
    
    command_reference = """NETBACKUP MONITORING COMMAND REFERENCE
=======================================

ENVIRONMENT INFORMATION:
-----------------------
1. NetBackup Version & Configuration:
   /usr/openv/netbackup/bin/admincmd/bpgetconfig
   /usr/openv/netbackup/bin/admincmd/nbgetconfig -L

2. Master Server:
   cat /usr/openv/netbackup/bp.conf | grep -i server

3. Media Servers:
   /usr/openv/netbackup/bin/admincmd/nbgetconfig -L -m

POLICY INFORMATION:
------------------
1. List all policies:
   /usr/openv/netbackup/bin/admincmd/bppllist

2. List active policies:
   /usr/openv/netbackup/bin/admincmd/bppllist -U

3. Get policy details:
   /usr/openv/netbackup/bin/admincmd/bppllist <policy_name> -L

CLIENT INFORMATION:
------------------
1. List all configured clients:
   /usr/openv/netbackup/bin/admincmd/bpgetconfig -L

2. Clients in a specific policy:
   /usr/openv/netbackup/bin/admincmd/bppllist <policy_name> -L | grep "Client Name:"

JOB MONITORING:
---------------
1. Job status report:
   /usr/openv/netbackup/bin/bpdbjobs -report -most_columns

2. Failed jobs:
   /usr/openv/netbackup/bin/bpdbjobs -report -most_columns | grep ",done,1,"

3. Active jobs:
   /usr/openv/netbackup/bin/bpdbjobs -report -most_columns | grep ",active,"

STORAGE & MEDIA:
---------------
1. Tape configuration:
   /usr/openv/volmgr/bin/tpconfig -l

2. Disk storage units:
   /usr/openv/volmgr/bin/vmquery -U

CATALOG & LICENSING:
-------------------
1. Catalog backups:
   /usr/openv/netbackup/bin/admincmd/bpcatlist -l

2. License information:
   /usr/openv/netbackup/bin/admincmd/nbgetconfig -L -license

SCRIPT-SPECIFIC ANALYSIS:
------------------------
The monitoring script analyzes:
- Policy configuration and distribution
- Client backup patterns and data consumption
- Schedule frequency and retention settings
- Job success/failure rates and error codes
- Problem clients and chronic failures
- Storage capacity and growth forecasting
- License compliance and catalog health

OUTPUT FILES GENERATED:
---------------------
1. Main report: nb_env_report_YYYYMMDD_HHMM.txt
2. JSON metrics: nb_env_metrics_YYYYMMDD_HHMM.json
3. Policy summary: policy_summary_YYYYMMDD_HHMM.csv
4. Client summary: client_summary_YYYYMMDD_HHMM.csv
5. Schedule summary: schedule_summary_YYYYMMDD_HHMM.csv
6. Status codes: status_codes_YYYYMMDD_HHMM.csv
7. Client errors: client_errors_YYYYMMDD_HHMM.csv
8. Capacity forecast: capacity_forecast_YYYYMMDD_HHMM.csv
9. Alerts: nb_alerts_YYYYMMDD_HHMM.txt
10. Command reference: command_summary_YYYYMMDD_HHMM.txt

MANUAL QUICK CHECKS:
-------------------
# Check if any backups are running right now:
/usr/openv/netbackup/bin/bpdbjobs -report -most_columns | grep ",active,"

# Check last 10 failed jobs:
/usr/openv/netbackup/bin/bpdbjobs -report -most_columns | grep ",done,1," | tail -10

# Quick policy count:
/usr/openv/netbackup/bin/admincmd/bppllist | grep -c "Policy Name:"

# Quick client count:
/usr/openv/netbackup/bin/admincmd/bpgetconfig -L | grep -c "Client Name:"

AUTOMATION TIPS:
---------------
1. Schedule script via cron:
   0 */4 * * * /opt/netbackup_monitor/nb_env_monitor.py

2. Email alerts for critical issues

3. Integrate with monitoring tools:
   Use JSON output for Prometheus/Grafana
   Use CSV files for spreadsheet analysis
"""
    
    with open(cmd_summary_file, 'w') as f:
        f.write(command_reference)
    
    with open(REPORT_FILE, 'a') as f:
        f.write(f"\nCommand reference saved to: {cmd_summary_file}\n")

def display_quick_summary():
    """Display quick summary to console"""
    print("\n" + "="*50)
    print("NETBACKUP ENVIRONMENT MONITORING SUMMARY")
    print("="*50)
    
    # Policy summary
    policy_summary_file = f"{OUTPUT_DIR}/policy_summary_{TIMESTAMP}.csv"
    if os.path.exists(policy_summary_file):
        total_policies = 0
        active_policies = 0
        try:
            with open(policy_summary_file, 'r') as csv_file:
                reader = csv.reader(csv_file)
                next(reader)  # Skip header
                for row in reader:
                    total_policies += 1
                    if len(row) >= 3 and row[2].lower() in ['yes', 'active', 'true']:
                        active_policies += 1
        except:
            pass
        
        print(f"Policies: {total_policies} total, {active_policies} active")
    
    # Client summary
    client_summary_file = f"{OUTPUT_DIR}/client_summary_{TIMESTAMP}.csv"
    if os.path.exists(client_summary_file):
        total_clients = 0
        total_data = 0.0
        try:
            with open(client_summary_file, 'r') as csv_file:
                reader = csv.reader(csv_file)
                next(reader)  # Skip header
                for row in reader:
                    total_clients += 1
                    if len(row) >= 5:
                        try:
                            total_data += float(row[4])
                        except:
                            pass
        except:
            pass
        
        print(f"Clients: {total_clients}, Estimated Data: {total_data:.2f} GB")
    
    # Schedule summary
    schedule_summary_file = f"{OUTPUT_DIR}/schedule_summary_{TIMESTAMP}.csv"
    if os.path.exists(schedule_summary_file):
        total_schedules = 0
        try:
            with open(schedule_summary_file, 'r') as csv_file:
                reader = csv.reader(csv_file)
                # Count rows minus header
                total_schedules = sum(1 for _ in reader) - 1
        except:
            pass
        
        print(f"Schedules: {total_schedules}")
    
    # Job summary
    jobs_report_file = f"{OUTPUT_DIR}/jobs_report_{TIMESTAMP}.csv"
    if os.path.exists(jobs_report_file):
        failed_jobs = 0
        try:
            with open(jobs_report_file, 'r') as csv_file:
                reader = csv.reader(csv_file)
                next(reader)  # Skip header
                for row in reader:
                    if len(row) >= 7 and row[6] == '1':
                        failed_jobs += 1
        except:
            pass
        
        print(f"Failed jobs (7 days): {failed_jobs}")
    
    # Show top data consumers
    if os.path.exists(client_summary_file):
        print("\n" + "="*30)
        print("TOP 5 DATA CONSUMERS:")
        print("="*30)
        
        try:
            clients_data = []
            with open(client_summary_file, 'r') as csv_file:
                reader = csv.reader(csv_file)
                next(reader)  # Skip header
                for row in reader:
                    if len(row) >= 5:
                        try:
                            client = row[0].replace('"', '')
                            data = float(row[4])
                            clients_data.append((client, data))
                        except:
                            pass
            
            # Sort by data size
            clients_data.sort(key=lambda x: x[1], reverse=True)
            
            for client, data in clients_data[:5]:
                print(f"{client[:30]:30} {data:8.2f} GB")
        except Exception as e:
            print(f"  Unable to display data consumers: {e}")
    
    # Show alerts
    if os.path.exists(ALERT_FILE):
        with open(ALERT_FILE, 'r') as f:
            alerts = f.read().strip()
            if alerts:
                print("\n" + "="*30)
                print("ALERTS FOUND!")
                print("="*30)
                print(alerts)
    
    print(f"\nDetailed reports saved in: {OUTPUT_DIR}")
    print("="*50 + "\n")

def main():
    """Main execution function"""
    log_message("Starting NetBackup environment monitoring")
    
    # Create output directory
    create_output_dir()
    
    # Initialize files
    with open(REPORT_FILE, 'w') as f:
        f.write(f"NetBackup Environment Report - {TIMESTAMP}\n")
        f.write("="*50 + "\n\n")
    
    with open(ALERT_FILE, 'w') as f:
        pass  # Create empty file
    
    # Initialize JSON
    init_json()
    
    # Run checks
    check_environment_status(REPORT_FILE)
    summarize_policies_detailed(REPORT_FILE)
    summarize_clients_detailed(REPORT_FILE)
    summarize_schedules_retention(REPORT_FILE)
    check_slp(REPORT_FILE)
    check_jobs_enhanced(REPORT_FILE)
    analyze_failed_status_codes(REPORT_FILE)
    identify_problem_clients(REPORT_FILE)
    check_tape_environment(REPORT_FILE)
    check_catalog_backup(REPORT_FILE)
    check_license(REPORT_FILE)
    generate_capacity_forecast(REPORT_FILE)
    generate_summary(REPORT_FILE)
    
    # Finalize JSON
    finalize_json()
    
    # Generate command summary
    generate_command_summary()
    
    # Display summary
    log_message(f"Report generated: {REPORT_FILE}")
    log_message(f"JSON metrics: {JSON_FILE}")
    
    # Display quick summary
    display_quick_summary()
    
    log_message("Monitoring completed")

if __name__ == "__main__":
    # Check if running as root or nbadmin
    import getpass
    current_user = getpass.getuser()
    
    if current_user not in ['root', 'nbadmin']:
        print(f"Warning: Running as user '{current_user}'. Some commands may require root or nbadmin privileges.")
        print("Press Enter to continue or Ctrl+C to abort...")
        input()
    
    # Setup logging
    setup_logging()
    
    # Run main function
    try:
        main()
    except KeyboardInterrupt:
        print("\nMonitoring interrupted by user.")
        sys.exit(1)
    except Exception as e:
        log_message(f"Error in main execution: {e}")
        raise
```

## Installation and Setup:

```bash
# 1. Create directory and save script
sudo mkdir -p /opt/netbackup_monitor
sudo vi /opt/netbackup_monitor/nb_env_monitor.py

# 2. Make executable
sudo chmod +x /opt/netbackup_monitor/nb_env_monitor.py

# 3. Install Python if not already installed
# For RHEL/CentOS:
# sudo yum install python3
# For Ubuntu/Debian:
# sudo apt-get install python3

# 4. Create cron job (run every 4 hours)
sudo crontab -e
# Add: 0 */4 * * * /usr/bin/python3 /opt/netbackup_monitor/nb_env_monitor.py

# 5. Run manually for test
sudo python3 /opt/netbackup_monitor/nb_env_monitor.py
```

## Key Differences from Bash Script:

### **Advantages of Python Version:**
1. **Better error handling** - Try/except blocks for robust execution
2. **Data structures** - Use of dictionaries, lists, and collections for better data management
3. **CSV/JSON handling** - Native libraries for proper CSV and JSON handling
4. **Regular expressions** - Better pattern matching for parsing output
5. **Type safety** - Variables have clear types
6. **Maintainability** - Easier to read, modify, and extend
7. **Cross-platform** - Can be adapted for other platforms more easily

### **Python-Specific Features Used:**
1. `subprocess` module for running shell commands
2. `csv` module for CSV file operations
3. `json` module for JSON serialization
4. `collections` module for Counter and defaultdict
5. `datetime` module for date/time operations
6. `re` module for regular expressions
7. `logging` module for proper logging
8. `os` module for file/directory operations

### **Functions Preserved from Bash Version:**
1. All monitoring functions with same capabilities
2. Same output files and formats
3. Same alerting logic
4. Same command summary
5. Same data analysis algorithms

### **Enhanced Error Handling:**
```python
try:
    result = subprocess.run(cmd, ...)
    return result.stdout.strip()
except subprocess.TimeoutExpired:
    log_message(f"Command timed out: {cmd}")
    return ""
except Exception as e:
    log_message(f"Error running command {cmd}: {e}")
    return ""
```

### **Better Data Processing:**
```python
# Using Counter for frequency analysis
status_codes = Counter()
for line in failed_job_lines:
    parts = line.split(',')
    if len(parts) >= 7:
        status_codes[parts[6]] += 1

# Using defaultdict for automatic initialization
client_policy_count = defaultdict(int)
```

The Python version provides all the same functionality as the bash script but with improved maintainability, error handling, and data processing capabilities.
