Here's a Python helper function that displays all ASCII color combinations with foreground and background:

```python
def show_ascii_colors():
    """
    Display all ASCII color combinations with foreground and background.
    Prints the escape codes so they can be easily copied.
    """
    
    # Color codes
    colors = {
        'black': 30,
        'red': 31,
        'green': 32,
        'yellow': 33,
        'blue': 34,
        'magenta': 35,
        'cyan': 36,
        'white': 37,
        'bright_black': 90,
        'bright_red': 91,
        'bright_green': 92,
        'bright_yellow': 93,
        'bright_blue': 94,
        'bright_magenta': 95,
        'bright_cyan': 96,
        'bright_white': 97
    }
    
    bg_colors = {
        'black': 40,
        'red': 41,
        'green': 42,
        'yellow': 43,
        'blue': 44,
        'magenta': 45,
        'cyan': 46,
        'white': 47,
        'bright_black': 100,
        'bright_red': 101,
        'bright_green': 102,
        'bright_yellow': 103,
        'bright_blue': 104,
        'bright_magenta': 105,
        'bright_cyan': 106,
        'bright_white': 107
    }
    
    styles = {
        'normal': 0,
        'bold': 1,
        'dim': 2,
        'italic': 3,
        'underline': 4,
        'blink': 5,
        'reverse': 7,
        'hidden': 8,
        'strikethrough': 9
    }
    
    print("=" * 80)
    print("ASCII COLOR CODES - Foreground & Background Combinations")
    print("=" * 80)
    print("\nFormat: \\033[style;fg;bgmText\\033[0m")
    print("Example: \\033[1;31;42mBold Red on Green\\033[0m\n")
    print("-" * 80)
    
    # Show individual foreground colors
    print("\n🔤 FOREGROUND COLORS ONLY:")
    print("-" * 40)
    for name, code in colors.items():
        print(f"\\033[{code}m{name:15} \\033[0m  Code: {code}")
    
    print("\n" + "-" * 80)
    
    # Show individual background colors
    print("\n🔤 BACKGROUND COLORS ONLY:")
    print("-" * 40)
    for name, code in bg_colors.items():
        print(f"\\033[{code}m{name:15} \\033[0m  Code: {code}")
    
    print("\n" + "-" * 80)
    
    # Show text styles
    print("\n🔤 TEXT STYLES:")
    print("-" * 40)
    for name, code in styles.items():
        print(f"\\033[{code}m{name:15} \\033[0m  Code: {code}")
    
    print("\n" + "-" * 80)
    
    # Show foreground + background combinations (sample)
    print("\n🎨 FOREGROUND + BACKGROUND COMBINATIONS (Sample):")
    print("-" * 40)
    
    fg_samples = ['red', 'green', 'blue', 'yellow', 'white']
    bg_samples = ['black', 'red', 'green', 'blue', 'yellow']
    
    for fg_name in fg_samples:
        for bg_name in bg_samples:
            fg_code = colors[fg_name]
            bg_code = bg_colors[bg_name]
            text = f"{fg_name} on {bg_name}"
            print(f"\\033[{fg_code};{bg_code}m{text:20}\\033[0m  Code: {fg_code};{bg_code}")
        print()
    
    print("\n" + "-" * 80)
    
    # Show all combinations with style (dense grid)
    print("\n🎨 ALL COLOR COMBINATIONS GRID:")
    print("-" * 40)
    print("FG\\BG  ", end="")
    for bg_name in ['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']:
        print(f"{bg_name[:6]:>7}", end="")
    print()
    
    for fg_name in ['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']:
        print(f"{fg_name[:6]:<6}", end="")
        for bg_name in ['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']:
            fg_code = colors[fg_name]
            bg_code = bg_colors[bg_name]
            print(f"\\033[{fg_code};{bg_code}m  X  \\033[0m", end="")
        print()
    
    print("\n" + "=" * 80)
    print("💡 TIPS:")
    print("• Use \\033[code1;code2;code3m for multiple effects")
    print("• Always reset with \\033[0m")
    print("• Combine: \\033[1;31;42m = Bold + Red FG + Green BG")
    print("=" * 80)


def get_color_code(fg_color=None, bg_color=None, style='normal'):
    """
    Helper to get ASCII escape code for a specific combination.
    
    Args:
        fg_color (str): Foreground color name (e.g., 'red', 'bright_blue')
        bg_color (str): Background color name (e.g., 'yellow', 'bright_green')
        style (str): Style name (e.g., 'bold', 'underline')
    
    Returns:
        str: The complete escape sequence
    """
    colors = {
        'black': 30, 'red': 31, 'green': 32, 'yellow': 33,
        'blue': 34, 'magenta': 35, 'cyan': 36, 'white': 37,
        'bright_black': 90, 'bright_red': 91, 'bright_green': 92,
        'bright_yellow': 93, 'bright_blue': 94, 'bright_magenta': 95,
        'bright_cyan': 96, 'bright_white': 97
    }
    
    bg_colors = {
        'black': 40, 'red': 41, 'green': 42, 'yellow': 43,
        'blue': 44, 'magenta': 45, 'cyan': 46, 'white': 47,
        'bright_black': 100, 'bright_red': 101, 'bright_green': 102,
        'bright_yellow': 103, 'bright_blue': 104, 'bright_magenta': 105,
        'bright_cyan': 106, 'bright_white': 107
    }
    
    styles = {
        'normal': 0, 'bold': 1, 'dim': 2, 'italic': 3,
        'underline': 4, 'blink': 5, 'reverse': 7,
        'hidden': 8, 'strikethrough': 9
    }
    
    codes = []
    codes.append(str(styles.get(style, 0)))
    
    if fg_color and fg_color in colors:
        codes.append(str(colors[fg_color]))
    
    if bg_color and bg_color in bg_colors:
        codes.append(str(bg_colors[bg_color]))
    
    return f"\\033[{';'.join(codes)}m"


def print_colored(text, fg_color=None, bg_color=None, style='normal'):
    """
    Print colored text using ASCII escape codes.
    
    Args:
        text (str): Text to print
        fg_color (str): Foreground color name
        bg_color (str): Background color name
        style (str): Style name
    """
    code = get_color_code(fg_color, bg_color, style)
    print(f"{code}{text}\\033[0m")
    print(f"Code used: {code}")


# Example usage
if __name__ == "__main__":
    # Show all available colors
    show_ascii_colors()
    
    print("\n" + "=" * 80)
    print("EXAMPLES:")
    print("=" * 80)
    
    # Example 1: Using the helper functions
    print_colored("This is bold red text on green background", 
                  fg_color='red', bg_color='green', style='bold')
    
    print_colored("This is bright blue on yellow background", 
                  fg_color='bright_blue', bg_color='yellow')
    
    print_colored("This is underlined cyan text", 
                  fg_color='cyan', style='underline')
    
    # Example 2: Direct usage
    print("\nDirect usage examples:")
    print("\\033[1;31;42mBold Red on Green\\033[0m")
    print("\\033[4;36mUnderlined Cyan\\033[0m")
    print("\\033[93;44mBright Yellow on Blue\\033[0m")
    
    # Example 3: Show a specific code
    code = get_color_code('magenta', 'cyan', 'bold')
    print(f"\nCode for bold magenta on cyan: {code}")
```

## How to use:

1. **Show all colors**: Just call `show_ascii_colors()` to see everything available

2. **Get a specific color code**: 
   ```python
   code = get_color_code('red', 'yellow', 'bold')
   print(f"{code}This is red on yellow{code}")
   ```

3. **Print colored text easily**:
   ```python
   print_colored("Hello World", fg_color='bright_blue', bg_color='yellow', style='bold')
   ```

4. **Direct usage** in your strings:
   ```python
   print("\033[1;31;42mBold Red on Green\033[0m")
   ```

The function displays:
- All foreground color codes
- All background color codes
- All text styles (bold, underline, etc.)
- Sample combinations
- A complete grid of all foreground/background combinations
- The exact escape codes you can copy and paste

The codes follow the format: `\033[style;foreground;backgroundm` where:
- `style`: 0=normal, 1=bold, 4=underline, etc.
- `foreground`: 30-37 (normal), 90-97 (bright)
- `background`: 40-47 (normal), 100-107 (bright)
