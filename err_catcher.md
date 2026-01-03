Perfect — that’s a clean design 👍
Below is a **wrapper/decorator** that:

* ✅ Keeps your existing `log()` function **independent**
* ✅ Catches **all exceptions**
* ✅ Logs the error using `log()`
* ✅ Lets you choose whether to **stop execution or continue** via a parameter

---

## Independent `log` function (unchanged)

```python
import logging

def log(message, level=logging.INFO):
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    logging.log(level, message)
```

---

## Error-catching decorator with `stop_execution` flag

```python
from functools import wraps
import logging

def catch_errors(stop_execution=True):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log(
                    f"Error in {func.__name__}: {e}",
                    level=logging.ERROR
                )
                if stop_execution:
                    raise
                return None
        return wrapper
    return decorator
```

---

## Usage examples

### Stop execution on error (default)

```python
@catch_errors()
def divide(a, b):
    return a / b

divide(10, 0)  # logs error, then raises exception
```

### Continue execution after error

```python
@catch_errors(stop_execution=False)
def divide(a, b):
    return a / b

result = divide(10, 0)  # logs error, returns None
print("Program continues")
```

---

## Why this design is solid

* 🔹 Logging is **fully decoupled**
* 🔹 Behavior is **explicit at call site**
* 🔹 Works for **scripts, services, and libraries**
* 🔹 Easy to extend (stack traces, retries, alerts)

If you want, I can also:

* add **full traceback logging**
* make it work for **async functions**
* convert it to a **context manager**

Just tell me.
