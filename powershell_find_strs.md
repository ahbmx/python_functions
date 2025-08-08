Here's a PowerShell script that recursively searches through multiple directories for `.py` files containing any of the specified strings ('symaccess', 'symcfg', 'symrdf'):

```powershell
<#
.SYNOPSIS
    Searches for .py files containing specific strings recursively in multiple directories.
.DESCRIPTION
    This script searches through specified directories (and their subdirectories) for Python files (.py)
    that contain any of the specified strings ('symaccess', 'symcfg', 'symrdf').
.PARAMETER Directories
    The directories to search in. If not specified, searches in the current directory.
.PARAMETER OutputFile
    Path to save the results. If not specified, results are displayed in the console.
.EXAMPLE
    .\Search-PyFiles.ps1 -Directories "C:\Project1", "D:\Project2" -OutputFile "results.txt"
#>

param(
    [Parameter(Mandatory=$false)]
    [string[]]$Directories = @("."),  # Default to current directory
    
    [Parameter(Mandatory=$false)]
    [string]$OutputFile = $null
)

# Strings to search for
$searchStrings = @('symaccess', 'symcfg', 'symrdf')

# Prepare the regex pattern (matches any of the strings)
$pattern = $searchStrings -join '|'

# Initialize results collection
$results = @()

foreach ($dir in $Directories) {
    # Get all .py files recursively
    $pyFiles = Get-ChildItem -Path $dir -Filter "*.py" -Recurse -File -ErrorAction SilentlyContinue

    foreach ($file in $pyFiles) {
        # Check if file contains any of the search strings
        $content = Get-Content -Path $file.FullName -Raw
        $matches = Select-String -InputObject $content -Pattern $pattern -AllMatches
        
        if ($matches.Matches.Count -gt 0) {
            $result = [PSCustomObject]@{
                FilePath = $file.FullName
                Matches = $matches.Matches.Count
                MatchingLines = ($content -split "`n" | Select-String -Pattern $pattern).Line
            }
            $results += $result
        }
    }
}

# Output results
if ($OutputFile) {
    $results | Format-List | Out-File -FilePath $OutputFile
    Write-Host "Results saved to $OutputFile"
} else {
    $results | Format-List
}

Write-Host "Search complete. Found $($results.Count) files containing the specified strings."
```

### How to use this script:

1. Save it as `Search-PyFiles.ps1`
2. Run it with default parameters (searches current directory):
   ```powershell
   .\Search-PyFiles.ps1
   ```
3. Or specify directories to search:
   ```powershell
   .\Search-PyFiles.ps1 -Directories "C:\Project1", "D:\Project2"
   ```
4. To save results to a file:
   ```powershell
   .\Search-PyFiles.ps1 -Directories "C:\Project1" -OutputFile "results.txt"
   ```

### Features:
- Recursively searches through directories
- Looks for any of the three specified strings
- Reports file path, total matches, and the matching lines
- Can output to console or file
- Handles errors gracefully (skips inaccessible directories)

You can easily modify the `$searchStrings` array to look for different strings if needed.
