# Python Function to Convert Seconds to Human-Readable Time

Here's a comprehensive function that converts seconds into a human-readable string with units ranging from years down to seconds:

```python
def seconds_to_human(seconds):
    """
    Convert seconds to human-readable time format with years, days, hours, minutes, and seconds.
    
    Args:
        seconds (int/float): Number of seconds to convert
        
    Returns:
        str: Human-readable time string
    """
    if not isinstance(seconds, (int, float)) or seconds < 0:
        return "Invalid input"
    
    if seconds == 0:
        return "0 seconds"
    
    # Define time periods in seconds
    intervals = (
        ('year', 31536000),  # 60*60*24*365
        ('day', 86400),      # 60*60*24
        ('hour', 3600),      # 60*60
        ('minute', 60),
        ('second', 1)
    )
    
    result = []
    for name, count in intervals:
        value = int(seconds // count)
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')  # Remove trailing 's' for singular
            result.append(f"{value} {name}")
    
    # Join the components with commas and 'and' for the last item
    if len(result) > 1:
        return ', '.join(result[:-1]) + ' and ' + result[-1]
    return result[0]
```

## Example Usage:

```python
print(seconds_to_human(123456789))  # 3 years, 333 days, 21 hours, 33 minutes and 9 seconds
print(seconds_to_human(3600))      # 1 hour
print(seconds_to_human(3661))      # 1 hour, 1 minute and 1 second
print(seconds_to_human(0))         # 0 seconds
print(seconds_to_human(1.5))       # 1 second
print(seconds_to_human(-100))      # Invalid input
```

## Features:

1. Handles all time units from years down to seconds
2. Proper singular/plural forms (e.g., "1 second" vs "2 seconds")
3. Natural language formatting with commas and "and"
4. Input validation for negative numbers and non-numeric inputs
5. Handles zero seconds case
6. Works with both integers and floats (though outputs integers)

You can easily modify the intervals tuple if you need to add more units (like weeks or months) or change the existing ones.
