```python
import yaml
import base64
import hashlib
from cryptography.fernet import Fernet

ST_TOKEN = "my_secret_password"  # your token/password

# Generate Fernet object from token using SHA256
def get_fernet(password: str) -> Fernet:
    # Hash the password to get 32 bytes
    hash_bytes = hashlib.sha256(password.encode()).digest()
    # Base64 encode for Fernet
    key = base64.urlsafe_b64encode(hash_bytes)
    return Fernet(key)

fernet = get_fernet(ST_TOKEN)

# Encrypt password field
def encrypt_password_in_yaml(input_file: str, output_file: str):
    with open(input_file, "r") as f:
        data = yaml.safe_load(f)
    
    for device in data.get("devices", []):
        if "password" in device:
            device["password"] = fernet.encrypt(device["password"].encode()).decode()
    
    with open(output_file, "w") as f:
        yaml.dump(data, f)

# Decrypt password field
def decrypt_password_in_yaml(input_file: str) -> dict:
    with open(input_file, "r") as f:
        data = yaml.safe_load(f)
    
    for device in data.get("devices", []):
        if "password" in device:
            device["password"] = fernet.decrypt(device["password"].encode()).decode()
    
    return data

# Example usage
if __name__ == "__main__":
    # Encrypt
    encrypt_password_in_yaml("data.yaml", "data_encrypted.yaml")
    
    # Decrypt
    decrypted_data = decrypt_password_in_yaml("data_encrypted.yaml")
    print("Decrypted YAML:", decrypted_data)
```


Here’s a minimal example for another script that reads `data_encrypted.yaml` and returns all device details with decrypted passwords:

```python
import yaml
import base64
import hashlib
from cryptography.fernet import Fernet

ST_TOKEN = "my_secret_password"  # same token used to encrypt

# Generate Fernet object from password
def get_fernet(password: str) -> Fernet:
    hash_bytes = hashlib.sha256(password.encode()).digest()
    key = base64.urlsafe_b64encode(hash_bytes)
    return Fernet(key)

fernet = get_fernet(ST_TOKEN)

# Load YAML and decrypt password fields
def load_devices(file_path: str):
    with open(file_path, "r") as f:
        data = yaml.safe_load(f)
    
    for device in data.get("devices", []):
        if "password" in device:
            device["password"] = fernet.decrypt(device["password"].encode()).decode()
    
    return data["devices"]

# Example usage
if __name__ == "__main__":
    devices = load_devices("data_encrypted.yaml")
    for d in devices:
        print(f"Type: {d.get('type')}, IP: {d.get('ip')}, User: {d.get('user')}, Password: {d.get('password')}")
```




