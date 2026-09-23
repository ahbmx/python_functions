If you want to **download the libraries locally using PowerShell** for an offline/self-hosted web application, you can use `Invoke-WebRequest`.

### Highcharts

```powershell
New-Item -ItemType Directory -Force -Path ".\libs\highcharts" | Out-Null

Invoke-WebRequest `
    -Uri "https://code.highcharts.com/highcharts.js" `
    -OutFile ".\libs\highcharts\highcharts.js"

Invoke-WebRequest `
    -Uri "https://code.highcharts.com/modules/exporting.js" `
    -OutFile ".\libs\highcharts\exporting.js"

Invoke-WebRequest `
    -Uri "https://code.highcharts.com/modules/export-data.js" `
    -OutFile ".\libs\highcharts\export-data.js"

Invoke-WebRequest `
    -Uri "https://code.highcharts.com/modules/accessibility.js" `
    -OutFile ".\libs\highcharts\accessibility.js"
```

### Highcharts Dashboards

```powershell
New-Item -ItemType Directory -Force -Path ".\libs\highcharts-dashboard" | Out-Null

Invoke-WebRequest `
    -Uri "https://code.highcharts.com/dashboards/dashboards.js" `
    -OutFile ".\libs\highcharts-dashboard\dashboards.js"
```

### Highcharts Grid

```powershell
New-Item -ItemType Directory -Force -Path ".\libs\highcharts-grid" | Out-Null

Invoke-WebRequest `
    -Uri "https://code.highcharts.com/grid/grid.js" `
    -OutFile ".\libs\highcharts-grid\grid.js"
```

### Bootstrap

For Bootstrap 5:

```powershell
New-Item -ItemType Directory -Force -Path ".\libs\bootstrap" | Out-Null

Invoke-WebRequest `
    -Uri "https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css" `
    -OutFile ".\libs\bootstrap\bootstrap.min.css"

Invoke-WebRequest `
    -Uri "https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js" `
    -OutFile ".\libs\bootstrap\bootstrap.bundle.min.js"
```

`bootstrap.bundle.min.js` already contains **Popper**, so you do not need to download Popper separately for Bootstrap 5.

### DataTables.js

DataTables requires jQuery.

```powershell
New-Item -ItemType Directory -Force -Path ".\libs\datatables" | Out-Null

Invoke-WebRequest `
    -Uri "https://code.jquery.com/jquery-3.7.1.min.js" `
    -OutFile ".\libs\datatables\jquery-3.7.1.min.js"

Invoke-WebRequest `
    -Uri "https://cdn.datatables.net/2.3.5/js/dataTables.min.js" `
    -OutFile ".\libs\datatables\dataTables.min.js"

Invoke-WebRequest `
    -Uri "https://cdn.datatables.net/2.3.5/css/dataTables.dataTables.min.css" `
    -OutFile ".\libs\datatables\dataTables.dataTables.min.css"
```

### One PowerShell script

If you want everything downloaded in one operation:

```powershell
$root = ".\libs"

$directories = @(
    "$root\highcharts",
    "$root\highcharts-dashboard",
    "$root\highcharts-grid",
    "$root\bootstrap",
    "$root\datatables"
)

foreach ($directory in $directories) {
    New-Item -ItemType Directory -Force -Path $directory | Out-Null
}

$files = @{
    "$root\highcharts\highcharts.js" =
        "https://code.highcharts.com/highcharts.js"

    "$root\highcharts\exporting.js" =
        "https://code.highcharts.com/modules/exporting.js"

    "$root\highcharts\export-data.js" =
        "https://code.highcharts.com/modules/export-data.js"

    "$root\highcharts\accessibility.js" =
        "https://code.highcharts.com/modules/accessibility.js"

    "$root\highcharts-dashboard\dashboards.js" =
        "https://code.highcharts.com/dashboards/dashboards.js"

    "$root\highcharts-grid\grid.js" =
        "https://code.highcharts.com/grid/grid.js"

    "$root\bootstrap\bootstrap.min.css" =
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css"

    "$root\bootstrap\bootstrap.bundle.min.js" =
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js"

    "$root\datatables\jquery-3.7.1.min.js" =
        "https://code.jquery.com/jquery-3.7.1.min.js"

    "$root\datatables\dataTables.min.js" =
        "https://cdn.datatables.net/2.3.5/js/dataTables.min.js"

    "$root\datatables\dataTables.dataTables.min.css" =
        "https://cdn.datatables.net/2.3.5/css/dataTables.dataTables.min.css"
}

foreach ($file in $files.GetEnumerator()) {
    Write-Host "Downloading $($file.Value)"
    Invoke-WebRequest -Uri $file.Value -OutFile $file.Key
}

Write-Host ""
Write-Host "Download complete."
```

### Important dependency note

For the libraries you've listed, the basic dependency relationship is:

```text
jQuery
   |
   +-- DataTables

Bootstrap
   |
   +-- Popper (included in bootstrap.bundle)

Highcharts
   |
   +-- Highcharts Dashboards
   |
   +-- Highcharts Grid
```

One caveat: **Highcharts Dashboards and Highcharts Grid have their own version/dependency requirements**, and the exact files needed can vary depending on whether you are using the current Highcharts distribution or a specific version. If this is for an **air-gapped/production environment**, I would recommend pinning **all versions** rather than downloading `latest`-style URLs.
