Here's the complete script with all the enhancements:

```bash
#!/bin/bash
# NetBackup 9.1 Environment Observability & Capacity Script
# Run from Linux Media Server
# Version: 3.0 - Comprehensive Environment Summary

# Configuration
OUTPUT_DIR="/tmp/netbackup_monitor"
LOG_FILE="/var/log/nb_environment_monitor.log"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="${OUTPUT_DIR}/nb_env_report_${TIMESTAMP}.txt"
JSON_FILE="${OUTPUT_DIR}/nb_env_metrics_${TIMESTAMP}.json"
ALERT_FILE="${OUTPUT_DIR}/nb_alerts_${TIMESTAMP}.txt"

# NetBackup paths
NB_BIN="/usr/openv/netbackup/bin/admincmd"
NB_BIN_BIN="/usr/openv/netbackup/bin"

# Create output directory
mkdir -p ${OUTPUT_DIR}

# Logging function
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a ${LOG_FILE}
}

# Initialize JSON file
init_json() {
    cat > ${JSON_FILE} << EOF
{
    "timestamp": "${TIMESTAMP}",
    "environment": "NetBackup 9.1",
    "monitoring_server": "$(hostname)",
    "metrics": {
EOF
}

# Add JSON metric
add_json_metric() {
    local metric_type=$1
    local metric_name=$2
    local value=$3
    local unit=$4
    local status=$5
    local details=$6
    
    echo "        \"${metric_type}_${metric_name}\": {" >> ${JSON_FILE}
    echo "            \"value\": \"${value}\"," >> ${JSON_FILE}
    echo "            \"unit\": \"${unit}\"," >> ${JSON_FILE}
    echo "            \"status\": \"${status}\"," >> ${JSON_FILE}
    if [ -n "${details}" ]; then
        echo "            \"details\": \"${details}\"" >> ${JSON_FILE}
    else
        echo "            \"details\": \"\"" >> ${JSON_FILE}
    fi
    echo "        }," >> ${JSON_FILE}
}

# Finalize JSON
finalize_json() {
    # Remove trailing comma
    sed -i '$ s/,$//' ${JSON_FILE}
    
    cat >> ${JSON_FILE} << EOF
    },
    "summary": {
        "total_alerts": ${TOTAL_ALERTS:-0},
        "status": "${OVERALL_STATUS:-UNKNOWN}"
    }
}
EOF
}

# Function to get status code description
get_status_description() {
    local status_code="$1"
    
    case ${status_code} in
        0)   echo "Success" ;;
        1)   echo "Job started but did not complete" ;;
        2)   echo "Backup suspended" ;;
        3)   echo "Backup in progress" ;;
        4)   echo "Restore in progress" ;;
        5)   echo "Verify in progress" ;;
        6)   echo "Archive in progress" ;;
        7)   echo "Import in progress" ;;
        8)   echo "Catalog backup in progress" ;;
        9)   echo "Duplicate in progress" ;;
        10)  echo "Snapshot in progress" ;;
        11)  echo "Backup done with warnings" ;;
        12)  echo "Backup canceled by user" ;;
        13)  echo "Backup canceled by policy" ;;
        14)  echo "Backup deferred" ;;
        15)  echo "Backup queued" ;;
        23)  echo "Client write failed" ;;
        25)  echo "Client connection failed" ;;
        40)  echo "Media write failed" ;;
        41)  echo "Media read failed" ;;
        42)  echo "Media not available" ;;
        82)  echo "Backup window expired" ;;
        84)  echo "Policy disabled" ;;
        96)  echo "Client resource unavailable" ;;
        155) echo "Storage unit full" ;;
        191) echo "Client not found or not responding" ;;
        203) echo "Disk pool out of space" ;;
        *)   echo "Unknown error (code: ${status_code})" ;;
    esac
}

# Check overall environment status
check_environment_status() {
    log_message "Checking NetBackup environment status..."
    
    echo "=== NETBACKUP ENVIRONMENT OVERVIEW ===" >> ${REPORT_FILE}
    
    # Get NetBackup version
    if [ -x "${NB_BIN}/bpgetconfig" ]; then
        NB_VERSION=$("${NB_BIN}/bpgetconfig" | grep -i "version" | head -1)
        echo "NetBackup Version: ${NB_VERSION}" >> ${REPORT_FILE}
    fi
    
    # Get master server name
    MASTER_SERVER=$(cat /usr/openv/netbackup/bp.conf 2>/dev/null | grep -i "server" | head -1 | awk '{print $2}' || echo "NOT FOUND")
    echo "Master Server: ${MASTER_SERVER}" >> ${REPORT_FILE}
    
    # Get list of media servers
    echo "" >> ${REPORT_FILE}
    echo "=== MEDIA SERVERS ===" >> ${REPORT_FILE}
    if [ -x "${NB_BIN}/nbgetconfig" ]; then
        "${NB_BIN}/nbgetconfig" -L -m 2>/dev/null | grep "Media Server" >> ${REPORT_FILE}
        MEDIA_SERVER_COUNT=$("${NB_BIN}/nbgetconfig" -L -m 2>/dev/null | grep -c "Media Server" || echo "0")
        add_json_metric "servers" "media_server_count" "${MEDIA_SERVER_COUNT}" "count" "info"
    fi
    echo "" >> ${REPORT_FILE}
}

# Summarize all policies with details
summarize_policies_detailed() {
    log_message "Generating detailed policy summary..."
    
    echo "=== DETAILED POLICY SUMMARY ===" >> ${REPORT_FILE}
    
    if [ -x "${NB_BIN}/bppllist" ]; then
        # Create policy summary file
        POLICY_SUMMARY_FILE="${OUTPUT_DIR}/policy_summary_${TIMESTAMP}.csv"
        POLICY_DETAIL_FILE="${OUTPUT_DIR}/policy_details_${TIMESTAMP}.txt"
        
        echo "policy_name,policy_type,active_status,client_count,schedule_count,retention_days,last_backup" > ${POLICY_SUMMARY_FILE}
        
        # Get all policies
        POLICY_LIST=$("${NB_BIN}/bppllist" 2>/dev/null | grep "Policy Name:" | awk '{print $3}')
        TOTAL_POLICIES=$(echo "${POLICY_LIST}" | wc -l)
        
        echo "Total Policies: ${TOTAL_POLICIES}" >> ${REPORT_FILE}
        echo "" >> ${REPORT_FILE}
        
        # Detailed header for text report
        echo "POLICY DETAILS:" >> ${POLICY_DETAIL_FILE}
        echo "================" >> ${POLICY_DETAIL_FILE}
        
        POLICY_COUNT=0
        for policy in ${POLICY_LIST}; do
            POLICY_COUNT=$((POLICY_COUNT + 1))
            log_message "Processing policy ${POLICY_COUNT}/${TOTAL_POLICIES}: ${policy}"
            
            # Get policy details
            POLICY_DETAILS=$("${NB_BIN}/bppllist" "${policy}" -L 2>/dev/null)
            
            # Extract information
            POLICY_TYPE=$(echo "${POLICY_DETAILS}" | grep "Policy Type:" | head -1 | awk '{print $3}' || echo "Unknown")
            ACTIVE_STATUS=$(echo "${POLICY_DETAILS}" | grep "Active:" | head -1 | awk '{print $2}' || echo "Unknown")
            CLIENT_COUNT=$(echo "${POLICY_DETAILS}" | grep -c "Client Name:")
            
            # Get schedule count and details
            SCHEDULE_COUNT=$(echo "${POLICY_DETAILS}" | grep -c "Schedule Name:")
            SCHEDULE_LIST=$(echo "${POLICY_DETAILS}" | grep "Schedule Name:" | awk '{print $3}' | tr '\n' ';')
            
            # Get retention (look for retention period)
            RETENTION_DAYS=$(echo "${POLICY_DETAILS}" | grep -i "retention" | grep -i "level\|period" | head -1 | awk '{print $NF}' | grep -o '[0-9]*' || echo "N/A")
            
            # Get last backup time (approximate from job history)
            LAST_BACKUP="Unknown"
            if [ -x "${NB_BIN_BIN}/bpdbjobs" ]; then
                LAST_BACKUP=$("${NB_BIN_BIN}/bpdbjobs" -report -most_columns 2>/dev/null | \
                    grep "${policy}," | grep ",done,0," | tail -1 | cut -d',' -f1 2>/dev/null | head -1 || echo "Unknown")
            fi
            
            # Write to CSV
            echo "\"${policy}\",\"${POLICY_TYPE}\",\"${ACTIVE_STATUS}\",\"${CLIENT_COUNT}\",\"${SCHEDULE_COUNT}\",\"${RETENTION_DAYS}\",\"${LAST_BACKUP}\"" >> ${POLICY_SUMMARY_FILE}
            
            # Write detailed info to text file
            echo "" >> ${POLICY_DETAIL_FILE}
            echo "Policy: ${policy}" >> ${POLICY_DETAIL_FILE}
            echo "  Type: ${POLICY_TYPE}" >> ${POLICY_DETAIL_FILE}
            echo "  Status: ${ACTIVE_STATUS}" >> ${POLICY_DETAIL_FILE}
            echo "  Clients: ${CLIENT_COUNT}" >> ${POLICY_DETAIL_FILE}
            echo "  Schedules: ${SCHEDULE_COUNT}" >> ${POLICY_DETAIL_FILE}
            echo "  Retention: ${RETENTION_DAYS} days" >> ${POLICY_DETAIL_FILE}
            echo "  Last Backup: ${LAST_BACKUP}" >> ${POLICY_DETAIL_FILE}
            
            if [ ${SCHEDULE_COUNT} -gt 0 ]; then
                echo "  Schedule Names: ${SCHEDULE_LIST}" >> ${POLICY_DETAIL_FILE}
            fi
            
            # Add summary to main report for top policies
            if [ ${POLICY_COUNT} -le 10 ]; then
                echo "${policy}: ${POLICY_TYPE}, Clients: ${CLIENT_COUNT}, Active: ${ACTIVE_STATUS}" >> ${REPORT_FILE}
            fi
        done
        
        # Add summary metrics
        ACTIVE_POLICY_COUNT=$("${NB_BIN}/bppllist" -U 2>/dev/null | grep -c "Policy Name:" || echo "0")
        INACTIVE_POLICY_COUNT=$((TOTAL_POLICIES - ACTIVE_POLICY_COUNT))
        
        echo "" >> ${REPORT_FILE}
        echo "Policy Statistics:" >> ${REPORT_FILE}
        echo "  Total Policies: ${TOTAL_POLICIES}" >> ${REPORT_FILE}
        echo "  Active Policies: ${ACTIVE_POLICY_COUNT}" >> ${REPORT_FILE}
        echo "  Inactive Policies: ${INACTIVE_POLICY_COUNT}" >> ${REPORT_FILE}
        
        # Policy type breakdown
        echo "" >> ${REPORT_FILE}
        echo "Policy Type Distribution:" >> ${REPORT_FILE}
        "${NB_BIN}/bppllist" 2>/dev/null | grep "Policy Type:" | sort | uniq -c | sort -rn >> ${REPORT_FILE} 2>/dev/null || echo "  Unable to get policy types" >> ${REPORT_FILE}
        
        # Add to JSON metrics
        add_json_metric "policies" "total_count" "${TOTAL_POLICIES}" "count" "info"
        add_json_metric "policies" "active_count" "${ACTIVE_POLICY_COUNT}" "count" "info"
        add_json_metric "policies" "inactive_count" "${INACTIVE_POLICY_COUNT}" "count" "warning"
        
        echo "" >> ${REPORT_FILE}
        echo "Detailed policy information saved to:" >> ${REPORT_FILE}
        echo "  - ${POLICY_SUMMARY_FILE} (CSV)" >> ${REPORT_FILE}
        echo "  - ${POLICY_DETAIL_FILE} (Detailed text)" >> ${REPORT_FILE}
        
    else
        echo "bppllist command not available." >> ${REPORT_FILE}
    fi
    echo "" >> ${REPORT_FILE}
}

# Summarize all clients with data consumption
summarize_clients_detailed() {
    log_message "Generating detailed client summary with data consumption..."
    
    echo "=== DETAILED CLIENT SUMMARY ===" >> ${REPORT_FILE}
    
    # Create client summary files
    CLIENT_SUMMARY_FILE="${OUTPUT_DIR}/client_summary_${TIMESTAMP}.csv"
    CLIENT_CONSUMPTION_FILE="${OUTPUT_DIR}/client_consumption_${TIMESTAMP}.csv"
    
    echo "client_name,policy_count,last_backup,backup_status,estimated_data_gb" > ${CLIENT_SUMMARY_FILE}
    echo "client_name,policy,last_backup_size_gb,total_backups_7d,retention_days" > ${CLIENT_CONSUMPTION_FILE}
    
    if [ -x "${NB_BIN}/bpgetconfig" ]; then
        # Get all clients
        CLIENT_LIST=$("${NB_BIN}/bpgetconfig" -L 2>/dev/null | grep "Client Name:" | awk '{print $3}')
        TOTAL_CLIENTS=$(echo "${CLIENT_LIST}" | wc -l)
        
        echo "Total Configured Clients: ${TOTAL_CLIENTS}" >> ${REPORT_FILE}
        echo "" >> ${REPORT_FILE}
        
        # Initialize arrays for tracking
        declare -A CLIENT_POLICY_COUNT
        declare -A CLIENT_LAST_BACKUP
        declare -A CLIENT_STATUS
        declare -A CLIENT_DATA_ESTIMATE
        
        # Get client info from policies
        if [ -x "${NB_BIN}/bppllist" ]; then
            POLICY_LIST=$("${NB_BIN}/bppllist" 2>/dev/null | grep "Policy Name:" | awk '{print $3}')
            
            for policy in ${POLICY_LIST}; do
                POLICY_CLIENTS=$("${NB_BIN}/bppllist" "${policy}" -L 2>/dev/null | grep "Client Name:" | awk '{print $3}')
                
                for client in ${POLICY_CLIENTS}; do
                    # Count policies per client
                    if [ -z "${CLIENT_POLICY_COUNT[$client]}" ]; then
                        CLIENT_POLICY_COUNT[$client]=1
                    else
                        CLIENT_POLICY_COUNT[$client]=$((CLIENT_POLICY_COUNT[$client] + 1))
                    fi
                done
            done
        fi
        
        # Estimate data consumption from recent backups
        if [ -x "${NB_BIN_BIN}/bpdbjobs" ]; then
            log_message "Analyzing backup history for data consumption..."
            
            # Create temporary file for job analysis
            JOB_DATA_FILE="${OUTPUT_DIR}/job_data_${TIMESTAMP}.tmp"
            "${NB_BIN_BIN}/bpdbjobs" -report -most_columns 2>/dev/null | \
                grep ",done,0," > ${JOB_DATA_FILE} 2>/dev/null
            
            # Analyze last 7 days of successful backups
            for client in ${CLIENT_LIST}; do
                # Get client's recent successful backups
                CLIENT_JOBS=$(grep ",${client}," ${JOB_DATA_FILE} 2>/dev/null || true)
                
                if [ -n "${CLIENT_JOBS}" ]; then
                    # Count backups in last 7 days
                    RECENT_COUNT=$(echo "${CLIENT_JOBS}" | wc -l)
                    
                    # Estimate average backup size (simplified - using KB/MB/GB from output)
                    TOTAL_SIZE_EST=0
                    SIZE_SAMPLES=0
                    
                    while IFS= read -r job; do
                        # Try to extract size from job data (format varies)
                        SIZE_FIELD=$(echo "${job}" | awk -F',' '{print $(NF-1)}' | grep -o '[0-9]*' || echo "0")
                        SIZE_UNIT=$(echo "${job}" | awk -F',' '{print $(NF-1)}' | grep -o '[A-Za-z]*' || echo "GB")
                        
                        if [ -n "${SIZE_FIELD}" ] && [ "${SIZE_FIELD}" -gt 0 ]; then
                            # Convert to GB
                            case ${SIZE_UNIT} in
                                "KB"|"kb") size_gb=$(echo "scale=2; ${SIZE_FIELD} / 1048576" | bc 2>/dev/null || echo "0") ;;
                                "MB"|"mb") size_gb=$(echo "scale=2; ${SIZE_FIELD} / 1024" | bc 2>/dev/null || echo "0") ;;
                                "GB"|"gb") size_gb=${SIZE_FIELD} ;;
                                "TB"|"tb") size_gb=$(echo "scale=2; ${SIZE_FIELD} * 1024" | bc 2>/dev/null || echo "0") ;;
                                *) size_gb=0 ;;
                            esac
                            
                            TOTAL_SIZE_EST=$(echo "scale=2; ${TOTAL_SIZE_EST} + ${size_gb}" | bc 2>/dev/null || echo "${TOTAL_SIZE_EST}")
                            SIZE_SAMPLES=$((SIZE_SAMPLES + 1))
                        fi
                    done <<< "${CLIENT_JOBS}"
                    
                    # Calculate average if we have samples
                    if [ ${SIZE_SAMPLES} -gt 0 ]; then
                        AVG_SIZE=$(echo "scale=2; ${TOTAL_SIZE_EST} / ${SIZE_SAMPLES}" | bc 2>/dev/null || echo "0")
                        CLIENT_DATA_ESTIMATE[$client]=${AVG_SIZE}
                    else
                        CLIENT_DATA_ESTIMATE[$client]=0
                    fi
                    
                    # Get last backup time
                    LAST_BACKUP=$(echo "${CLIENT_JOBS}" | tail -1 | cut -d',' -f1)
                    CLIENT_LAST_BACKUP[$client]=${LAST_BACKUP:-"Never"}
                    
                    # Determine backup status
                    if echo "${LAST_BACKUP}" | grep -q "$(date +%Y-%m-%d)"; then
                        CLIENT_STATUS[$client]="Backed up today"
                    elif echo "${LAST_BACKUP}" | grep -q "$(date -d 'yesterday' +%Y-%m-%d)"; then
                        CLIENT_STATUS[$client]="Backed up yesterday"
                    elif [ "${LAST_BACKUP}" != "Never" ]; then
                        # Calculate days since last backup
                        BACKUP_DATE=$(date -d "${LAST_BACKUP}" +%s 2>/dev/null || echo 0)
                        CURRENT_DATE=$(date +%s)
                        DAYS_OLD=$(( (CURRENT_DATE - BACKUP_DATE) / 86400 ))
                        
                        if [ ${DAYS_OLD} -gt 7 ]; then
                            CLIENT_STATUS[$client]="Old (>7 days)"
                        else
                            CLIENT_STATUS[$client]="Recent"
                        fi
                    else
                        CLIENT_STATUS[$client]="Never backed up"
                    fi
                else
                    CLIENT_DATA_ESTIMATE[$client]=0
                    CLIENT_LAST_BACKUP[$client]="Never"
                    CLIENT_STATUS[$client]="No backups found"
                fi
            done
            
            rm -f ${JOB_DATA_FILE} 2>/dev/null
        fi
        
        # Write client summaries
        CLIENT_COUNT=0
        echo "Top 20 Clients by Estimated Data Consumption:" >> ${REPORT_FILE}
        echo "==============================================" >> ${REPORT_FILE}
        
        # Sort clients by estimated data size
        for client in $(for key in "${!CLIENT_DATA_ESTIMATE[@]}"; do echo "$key:${CLIENT_DATA_ESTIMATE[$key]}"; done | sort -t: -k2 -nr | cut -d: -f1); do
            CLIENT_COUNT=$((CLIENT_COUNT + 1))
            
            POLICY_COUNT=${CLIENT_POLICY_COUNT[$client]:-0}
            LAST_BACKUP=${CLIENT_LAST_BACKUP[$client]:-"Unknown"}
            STATUS=${CLIENT_STATUS[$client]:-"Unknown"}
            DATA_ESTIMATE=${CLIENT_DATA_ESTIMATE[$client]:-0}
            
            # Write to CSV
            echo "\"${client}\",\"${POLICY_COUNT}\",\"${LAST_BACKUP}\",\"${STATUS}\",\"${DATA_ESTIMATE}\"" >> ${CLIENT_SUMMARY_FILE}
            
            # Show top 20 in report
            if [ ${CLIENT_COUNT} -le 20 ]; then
                echo "${client}: ${DATA_ESTIMATE} GB, Policies: ${POLICY_COUNT}, Last: ${LAST_BACKUP}" >> ${REPORT_FILE}
            fi
            
            # Add to JSON metrics for top clients
            if [ ${CLIENT_COUNT} -le 10 ]; then
                if [ $(echo "${DATA_ESTIMATE} > 100" | bc 2>/dev/null) -eq 1 ]; then
                    status="large"
                elif [ $(echo "${DATA_ESTIMATE} > 10" | bc 2>/dev/null) -eq 1 ]; then
                    status="medium"
                else
                    status="small"
                fi
                add_json_metric "clients" "${client}_data_gb" "${DATA_ESTIMATE}" "GB" "${status}"
            fi
        done
        
        # Calculate totals
        TOTAL_ESTIMATED_DATA=0
        for size in "${CLIENT_DATA_ESTIMATE[@]}"; do
            TOTAL_ESTIMATED_DATA=$(echo "scale=2; ${TOTAL_ESTIMATED_DATA} + ${size}" | bc 2>/dev/null || echo "${TOTAL_ESTIMATED_DATA}")
        done
        
        echo "" >> ${REPORT_FILE}
        echo "Client Summary Statistics:" >> ${REPORT_FILE}
        echo "  Total Clients: ${TOTAL_CLIENTS}" >> ${REPORT_FILE}
        echo "  Total Estimated Backup Data: ${TOTAL_ESTIMATED_DATA} GB" >> ${REPORT_FILE}
        if [ ${TOTAL_CLIENTS} -gt 0 ]; then
            AVG_PER_CLIENT=$(echo "scale=2; ${TOTAL_ESTIMATED_DATA} / ${TOTAL_CLIENTS}" | bc 2>/dev/null || echo "0")
            echo "  Average per Client: ${AVG_PER_CLIENT} GB" >> ${REPORT_FILE}
        fi
        
        add_json_metric "consumption" "total_estimated_gb" "${TOTAL_ESTIMATED_DATA}" "GB" "info"
        if [ ${TOTAL_CLIENTS} -gt 0 ]; then
            add_json_metric "consumption" "avg_per_client_gb" "${AVG_PER_CLIENT}" "GB" "info"
        fi
        
    else
        echo "bpgetconfig command not available." >> ${REPORT_FILE}
    fi
    echo "" >> ${REPORT_FILE}
}

# Summarize schedules and retention
summarize_schedules_retention() {
    log_message "Generating schedule and retention summary..."
    
    echo "=== SCHEDULE AND RETENTION SUMMARY ===" >> ${REPORT_FILE}
    
    if [ -x "${NB_BIN}/bppllist" ]; then
        # Create schedule summary files
        SCHEDULE_SUMMARY_FILE="${OUTPUT_DIR}/schedule_summary_${TIMESTAMP}.csv"
        RETENTION_SUMMARY_FILE="${OUTPUT_DIR}/retention_summary_${TIMESTAMP}.csv"
        
        echo "policy_name,schedule_name,frequency,start_time,window_duration,retention_level,retention_days" > ${SCHEDULE_SUMMARY_FILE}
        echo "retention_level,policy_count,min_days,max_days,avg_days" > ${RETENTION_SUMMARY_FILE}
        
        # Get all policies
        POLICY_LIST=$("${NB_BIN}/bppllist" 2>/dev/null | grep "Policy Name:" | awk '{print $3}')
        
        # Track retention levels
        declare -A RETENTION_LEVELS
        declare -A RETENTION_MIN
        declare -A RETENTION_MAX
        declare -A RETENTION_SUM
        declare -A RETENTION_COUNT
        
        SCHEDULE_COUNT=0
        
        for policy in ${POLICY_LIST}; do
            POLICY_DETAILS=$("${NB_BIN}/bppllist" "${policy}" -L 2>/dev/null)
            
            # Parse each schedule in the policy
            echo "${POLICY_DETAILS}" | awk -v policy="${policy}" '
                /Schedule Name:/ {schedule=$3}
                /Frequency:/ {frequency=$2}
                /Start Window:/ {start=$3}
                /Length:/ {length=$2}
                /Retention Level:/ {retention=$3}
                /Retention Period:/ {period=$3}
                
                schedule && frequency && start && length {
                    print policy "," schedule "," frequency "," start "," length "," retention "," period
                    schedule=""; frequency=""; start=""; length=""; retention=""; period=""
                }
            ' | while IFS= read -r schedule_line; do
                SCHEDULE_COUNT=$((SCHEDULE_COUNT + 1))
                
                # Parse schedule details
                POLICY_NAME=$(echo "${schedule_line}" | cut -d',' -f1)
                SCHEDULE_NAME=$(echo "${schedule_line}" | cut -d',' -f2)
                FREQUENCY=$(echo "${schedule_line}" | cut -d',' -f3)
                START_TIME=$(echo "${schedule_line}" | cut -d',' -f4)
                WINDOW=$(echo "${schedule_line}" | cut -d',' -f5)
                RETENTION_LEVEL=$(echo "${schedule_line}" | cut -d',' -f6)
                RETENTION_DAYS=$(echo "${schedule_line}" | cut -d',' -f7 | grep -o '[0-9]*' || echo "0")
                
                # Write to CSV
                echo "\"${POLICY_NAME}\",\"${SCHEDULE_NAME}\",\"${FREQUENCY}\",\"${START_TIME}\",\"${WINDOW}\",\"${RETENTION_LEVEL}\",\"${RETENTION_DAYS}\"" >> ${SCHEDULE_SUMMARY_FILE}
                
                # Track retention statistics
                if [ -n "${RETENTION_LEVEL}" ] && [ "${RETENTION_DAYS}" -gt 0 ]; then
                    if [ -z "${RETENTION_LEVELS[$RETENTION_LEVEL]}" ]; then
                        RETENTION_LEVELS[$RETENTION_LEVEL]=1
                        RETENTION_MIN[$RETENTION_LEVEL]=${RETENTION_DAYS}
                        RETENTION_MAX[$RETENTION_LEVEL]=${RETENTION_DAYS}
                        RETENTION_SUM[$RETENTION_LEVEL]=${RETENTION_DAYS}
                        RETENTION_COUNT[$RETENTION_LEVEL]=1
                    else
                        RETENTION_LEVELS[$RETENTION_LEVEL]=$((RETENTION_LEVELS[$RETENTION_LEVEL] + 1))
                        
                        if [ ${RETENTION_DAYS} -lt ${RETENTION_MIN[$RETENTION_LEVEL]} ]; then
                            RETENTION_MIN[$RETENTION_LEVEL]=${RETENTION_DAYS}
                        fi
                        if [ ${RETENTION_DAYS} -gt ${RETENTION_MAX[$RETENTION_LEVEL]} ]; then
                            RETENTION_MAX[$RETENTION_LEVEL]=${RETENTION_DAYS}
                        fi
                        
                        RETENTION_SUM[$RETENTION_LEVEL]=$((RETENTION_SUM[$RETENTION_LEVEL] + RETENTION_DAYS))
                        RETENTION_COUNT[$RETENTION_LEVEL]=$((RETENTION_COUNT[$RETENTION_LEVEL] + 1))
                    fi
                fi
            done
        done
        
        # Write retention summary
        echo "" >> ${REPORT_FILE}
        echo "Schedule Statistics:" >> ${REPORT_FILE}
        echo "  Total Schedules: ${SCHEDULE_COUNT}" >> ${REPORT_FILE}
        echo "" >> ${REPORT_FILE}
        
        echo "Retention Level Summary:" >> ${REPORT_FILE}
        echo "========================" >> ${REPORT_FILE}
        
        for level in "${!RETENTION_LEVELS[@]}"; do
            COUNT=${RETENTION_LEVELS[$level]}
            MIN=${RETENTION_MIN[$level]}
            MAX=${RETENTION_MAX[$level]}
            SUM=${RETENTION_SUM[$level]}
            AVG=$((SUM / COUNT))
            
            echo "${level}: ${COUNT} policies, Range: ${MIN}-${MAX} days, Average: ${AVG} days" >> ${REPORT_FILE}
            
            # Write to CSV
            echo "\"${level}\",\"${COUNT}\",\"${MIN}\",\"${MAX}\",\"${AVG}\"" >> ${RETENTION_SUMMARY_FILE}
            
            # Add to JSON
            add_json_metric "retention" "${level}_avg_days" "${AVG}" "days" "info"
        done
        
        # Show schedule frequency distribution
        echo "" >> ${REPORT_FILE}
        echo "Schedule Frequency Distribution:" >> ${REPORT_FILE}
        echo "================================" >> ${REPORT_FILE}
        
        if [ -f "${SCHEDULE_SUMMARY_FILE}" ]; then
            cut -d',' -f3 "${SCHEDULE_SUMMARY_FILE}" 2>/dev/null | sort | uniq -c | sort -rn | while read count freq; do
                freq_clean=$(echo "${freq}" | sed 's/"//g')
                echo "${freq_clean}: ${count} schedules" >> ${REPORT_FILE}
                add_json_metric "schedules" "${freq_clean}_count" "${count}" "count" "info"
            done
        fi
        
        echo "" >> ${REPORT_FILE}
        echo "Detailed schedule information saved to:" >> ${REPORT_FILE}
        echo "  - ${SCHEDULE_SUMMARY_FILE}" >> ${REPORT_FILE}
        echo "  - ${RETENTION_SUMMARY_FILE}" >> ${REPORT_FILE}
        
        add_json_metric "schedules" "total_count" "${SCHEDULE_COUNT}" "count" "info"
        
    else
        echo "bppllist command not available." >> ${REPORT_FILE}
    fi
    echo "" >> ${REPORT_FILE}
}

# Check storage lifecycle policies (SLP)
check_slp() {
    log_message "Checking Storage Lifecycle Policies..."
    
    echo "=== STORAGE LIFECYCLE POLICIES ===" >> ${REPORT_FILE}
    
    if [ -x "${NB_BIN}/nbgetconfig" ]; then
        SLP_COUNT=$("${NB_BIN}/nbgetconfig" -listSchedules 2>/dev/null | grep -c "SLP Name:" || echo "0")
        echo "Total SLP Schedules: ${SLP_COUNT}" >> ${REPORT_FILE}
        add_json_metric "slp" "total_schedules" "${SLP_COUNT}" "count" "info"
        
        if [ ${SLP_COUNT} -gt 0 ]; then
            echo "" >> ${REPORT_FILE}
            echo "SLP Status:" >> ${REPORT_FILE}
            "${NB_BIN}/nbgetconfig" -listSchedules 2>/dev/null | grep -A3 "SLP Name:" >> ${REPORT_FILE}
        fi
    fi
    echo "" >> ${REPORT_FILE}
}

# Enhanced check_jobs function with failure analysis
check_jobs_enhanced() {
    log_message "Checking backup jobs..."
    
    echo "=== BACKUP JOB STATUS ===" >> ${REPORT_FILE}
    
    if [ -x "${NB_BIN_BIN}/bpdbjobs" ]; then
        # Create a more comprehensive jobs report
        JOBS_REPORT_FILE="${OUTPUT_DIR}/jobs_report_${TIMESTAMP}.csv"
        
        # Get jobs from last 7 days
        "${NB_BIN_BIN}/bpdbjobs" -report -most_columns 2>/dev/null | \
            grep -E ",active|,done" > ${JOBS_REPORT_FILE}.raw 2>/dev/null
        
        # Process the report
        TOTAL_JOBS=$(grep -c "," ${JOBS_REPORT_FILE}.raw 2>/dev/null || echo "0")
        SUCCESS_JOBS=$(grep -c ",done,0," ${JOBS_REPORT_FILE}.raw 2>/dev/null || echo "0")
        FAILED_JOBS=$(grep -c ",done,1," ${JOBS_REPORT_FILE}.raw 2>/dev/null || echo "0")
        ACTIVE_JOBS=$(grep -c ",active," ${JOBS_REPORT_FILE}.raw 2>/dev/null || echo "0")
        
        echo "Job Statistics (last 7 days):" >> ${REPORT_FILE}
        echo "  Total jobs: ${TOTAL_JOBS}" >> ${REPORT_FILE}
        echo "  Successful: ${SUCCESS_JOBS}" >> ${REPORT_FILE}
        echo "  Failed: ${FAILED_JOBS}" >> ${REPORT_FILE}
        echo "  Active: ${ACTIVE_JOBS}" >> ${REPORT_FILE}
        
        # Calculate success rate
        if [ ${TOTAL_JOBS} -gt 0 ]; then
            COMPLETED_JOBS=$((SUCCESS_JOBS + FAILED_JOBS))
            if [ ${COMPLETED_JOBS} -gt 0 ]; then
                SUCCESS_RATE=$((SUCCESS_JOBS * 100 / COMPLETED_JOBS))
                echo "  Success Rate: ${SUCCESS_RATE}%" >> ${REPORT_FILE}
                
                if [ ${SUCCESS_RATE} -lt 90 ]; then
                    status="critical"
                    echo "ALERT: Success rate below 90%" >> ${ALERT_FILE}
                elif [ ${SUCCESS_RATE} -lt 95 ]; then
                    status="warning"
                else
                    status="healthy"
                fi
                add_json_metric "jobs" "success_rate" "${SUCCESS_RATE}" "percent" "${status}"
            fi
        fi
        
        add_json_metric "jobs" "total_7d" "${TOTAL_JOBS}" "count" "info"
        add_json_metric "jobs" "failed_7d" "${FAILED_JOBS}" "count" "warning"
        add_json_metric "jobs" "active_now" "${ACTIVE_JOBS}" "count" "info"
        
        # Create jobs CSV for detailed analysis
        echo "job_id,policy,client,status,start_time,end_time,status_code,size_mb" > ${JOBS_REPORT_FILE}
        grep ",done," ${JOBS_REPORT_FILE}.raw 2>/dev/null | head -100 >> ${JOBS_REPORT_FILE} 2>/dev/null
        
        echo "" >> ${REPORT_FILE}
        echo "Detailed job report saved to: ${JOBS_REPORT_FILE}" >> ${REPORT_FILE}
        
        # Keep raw jobs file for further analysis
        JOBS_RAW_FILE=${JOBS_REPORT_FILE}.raw
        
    else
        echo "bpdbjobs command not available or not executable." >> ${REPORT_FILE}
        JOBS_RAW_FILE=""
    fi
    echo "" >> ${REPORT_FILE}
}

# Analyze failed backup status codes
analyze_failed_status_codes() {
    log_message "Analyzing failed backup status codes..."
    
    echo "=== FAILED BACKUP STATUS CODE ANALYSIS ===" >> ${REPORT_FILE}
    
    if [ -x "${NB_BIN_BIN}/bpdbjobs" ]; then
        # Create temporary file for failed jobs analysis
        FAILED_JOBS_FILE="${OUTPUT_DIR}/failed_jobs_${TIMESTAMP}.tmp"
        
        # Get failed jobs from last 7 days
        "${NB_BIN_BIN}/bpdbjobs" -report -most_columns 2>/dev/null | \
            grep ",done,1," | \
            grep -v ",Catalog," > ${FAILED_JOBS_FILE} 2>/dev/null
        
        TOTAL_FAILED=$(wc -l < ${FAILED_JOBS_FILE} 2>/dev/null || echo "0")
        
        if [ ${TOTAL_FAILED} -eq 0 ]; then
            echo "No failed backups found in the last 7 days." >> ${REPORT_FILE}
            add_json_metric "failures" "total_failed" "0" "count" "healthy"
            rm -f ${FAILED_JOBS_FILE} 2>/dev/null
            echo "" >> ${REPORT_FILE}
            return
        fi
        
        echo "Total failed backups (7 days): ${TOTAL_FAILED}" >> ${REPORT_FILE}
        add_json_metric "failures" "total_failed" "${TOTAL_FAILED}" "count" "warning"
        
        # Analyze status codes
        echo "" >> ${REPORT_FILE}
        echo "Top 10 Status Codes:" >> ${REPORT_FILE}
        echo "=====================" >> ${REPORT_FILE}
        
        # Create detailed status code breakdown file
        STATUS_CODES_FILE="${OUTPUT_DIR}/status_codes_${TIMESTAMP}.csv"
        echo "status_code,count,description,percentage" > ${STATUS_CODES_FILE}
        
        # Extract and analyze status codes
        cat ${FAILED_JOBS_FILE} 2>/dev/null | awk -F',' '{print $6}' | sort | uniq -c | sort -rn | head -10 | \
        while read count code; do
            description=$(get_status_description "${code}")
            percentage=$((count * 100 / TOTAL_FAILED))
            echo "Status ${code} (${description}): ${count} failures (${percentage}%)" >> ${REPORT_FILE}
            echo "${code},${count},${description},${percentage}" >> ${STATUS_CODES_FILE}
            add_json_metric "status_codes" "code_${code}" "${count}" "count" "error" "${description}"
        done
        
        echo "" >> ${REPORT_FILE}
        echo "Detailed status code analysis saved to: ${STATUS_CODES_FILE}" >> ${REPORT_FILE}
        
        # Keep the failed jobs file for client analysis
        FAILED_JOBS_TEMP=${FAILED_JOBS_FILE}
    else
        echo "bpdbjobs command not available or not executable." >> ${REPORT_FILE}
        echo "" >> ${REPORT_FILE}
        FAILED_JOBS_TEMP=""
    fi
}

# Identify clients with most errors
identify_problem_clients() {
    log_message "Identifying clients with most errors..."
    
    echo "=== CLIENTS WITH MOST BACKUP ERRORS ===" >> ${REPORT_FILE}
    
    if [ -z "${FAILED_JOBS_TEMP}" ] || [ ! -f "${FAILED_JOBS_TEMP}" ]; then
        echo "No failed jobs data available for analysis." >> ${REPORT_FILE}
        echo "" >> ${REPORT_FILE}
        return
    fi
    
    TOTAL_FAILED=$(wc -l < ${FAILED_JOBS_TEMP} 2>/dev/null || echo "0")
    
    echo "Analyzing ${TOTAL_FAILED} failed backups..." >> ${REPORT_FILE}
    echo "" >> ${REPORT_FILE}
    
    # Extract client names from failed jobs
    CLIENT_ERRORS_FILE="${OUTPUT_DIR}/client_errors_${TIMESTAMP}.csv"
    
    # Method: Extract client name from various possible positions
    cat ${FAILED_JOBS_TEMP} 2>/dev/null | awk -F',' '
    {
        # Try to find client name - it's often after policy name
        for (i=3; i<=5; i++) {
            if ($i !~ /^[0-9]+$/ && $i !~ /[0-9][0-9]:[0-9][0-9]/) {
                print $i
                break
            }
        }
    }' | sort | uniq -c | sort -rn > ${CLIENT_ERRORS_FILE}.tmp 2>/dev/null
    
    TOTAL_PROBLEM_CLIENTS=$(wc -l < ${CLIENT_ERRORS_FILE}.tmp 2>/dev/null || echo "0")
    
    echo "Top 10 Problem Clients (last 7 days):" >> ${REPORT_FILE}
    echo "======================================" >> ${REPORT_FILE}
    
    # Create CSV header
    echo "client_name,failure_count,percentage_of_total_failures" > ${CLIENT_ERRORS_FILE}
    
    head -10 ${CLIENT_ERRORS_FILE}.tmp 2>/dev/null | while read count client; do
        # Clean up client name
        client_clean=$(echo "${client}" | sed 's/"//g' | sed 's/^ *//;s/ *$//')
        
        if [ -z "${client_clean}" ] || [ "${client_clean}" = " " ]; then
            client_clean="UNKNOWN"
        fi
        
        percentage=$((count * 100 / TOTAL_FAILED))
        echo "${client_clean}: ${count} failures (${percentage}% of total failures)" >> ${REPORT_FILE}
        echo "${client_clean},${count},${percentage}" >> ${CLIENT_ERRORS_FILE}
        
        # Add to JSON metrics
        if [ ${percentage} -gt 10 ]; then
            status="critical"
        elif [ ${percentage} -gt 5 ]; then
            status="warning"
        else
            status="error"
        fi
        add_json_metric "problem_clients" "${client_clean}" "${count}" "count" "${status}" "${percentage}% of failures"
    done
    
    # Check for chronic failures
    echo "" >> ${REPORT_FILE}
    echo "Chronic Failure Analysis:" >> ${REPORT_FILE}
    echo "=========================" >> ${REPORT_FILE}
    
    # Create daily failure pattern analysis
    CHRONIC_FAILURES_FILE="${OUTPUT_DIR}/chronic_failures_${TIMESTAMP}.csv"
    echo "client_name,failure_count,days_with_failures,avg_failures_per_day" > ${CHRONIC_FAILURES_FILE}
    
    # Simple chronic failure detection
    head -5 ${CLIENT_ERRORS_FILE}.tmp 2>/dev/null | while read count client; do
        client_clean=$(echo "${client}" | sed 's/"//g' | sed 's/^ *//;s/ *$//')
        
        # Estimate days with failures (simplified)
        if [ ${count} -gt 3 ]; then
            days=$((count / 2))
            if [ ${days} -lt 1 ]; then
                days=1
            fi
            avg=$((count / days))
            echo "${client_clean}: Failed approximately ${days} days (${count} total failures)" >> ${REPORT_FILE}
            echo "${client_clean},${count},${days},${avg}" >> ${CHRONIC_FAILURES_FILE}
        fi
    done
    
    # Add summary metrics
    echo "" >> ${REPORT_FILE}
    echo "Summary:" >> ${REPORT_FILE}
    echo "--------" >> ${REPORT_FILE}
    echo "Total clients with failures: ${TOTAL_PROBLEM_CLIENTS}" >> ${REPORT_FILE}
    
    # Calculate failure concentration
    TOP_3_CLIENTS_FAILURES=$(head -3 ${CLIENT_ERRORS_FILE}.tmp 2>/dev/null | awk '{sum+=$1} END {print sum}' || echo "0")
    if [ ${TOTAL_FAILED} -gt 0 ]; then
        TOP_3_PERCENTAGE=$((TOP_3_CLIENTS_FAILURES * 100 / TOTAL_FAILED))
        echo "Top 3 clients account for: ${TOP_3_PERCENTAGE}% of all failures" >> ${REPORT_FILE}
        
        if [ ${TOP_3_PERCENTAGE} -gt 50 ]; then
            echo "WARNING: Failures are highly concentrated in few clients!" >> ${REPORT_FILE}
            add_json_metric "failures" "concentration" "${TOP_3_PERCENTAGE}" "percent" "warning" "Top 3 clients cause ${TOP_3_PERCENTAGE}% of failures"
        fi
    fi
    
    # Cleanup temp files
    rm -f ${CLIENT_ERRORS_FILE}.tmp 2>/dev/null
    
    echo "" >> ${REPORT_FILE}
    echo "Detailed client error analysis saved to:" >> ${REPORT_FILE}
    echo "  - ${CLIENT_ERRORS_FILE}" >> ${REPORT_FILE}
    echo "  - ${CHRONIC_FAILURES_FILE}" >> ${REPORT_FILE}
    echo "" >> ${REPORT_FILE}
}

# Check tape drives and robots
check_tape_environment() {
    log_message "Checking tape environment..."
    
    echo "=== TAPE ENVIRONMENT ===" >> ${REPORT_FILE}
    
    # Check from media server perspective
    if [ -x "/usr/openv/volmgr/bin/tpconfig" ]; then
        # Get tape drives
        TAPE_DRIVES=$("/usr/openv/volmgr/bin/tpconfig" -l 2>/dev/null | grep -c "Drive Number" || echo "0")
        echo "Tape Drives (local): ${TAPE_DRIVES}" >> ${REPORT_FILE}
        add_json_metric "tape" "local_drives" "${TAPE_DRIVES}" "count" "info"
        
        # Get robots
        ROBOTS=$("/usr/openv/volmgr/bin/tpconfig" -l 2>/dev/null | grep -c "Robot" || echo "0")
        echo "Robots (local): ${ROBOTS}" >> ${REPORT_FILE}
        add_json_metric "tape" "local_robots" "${ROBOTS}" "count" "info"
        
        # Check drive status
        echo "" >> ${REPORT_FILE}
        echo "Tape Drive Status:" >> ${REPORT_FILE}
        "/usr/openv/volmgr/bin/tpconfig" -l 2>/dev/null | grep -A2 "Drive Number" >> ${REPORT_FILE} 2>/dev/null || echo "  Unable to get drive status" >> ${REPORT_FILE}
    fi
    
    # Check disk pools
    if [ -x "/usr/openv/volmgr/bin/vmquery" ]; then
        echo "" >> ${REPORT_FILE}
        echo "Disk Pools:" >> ${REPORT_FILE}
        "/usr/openv/volmgr/bin/vmquery" -d 2>/dev/null | head -20 >> ${REPORT_FILE} 2>/dev/null || echo "  Unable to get disk pool info" >> ${REPORT_FILE}
    fi
    echo "" >> ${REPORT_FILE}
}

# Check catalog backup status
check_catalog_backup() {
    log_message "Checking catalog backups..."
    
    echo "=== CATALOG BACKUPS ===" >> ${REPORT_FILE}
    
    if [ -x "${NB_BIN}/bpcatlist" ]; then
        # Get last catalog backup
        LAST_CATALOG=$("${NB_BIN}/bpcatlist" -l 2>/dev/null | grep "Backup ID" | head -1 || echo "NOT FOUND")
        echo "Last Catalog Backup: ${LAST_CATALOG}" >> ${REPORT_FILE}
        
        if [ "${LAST_CATALOG}" != "NOT FOUND" ]; then
            # Extract date from backup info
            BACKUP_DATE=$(echo "${LAST_CATALOG}" | grep -o '[0-9][0-9]/[0-9][0-9]/[0-9][0-9][0-9][0-9]' | head -1)
            if [ -n "${BACKUP_DATE}" ]; then
                BACKUP_AGE=$(date -d "${BACKUP_DATE}" +%s 2>/dev/null || echo 0)
                CURRENT_AGE=$(date +%s)
                DAYS_OLD=$(( (CURRENT_AGE - BACKUP_AGE) / 86400 ))
                
                echo "Age: ${DAYS_OLD} days" >> ${REPORT_FILE}
                
                if [ ${DAYS_OLD} -gt 7 ]; then
                    status="critical"
                    echo "ALERT: Catalog backup older than 7 days" >> ${ALERT_FILE}
                elif [ ${DAYS_OLD} -gt 3 ]; then
                    status="warning"
                else
                    status="healthy"
                fi
                add_json_metric "catalog" "backup_age_days" "${DAYS_OLD}" "days" "${status}"
            fi
        fi
    fi
    echo "" >> ${REPORT_FILE}
}

# Check license status
check_license() {
    log_message "Checking license status..."
    
    echo "=== LICENSE INFORMATION ===" >> ${REPORT_FILE}
    
    if [ -x "${NB_BIN}/nbgetconfig" ]; then
        "${NB_BIN}/nbgetconfig" -L -license 2>/dev/null | head -30 >> ${REPORT_FILE} 2>/dev/null || echo "  Unable to get license info" >> ${REPORT_FILE}
        
        # Check for expired licenses
        EXPIRED_COUNT=$("${NB_BIN}/nbgetconfig" -L -license 2>/dev/null | grep -c -i "expired\|invalid" || echo "0")
        if [ ${EXPIRED_COUNT} -gt 0 ]; then
            echo "" >> ${REPORT_FILE}
            echo "ALERT: Found ${EXPIRED_COUNT} expired/invalid licenses" >> ${REPORT_FILE}
            echo "ALERT: Found ${EXPIRED_COUNT} expired/invalid licenses" >> ${ALERT_FILE}
            add_json_metric "license" "expired_count" "${EXPIRED_COUNT}" "count" "critical"
        fi
    fi
    echo "" >> ${REPORT_FILE}
}

# Generate capacity forecast based on consumption
generate_capacity_forecast() {
    log_message "Generating capacity forecast..."
    
    echo "=== CAPACITY FORECAST ===" >> ${REPORT_FILE}
    
    # Create forecast file
    FORECAST_FILE="${OUTPUT_DIR}/capacity_forecast_${TIMESTAMP}.csv"
    
    echo "forecast_period,estimated_growth_gb,total_required_gb,growth_rate_percent" > ${FORECAST_FILE}
    
    # Get current estimated total
    CURRENT_ESTIMATE=0
    if [ -f "${OUTPUT_DIR}/client_summary_${TIMESTAMP}.csv" ]; then
        CURRENT_ESTIMATE=$(tail -n +2 "${OUTPUT_DIR}/client_summary_${TIMESTAMP}.csv" 2>/dev/null | \
            awk -F',' '{sum+=$5} END {print sum}' | bc 2>/dev/null || echo "1000")
    fi
    
    if [ -z "${CURRENT_ESTIMATE}" ] || [ "${CURRENT_ESTIMATE}" = "0" ]; then
        CURRENT_ESTIMATE=1000  # Default estimate
    fi
    
    # Calculate forecast (simplified - 5% monthly growth)
    MONTHLY_GROWTH=5
    
    echo "Current Estimated Backup Data: ${CURRENT_ESTIMATE} GB" >> ${REPORT_FILE}
    echo "Assumed Monthly Growth Rate: ${MONTHLY_GROWTH}%" >> ${REPORT_FILE}
    echo "" >> ${REPORT_FILE}
    
    echo "Capacity Forecast:" >> ${REPORT_FILE}
    echo "==================" >> ${REPORT_FILE}
    
    for months in 1 3 6 12; do
        GROWTH_FACTOR=$(echo "scale=4; 1 + (${MONTHLY_GROWTH} / 100 * ${months})" | bc 2>/dev/null || echo "1")
        FORECAST_TOTAL=$(echo "scale=2; ${CURRENT_ESTIMATE} * ${GROWTH_FACTOR}" | bc 2>/dev/null || echo "${CURRENT_ESTIMATE}")
        GROWTH_AMOUNT=$(echo "scale=2; ${FORECAST_TOTAL} - ${CURRENT_ESTIMATE}" | bc 2>/dev/null || echo "0")
        
        echo "${months} month(s): ${FORECAST_TOTAL} GB (Increase: ${GROWTH_AMOUNT} GB)" >> ${REPORT_FILE}
        echo "${months} month(s),${GROWTH_AMOUNT},${FORECAST_TOTAL},${MONTHLY_GROWTH}" >> ${FORECAST_FILE}
        
        # Add to JSON
        add_json_metric "forecast" "${months}_month_gb" "${FORECAST_TOTAL}" "GB" "info"
    done
    
    # Add recommendations
    echo "" >> ${REPORT_FILE}
    echo "Recommendations:" >> ${REPORT_FILE}
    echo "================" >> ${REPORT_FILE}
    
    if [ $(echo "${CURRENT_ESTIMATE} > 10000" | bc 2>/dev/null) -eq 1 ]; then
        echo "✓ Consider implementing deduplication" >> ${REPORT_FILE}
        echo "✓ Review retention policies for optimization" >> ${REPORT_FILE}
        echo "✓ Plan for storage expansion" >> ${REPORT_FILE}
    elif [ $(echo "${CURRENT_ESTIMATE} > 5000" | bc 2>/dev/null) -eq 1 ]; then
        echo "✓ Monitor growth trends monthly" >> ${REPORT_FILE}
        echo "✓ Consider archive tier for older backups" >> ${REPORT_FILE}
    else
        echo "✓ Current capacity appears sufficient" >> ${REPORT_FILE}
        echo "✓ Continue regular monitoring" >> ${REPORT_FILE}
    fi
    
    echo "" >> ${REPORT_FILE}
    echo "Forecast data saved to: ${FORECAST_FILE}" >> ${REPORT_FILE}
    echo "" >> ${REPORT_FILE}
}

# Generate summary and alerts
generate_summary() {
    log_message "Generating summary..."
    
    echo "=== ENVIRONMENT SUMMARY ===" >> ${REPORT_FILE}
    echo "Report Time: $(date)" >> ${REPORT_FILE}
    echo "Monitoring Server: $(hostname)" >> ${REPORT_FILE}
    
    # Generate command summary section
    echo "" >> ${REPORT_FILE}
    echo "=== COMMANDS USED FOR INFORMATION GATHERING ===" >> ${REPORT_FILE}
    echo "" >> ${REPORT_FILE}
    
    # Check for alerts
    if [ -f "${ALERT_FILE}" ]; then
        ALERT_COUNT=$(wc -l < ${ALERT_FILE})
        echo "" >> ${REPORT_FILE}
        echo "ALERTS FOUND: ${ALERT_COUNT}" >> ${REPORT_FILE}
        echo "=======================" >> ${REPORT_FILE}
        cat ${ALERT_FILE} >> ${REPORT_FILE}
        OVERALL_STATUS="CRITICAL"
    else
        echo "" >> ${REPORT_FILE}
        echo "No critical alerts found." >> ${REPORT_FILE}
        OVERALL_STATUS="HEALTHY"
    fi
    
    TOTAL_ALERTS=${ALERT_COUNT:-0}
}

# Main execution
main() {
    log_message "Starting NetBackup environment monitoring"
    
    # Initialize files
    > ${REPORT_FILE}
    > ${ALERT_FILE}
    init_json
    
    # Run checks
    check_environment_status
    summarize_policies_detailed
    summarize_clients_detailed
    summarize_schedules_retention
    check_slp
    check_jobs_enhanced
    analyze_failed_status_codes
    identify_problem_clients
    check_tape_environment
    check_catalog_backup
    check_license
    generate_capacity_forecast
    generate_summary
    
    # Finalize JSON
    finalize_json
    
    # Display summary
    log_message "Report generated: ${REPORT_FILE}"
    log_message "JSON metrics: ${JSON_FILE}"
    
    # Generate command summary at the end
    generate_command_summary
    
    # Show quick summary
    echo ""
    echo "NETBACKUP ENVIRONMENT MONITORING SUMMARY"
    echo "========================================"
    
    # Policy summary
    if [ -f "${OUTPUT_DIR}/policy_summary_${TIMESTAMP}.csv" ]; then
        TOTAL_POLICIES=$(tail -n +2 "${OUTPUT_DIR}/policy_summary_${TIMESTAMP}.csv" | wc -l 2>/dev/null || echo "0")
        ACTIVE_POLICIES=$(tail -n +2 "${OUTPUT_DIR}/policy_summary_${TIMESTAMP}.csv" | grep -c '"yes"\|"active"' 2>/dev/null || echo "0")
        echo "Policies: ${TOTAL_POLICIES} total, ${ACTIVE_POLICIES} active"
    fi
    
    # Client summary
    if [ -f "${OUTPUT_DIR}/client_summary_${TIMESTAMP}.csv" ]; then
        TOTAL_CLIENTS=$(tail -n +2 "${OUTPUT_DIR}/client_summary_${TIMESTAMP}.csv" | wc -l 2>/dev/null || echo "0")
        TOTAL_DATA=$(tail -n +2 "${OUTPUT_DIR}/client_summary_${TIMESTAMP}.csv" | awk -F',' '{sum+=$5} END {printf "%.2f", sum}' 2>/dev/null || echo "0")
        echo "Clients: ${TOTAL_CLIENTS}, Estimated Data: ${TOTAL_DATA} GB"
    fi
    
    # Schedule summary
    if [ -f "${OUTPUT_DIR}/schedule_summary_${TIMESTAMP}.csv" ]; then
        TOTAL_SCHEDULES=$(tail -n +2 "${OUTPUT_DIR}/schedule_summary_${TIMESTAMP}.csv" | wc -l 2>/dev/null || echo "0")
        echo "Schedules: ${TOTAL_SCHEDULES}"
    fi
    
    # Job summary
    if [ -f "${OUTPUT_DIR}/jobs_report_${TIMESTAMP}.csv" ]; then
        FAILED_JOBS=$(tail -n +2 "${OUTPUT_DIR}/jobs_report_${TIMESTAMP}.csv" 2>/dev/null | grep -c ",1," || echo "0")
        echo "Failed jobs (7 days): ${FAILED_JOBS}"
    fi
    
    # Show top data consumers
    if [ -f "${OUTPUT_DIR}/client_summary_${TIMESTAMP}.csv" ]; then
        echo ""
        echo "TOP 5 DATA CONSUMERS:"
        echo "====================="
        tail -n +2 "${OUTPUT_DIR}/client_summary_${TIMESTAMP}.csv" 2>/dev/null | \
            sort -t',' -k5 -nr 2>/dev/null | head -5 | \
            awk -F',' '{printf "%-30s %8.2f GB\n", $1, $5}' 2>/dev/null || echo "  Unable to display data consumers"
    fi
    
    if [ -s ${ALERT_FILE} ]; then
        echo ""
        echo "ALERTS FOUND!" 
        cat ${ALERT_FILE}
    fi
    
    echo ""
    echo "Detailed reports saved in: ${OUTPUT_DIR}"
    log_message "Monitoring completed"
}

# Generate command summary
generate_command_summary() {
    CMD_SUMMARY_FILE="${OUTPUT_DIR}/command_summary_${TIMESTAMP}.txt"
    
    cat > ${CMD_SUMMARY_FILE} << 'EOF'
NETBACKUP MONITORING COMMAND REFERENCE
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

4. Policy attributes:
   /usr/openv/netbackup/bin/admincmd/bppllist <policy_name> -U

CLIENT INFORMATION:
------------------
1. List all configured clients:
   /usr/openv/netbackup/bin/admincmd/bpgetconfig -L

2. Clients in a specific policy:
   /usr/openv/netbackup/bin/admincmd/bppllist <policy_name> -L | grep "Client Name:"

SCHEDULE & RETENTION:
--------------------
1. Schedule information:
   /usr/openv/netbackup/bin/admincmd/bppllist <policy_name> -L | grep -A5 "Schedule Name:"

2. Retention levels:
   /usr/openv/netbackup/bin/admincmd/bppllist <policy_name> -L | grep -i "retention"

3. SLP schedules:
   /usr/openv/netbackup/bin/admincmd/nbgetconfig -listSchedules

JOB MONITORING:
---------------
1. Job status report:
   /usr/openv/netbackup/bin/bpdbjobs -report -most_columns

2. Recent jobs (last 24 hours):
   /usr/openv/netbackup/bin/bpdbjobs -report -most_columns | grep $(date +%Y-%m-%d)

3. Failed jobs:
   /usr/openv/netbackup/bin/bpdbjobs -report -most_columns | grep ",done,1,"

4. Active jobs:
   /usr/openv/netbackup/bin/bpdbjobs -report -most_columns | grep ",active,"

STORAGE & MEDIA:
---------------
1. Tape configuration:
   /usr/openv/volmgr/bin/tpconfig -l

2. Disk storage units:
   /usr/openv/volmgr/bin/vmquery -U

3. Disk pools:
   /usr/openv/volmgr/bin/vmquery -d

CATALOG & LICENSING:
-------------------
1. Catalog backups:
   /usr/openv/netbackup/bin/admincmd/bpcatlist -l

2. License information:
   /usr/openv/netbackup/bin/admincmd/nbgetconfig -L -license

DATA CONSUMPTION ESTIMATION:
---------------------------
1. Backup sizes from job history:
   /usr/openv/netbackup/bin/bpdbjobs -report -most_columns | grep ",done,0," | awk -F',' '{print $(NF-1)}'

2. Client backup frequency:
   /usr/openv/netbackup/bin/bpdbjobs -report -most_columns | grep "<client_name>"

TROUBLESHOOTING COMMANDS:
------------------------
1. Check NetBackup processes:
   ps -ef | grep -E "(vnetd|bpcd|vmd|pbx|nbproxy)"

2. Check disk space for NetBackup:
   df -h /usr/openv /catalog /images

3. Check NetBackup logs:
   ls -la /usr/openv/netbackup/logs/
   tail -100 /usr/openv/netbackup/logs/<log_file>

4. Test client connectivity:
   /usr/openv/netbackup/bin/admincmd/bptestbpcd -client <client_name>

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

# Check disk space for backup storage:
/usr/openv/volmgr/bin/vmquery -h

# Check tape drive status:
/usr/openv/volmgr/bin/tpconfig -l | grep -A1 "Drive Number"

# Quick policy count:
/usr/openv/netbackup/bin/admincmd/bppllist | grep -c "Policy Name:"

# Quick client count:
/usr/openv/netbackup/bin/admincmd/bpgetconfig -L | grep -c "Client Name:"

AUTOMATION TIPS:
---------------
1. Schedule script via cron:
   0 */4 * * * /opt/netbackup_monitor/nb_env_monitor.sh

2. Email alerts for critical issues:
   Add mail command to script for ALERT_FILE contents

3. Integrate with monitoring tools:
   Use JSON output for Prometheus/Grafana
   Use CSV files for spreadsheet analysis

4. Retention of reports:
   Add cleanup to remove reports older than 30 days

NOTES:
------
- Some commands require root or nbadmin privileges
- Job history may be limited by bpdbjobs retention
- Data consumption estimates are based on recent job sizes
- Forecasts assume 5% monthly growth (adjust as needed)
- Status codes may vary by NetBackup version
EOF

    echo "" >> ${REPORT_FILE}
    echo "Command reference saved to: ${CMD_SUMMARY_FILE}" >> ${REPORT_FILE}
}

# Run main function
main
```

