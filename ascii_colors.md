You're right! The issue is that the escape sequences need to be interpreted by the terminal, but when we print them with double backslashes (`\\033`), they're printed as literal text. Let me fix this so the colors actually display:

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
    
    RESET = '\033[0m'
    
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
        # Display the color AND show the code
        print(f"\033[{code}m{name:15} \033[0m  Code: {code}")
    
    print("\n" + "-" * 80)
    
    # Show individual background colors
    print("\n🔤 BACKGROUND COLORS ONLY:")
    print("-" * 40)
    for name, code in bg_colors.items():
        print(f"\033[{code}m{name:15} \033[0m  Code: {code}")
    
    print("\n" + "-" * 80)
    
    # Show text styles
    print("\n🔤 TEXT STYLES:")
    print("-" * 40)
    for name, code in styles.items():
        print(f"\033[{code}m{name:15} \033[0m  Code: {code}")
    
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
            # Display with color AND show the code
            print(f"\033[{fg_code};{bg_code}m{text:20}\033[0m  Code: {fg_code};{bg_code}")
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
            # Display colored block
            print(f"\033[{fg_code};{bg_code}m  X  \033[0m", end="")
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
        str: The complete escape sequence (ready to use)
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
    
    # Return the actual escape sequence (not escaped)
    return f"\033[{';'.join(codes)}m"


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
    reset = '\033[0m'
    print(f"{code}{text}{reset}")
    # Show the code that was used (escaped for display)
    display_code = code.replace('\033', '\\033')
    print(f"Code used: {display_code}")


def show_code_only(fg_color=None, bg_color=None, style='normal'):
    """
    Just show the escape code without applying it.
    Useful for copying.
    """
    code = get_color_code(fg_color, bg_color, style)
    display_code = code.replace('\033', '\\033')
    print(f"Copy this: {display_code}")


# Example usage
if __name__ == "__main__":
    # Show all available colors (with actual colors displayed)
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
    
    # Example 2: Show code only (for copying)
    print("\n" + "-" * 40)
    print("COPY THESE CODES:")
    print("-" * 40)
    show_code_only('red', 'green', 'bold')
    show_code_only('bright_blue', 'yellow')
    show_code_only('cyan', None, 'underline')
    
    # Example 3: Direct usage
    print("\nDirect usage examples (copy these):")
    print("\\033[1;31;42mBold Red on Green\\033[0m")
    print("\\033[4;36mUnderlined Cyan\\033[0m")
    print("\\033[93;44mBright Yellow on Blue\\033[0m")
    
    # Example 4: Get code as variable
    my_code = get_color_code('magenta', 'cyan', 'bold')
    print(f"\n{my_code}This is bold magenta on cyan{'\033[0m'}")
    print(f"Code used: {my_code.replace('\033', '\\033')}")
```

The key changes:
1. **Removed double backslashes** - Now using `\033` (actual escape character) instead of `\\033` (literal backslash)
2. **Added RESET variable** - Using `\033[0m` to reset colors after each display
3. **Both display AND show codes** - The text displays in color, and the code is shown next to it
4. **Added `show_code_only()`** - A helper to just display the code you need to copy

Now when you run this, you'll see:
- ✅ Actual colors displayed in your terminal
- ✅ The escape codes shown next to each color for easy copying
- ✅ Helper functions to generate codes for your own use

To copy a code, just look at what's displayed next to the colored text. For example, you'll see something like:
```
red              Code: 31        (with red text)
Bold Red on Green Code: 1;31;42  (with bold red on green text)
```
