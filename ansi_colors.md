Here's an enhanced Python function that displays **all ANSI colors, backgrounds, and text styles** (bold, underline, etc.) in an organized way, with clear labels for easy selection:

```python
def show_ansi_colors():
    """
    Displays all ANSI colors, backgrounds, styles, and combinations with labels.
    """
    reset = "\033[0m"
    
    # Styles (additive - can be combined)
    styles = {
        'Normal': 0,
        'Bold': 1,
        'Dim': 2,
        'Italic': 3,
        'Underline': 4,
        'Blink': 5,
        'Reverse': 7,
        'Hidden': 8,
        'Strikethrough': 9
    }
    
    # Foreground colors (standard and bright)
    fg_colors = {
        'Black': 30,
        'Red': 31,
        'Green': 32,
        'Yellow': 33,
        'Blue': 34,
        'Magenta': 35,
        'Cyan': 36,
        'White': 37,
        'Bright Black': 90,
        'Bright Red': 91,
        'Bright Green': 92,
        'Bright Yellow': 93,
        'Bright Blue': 94,
        'Bright Magenta': 95,
        'Bright Cyan': 96,
        'Bright White': 97
    }
    
    # Background colors (standard and bright)
    bg_colors = {
        'Black': 40,
        'Red': 41,
        'Green': 42,
        'Yellow': 43,
        'Blue': 44,
        'Magenta': 45,
        'Cyan': 46,
        'White': 47,
        'Bright Black': 100,
        'Bright Red': 101,
        'Bright Green': 102,
        'Bright Yellow': 103,
        'Bright Blue': 104,
        'Bright Magenta': 105,
        'Bright Cyan': 106,
        'Bright White': 107
    }
    
    # Print all text styles
    print("\n=== TEXT STYLES ===")
    for name, code in styles.items():
        print(f"\033[{code}m{name.ljust(15)}\033[0m", end=" ")
        if list(styles.keys()).index(name) % 4 == 3:
            print()
    
    # Print foreground colors
    print("\n\n=== FOREGROUND COLORS ===")
    for name, code in fg_colors.items():
        print(f"\033[{code}m{name.ljust(15)}\033[0m", end=" ")
        if list(fg_colors.keys()).index(name) % 4 == 3:
            print()
    
    # Print background colors
    print("\n\n=== BACKGROUND COLORS ===")
    for name, code in bg_colors.items():
        print(f"\033[{code}m{' ' * 15}\033[0m {name.ljust(15)}", end=" ")
        if list(bg_colors.keys()).index(name) % 4 == 3:
            print()
    
    # Print style + color combinations
    print("\n\n=== STYLE + COLOR COMBINATIONS ===")
    for style_name, style_code in styles.items():
        print(f"\n** {style_name} **")
        for fg_name, fg_code in fg_colors.items():
            print(f"\033[{style_code};{fg_code}m{fg_name.ljust(15)}\033[0m", end=" ")
            if list(fg_colors.keys()).index(fg_name) % 4 == 3:
                print()
    
    # Print full combinations (style + fg + bg)
    print("\n\n=== FULL COMBINATIONS (STYLE + FG + BG) ===")
    for style_name, style_code in styles.items():
        print(f"\n--- {style_name} ---")
        for fg_name, fg_code in fg_colors.items():
            for bg_name, bg_code in bg_colors.items():
                combo = f"{fg_name} on {bg_name}"
                print(f"\033[{style_code};{fg_code};{bg_code}m{combo.ljust(30)}\033[0m", end=" ")
                if list(bg_colors.keys()).index(bg_name) % 2 == 1:
                    print()
            print()

if __name__ == "__main__":
    show_ansi_colors()
```

### Key Features:
1. **Text Styles**: Shows all 9 text styles (bold, underline, etc.)
2. **Colors**: 16 foreground and 16 background colors
3. **Combinations**:
   - Style + Foreground color
   - Style + Foreground + Background
4. **Clear Labeling**: Every combination is labeled for easy reference
5. **Organized Layout**: Grid-based display for readability

### Example Output Snippet:
```
=== TEXT STYLES ===
Normal          Bold            Dim             Italic         
Underline       Blink           Reverse         Hidden         
Strikethrough   

=== FOREGROUND COLORS ===
Black           Red             Green           Yellow         
Blue            Magenta         Cyan            White          
Bright Black    Bright Red      Bright Green    Bright Yellow  
Bright Blue     Bright Magenta  Bright Cyan     Bright White   

=== FULL COMBINATIONS (STYLE + FG + BG) ===
--- Bold ---
Black on Black             Black on Red              
Black on Green             Black on Yellow           
...
Bright White on Bright Cyan Bright White on Bright White
```

### Usage Tips:
- Copy the ANSI codes directly from the labels
- Combine multiple styles by separating codes with semicolons (e.g., `\033[1;4;31m` = bold + underline + red)
- Not all terminals support every style (especially blink/hidden)

Want me to add anything else, like 256-color mode or RGB support?