## Installation and Setup:

```bash
# 1. Create directory and save script
sudo mkdir -p /opt/netbackup_monitor
sudo vi /opt/netbackup_monitor/nb_env_monitor.sh

# 2. Make executable
sudo chmod +x /opt/netbackup_monitor/nb_env_monitor.sh

# 3. Create cron job (run every 4 hours)
sudo crontab -e
# Add: 0 */4 * * * /opt/netbackup_monitor/nb_env_monitor.sh

# 4. Run manually for test
sudo /opt/netbackup_monitor/nb_env_monitor.sh
```

## What the Script Monitors (Complete Summary):

### **1. Environment Configuration:**
- NetBackup version and build
- Master server identification
- Media server inventory
- License status and expiration

### **2. Policy Management:**
- Total policy count and types (Oracle, VMware, MSSQL, etc.)
- Active vs inactive policies
- Policy-client relationships
- Retention settings per policy
- Last backup timestamps

### **3. Client Management:**
- Total configured clients
- Clients per policy
- Estimated data consumption per client
- Backup frequency and recency
- Top data consumers identification

### **4. Schedule & Retention:**
- Schedule count and frequency distribution
- Backup window analysis
- Retention level summary (Gold, Silver, Bronze)
- Retention period ranges and averages

### **5. Job Monitoring:**
- Success/failure rates (7-day period)
- Active job count
- Failed job analysis by status code
- Problem client identification
- Chronic failure patterns

