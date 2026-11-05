```python
import csv
import urllib3
import purestorage

# Disable SSL verification warnings if using internal IP addresses with self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- CONFIGURATION SETTINGS ---
# Define your target FlashArray IPs or FQDNs
TARGET_ARRAYS = [
    "10.0.1.10",
    "10.0.1.11",
    "10.0.1.12"
]

# Administrative credentials used to run this configuration script
ADMIN_USER = "pureuser"
ADMIN_PASSWORD = "YourSecureAdminPasswordHere"

# New automated account configuration
READONLY_USER = "svc_monitoring"
TEMP_PASSWORD = "SafeSecureReadOnlyPassword123!"  # Placeholder required by local accounts
OUTPUT_CSV_FILE = "pure_api_tokens.csv"

def deploy_fleet_tokens():
    print(f"Starting unexpiring token deployment across {len(TARGET_ARRAYS)} arrays...")
    
    # Store token results to write to CSV later
    results_data = []
    
    for ip in TARGET_ARRAYS:
        print(f"\n[➡] Connecting to FlashArray: {ip}")
        array_token = None
        status_msg = "Success"
        
        try:
            # 1. Establish session using administrative username/password credentials
            array = purestorage.FlashArray(
                target=ip, 
                username=ADMIN_USER, 
                password=ADMIN_PASSWORD,
                verify_https=False
            )
            
            # 2. Check if the read-only user already exists to prevent duplicate execution errors
            user_exists = False
            try:
                current_admins = array.list_admins()
                user_exists = any(admin['name'] == READONLY_USER for admin in current_admins)
            except Exception:
                pass  # Fall back to implicit creation if list permissions are strict

            # 3. Create the account with a native 'readonly' administrative permission profile
            if not user_exists:
                array.create_admin(READONLY_USER, password=TEMP_PASSWORD, role="readonly")
                print(f"    [✔] Created local account: '{READONLY_USER}' (Role: readonly)")
            else:
                print(f"    [i] Local account '{READONLY_USER}' already exists.")

            # 4. Generate the unexpiring API token 
            # Note: Passing no expiration parameters defaults strictly to permanent/never-expiring
            token_response = array.create_api_token(READONLY_USER)
            array_token = token_response.get("api_token")
            
            print(f"    [🎉] Token generated successfully.")
            
            # 5. Log out cleanly and drop the session cookie from memory
            array.invalidate_cookie()
            
        except purestorage.PureError as pe:
            status_msg = f"API Error: {str(pe)}"
            print(f"    [❌] {status_msg}")
        except Exception as e:
            status_msg = f"Connection Error: {str(e)}"
            print(f"    [❌] {status_msg}")
            
        # Append target metrics to row data tracking array
        results_data.append({
            "Array_IP": ip,
            "Service_User": READONLY_USER,
            "API_Token": array_token if array_token else "N/A",
            "Execution_Status": status_msg
        })

    # Save all gathered keys and execution metrics safely to a localized CSV spreadsheet
    write_to_csv(results_data)

def write_to_csv(data):
    fields = ["Array_IP", "Service_User", "API_Token", "Execution_Status"]
    try:
        with open(OUTPUT_CSV_FILE, mode="w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fields)
            writer.writeheader()
            writer.writerows(data)
        print(f"\n[💾] Summary saved! View your newly provisioned tokens inside: '{OUTPUT_CSV_FILE}'")
    except IOError as ioe:
        print(f"\n[❌] Failed writing out performance spreadsheet log file: {str(ioe)}")

if __name__ == "__main__":
    deploy_fleet_tokens()
```
