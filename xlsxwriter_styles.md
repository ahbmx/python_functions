# Python Dictionary with Styles for XlsxWriter

Here's a comprehensive dictionary of styles for XlsxWriter that includes status styles and styles for different storage arrays and operating systems. All styles are centered both vertically and horizontally.

```python
import xlsxwriter

# Create a workbook and add a worksheet
workbook = xlsxwriter.Workbook('styles_demo.xlsx')
worksheet = workbook.add_worksheet()

# Define a base format with center alignment
base_format = {
    'align': 'center',
    'valign': 'vcenter',
    'border': 1
}

# Status styles
styles = {
    # Base formats
    'base': workbook.add_format({**base_format}),
    'base_bold': workbook.add_format({**base_format, 'bold': True}),
    
    # Status styles
    'disabled': workbook.add_format({
        **base_format,
        'bg_color': '#CCCCCC',  # Light gray
        'font_color': '#666666',
        'bold': True
    }),
    'offline': workbook.add_format({
        **base_format,
        'bg_color': '#FF9999',  # Light red
        'font_color': '#990000',
        'bold': True
    }),
    'online': workbook.add_format({
        **base_format,
        'bg_color': '#99FF99',  # Light green
        'font_color': '#006600',
        'bold': True
    }),
    'warning': workbook.add_format({
        **base_format,
        'bg_color': '#FFFF99',  # Light yellow
        'font_color': '#996600',
        'bold': True
    }),
    'success': workbook.add_format({
        **base_format,
        'bg_color': '#99FF99',  # Light green
        'font_color': '#006600',
        'bold': True
    }),
    'error': workbook.add_format({
        **base_format,
        'bg_color': '#FF9999',  # Light red
        'font_color': '#990000',
        'bold': True
    }),
    
    # Storage array styles
    'purestorage': workbook.add_format({
        **base_format,
        'bg_color': '#FFCCCC',  # Very light red
        'font_color': '#CC0000'
    }),
    'powermax': workbook.add_format({
        **base_format,
        'bg_color': '#CCE5FF',  # Very light blue
        'font_color': '#0066CC'
    }),
    'datadomain': workbook.add_format({
        **base_format,
        'bg_color': '#E5CCFF',  # Very light purple
        'font_color': '#6600CC'
    }),
    'teradata': workbook.add_format({
        **base_format,
        'bg_color': '#FFE5CC',  # Very light orange
        'font_color': '#CC6600'
    }),
    'netapp': workbook.add_format({
        **base_format,
        'bg_color': '#CCFFCC',  # Very light green
        'font_color': '#006600'
    }),
    
    # Operating system styles
    'linux': workbook.add_format({
        **base_format,
        'bg_color': '#FFFFCC',  # Light yellow
        'font_color': '#333300',
        'bold': True
    }),
    'windows': workbook.add_format({
        **base_format,
        'bg_color': '#CCFFFF',  # Light cyan
        'font_color': '#006666',
        'bold': True
    }),
    'vmware': workbook.add_format({
        **base_format,
        'bg_color': '#E6E6FA',  # Lavender
        'font_color': '#4B0082',
        'bold': True
    }),
    'aix': workbook.add_format({
        **base_format,
        'bg_color': '#FFE4E1',  # Misty rose
        'font_color': '#8B0000',
        'bold': True
    }),
    'solaris': workbook.add_format({
        **base_format,
        'bg_color': '#F0FFF0',  # Honeydew
        'font_color': '#2E8B57',
        'bold': True
    }),
    'hpux': workbook.add_format({
        **base_format,
        'bg_color': '#FFF0F5',  # Lavender blush
        'font_color': '#DB7093',
        'bold': True
    }),
    'freebsd': workbook.add_format({
        **base_format,
        'bg_color': '#F5F5DC',  # Beige
        'font_color': '#8B4513',
        'bold': True
    })
}

# Example usage:
worksheet.write('A1', 'Disabled', styles['disabled'])
worksheet.write('B1', 'Online', styles['online'])
worksheet.write('C1', 'Error', styles['error'])
worksheet.write('D1', 'Linux', styles['linux'])
worksheet.write('E1', 'Windows', styles['windows'])
worksheet.write('F1', 'Pure Storage', styles['purestorage'])

workbook.close()
```

## Style Breakdown:

### Status Styles:
1. **disabled**: Light gray background with dark gray text
2. **offline**: Light red background with dark red text
3. **online**: Light green background with dark green text
4. **warning**: Light yellow background with brown text
5. **success**: Light green background with dark green text (similar to online)
6. **error**: Light red background with dark red text (similar to offline)

### Storage Array Styles:
1. **purestorage**: Very light red background with red text
2. **powermax**: Very light blue background with blue text
3. **datadomain**: Very light purple background with purple text
4. **teradata**: Very light orange background with orange text
5. **netapp**: Very light green background with green text

### Operating System Styles:
1. **linux**: Light yellow background with dark yellow text
2. **windows**: Light cyan background with teal text
3. **vmware**: Lavender background with indigo text
4. **aix**: Misty rose background with dark red text
5. **solaris**: Honeydew background with sea green text
6. **hpux**: Lavender blush background with pale violet red text
7. **freebsd**: Beige background with saddle brown text

All styles include center alignment (both vertical and horizontal) and a border by default. You can adjust the colors or add more styles as needed.


https://atlassian.design/foundations/color-new/color-palette-new#picking-colors-for-dark-mode

