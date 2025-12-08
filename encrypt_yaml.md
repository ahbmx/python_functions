Perfect! If the YAML structure is always like this and the password is always in a **single, predictable field**, we can simplify the script a lot. No recursion is needed.

Here’s a minimal script for your YAML format:

```python
import yaml
import base64
from cryptography.fernet import Fernet

ST_TOKEN = "my_secret_password"  # your token/password

# Generate Fernet object from token
def get_fernet(password: str) -> Fernet:
    # Fernet key must be 32 bytes base64-encoded
    key = base64.urlsafe_b64encode(password.encode().ljust(32, b'\0'))
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

---

### ✅ How it works:

1. Only the **`password` field** under `devices` is encrypted.
2. Deterministic encryption using your `ST_TOKEN`.
3. YAML structure remains unchanged and readable for all other fields.

This is simple, clean, and matches exactly your format.

If you want, I can also add a **one-liner `ENC(...)` marker** around encrypted passwords so you can clearly see which values are encrypted. This is useful if you want to mix plaintext and encrypted YAML.

Do you want me to add that?
