You're right to notice that the background color might not be working as expected in the previous implementation. Let me fix that and provide you with a corrected version that properly handles background colors.

## Fixed Version with Working Background Colors

```python
def color_text(text, fg=None, bg=None, style=None, reset=True):
    """
    Colorize text using ANSI escape codes for Linux console.
    
    Parameters:
    - text: The text to colorize
    - fg: Foreground color (name or code)
    - bg: Background color (name or code)
    - style: Text style (name or code)
    - reset: Whether to reset formatting at the end (default: True)
    
    Returns:
    - String with ANSI escape codes for coloring
    
    Color Options:
    - Foreground: black, red, green, yellow, blue, magenta, cyan, white,
                  bright_black, bright_red, bright_green, bright_yellow,
                  bright_blue, bright_magenta, bright_cyan, bright_white,
                  or 0-255 for 256-color mode, or (r,g,b) for true color
    
    - Background: same as foreground but prefixed with 'bg_' (e.g., 'bg_red')
    
    - Styles: bold, dim, italic, underline, blink, reverse, hidden, strike
    """
    
    # Reset code
    RESET = '\033[0m'
    
    # Foreground color codes (8/16 colors)
    FG_COLORS = {
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
        'bright_white': 97,
    }
    
    # Background color codes (8/16 colors)
    BG_COLORS = {
        'bg_black': 40,
        'bg_red': 41,
        'bg_green': 42,
        'bg_yellow': 43,
        'bg_blue': 44,
        'bg_magenta': 45,
        'bg_cyan': 46,
        'bg_white': 47,
        'bg_bright_black': 100,
        'bg_bright_red': 101,
        'bg_bright_green': 102,
        'bg_bright_yellow': 103,
        'bg_bright_blue': 104,
        'bg_bright_magenta': 105,
        'bg_bright_cyan': 106,
        'bg_bright_white': 107,
    }
    
    # Style codes
    STYLES = {
        'bold': 1,
        'dim': 2,
        'italic': 3,
        'underline': 4,
        'blink': 5,
        'reverse': 7,
        'hidden': 8,
        'strike': 9,
    }
    
    codes = []
    
    # Process foreground color
    if fg is not None:
        if isinstance(fg, str):
            if fg in FG_COLORS:
                codes.append(FG_COLORS[fg])
            elif fg.startswith('#'):
                # Hex color (true color)
                r, g, b = int(fg[1:3], 16), int(fg[3:5], 16), int(fg[5:7], 16)
                codes.extend([38, 2, r, g, b])
        elif isinstance(fg, (tuple, list)) and len(fg) == 3:
            # RGB tuple (true color)
            codes.extend([38, 2, fg[0], fg[1], fg[2]])
        elif isinstance(fg, int) and 0 <= fg <= 255:
            # 256-color mode
            codes.extend([38, 5, fg])
    
    # Process background color
    if bg is not None:
        if isinstance(bg, str):
            if bg.startswith('bg_'):
                # Named background color
                if bg in BG_COLORS:
                    codes.append(BG_COLORS[bg])
            elif bg.startswith('#'):
                # Hex color (true color)
                r, g, b = int(bg[1:3], 16), int(bg[3:5], 16), int(bg[5:7], 16)
                codes.extend([48, 2, r, g, b])
        elif isinstance(bg, (tuple, list)) and len(bg) == 3:
            # RGB tuple (true color)
            codes.extend([48, 2, bg[0], bg[1], bg[2]])
        elif isinstance(bg, int) and 0 <= bg <= 255:
            # 256-color mode
            codes.extend([48, 5, bg])
    
    # Process style
    if style is not None:
        if isinstance(style, str):
            if style in STYLES:
                codes.append(STYLES[style])
        elif isinstance(style, (list, tuple)):
            for s in style:
                if s in STYLES:
                    codes.append(STYLES[s])
    
    # Build the ANSI escape sequence
    if codes:
        ansi_code = '\033[' + ';'.join(map(str, codes)) + 'm'
        result = ansi_code + text
        if reset:
            result += RESET
        return result
    return text


# Example usage with background colors
if __name__ == "__main__":
    # Basic background colors
    print(color_text("White text on red background", fg='white', bg='bg_red'))
    print(color_text("Black text on bright green background", fg='black', bg='bg_bright_green'))
    
    # 256-color background
    print(color_text("Text with 256-color background", fg='white', bg=196))  # bright red
    
    # True color background
    print(color_text("Text with RGB background", fg='black', bg=(255, 200, 150)))
    print(color_text("Text with hex background", fg='white', bg='#303030'))
    
    # Combination of foreground, background and style
    print(color_text("Bold yellow on blue background", 
                    fg='yellow', bg='bg_blue', style='bold'))
    
    # All background colors demonstration
    bg_colors = ['bg_black', 'bg_red', 'bg_green', 'bg_yellow', 'bg_blue', 
                'bg_magenta', 'bg_cyan', 'bg_white', 'bg_bright_black', 
                'bg_bright_red', 'bg_bright_green', 'bg_bright_yellow',
                'bg_bright_blue', 'bg_bright_magenta', 'bg_bright_cyan', 
                'bg_bright_white']
    
    print("\nAll background colors with black text:")
    for bg_color in bg_colors:
        print(color_text(f"{bg_color:20}", fg='black', bg=bg_color))
    
    print("\nAll background colors with white text:")
    for bg_color in bg_colors:
        print(color_text(f"{bg_color:20}", fg='white', bg=bg_color))
```

## Key Fixes:

1. **Background Color Handling**:
   - The original version didn't properly handle the `bg_` prefix for named background colors
   - Now explicitly checks for `bg_` prefix when processing named background colors

2. **Color Code Separation**:
   - Ensured foreground and background codes are properly separated in the ANSI sequence

3. **Demonstration Examples**:
   - Added more comprehensive examples showing background colors working
   - Included demonstrations of all background colors with both black and white text

## How to Use Background Colors:

1. **Named Colors**: Use `bg='bg_red'`, `bg='bg_bright_green'`, etc.
2. **256-color Mode**: Use `bg=196` (where 196 is a color index 0-255)
3. **RGB Tuples**: Use `bg=(255, 0, 0)` for pure red background
4. **Hex Colors**: Use `bg='#FF0000'` for pure red background

This fixed version should now properly display all background colors in your Linux terminal.
