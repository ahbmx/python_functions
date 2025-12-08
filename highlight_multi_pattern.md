```python
import re

def hl_multi(text, patterns, markers=None):
    c = {"black":30,"red":31,"green":32,"yellow":33,"blue":34,
         "magenta":35,"cyan":36,"white":37}
    reset = "\033[0m"
    markers = markers if markers else [None]*len(patterns)

    def replacer(match, color, marker):
        return f"{marker if marker else ''}\033[{c[color]}m{match.group(0)}{reset}{marker if marker else ''}"

    # Apply all patterns sequentially
    highlighted = text
    for (pat, color), marker in zip(patterns, markers):
        highlighted = re.sub(pat, lambda m: replacer(m, color, marker), highlighted)

    print(highlighted)
```

### Usage Examples:

```python
text = "Errors: 3 critical, 5 minor. Warning: Check system!"

# Highlight numbers in cyan, "critical" in red, "Warning" in yellow
hl_multi(
    text,
    patterns=[("\d+", "cyan"), ("critical", "red"), ("Warning", "yellow")],
    markers=[None, "*", None]  # optional: wrap "critical" in *
)

# Highlight words without markers
hl_multi(
    "User john logged in, admin root logged out",
    patterns=[("john", "green"), ("root", "red")]
)
```
