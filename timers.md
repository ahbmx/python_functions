## Decorator version of `timer` for functions

```python
import time
import functools

def timed(label=None, logger=None):
    """
    Decorator to time a function.

    label:  str | None            -> override label (defaults to function name)
    logger: logging.Logger | None -> optional logger
    """
    def decorator(func):
        name = label or func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                elapsed = time.perf_counter() - start
                message = f"{name}: {elapsed:.4f}s"

                if logger is not None:
                    logger.info(message)
                else:
                    print(message)

        return wrapper
    return decorator
```

---



## timer context manager (logger optional)

```python
import time
from contextlib import contextmanager

@contextmanager
def timer(label, logger=None):
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        message = f"{label}: {elapsed:.4f}s"

        if logger is not None:
            logger.info(message)
        else:
            print(message)
```

---

## Usage examples

### 1️⃣ Without logging (prints)

```python
with timer("Step 1"):
    do_step_1()
```

Output:

```
Step 1: 0.1234s
```

---

### 2️⃣ With a logger

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

with timer("Step 2", logger):
    do_step_2()
```

Output (via logging):

```
INFO:__main__:Step 2: 0.0876s
```

---

### 3️⃣ Nested + mixed usage

```python
with timer("Pipeline", logger):
    with timer("Load data", logger):
        load_data()

    with timer("Process data"):
        process_data()  # prints
```

---

## Why this is robust

* `try/finally` ensures timing is logged **even if an exception occurs**
* Only two `perf_counter()` calls → minimal overhead
* Logger integration is optional and unobtrusive

---

If you want, I can also:

* Add **log levels** (`debug`, `info`, etc.)
* Accumulate timings into a dict
* Make a **decorator version** for functions
* Add **async (`async with`) support**

Just tell me what you need next.
