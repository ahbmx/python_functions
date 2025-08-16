Sure! Here's a complete example with:

* `logging` instead of `print`
* **16 dummy blocking functions** to simulate your actual per-switch sub-tasks
* Concurrency as discussed: 10 switches in parallel, each running 16 tasks, 3 at a time

---

## ✅ Full Python Script

```python
import time
import random
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# === Dummy blocking sub-tasks ===
def check_interface_status(switch_id): time.sleep(random.uniform(0.5, 1.5)); return f"{switch_id}: Interface OK"
def check_cpu_usage(switch_id): time.sleep(random.uniform(0.5, 1.5)); return f"{switch_id}: CPU OK"
def check_memory_usage(switch_id): time.sleep(random.uniform(0.5, 1.5)); return f"{switch_id}: Memory OK"
def check_vlan_config(switch_id): time.sleep(random.uniform(0.5, 1.5)); return f"{switch_id}: VLAN OK"
def check_port_errors(switch_id): time.sleep(random.uniform(0.5, 1.5)); return f"{switch_id}: Ports OK"
def check_uptime(switch_id): time.sleep(random.uniform(0.5, 1.5)); return f"{switch_id}: Uptime OK"
def check_ntp_sync(switch_id): time.sleep(random.uniform(0.5, 1.5)); return f"{switch_id}: NTP OK"
def check_temperature(switch_id): time.sleep(random.uniform(0.5, 1.5)); return f"{switch_id}: Temp OK"
def check_fan_status(switch_id): time.sleep(random.uniform(0.5, 1.5)); return f"{switch_id}: Fans OK"
def check_power_supplies(switch_id): time.sleep(random.uniform(0.5, 1.5)); return f"{switch_id}: PSU OK"
def check_mac_table(switch_id): time.sleep(random.uniform(0.5, 1.5)); return f"{switch_id}: MAC OK"
def check_arp_table(switch_id): time.sleep(random.uniform(0.5, 1.5)); return f"{switch_id}: ARP OK"
def check_routing_table(switch_id): time.sleep(random.uniform(0.5, 1.5)); return f"{switch_id}: Routes OK"
def check_spanning_tree(switch_id): time.sleep(random.uniform(0.5, 1.5)); return f"{switch_id}: STP OK"
def check_snmp_status(switch_id): time.sleep(random.uniform(0.5, 1.5)); return f"{switch_id}: SNMP OK"
def check_logs(switch_id): time.sleep(random.uniform(0.5, 1.5)); return f"{switch_id}: Logs OK"

# List of all sub-tasks
sub_tasks = [
    check_interface_status,
    check_cpu_usage,
    check_memory_usage,
    check_vlan_config,
    check_port_errors,
    check_uptime,
    check_ntp_sync,
    check_temperature,
    check_fan_status,
    check_power_supplies,
    check_mac_table,
    check_arp_table,
    check_routing_table,
    check_spanning_tree,
    check_snmp_status,
    check_logs,
]

# === Handle one switch ===
def handle_switch(switch_id):
    logger.info(f"Switch {switch_id}: Starting 16 health checks")

    results = []
    with ThreadPoolExecutor(max_workers=3) as task_executor:
        futures = [task_executor.submit(task_func, switch_id) for task_func in sub_tasks]
        for future in as_completed(futures):
            try:
                result = future.result()
                logger.info(f"Switch {switch_id}: {result}")
                results.append(result)
            except Exception as e:
                logger.error(f"Switch {switch_id}: Task failed with error: {e}")
    logger.info(f"Switch {switch_id}: Completed all tasks")
    return results

# === Main function to run all switches ===
def main():
    logger.info("Starting health checks for all switches")
    switch_ids = range(1, 11)  # 10 switches: 1 through 10
    all_results = []

    with ThreadPoolExecutor(max_workers=10) as switch_executor:
        futures = {switch_executor.submit(handle_switch, switch_id): switch_id for switch_id in switch_ids}
        for future in as_completed(futures):
            switch_id = futures[future]
            try:
                results = future.result()
                all_results.append((switch_id, results))
            except Exception as e:
                logger.error(f"Switch {switch_id}: Failed with exception: {e}")

    logger.info("Completed all switch checks.")
    return all_results

if __name__ == "__main__":
    final_results = main()
```

---

## 🧪 What You Get When You Run This

* Parallel logging from multiple switches.
* Each switch runs 16 checks, but only 3 at once (per switch).
* All 10 switches are handled in parallel.

---

## ✅ Output Sample (shortened):

```
[12:00:00] INFO: Switch 1: Starting 16 health checks
[12:00:00] INFO: Switch 2: Starting 16 health checks
...
[12:00:02] INFO: Switch 1: 1: Interface OK
[12:00:02] INFO: Switch 2: 2: Interface OK
...
[12:00:10] INFO: Switch 1: Completed all tasks
...
[12:00:15] INFO: Completed all switch checks.
```

---

Let me know if you want to log to a file, log per-switch to separate files, or adapt the tasks to match your real ones.
