# Python Function to Display ANSI Color Codes

Here's a Python function that displays all basic ANSI color codes for both foreground and background, including bright versions. Each example shows the color name, the ANSI sequence, and a sample text in that color.

```python
def show_ansi_colors():
    # ANSI escape codes for foreground (text) colors
    fg_colors = {
        'Black': '30',
        'Red': '31',
        'Green': '32',
        'Yellow': '33',
        'Blue': '34',
        'Magenta': '35',
        'Cyan': '36',
        'White': '37',
        'Bright Black': '90',
        'Bright Red': '91',
        'Bright Green': '92',
        'Bright Yellow': '93',
        'Bright Blue': '94',
        'Bright Magenta': '95',
        'Bright Cyan': '96',
        'Bright White': '97'
    }
    
    # ANSI escape codes for background colors
    bg_colors = {
        'Black': '40',
        'Red': '41',
        'Green': '42',
        'Yellow': '43',
        'Blue': '44',
        'Magenta': '45',
        'Cyan': '46',
        'White': '47',
        'Bright Black': '100',
        'Bright Red': '101',
        'Bright Green': '102',
        'Bright Yellow': '103',
        'Bright Blue': '104',
        'Bright Magenta': '105',
        'Bright Cyan': '106',
        'Bright White': '107'
    }
    
    # Reset code
    reset = '\033[0m'
    
    print("="*80)
    print("ANSI COLOR CODEMAP")
    print("="*80)
    print("\nFOREGROUND COLORS:")
    print("-"*40)
    
    # Display foreground colors
    for name, code in fg_colors.items():
        ansi_seq = f'\\033[{code}m'
        colored_text = f'\033[{code}m{name.ljust(15)}\033[0m'
        print(f"{colored_text} {ansi_seq.ljust(10)} Example text")
    
    print("\nBACKGROUND COLORS:")
    print("-"*40)
    
    # Display background colors (with black or white text for contrast)
    for name, code in bg_colors.items():
        ansi_seq = f'\\033[{code}m'
        # Use white text for dark backgrounds, black for light backgrounds
        text_color = '97' if code in ['40', '41', '42', '43', '44', '45', '46', '100'] else '30'
        colored_bg = f'\033[{text_color}m\033[{code}m{name.ljust(15)}\033[0m'
        print(f"{colored_bg} {ansi_seq.ljust(10)} Example text")
    
    print("\nCOMBINATIONS (Foreground + Background):")
    print("-"*40)
    
    # Display some combinations
    combinations = [
        ('Bright White', 'Blue'),
        ('Yellow', 'Bright Black'),
        ('Bright Cyan', 'Magenta'),
        ('Bright Red', 'Bright Yellow'),
        ('Black', 'Bright White')
    ]
    
    for fg_name, bg_name in combinations:
        fg_code = fg_colors[fg_name]
        bg_code = bg_colors[bg_name]
        ansi_seq = f'\\033[{fg_code};{bg_code}m'
        colored_text = f'\033[{fg_code};{bg_code}m{fg_name + " on " + bg_name.ljust(25)}\033[0m'
        print(f"{colored_text} {ansi_seq.ljust(15)} Example text")
    
    print("\nUSAGE NOTES:")
    print("-"*40)
    print("1. All ANSI sequences start with \\033[ and end with m")
    print("2. Separate multiple codes with semicolons (e.g., \\033[31;44m)")
    print("3. Reset formatting with \\033[0m")
    print("="*80)

# Run the function
show_ansi_colors()
```

## How to Use This Function

1. Copy the entire code block into a Python file or directly into your Python interpreter.
2. Call the `show_ansi_colors()` function.
3. The function will display:
   - All foreground colors with their names and ANSI codes
   - All background colors with their names and ANSI codes
   - Some example combinations of foreground and background colors
   - Usage notes about ANSI escape sequences

## Features

- Shows standard 8 colors and their bright variants (16 colors total) for both foreground and background
- Displays the actual ANSI sequence that you can copy and use in your code
- Shows the colors rendered in your terminal for easy reference
- Includes some useful combinations of foreground and background colors
- Provides usage notes about ANSI escape sequences

The output will show each color with its name, the exact ANSI sequence needed to produce it, and an example of text in that color.
