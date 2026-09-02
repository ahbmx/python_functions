Absolutely. I would structure this so that configHelper.py contains only configuration values, while logHelper.py owns all logging behavior.

One useful design choice is to make the log file unique for each execution, e.g.:
```python
logs/
├── st_20260902_120501.log
├── st_20260902_121233.log
├── st_20260902_122010.log
└── ...
```

Then logHelper.py deletes old execution logs once the configured limit is exceeded.

dvl/configHelper.py
# Logging configuration
```python
LOG_OUTPUT = "console"       # "console" or "file"

LOG_DIR = "logs"

LOG_LEVEL = "debug"          # debug, info, platform, command, success,
                             # warning, system, error, critical

LOG_MAX_FILES = 10           # Keep the latest N execution logs

LOG_COLORS = {
    "debug": "\033[37m",       # White
    "info": "\033[36m",        # Cyan
    "platform": "\033[35m",    # Magenta
    "command": "\033[34m",     # Blue
    "success": "\033[32m",     # Green
    "warning": "\033[33m",     # Yellow
    "system": "\033[95m",      # Bright magenta
    "error": "\033[31m",       # Red
    "critical": "\033[91m",    # Bright red
    "reset": "\033[0m",
}
```

You can change these without touching your logging implementation.

dvl/logHelper.py

```python
import inspect
import logging
import logging.handlers
import os
import sys
from datetime import datetime

from dvl import configHelper


# ---------------------------------------------------------
# Custom log levels
# ---------------------------------------------------------

PLATFORM_LEVEL = 24
COMMAND_LEVEL = 25
SUCCESS_LEVEL = 26
SYSTEM_LEVEL = 35


logging.addLevelName(PLATFORM_LEVEL, "PLATFORM")
logging.addLevelName(COMMAND_LEVEL, "COMMAND")
logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")
logging.addLevelName(SYSTEM_LEVEL, "SYSTEM")


# Add convenience methods to Logger
def platform(self, message, *args, **kwargs):
    if self.isEnabledFor(PLATFORM_LEVEL):
        self._log(PLATFORM_LEVEL, message, args, **kwargs)


def command(self, message, *args, **kwargs):
    if self.isEnabledFor(COMMAND_LEVEL):
        self._log(COMMAND_LEVEL, message, args, **kwargs)


def success(self, message, *args, **kwargs):
    if self.isEnabledFor(SUCCESS_LEVEL):
        self._log(SUCCESS_LEVEL, message, args, **kwargs)


def system(self, message, *args, **kwargs):
    if self.isEnabledFor(SYSTEM_LEVEL):
        self._log(SYSTEM_LEVEL, message, args, **kwargs)


logging.Logger.platform = platform
logging.Logger.command = command
logging.Logger.success = success
logging.Logger.system = system


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "platform": PLATFORM_LEVEL,
    "command": COMMAND_LEVEL,
    "success": SUCCESS_LEVEL,
    "warning": logging.WARNING,
    "system": SYSTEM_LEVEL,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


# ---------------------------------------------------------
# Color formatter
# ---------------------------------------------------------

class ColorFormatter(logging.Formatter):

    def __init__(self, fmt, colors):
        super().__init__(fmt)
        self.colors = colors

    def format(self, record):
        message = super().format(record)

        color = self.colors.get(
            record.levelname.lower(),
            ""
        )

        reset = self.colors.get("reset", "")

        if color:
            return f"{color}{message}{reset}"

        return message


# ---------------------------------------------------------
# Logger setup
# ---------------------------------------------------------

def setup_logger():
    """
    Configure the application logging system.

    Logging configuration is read from dvl.configHelper.

    Returns:
        logging.Logger: Logger for the calling module.
    """

    root_logger = logging.getLogger()

    # Prevent duplicate handlers if setup_logger() is called
    # more than once.
    if root_logger.handlers:
        return logging.getLogger(_get_caller_module())

    # -----------------------------------------------------
    # Get configuration
    # -----------------------------------------------------

    output = configHelper.LOG_OUTPUT.lower()
    log_dir = configHelper.LOG_DIR or "logs"
    level_name = configHelper.LOG_LEVEL.lower()
    max_files = configHelper.LOG_MAX_FILES

    if level_name not in LOG_LEVELS:
        raise ValueError(
            f"Invalid log level '{configHelper.LOG_LEVEL}'. "
            f"Valid levels: {', '.join(LOG_LEVELS)}"
        )

    level = LOG_LEVELS[level_name]

    root_logger.setLevel(level)

    # -----------------------------------------------------
    # Format
    # -----------------------------------------------------

    log_format = (
        "%(asctime)s | "
        "%(levelname)-8s | "
        "%(name)s | "
        "%(message)s"
    )

    # -----------------------------------------------------
    # Console
    # -----------------------------------------------------

    if output == "console":

        handler = logging.StreamHandler(sys.stdout)

        handler.setLevel(level)

        handler.setFormatter(
            ColorFormatter(
                log_format,
                configHelper.LOG_COLORS
            )
        )

        root_logger.addHandler(handler)

    # -----------------------------------------------------
    # File
    # -----------------------------------------------------

    elif output == "file":

        os.makedirs(log_dir, exist_ok=True)

        script_name = os.path.splitext(
            os.path.basename(sys.argv[0])
        )[0]

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        log_file = os.path.join(
            log_dir,
            f"{script_name}_{timestamp}.log"
        )

        handler = logging.FileHandler(
            log_file,
            encoding="utf-8"
        )

        handler.setLevel(level)

        # Do NOT use ColorFormatter for files.
        # ANSI color codes should not end up in the log file.
        handler.setFormatter(
            logging.Formatter(log_format)
        )

        root_logger.addHandler(handler)

        _cleanup_old_logs(
            log_dir,
            script_name,
            max_files
        )

    else:
        raise ValueError(
            "LOG_OUTPUT must be either 'console' or 'file'"
        )

    return logging.getLogger(_get_caller_module())


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def _get_caller_module():
    """
    Return the module that called setup_logger().
    """

    frame = inspect.currentframe()

    try:
        caller = frame.f_back.f_back

        module = inspect.getmodule(caller)

        if module is not None:
            return module.__name__

        return "__main__"

    finally:
        del frame


def _cleanup_old_logs(log_dir, script_name, max_files):
    """
    Keep only the newest max_files logs for this script.
    """

    if max_files <= 0:
        return

    prefix = f"{script_name}_"
    suffix = ".log"

    files = []

    for filename in os.listdir(log_dir):

        if filename.startswith(prefix) and filename.endswith(suffix):

            path = os.path.join(log_dir, filename)

            if os.path.isfile(path):
                files.append(path)

    # Newest first
    files.sort(
        key=os.path.getmtime,
        reverse=True
    )

    # Delete everything beyond the limit
    for old_file in files[max_files:]:
        try:
            os.remove(old_file)
        except OSError:
            pass
```




