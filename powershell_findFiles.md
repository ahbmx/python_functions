This error occurs when you're running PowerShell in Constrained Language Mode. Here's a simplified version that should work in restricted environments:

```powershell
# Simple File System Analyzer
# Works in Constrained Language Mode

param(
    [string]$Path = ".",
    [string]$OutputFile
)

function Get-EmptyFolders {
    param([string]$SearchPath)
    
    $emptyFolders = @()
    $allFolders = Get-ChildItem -Path $SearchPath -Directory -Recurse -ErrorAction SilentlyContinue
    
    foreach ($folder in $allFolders) {
        try {
            $items = Get-ChildItem -Path $folder.FullName -ErrorAction SilentlyContinue
            if ($items -eq $null -or $items.Count -eq 0) {
                $emptyFolders += $folder
            }
        }
        catch {
            # Skip folders we can't access
        }
    }
    
    return $emptyFolders
}

function Get-FileInfoSimple {
    param([string]$SearchPath)
    
    $files = Get-ChildItem -Path $SearchPath -File -Recurse -ErrorAction SilentlyContinue
    
    $fileInfo = @()
    foreach ($file in $files) {
        $fileInfo += New-Object PSObject -Property @{
            Name = $file.Name
            FullPath = $file.FullName
            Directory = $file.DirectoryName
            Size = $file.Length
            LastAccessTime = $file.LastAccessTime
            LastWriteTime = $file.LastWriteTime
            Extension = $file.Extension
        }
    }
    
    return $fileInfo | Sort-Object FullPath
}

# Main execution
try {
    # Validate path
    if (-not (Test-Path -Path $Path)) {
        Write-Host "Error: Path '$Path' does not exist" -ForegroundColor Red
        exit 1
    }

    $absolutePath = (Resolve-Path $Path).Path
    Write-Host "Scanning directory: $absolutePath"
    Write-Host "=============================================="

    # Get empty folders
    Write-Host "Finding empty folders..."
    $emptyFolders = Get-EmptyFolders -SearchPath $Path
    
    # Get file information
    Write-Host "Gathering file information..."
    $fileInfo = Get-FileInfoSimple -SearchPath $Path

    # Display results
    Write-Host "`nEMPTY FOLDERS ($($emptyFolders.Count) found):"
    Write-Host "=============================================="
    if ($emptyFolders.Count -gt 0) {
        foreach ($folder in $emptyFolders) {
            Write-Host $folder.FullName
        }
    } else {
        Write-Host "No empty folders found."
    }

    Write-Host "`nFILE INFORMATION ($($fileInfo.Count) files):"
    Write-Host "=============================================="
    
    # Simple table display
    foreach ($file in $fileInfo) {
        Write-Host ("{0,-40} {1,-12} {2} {3}" -f 
            $file.Name, 
            ("{0:N0} KB" -f ($file.Size/1KB)), 
            $file.LastAccessTime.ToString("yyyy-MM-dd"),
            $file.LastWriteTime.ToString("yyyy-MM-dd"))
    }

    # Export to file if specified
    if ($OutputFile) {
        try {
            $content = @()
            $content += "EMPTY FOLDERS REPORT"
            $content += "Generated on: $(Get-Date)"
            $content += "Search path: $absolutePath"
            $content += "=============================================="
            $content += ""
            
            if ($emptyFolders.Count -gt 0) {
                $content += "Empty folders found: $($emptyFolders.Count)"
                foreach ($folder in $emptyFolders) {
                    $content += $folder.FullName
                }
            } else {
                $content += "No empty folders found."
            }
            
            $content += ""
            $content += "FILE INFORMATION REPORT"
            $content += "=============================================="
            $content += "Total files: $($fileInfo.Count)"
            $content += ""
            
            foreach ($file in $fileInfo) {
                $content += "File: $($file.FullPath)"
                $content += "  Size: $([math]::Round($file.Size/1KB, 2)) KB"
                $content += "  Last Accessed: $($file.LastAccessTime)"
                $content += "  Last Modified: $($file.LastWriteTime)"
                $content += "----------------------------------------------"
            }
            
            $content | Out-File -FilePath $OutputFile -Encoding ASCII
            Write-Host "`nResults exported to: $OutputFile"
        }
        catch {
            Write-Host "Failed to export results to file: $($_.Exception.Message)" -ForegroundColor Red
        }
    }

    # Summary
    Write-Host "`nSUMMARY:"
    Write-Host "========="
    Write-Host "Empty folders: $($emptyFolders.Count)"
    Write-Host "Total files: $($fileInfo.Count)"
    $totalSize = 0
    foreach ($file in $fileInfo) { $totalSize += $file.Size }
    Write-Host "Total size: $([math]::Round($totalSize/1MB, 2)) MB"

}
catch {
    Write-Host "An error occurred: $($_.Exception.Message)" -ForegroundColor Red
}
```

## Key changes for Constrained Language Mode:

1. **Removed advanced language features** like `[PSCustomObject]` with property syntax
2. **Used basic object creation** with `New-Object PSObject`
3. **Simplified error handling** without advanced try-catch patterns
4. **Removed custom formatting functions** that might use restricted methods
5. **Basic string formatting** instead of advanced .NET methods
6. **Simplified file size calculations**

## Usage:

```powershell
# Basic usage
.\SimpleFileAnalyzer.ps1

# With specific path
.\SimpleFileAnalyzer.ps1 -Path "C:\Temp"

# With output file
.\SimpleFileAnalyzer.ps1 -Path "C:\Temp" -OutputFile "results.txt"
```

This simplified version should work in restricted PowerShell environments while still providing the core functionality you requested.
