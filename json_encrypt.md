```python
import os
import json
from typing import Any, Dict, Union
from cryptography.fernet import Fernet


# Load Fernet key from environment variable
def get_fernet_from_env() -> Fernet:
    """
    Retrieve ST_TOKEN from environment and return a Fernet instance.
    """
    key = os.getenv("ST_TOKEN")

    if not key:
        raise ValueError("Environment variable ST_TOKEN not set!")

    # Ensure key is bytes
    if isinstance(key, str):
        key = key.encode()

    return Fernet(key)


# Keys to encrypt
SENSITIVE_KEYS = {"password", "api_token", "token"}


def encrypt_sensitive(data: Union[Dict, list], fernet: Fernet) -> Union[Dict, list]:
    """
    Recursively encrypt sensitive keys.
    """
    if isinstance(data, dict):
        encrypted = {}
        for k, v in data.items():
            if k in SENSITIVE_KEYS and isinstance(v, str):
                encrypted[k] = fernet.encrypt(v.encode()).decode()
            else:
                encrypted[k] = encrypt_sensitive(v, fernet)
        return encrypted

    elif isinstance(data, list):
        return [encrypt_sensitive(item, fernet) for item in data]

    return data


def decrypt_sensitive(data: Union[Dict, list], fernet: Fernet) -> Union[Dict, list]:
    """
    Recursively decrypt sensitive keys.
    """
    if isinstance(data, dict):
        decrypted = {}
        for k, v in data.items():
            if k in SENSITIVE_KEYS and isinstance(v, str):
                try:
                    decrypted[k] = fernet.decrypt(v.encode()).decode()
                except Exception:
                    # If it's not encrypted or is invalid, leave it unchanged
                    decrypted[k] = v
            else:
                decrypted[k] = decrypt_sensitive(v, fernet)
        return decrypted

    elif isinstance(data, list):
        return [decrypt_sensitive(item, fernet) for item in data]

    return data


def encrypt_to_json(data: Dict[str, Any], json_path: str):
    """
    Encrypt sensitive fields and save to JSON.
    """
    fernet = get_fernet_from_env()
    encrypted_data = encrypt_sensitive(data, fernet)

    with open(json_path, "w") as f:
        json.dump(encrypted_data, f, indent=2)


def decrypt_from_json(json_path: str) -> Dict[str, Any]:
    """
    Load JSON and decrypt sensitive fields.
    """
    fernet = get_fernet_from_env()

    with open(json_path, "r") as f:
        data = json.load(f)

    return decrypt_sensitive(data, fernet)
```

---

# ✅ Example Usage

```python
if __name__ == "__main__":
    # Example data
    config = {
        "service": {
            "user": "alice",
            "password": "mypassword123",
            "api_token": "XYZ-123",
        },
        "metadata": {
            "nested": {
                "token": "abcdef"
            }
        }
    }

    encrypt_to_json(config, "config.enc.json")
    decrypted = decrypt_from_json("config.enc.json")
    print(decrypted)
```

---

Here’s a clean, recommended way to **integrate the decryption logic into other scripts**.

---

# ✅ Step 1 — Put all encryption/decryption logic in a separate module

Create a file called:

```
secure_json.py
```

Put **only the encryption/decryption functions** inside it:

```python
# secure_json.py

import os
import json
from typing import Any, Dict, Union
from cryptography.fernet import Fernet


SENSITIVE_KEYS = {"password", "api_token", "token"}


def get_fernet_from_env() -> Fernet:
    key = os.getenv("ST_TOKEN")
    if not key:
        raise ValueError("Environment variable ST_TOKEN is not set!")
    return Fernet(key.encode())


def decrypt_sensitive(data: Union[Dict, list], fernet: Fernet) -> Union[Dict, list]:
    if isinstance(data, dict):
        result = {}
        for k, v in data.items():
            if k in SENSITIVE_KEYS and isinstance(v, str):
                try:
                    result[k] = fernet.decrypt(v.encode()).decode()
                except Exception:
                    result[k] = v
            else:
                result[k] = decrypt_sensitive(v, fernet)
        return result

    elif isinstance(data, list):
        return [decrypt_sensitive(item, fernet) for item in data]

    return data


def decrypt_from_json(json_path: str) -> Dict[str, Any]:
    fernet = get_fernet_from_env()
    with open(json_path, "r") as f:
        data = json.load(f)
    return decrypt_sensitive(data, fernet)
```

This becomes a reusable library module.

---

# ✅ Step 2 — Import it in any script that needs decryption

Example:

```python
# my_other_script.py

from secure_json import decrypt_from_json

config = decrypt_from_json("config.enc.json")

print(config["service"]["password"])     # decrypted
print(config["service"]["api_token"])    # decrypted
print(config["metadata"]["nested"]["token"])  # decrypted
```

That's it — the decrypted data is now a normal Python dict you can work with.

---

# ✅ Step 3 — Make sure ST_TOKEN is in your environment

Before running any script:

```bash
export ST_TOKEN="your_fernet_key_here"
```

(Or load it from `.env` using python-dotenv if you prefer.)

---

# 🔍 Optional but recommended: Add a convenience helper

If many scripts will need access to decrypted config, you can add a helper function:

```python
# secure_json.py

def load_config(json_path="config.enc.json"):
    return decrypt_from_json(json_path)
```

Then in any script:

```python
from secure_json import load_config

cfg = load_config()

print(cfg["database"]["password"])
```

---

# Want additional improvements?

I can add:

✅ automatic regeneration of missing keys
✅ caching for faster load in multiple modules
✅ dotenv support
✅ type hints for editor autocompletion
✅ class-based configuration loader

Just tell me!

