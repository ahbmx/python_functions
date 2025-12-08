```python
def spacer(color=None, bgcolor=None, length=50, marker="="):
    c = {"black":30,"red":31,"green":32,"yellow":33,"blue":34,
         "magenta":35,"cyan":36,"white":37}
    b = {"black":40,"red":41,"green":42,"yellow":43,"blue":44,
         "magenta":45,"cyan":46,"white":47}
    
    codes = []
    if color in c: codes.append(str(c[color]))
    if bgcolor in b: codes.append(str(b[bgcolor]))
    
    prefix = f"\033[{';'.join(codes)}m" if codes else ""
    reset = "\033[0m"
    print(f"{prefix}{marker*length}{reset}")
```

### Usage Examples:

```python
spacer()                         # default line
spacer("cyan")                    # cyan line
spacer("yellow", "blue")          # yellow on blue
spacer("red", length=30, marker="*")  # red stars, length 30
```
