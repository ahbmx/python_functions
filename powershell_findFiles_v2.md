Here's the enhanced PowerShell script with folder summarization and old file counts:

```powershell
# Enhanced File System Analyzer with Folder Summarization
# Supports constrained language mode

param(
    [string]$Path = ".",
    [string]$OutputCSV = "",
    [string]$SummaryCSV = "",
    [switch]$DeleteEmptyFolders,
    [switch]$FlagOldFiles,
    [switch]$SummarizeFolders,
    [switch]$WhatIf
)

function Get-EmptyFolders {
    param([string]$SearchPath)
    
    $emptyFolders = @()
    $allFolders = Get-ChildItem -Path $SearchPath -Directory -Recurse -ErrorAction SilentlyContinue
    
    foreach ($folder in $allFolders) {
        try {
            $items = Get-ChildItem -Path $folder.FullName -Force -ErrorAction SilentlyContinue
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

function Get-FileInfoEnhanced {
    param([string]$SearchPath, [bool]$CheckOldFiles)
    
    $files = Get-ChildItem -Path $SearchPath -File -Recurse -ErrorAction SilentlyContinue
    
    $fileInfo = @()
    $currentYear = (Get-Date).Year
    
    foreach ($file in $files) {
        $lastAccessYear = $file.LastAccessTime.Year
        $notAccessedThisYear = $CheckOldFiles -and ($lastAccessYear -ne $currentYear)
        
        $fileInfo += New-Object PSObject -Property @{
            Name = $file.Name
            FullPath = $file.FullName
            Directory = $file.DirectoryName
            Size = $file.Length
            SizeKB = [math]::Round($file.Length / 1KB, 2)
            SizeMB = [math]::Round($file.Length / 1MB, 2)
            LastAccessTime = $file.LastAccessTime
            LastWriteTime = $file.LastWriteTime
            CreationTime = $file.CreationTime
            Extension = $file.Extension
            NotAccessedThisYear = $notAccessedThisYear
            LastAccessYear = $lastAccessYear
        }
    }
    
    return $fileInfo | Sort-Object FullPath
}

function Get-FolderSummary {
    param([array]$FileInfo, [bool]$CheckOldFiles)
    
    $folderSummary = @{}
    $currentYear = (Get-Date).Year
    
    foreach ($file in $FileInfo) {
        $folderPath = $file.Directory
        
        if (-not $folderSummary.ContainsKey($folderPath)) {
            $folderSummary[$folderPath] = @{
                TotalFiles = 0
                OldFiles = 0
                TotalSize = 0
            }
        }
        
        $folderSummary[$folderPath].TotalFiles++
        $folderSummary[$folderPath].TotalSize += $file.Size
        
        if ($CheckOldFiles -and $file.NotAccessedThisYear) {
            $folderSummary[$folderPath].OldFiles++
        }
    }
    
    # Convert to array of objects
    $summaryArray = @()
    foreach ($folder in $folderSummary.Keys) {
        $summary = $folderSummary[$folder]
        $summaryArray += New-Object PSObject -Property @{
            FolderPath = $folder
            TotalFiles = $summary.TotalFiles
            OldFiles = $summary.OldFiles
            OldFilePercentage = if ($summary.TotalFiles -gt 0) { [math]::Round(($summary.OldFiles / $summary.TotalFiles) * 100, 2) } else { 0 }
            TotalSizeBytes = $summary.TotalSize
            TotalSizeMB = [math]::Round($summary.TotalSize / 1MB, 2)
            TotalSizeGB = [math]::Round($summary.TotalSize / 1GB, 2)
        }
    }
    
    return $summaryArray | Sort-Object FolderPath
}

function Remove-EmptyFolders {
    param([array]$Folders, [bool]$Simulate)
    
    $removedCount = 0
    $failedCount = 0
    
    foreach ($folder in $Folders) {
        try {
            if ($Simulate) {
                Write-Host "WOULD DELETE: $($folder.FullName)" -ForegroundColor Yellow
            } else {
                Remove-Item -Path $folder.FullName -Force -Recurse -ErrorAction Stop
                Write-Host "DELETED: $($folder.FullName)" -ForegroundColor Red
            }
            $removedCount++
        }
        catch {
            Write-Host "FAILED to delete: $($folder.FullName) - $($_.Exception.Message)" -ForegroundColor Magenta
            $failedCount++
        }
    }
    
    return @{Removed = $removedCount; Failed = $failedCount}
}

# Main execution
try {
    # Validate path
    if (-not (Test-Path -Path $Path)) {
        Write-Host "Error: Path '$Path' does not exist" -ForegroundColor Red
        exit 1
    }

    $absolutePath = (Resolve-Path $Path).Path
    Write-Host "Scanning directory: $absolutePath" -ForegroundColor Green
    Write-Host "==============================================" -ForegroundColor Green

    # Get empty folders
    Write-Host "Finding empty folders..." -ForegroundColor Yellow
    $emptyFolders = Get-EmptyFolders -SearchPath $Path
    
    # Get file information
    Write-Host "Gathering file information..." -ForegroundColor Yellow
    $fileInfo = Get-FileInfoEnhanced -SearchPath $Path -CheckOldFiles $FlagOldFiles

    # Get folder summary if requested
    if ($SummarizeFolders -or $SummaryCSV -ne "") {
        Write-Host "Generating folder summary..." -ForegroundColor Yellow
        $folderSummary = Get-FolderSummary -FileInfo $fileInfo -CheckOldFiles $FlagOldFiles
    }

    # Display empty folders
    Write-Host "`nEMPTY FOLDERS ($($emptyFolders.Count) found):" -ForegroundColor Cyan
    Write-Host "==============================================" -ForegroundColor Cyan
    if ($emptyFolders.Count -gt 0) {
        foreach ($folder in $emptyFolders) {
            Write-Host $folder.FullName -ForegroundColor Red
        }
        
        # Handle folder deletion
        if ($DeleteEmptyFolders) {
            Write-Host "`nEMPTY FOLDER DELETION:" -ForegroundColor Magenta
            Write-Host "==============================================" -ForegroundColor Magenta
            
            if ($WhatIf) {
                Write-Host "SIMULATION MODE - No folders will actually be deleted" -ForegroundColor Yellow
                Remove-EmptyFolders -Folders $emptyFolders -Simulate $true
            } else {
                Write-Host "WARNING: This will permanently delete empty folders!" -ForegroundColor Red
                $confirmation = Read-Host "Are you sure you want to continue? (y/N)"
                
                if ($confirmation -eq 'y' -or $confirmation -eq 'Y') {
                    $deleteResult = Remove-EmptyFolders -Folders $emptyFolders -Simulate $false
                    Write-Host "Deleted: $($deleteResult.Removed), Failed: $($deleteResult.Failed)" -ForegroundColor White
                } else {
                    Write-Host "Deletion cancelled." -ForegroundColor Green
                }
            }
        }
    } else {
        Write-Host "No empty folders found." -ForegroundColor Green
    }

    # Display file information
    Write-Host "`nFILE INFORMATION ($($fileInfo.Count) files):" -ForegroundColor Cyan
    Write-Host "==============================================" -ForegroundColor Cyan
    
    $oldFileCount = ($fileInfo | Where-Object { $_.NotAccessedThisYear -eq $true }).Count
    
    if ($FlagOldFiles) {
        Write-Host "Files not accessed this year: $oldFileCount" -ForegroundColor $(if ($oldFileCount -gt 0) { "Red" } else { "Green" })
    }
    
    # Display sample of files
    $sampleFiles = $fileInfo | Select-Object -First 5
    foreach ($file in $sampleFiles) {
        $color = if ($file.NotAccessedThisYear) { "Red" } else { "White" }
        Write-Host ("{0,-30} {1,-8} {2} {3}" -f 
            $file.Name, 
            ("{0:N0} KB" -f $file.SizeKB), 
            $file.LastAccessTime.ToString("yyyy-MM-dd"),
            $(if ($file.NotAccessedThisYear) { "[OLD]" } else { "" })) -ForegroundColor $color
    }
    
    if ($fileInfo.Count -gt 5) {
        Write-Host "... and $($fileInfo.Count - 5) more files" -ForegroundColor Gray
    }

    # Display folder summary
    if ($SummarizeFolders -and $folderSummary) {
        Write-Host "`nFOLDER SUMMARY (Top 10 by old files):" -ForegroundColor Cyan
        Write-Host "==============================================" -ForegroundColor Cyan
        
        $topFolders = $folderSummary | Where-Object { $_.OldFiles -gt 0 } | Sort-Object OldFiles -Descending | Select-Object -First 10
        
        if ($topFolders.Count -gt 0) {
            Write-Host "Folder".PadRight(50) "Files".PadRight(8) "Old".PadRight(8) "% Old".PadRight(8) "Size" -ForegroundColor Yellow
            Write-Host "--------------------------------------------------------------------" -ForegroundColor Yellow
            
            foreach ($folder in $topFolders) {
                $folderName = if ($folder.FolderPath.Length -gt 47) { "..." + $folder.FolderPath.Substring($folder.FolderPath.Length - 47) } else { $folder.FolderPath }
                $color = if ($folder.OldFilePercentage -gt 50) { "Red" } else { "White" }
                
                Write-Host ($folderName.PadRight(50) + 
                          $folder.TotalFiles.ToString().PadRight(8) +
                          $folder.OldFiles.ToString().PadRight(8) +
                          ("{0}%".PadRight(8) -f $folder.OldFilePercentage) +
                          ("{0:N1} MB" -f $folder.TotalSizeMB)) -ForegroundColor $color
            }
        } else {
            Write-Host "No folders with old files found." -ForegroundColor Green
        }
    }

    # Export to CSV if specified
    if ($OutputCSV -ne "") {
        try {
            # Prepare data for CSV export
            $exportData = @()
            foreach ($file in $fileInfo) {
                $exportData += New-Object PSObject -Property @{
                    Name = $file.Name
                    FullPath = $file.FullPath
                    Directory = $file.Directory
                    SizeBytes = $file.Size
                    SizeKB = $file.SizeKB
                    SizeMB = $file.SizeMB
                    LastAccessTime = $file.LastAccessTime
                    LastWriteTime = $file.LastWriteTime
                    CreationTime = $file.CreationTime
                    Extension = $file.Extension
                    NotAccessedThisYear = $file.NotAccessedThisYear
                    LastAccessYear = $file.LastAccessYear
                }
            }
            
            # Export to CSV
            $exportData | Export-Csv -Path $OutputCSV -NoTypeInformation -Encoding UTF8
            Write-Host "`nFile results exported to CSV: $OutputCSV" -ForegroundColor Green
        }
        catch {
            Write-Host "Failed to export file results to CSV: $($_.Exception.Message)" -ForegroundColor Red
        }
    }

    # Export summary to CSV if specified
    if ($SummaryCSV -ne "" -and $folderSummary) {
        try {
            $folderSummary | Export-Csv -Path $SummaryCSV -NoTypeInformation -Encoding UTF8
            Write-Host "Folder summary exported to CSV: $SummaryCSV" -ForegroundColor Green
        }
        catch {
            Write-Host "Failed to export folder summary to CSV: $($_.Exception.Message)" -ForegroundColor Red
        }
    }

    # Summary
    Write-Host "`nSUMMARY:" -ForegroundColor Magenta
    Write-Host "=========" -ForegroundColor Magenta
    Write-Host "Empty folders: $($emptyFolders.Count)" -ForegroundColor White
    Write-Host "Total files: $($fileInfo.Count)" -ForegroundColor White
    $totalSizeMB = ($fileInfo | Measure-Object -Property SizeMB -Sum).Sum
    Write-Host "Total size: $([math]::Round($totalSizeMB, 2)) MB" -ForegroundColor White
    
    if ($FlagOldFiles) {
        Write-Host "Files not accessed this year: $oldFileCount" -ForegroundColor $(if ($oldFileCount -gt 0) { "Red" } else { "Green" })
        Write-Host "Percentage of old files: $([math]::Round(($oldFileCount / $fileInfo.Count) * 100, 2))%" -ForegroundColor White
    }
    
    if ($SummarizeFolders -and $folderSummary) {
        $foldersWithOldFiles = ($folderSummary | Where-Object { $_.OldFiles -gt 0 }).Count
        Write-Host "Folders with old files: $foldersWithOldFiles" -ForegroundColor White
    }

}
catch {
    Write-Host "An error occurred: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
```

## New Usage Examples:

```powershell
# Basic scan with folder summarization
.\FileAnalyzer.ps1 -Path "C:\MyFolder" -SummarizeFolders

# Export both file details and folder summary to CSV
.\FileAnalyzer.ps1 -Path "C:\MyFolder" -OutputCSV "files.csv" -SummaryCSV "folders.csv"

# Flag old files and show folder summary
.\FileAnalyzer.ps1 -Path "C:\MyFolder" -FlagOldFiles -SummarizeFolders

# Combined: Delete empty folders, flag old files, summarize folders, export to CSV
.\FileAnalyzer.ps1 -Path "C:\MyFolder" -DeleteEmptyFolders -FlagOldFiles -SummarizeFolders -OutputCSV "results.csv" -SummaryCSV "summary.csv"

# Simulation mode with folder summary
.\FileAnalyzer.ps1 -Path "C:\MyFolder" -DeleteEmptyFolders -SummarizeFolders -WhatIf
```

## New Features Added:

1. **Folder Summarization**: Shows count of files and old files per folder
2. **Percentage Calculation**: Displays percentage of old files in each folder
3. **Top Folders Display**: Shows top 10 folders with most old files
4. **Separate CSV Export**: Option to export folder summary to separate CSV file
5. **Size Statistics**: Total size per folder in bytes, MB, and GB
6. **Color-Coded Output**: Red highlighting for folders with high percentages of old files
7. **Comprehensive Summary**: Additional summary statistics including folders with old files

The folder summary CSV includes: FolderPath, TotalFiles, OldFiles, OldFilePercentage, TotalSizeBytes, TotalSizeMB, TotalSizeGB.
