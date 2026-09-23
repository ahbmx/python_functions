Add Bulma to the same `libs` structure:

```powershell
New-Item -ItemType Directory -Force -Path ".\libs\bulma" | Out-Null

Invoke-WebRequest `
    -Uri "https://cdn.jsdelivr.net/npm/bulma@1.0.4/css/bulma.min.css" `
    -OutFile ".\libs\bulma\bulma.min.css"
```

Or add it to the combined script:

```powershell
$root = ".\libs"

$directories = @(
    "$root\highcharts",
    "$root\highcharts-dashboard",
    "$root\highcharts-grid",
    "$root\bootstrap",
    "$root\bulma",
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

    "$root\bulma\bulma.min.css" =
        "https://cdn.jsdelivr.net/npm/bulma@1.0.4/css/bulma.min.css"

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

This gives you:

```text
libs/
├── bootstrap/
│   ├── bootstrap.min.css
│   └── bootstrap.bundle.min.js
├── bulma/
│   └── bulma.min.css
├── datatables/
│   ├── jquery-3.7.1.min.js
│   ├── dataTables.min.js
│   └── dataTables.dataTables.min.css
├── highcharts/
│   ├── highcharts.js
│   ├── exporting.js
│   ├── export-data.js
│   └── accessibility.js
├── highcharts-dashboard/
│   └── dashboards.js
└── highcharts-grid/
    └── grid.js
```

**Note:** Bootstrap and Bulma are both CSS frameworks. If you're using both in the same application, their generic class names and styles can interact, so it is generally preferable to use one framework for a given page/component rather than mixing their components indiscriminately.
