```python
import re

def hl(text, pattern=None, color="yellow", marker=None):
    c = {"black":30,"red":31,"green":32,"yellow":33,"blue":34,
         "magenta":35,"cyan":36,"white":37}
    
    color_code = f"\033[{c[color]}m" if color in c else ""
    reset = "\033[0m"

    if pattern is None:
        line = f"{color_code}{text}{reset}"
        if marker: line = f"{marker}{line}{marker}"
        print(line)
    else:
        def repl(m): 
            return f"{marker if marker else ''}{color_code}{m.group(0)}{reset}{marker if marker else ''}"
        print(re.sub(pattern, repl, text))
```

### Usage Examples:

```python
hl("This is an important line", color="red")  
# Whole line in red

hl("Warning: something went wrong", pattern="Warning", color="yellow")  
# Only "Warning" highlighted

hl("Errors: 3 critical, 5 minor", pattern="\d+", color="cyan", marker="*")  
# Numbers highlighted in cyan, wrapped with *
```
