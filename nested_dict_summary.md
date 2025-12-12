Perfect! Let’s build a fully **recursive version** that works for any depth of nesting and prints a nice **summary table** showing the path to each innermost dictionary and the number of rows it would produce in a DataFrame.

Here’s a complete example:

```python
from collections import defaultdict
import pandas as pd

# Example nested defaultdict
dfs_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
dfs_dict['brocade']['firmwareshow']['switch_name'].extend(['sw1','sw2'])
dfs_dict['brocade']['firmwareshow']['cp_id'].extend([101,102])
dfs_dict['cisco']['interfaces']['interface_name'].extend(['eth0','eth1','eth2'])
dfs_dict['cisco']['interfaces']['status'].extend(['up','down','up'])
dfs_dict['cisco']['routes']['destination'].extend(['10.0.0.0','192.168.1.0'])
dfs_dict['cisco']['routes']['next_hop'].extend(['1.1.1.1','2.2.2.2'])

# Recursive function to find innermost dicts and row counts
def collect_row_counts(d, path=None, result=None):
    if path is None:
        path = []
    if result is None:
        result = []
        
    for k, v in d.items():
        current_path = path + [k]
        if isinstance(v, dict):
            # check if it contains lists (innermost level)
            if all(isinstance(val, list) for val in v.values()):
                # take length of first list (assumes all lists same length)
                num_rows = len(next(iter(v.values()))) if v else 0
                result.append({"Path": " -> ".join(current_path), "Rows": num_rows})
            else:
                # keep recursing
                collect_row_counts(v, current_path, result)
    return result

# Collect summary
summary = collect_row_counts(dfs_dict)

# Convert to pandas DataFrame for pretty table
summary_df = pd.DataFrame(summary)
print(summary_df)
```

**Output:**

```
                     Path  Rows
0  brocade -> firmwareshow     2
1      cisco -> interfaces     3
2          cisco -> routes     2
```

---

### ✅ Features

1. Works for **any depth** of nesting.
2. Prints a **clear summary table** with the path and the number of rows.
3. Assumes **all lists in an innermost dict have the same length**.
4. You can later loop through `summary_df` to automatically create DataFrames if needed.

---

If you want, I can also modify it so it **checks if the lists in a group have inconsistent lengths** and warns you, which is very useful to avoid `NaN` surprises in DataFrames.

Do you want me to add that check?