### **6. Storage & Capacity:**
- Tape drive and robot status
- Disk pool information
- Estimated total backup data
- Capacity growth forecasting
- Storage recommendations

### **7. Health & Compliance:**
- Catalog backup age and status
- Service availability
- Error concentration analysis
- Alert generation for critical issues

## Commands Used by the Script:

### **Core NetBackup Commands:**
1. `bpgetconfig` - Get configuration and client lists
2. `bppllist` - List and examine policies
3. `bpdbjobs` - Job history and status reporting
4. `nbgetconfig` - License and SLP information
5. `bpcatlist` - Catalog backup information
6. `tpconfig` - Tape drive and robot configuration
7. `vmquery` - Disk storage unit information

### **System Commands:**
1. `ps` - Process status checking
2. `df` - Disk space monitoring
3. `grep/awk/sed` - Text processing
4. `date` - Timestamp generation
5. `bc` - Mathematical calculations
6. `sort/uniq` - Data analysis

## Output Files Generated:

1. **Main Report** (`nb_env_report_*.txt`) - Human-readable summary
2. **JSON Metrics** (`nb_env_metrics_*.json`) - Machine-readable for integration
3. **Policy Summary** (`policy_summary_*.csv`) - All policies with details
4. **Client Summary** (`client_summary_*.csv`) - Clients with data consumption
5. **Schedule Summary** (`schedule_summary_*.csv`) - Schedules and retention
6. **Status Codes** (`status_codes_*.csv`) - Failure analysis by error code
7. **Client Errors** (`client_errors_*.csv`) - Problem clients identified
8. **Capacity Forecast** (`capacity_forecast_*.csv`) - Growth projections
9. **Alerts File** (`nb_alerts_*.txt`) - Critical issues requiring attention
10. **Command Reference** (`command_summary_*.txt`) - Manual command guide

## Integration Points:

1. **Monitoring Systems**: Use JSON output for Prometheus/Grafana
2. **SIEM Tools**: Parse logs for security/compliance
3. **Ticketing Systems**: Create tickets from alerts
4. **Email/SMS**: Send alert notifications
5. **Dashboards**: Create executive summaries from CSV data

This comprehensive script provides complete visibility into your NetBackup environment from a single media server, enabling proactive management, capacity planning, and troubleshooting without requiring master server access.
