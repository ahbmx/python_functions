# Python Regex to Parse the Given Output

Here's a Python solution using regex to parse the provided output:

```python
import re

output = """   0    3    0   010000   id    N32    Online      FC  F-Port  86:0d:00:11:0d:06:00:00 
   1    3    1   010100   id    N32    Online      FC  F-Port  86:24:00:11:0d:07:00:00
   2    3    2   010200   id    N32    Online      FC  F-Port  86:0c:00:11:0d:05:00:00 
   3    3    3   010300   id    N32    Online      FC  F-Port  86:25:00:11:0d:08:00:00
   4    3    4   010400   id    N32    Online      FC  F-Port  21:00:00:24:ff:90:55:30
   5    3    5   010500   id    N32    Online      FC  F-Port  21:00:00:24:ff:90:55:31
   6    3    6   010600   id    N32    Online      FC  F-Port  21:00:00:24:ff:90:55:9e
   7    3    7   010700   id    N32    ONline      FC  F-Port  21:00:00:24:ff:90:55:9f 
   8    3    8   010800   id    N32    Online      FC  E-Port  10:00:00:27:f8:f2:c8:b8 
   9    3    9   010900   id    N32    Online      FC  E-Port  10:00:00:27:f8:f2:c6:b8 "ras010" (Trunk master) 
  10    3   10   010a00   id    N32    Online      FC  E-Port  10:00:00:27:f8:f2:c7:b8 "ras010" (Trunk master)
  11    3   11   010b00   id    N32    Online      FC  E-Port  10:00:00:27:f8:f2:c8:b8 "ras010" (Trunk master)  
  12    3   12   010c00   --    N32    No_Module   FC   
  13    3   13   010d00   --    N32    No_Module   FC 
  14    3   14   010e00   --    N32    No_Module   FC 
  15    3   15   010f00   --    N32    No_Module   FC 
 128    3   16   018000   --    N32    No_Module   FC 
 129    3   17   018100   --    N32    No_Module   FC  
 130    3   18   018200   id    N32    Online      FC  E-Port  10:00:50:eb:1a:f6:6c:68 "ras006" (Trunk master)
 131    3   19   018300   id    N32    Online      FC  E-Port  10:00:51:ee:1a:f6:6c:68 "ras006" (Trunk master)
 132    3   20   018400   id    N32    Online      FC  E-Port  10:00:52:ee:1a:f6:6c:68 "ras006" (Trunk master)"""

# Define the regex pattern
pattern = re.compile(
    r'^\s*(?P<index>\d+)\s+'  # First column (index)
    r'(?P<col2>\d+)\s+'       # Second column
    r'(?P<col3>\d+)\s+'       # Third column
    r'(?P<hex_code>[0-9a-fA-F]+)\s+'  # Hex code
    r'(?P<id>\S+)\s+'         # id/--
    r'(?P<n32>N32)\s+'        # N32
    r'(?P<status>[A-Za-z_]+)\s+'  # Status
    r'(?P<fc>FC)\s*'          # FC
    r'(?:(?P<port_type>[EF]-Port)\s+'  # Port type (optional)
    r'(?P<wwpn>(?:[0-9a-fA-F]{2}:){7}[0-9a-fA-F]{2})\s*'  # WWPN (optional)
    r'(?:"(?P<name>[^"]+)"\s*'  # Name in quotes (optional)
    r'(?:\((?P<trunk>[^)]+)\)\s*)?)?)?',  # Trunk info (optional)
    re.MULTILINE
)

# Parse all matches
parsed_data = []
for match in pattern.finditer(output):
    row = match.groupdict()
    parsed_data.append(row)

# Example: Print parsed data
for item in parsed_data:
    print(item)
```

## Explanation:

1. The regex pattern breaks down each line into named capture groups:
   - `index`: First numeric column
   - `col2`, `col3`: Next two numeric columns
   - `hex_code`: The hexadecimal code
   - `id`: Either "id" or "--"
   - `n32`: Always "N32"
   - `status`: Status like "Online" or "No_Module"
   - `fc`: Always "FC"
   - `port_type`: Optional "F-Port" or "E-Port"
   - `wwpn`: Optional WWPN (8-byte FC address)
   - `name`: Optional name in quotes
   - `trunk`: Optional trunk information

2. The `re.MULTILINE` flag allows matching the start (^) of each line in a multi-line string.

3. The pattern handles both complete lines (with all fields) and incomplete lines (like the No_Module cases).

4. The results are stored as dictionaries with the named groups, making it easy to access each field.

You can then process the `parsed_data` list as needed - for example, filtering for only Online ports, extracting specific fields, etc.
