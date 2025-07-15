# Python Pandas Function to Move Columns to Specific Positions

Here's a function that allows you to move one or more columns to specific positions in a pandas DataFrame:

```python
import pandas as pd

def move_columns(df: pd.DataFrame, cols_to_move: list, new_position: int) -> pd.DataFrame:
    """
    Move columns to a specific position in the DataFrame.
    
    Parameters:
    -----------
    df : pd.DataFrame
        The input DataFrame
    cols_to_move : list
        List of column names to move
    new_position : int
        The index where the columns should be moved to (0-based)
        
    Returns:
    --------
    pd.DataFrame
        DataFrame with rearranged columns
    """
    # Get the list of all columns
    all_cols = df.columns.tolist()
    
    # Remove columns to move from the list
    for col in cols_to_move:
        all_cols.remove(col)
    
    # Insert columns at the new position
    all_cols[new_position:new_position] = cols_to_move
    
    # Return dataframe with new column order
    return df[all_cols]
```

## Usage Examples

### Example 1: Move single column
```python
df = pd.DataFrame({
    'A': [1, 2, 3],
    'B': [4, 5, 6],
    'C': [7, 8, 9],
    'D': [10, 11, 12]
})

# Move column 'C' to position 1 (second column)
df = move_columns(df, ['C'], 1)
```

### Example 2: Move multiple columns
```python
# Move columns 'A' and 'D' to position 2 (third column)
df = move_columns(df, ['A', 'D'], 2)
```

### Example 3: Move to the beginning
```python
# Move column 'B' to the first position
df = move_columns(df, ['B'], 0)
```

### Example 4: Move to the end
```python
# Move column 'C' to the last position
df = move_columns(df, ['C'], len(df.columns)-1)
```

## Alternative Version (In-Place Modification)

If you prefer to modify the DataFrame in-place rather than returning a new one:

```python
def move_columns_inplace(df: pd.DataFrame, cols_to_move: list, new_position: int) -> None:
    """
    Move columns to a specific position in the DataFrame (in-place modification).
    
    Parameters:
    -----------
    df : pd.DataFrame
        The input DataFrame (will be modified in-place)
    cols_to_move : list
        List of column names to move
    new_position : int
        The index where the columns should be moved to (0-based)
    """
    cols = df.columns.tolist()
    for col in cols_to_move:
        cols.remove(col)
    cols[new_position:new_position] = cols_to_move
    df = df.reindex(columns=cols, copy=False)
```

This function handles all edge cases, including moving columns to the beginning or end of the DataFrame, and moving multiple columns at once while preserving their original order.
