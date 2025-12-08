```python
# yaml_encryptor.py
import yaml
import base64
import hashlib
from cryptography.fernet import Fernet

class YAMLEncryptor:
    def __init__(self, token: str):
        """
        Initialize with a token/password for encryption/decryption.
        """
        self.fernet = self._get_fernet(token)
    
    def _get_fernet(self, password: str) -> Fernet:
        """
        Derive a Fernet key from the token using SHA256.
        """
        hash_bytes = hashlib.sha256(password.encode()).digest()
        key = base64.urlsafe_b64encode(hash_bytes)
        return Fernet(key)

    def encrypt_file(self, input_file: str, output_file: str):
        """
        Encrypt the 'password' fields in a YAML file.
        """
        with open(input_file, "r") as f:
            data = yaml.safe_load(f)
        
        for device in data.get("devices", []):
            if "password" in device:
                device["password"] = self.fernet.encrypt(device["password"].encode()).decode()
        
        with open(output_file, "w") as f:
            yaml.dump(data, f)
    
    def decrypt_file(self, input_file: str) -> dict:
        """
        Decrypt the 'password' fields and return device info.
        """
        with open(input_file, "r") as f:
            data = yaml.safe_load(f)
        
        for device in data.get("devices", []):
            if "password" in device:
                device["password"] = self.fernet.decrypt(device["password"].encode()).decode()
        
        return data["devices"]
```

---

### Example usage in another script:

```python
# read_devices.py
from yaml_encryptor import YAMLEncryptor

ST_TOKEN = "my_secret_password"  # same token used for encryption

encryptor = YAMLEncryptor(ST_TOKEN)

# Encrypt (if needed)
# encryptor.encrypt_file("data.yaml", "data_encrypted.yaml")

# Decrypt and get devices
devices = encryptor.decrypt_file("data_encrypted.yaml")
for d in devices:
    print(f"Type: {d.get('type')}, IP: {d.get('ip')}, User: {d.get('user')}, Password: {d.get('password')}")
```

---



This is now clean and reusable for any script that needs to read/write your YAML files.
