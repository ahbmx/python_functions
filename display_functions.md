Below is an **expanded utility module** that adds:

### ✔ Additional helper functions

* **colored(text, fore=None, back=None, style=None)** — more flexible wrapper
* **info / warning / error** — convenience message styles
* **bullet(text, symbol="•", fore=None, back=None)** — colored bullet-point line

### ✔ Chained regex coloring

* **color_patterns_multi(text, patterns)**

  * `patterns` is a list of tuples:
    `[(regex, fore, back, style), ...]`
  * Applies multiple regex rules in sequence without breaking previous colorization.

All functions return colored strings.

---

# 🧩 Expanded Python Module

```python
import re
from colorama import Fore, Back, Style, init

init(autoreset=True)

# Maps
FOREGROUND_COLORS = {
    None: "",
    "black": Fore.BLACK,
    "red": Fore.RED,
    "green": Fore.GREEN,
    "yellow": Fore.YELLOW,
    "blue": Fore.BLUE,
    "magenta": Fore.MAGENTA,
    "cyan": Fore.CYAN,
    "white": Fore.WHITE,
    "reset": Fore.RESET,
}

BACKGROUND_COLORS = {
    None: "",
    "black": Back.BLACK,
    "red": Back.RED,
    "green": Back.GREEN,
    "yellow": Back.YELLOW,
    "blue": Back.BLUE,
    "magenta": Back.MAGENTA,
    "cyan": Back.CYAN,
    "white": Back.WHITE,
    "reset": Back.RESET,
}

STYLES = {
    None: "",
    "bright": Style.BRIGHT,
    "dim": Style.DIM,
    "normal": Style.NORMAL,
    "reset": Style.RESET_ALL,
}


def colored(text, fore=None, back=None, style=None):
    """Fully configurable color wrapper."""
    return f"{STYLES.get(style, '')}{FOREGROUND_COLORS.get(fore, '')}{BACKGROUND_COLORS.get(back, '')}{text}{Style.RESET_ALL}"


def highlight_line(text, fore=None, back=None, style=None):
    """Color an entire line."""
    return colored(text, fore, back, style)


def spacer(char='-', length=40, fore=None, back=None, style=None):
    """Return a horizontal spacer line."""
    return colored(char * length, fore, back, style)


def bullet(text, symbol="•", fore=None, back=None, style=None):
    """Return a bullet-point line with colored symbol."""
    sym = colored(symbol, fore, back, style)
    return f"{sym} {text}"


def info(text):
    return colored(text, fore="cyan")

def warning(text):
    return colored(text, fore="yellow", style="bright")

def error(text):
    return colored(text, fore="red", style="bright")


# -------------------------
# Regex Coloring Functions
# -------------------------

def color_patterns(text, pattern, fore=None, back=None, style=None):
    """
    Color every match of 'pattern' using regex.
    """
    fore_code = FOREGROUND_COLORS.get(fore, "")
    back_code = BACKGROUND_COLORS.get(back, "")
    style_code = STYLES.get(style, "")

    def replace(match):
        return f"{style_code}{fore_code}{back_code}{match.group(0)}{Style.RESET_ALL}"

    return re.sub(pattern, replace, text)


def color_patterns_multi(text, patterns):
    """
    Apply multiple regex-color rules in sequence.

    patterns = [
        (regex, fore, back, style),
        ...
    ]
    """
    result = text

    for regex, fore, back, style in patterns:
        result = color_patterns(result, regex, fore, back, style)

    return result
```

---

# 💡 Example Usage

```python
print(highlight_line("System Initialized", fore="black", back="green"))
print(spacer("=", 60, fore="white", style="bright"))
print(bullet("Task completed.", symbol="→", fore="cyan"))

print(info("Info: Config loaded"))
print(warning("Warning: Disk space low"))
print(error("ERROR: Failed to connect"))


# Regex single-color
line = "Request failed: status=404 endpoint=/api/users"
print(color_patterns(line, r"\b404\b", fore="red", style="bright"))


# Chained regex coloring
patterns = [
    (r"\b404\b", "red", None, "bright"),
    (r"/api/\w+", "yellow", None, None),
    (r"Request failed", "magenta", None, "bright")
]

print(color_patterns_multi(line, patterns))
```

---

If you want, I can also add:

✅ automatic log timestamp formatting
✅ block-style banners
✅ table-printing helpers with alignment
Just tell me!
