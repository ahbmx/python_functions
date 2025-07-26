# Python Functions for Nested Dictionary Handling

Here are two Python functions that work with both simple and nested dictionaries. The first retrieves values based on keys (passed as strings or lists), and the second removes keys (passed as strings or lists). Both return dictionaries ready for pandas DataFrame creation.

```python
def get_nested_values(d, keys):
    """
    Get values from a nested dictionary based on keys.
    
    Args:
        d (dict): Input dictionary (can be nested)
        keys (str or list): Key or list of keys to retrieve
        
    Returns:
        dict: Dictionary with the retrieved values, ready for pandas DataFrame
    """
    if isinstance(keys, str):
        keys = [keys]
    
    result = {}
    
    for key in keys:
        current = d
        key_parts = key.split('.')  # Handle nested keys with dot notation
        try:
            for part in key_parts:
                current = current[part]
            result[key] = current
        except (KeyError, TypeError):
            result[key] = None  # Return None if key doesn't exist
    
    return result


def remove_nested_keys(d, keys):
    """
    Remove keys from a nested dictionary.
    
    Args:
        d (dict): Input dictionary (can be nested)
        keys (str or list): Key or list of keys to remove
        
    Returns:
        dict: Dictionary with keys removed, ready for pandas DataFrame
    """
    if isinstance(keys, str):
        keys = [keys]
    
    # Create a deep copy to avoid modifying the original dictionary
    import copy
    result = copy.deepcopy(d)
    
    for key in keys:
        current = result
        key_parts = key.split('.')  # Handle nested keys with dot notation
        try:
            # Navigate to the parent of the target key
            for part in key_parts[:-1]:
                current = current[part]
            # Remove the target key
            del current[key_parts[-1]]
        except (KeyError, TypeError):
            continue  # Key doesn't exist, just continue
    
    return result
```

## Usage Examples

```python
# Example nested dictionary
data = {
    'name': 'John',
    'age': 30,
    'address': {
        'street': '123 Main St',
        'city': 'New York',
        'zip': '10001'
    },
    'contacts': {
        'email': 'john@example.com',
        'phone': '555-1234'
    }
}

# Get values examples
print(get_nested_values(data, 'name'))  # {'name': 'John'}
print(get_nested_values(data, ['name', 'age']))  # {'name': 'John', 'age': 30}
print(get_nested_values(data, 'address.city'))  # {'address.city': 'New York'}
print(get_nested_values(data, ['name', 'contacts.email']))  
# {'name': 'John', 'contacts.email': 'john@example.com'}

# Remove keys examples
print(remove_nested_keys(data, 'age'))  # Removes top-level 'age'
print(remove_nested_keys(data, ['age', 'address.zip']))  # Removes both keys
print(remove_nested_keys(data, 'contacts.phone'))  # Removes nested phone
print(remove_nested_keys(data, ['address.street', 'contacts']))  # Removes street and entire contacts
```

## Pandas DataFrame Integration

Both functions return dictionaries that can be directly used with pandas:

```python
import pandas as pd

# Get values and create DataFrame
values_dict = get_nested_values(data, ['name', 'age', 'address.city'])
df = pd.DataFrame([values_dict])

# Remove keys and create DataFrame
filtered_data = remove_nested_keys(data, ['contacts', 'address.zip'])
df = pd.DataFrame([filtered_data])
```

The functions handle:
- Both simple and nested dictionaries
- Both string keys and lists of keys
- Dot notation for nested keys (e.g., 'address.city')
- Missing keys (returns None for get, skips for remove)
- Returns new dictionaries without modifying the original