st.py

Then your entry-point script becomes very simple:

```python
from dvl.logHelper import setup_logger

log = setup_logger()

log.debug("Starting application")
log.info("Loading configuration")
log.platform("Connected to platform")
log.command("Executing command")
log.success("Operation completed successfully")
log.warning("Something looks unusual")
log.system("System-level event")
log.error("Something went wrong")
```

And in dbHelper.py:
```python
import logging

log = logging.getLogger(__name__)


def connect():
    log.info("Connecting to database")
    log.success("Database connection established")
```

Similarly, reporthelper.py:
```python
import logging

log = logging.getLogger(__name__)


def generate_report():
    log.command("Generating report")
    log.success("Report generated")
```
The resulting output

With:
```python
LOG_OUTPUT = "console"
LOG_LEVEL = "debug"
```

you'll get something along the lines of:
```python
2026-09-02 12:15:01,123 | DEBUG    | __main__        | Starting application
2026-09-02 12:15:01,124 | INFO     | __main__        | Loading configuration
2026-09-02 12:15:01,125 | PLATFORM | dvl.dbHelper    | Connected to platform
2026-09-02 12:15:01,126 | COMMAND  | dvl.reporthelper | Generating report
2026-09-02 12:15:01,127 | SUCCESS  | dvl.reporthelper | Report generated
```

The %(name)s is what gives you:
```python
__main__
dvl.dbHelper
dvl.reporthelper
dvl.configHelper
```

automatically.

One thing I'd change from your original idea

I wouldn't import configHelper into every module just to get the logger.

Use this pattern everywhere except your entry point:
```python
import logging

log = logging.getLogger(__name__)
```

Only st.py needs:
```python
from dvl.logHelper import setup_logger

log = setup_logger()
```

setup_logger() configures the global logging system, and all the other modules automatically inherit that configuration.

Also, because your custom levels are deliberately positioned between the standard levels:
```python
DEBUG       10
INFO        20
PLATFORM    24
COMMAND     25
SUCCESS     26
WARNING     30
SYSTEM      35
ERROR       40
CRITICAL    50
```

you can do useful filtering. For example, setting:
```python
LOG_LEVEL = "command"
```

will show COMMAND, SUCCESS, WARNING, SYSTEM, ERROR, and CRITICAL, but not INFO, PLATFORM, or DEBUG.

One caveat: "one log per script execution" means one file created when setup_logger() runs. If the same process calls setup_logger() twice, this implementation intentionally doesn't create a second file.
