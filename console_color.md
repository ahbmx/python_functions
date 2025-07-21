# Python Function for ANSI Color Output in Linux Console

Here's a comprehensive Python function to color text output in the Linux console using ANSI escape codes. It includes extensive color combinations for both foreground and background.

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


# Example usage
if __name__ == "__main__":
    # Basic 8/16 colors
    print(color_text("Red text", fg='red'))
    print(color_text("Green text on yellow", fg='green', bg='yellow'))
    print(color_text("Bold blue text", fg='blue', style='bold'))
    
    # Bright colors
    print(color_text("Bright cyan", fg='bright_cyan'))
    print(color_text("White on bright magenta", fg='white', bg='bright_magenta'))
    
    # 256-color mode
    print(color_text("Color 201 (pink)", fg=201))
    print(color_text("Color 123 on 45", fg=123, bg=45))
    
    # True color (RGB)
    print(color_text("Custom RGB color", fg=(255, 128, 0)))
    print(color_text("Hex color", fg='#FF00FF'))
    print(color_text("RGB text on hex background", 
                    fg=(100, 200, 50), bg='#303030'))
    
    # Multiple styles
    print(color_text("Bold, italic, underlined", 
                    fg='bright_red', style=['bold', 'italic', 'underline']))
    
    # All 16 colors demonstration
    colors = ['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white',
             'bright_black', 'bright_red', 'bright_green', 'bright_yellow',
             'bright_blue', 'bright_magenta', 'bright_cyan', 'bright_white']
    
    print("\nAll 16 foreground colors:")
    for color in colors:
        print(color_text(f"{color:15}", fg=color))
    
    print("\nAll 16 background colors:")
    for color in colors:
        print(color_text(f"{'bg_'+color:20}", bg=color))
```

## Features:

1. **Foreground Colors**:
   - Standard 8 colors (30-37)
   - Bright variants (90-97)
   - 256-color mode (38;5;n)
   - True color/RGB mode (38;2;r;g;b)

2. **Background Colors**:
   - Standard 8 colors (40-47)
   - Bright variants (100-107)
   - 256-color mode (48;5;n)
   - True color/RGB mode (48;2;r;g;b)

3. **Text Styles**:
   - Bold, dim, italic, underline
   - Blink, reverse, hidden, strike-through

4. **Input Formats**:
   - Named colors ('red', 'bright_blue')
   - 256-color index (0-255)
   - RGB tuples (0-255, 0-255, 0-255)
   - Hex strings ('#RRGGBB')

5. **Automatic Reset**:
   - Option to automatically reset formatting after text

The function provides a flexible way to colorize terminal output with support for all modern terminal color capabilities.
