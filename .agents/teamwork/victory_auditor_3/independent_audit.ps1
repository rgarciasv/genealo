# Independent Victory Audit Forensic Script
# Auditor: victory_auditor_3

$ErrorActionPreference = "Stop"

$baseDir = "c:\TRABAJOS\personal\genealo"
$catalogPath = Join-Path $baseDir "catalogo_corpus.json"
$checkpointPath = Join-Path $baseDir "scripts\ingest_checkpoint_jmol.json"
$reportPath = Join-Path $baseDir "scripts\verification_report_jmol.json"
$outReportPath = Join-Path $baseDir ".agents\teamwork\victory_auditor_3\independent_audit_results.json"

Write-Host "=== INDEPENDENT VICTORY AUDIT FORENSICS ==="

$expectedNotebooks = @{
    "JMOL-BAUT-01" = 175
    "JMOL-BAUT-02" = 276
    "JMOL-BAUT-03" = 190
    "JMOL-BAUT-04" = 189
    "JMOL-BAUT-05" = 139
    "JMOL-INDICE-BAUT" = 111
    "JMOL-MATR-01" = 194
    "JMOL-MATR-02" = 134
    "JMOL-MATR-03" = 198
    "JMOL-MIXTO-04" = 91
    "JMOL-DIFU-01" = 202
    "JMOL-DIFU-02" = 277
    "JMOL-DIFU-03" = 17
    "JMOL-DIFU-04" = 214
    "JMOL-DIFU-05" = 99
    "JMOL-DIFU-06" = 177
    "JMOL-DIFU-PARVULOS" = 27
    "JMOL-INDICE-DIFU" = 21
}

# --- 1. Canonical Catalog Analysis ---
Write-Host "1. Parsing and auditing catalogo_corpus.json..."
$rawCat = Get-Content -Path $catalogPath -Raw -Encoding UTF8
$catalog = ConvertFrom-Json $rawCat
$targetNames = $expectedNotebooks.Keys

$jmolRecords = @($catalog | Where-Object { $targetNames -contains $_.cuaderno_asignado_id })
$catalogCount = $jmolRecords.Count
$catalogImages = @($jmolRecords | ForEach-Object { $_.id_imagen })
$uniqueCatalogImages = @($catalogImages | Select-Object -Unique)

$l28Regex = "^\d{9}_\d{5}\.jpg$"
$l28Compliant = 0
$l28Violations = 0
foreach ($img in $catalogImages) {
    if ($img -match $l28Regex) { $l28Compliant++ } else { $l28Violations++ }
}

$perNotebookCatalog = @{}
$catalogDiscrepancies = @()
foreach ($key in $expectedNotebooks.Keys) {
    $c = @($jmolRecords | Where-Object { $_.cuaderno_asignado_id -eq $key }).Count
    $perNotebookCatalog[$key] = $c
    if ($c -ne $expectedNotebooks[$key]) {
        $catalogDiscrepancies += "$key expected $($expectedNotebooks[$key]) but found $c in catalog"
    }
}

Write-Host "   JMOL records in catalog: $catalogCount"
Write-Host "   Unique images: $($uniqueCatalogImages.Count)"
Write-Host "   L28 compliant: $l28Compliant, violations: $l28Violations"

# --- 2. Physical File Integrity Verification ---
Write-Host "2. Verifying physical JPEG files on disk..."
$searchDirs = @(
    (Join-Path $baseDir "imagenes\rollo 004298570"),
    (Join-Path $baseDir "imagenes\rollo 004298571"),
    (Get-Item (Join-Path $baseDir "San Juan Bautista. Bautismos enero de 1801*")).FullName,
    (Get-Item (Join-Path $baseDir "San Juan Bautista. Bautismos julio de 1752*")).FullName
)

$diskMap = @{}
foreach ($dir in $searchDirs) {
    if (Test-Path $dir) {
        $files = Get-ChildItem -Path $dir -Filter "*.jpg" -File
        foreach ($f in $files) {
            $diskMap[$f.Name] = $f.FullName
        }
    }
}

$resolvedDisk = 0
$missingDisk = @()
$corruptDisk = @()
$totalBytes = 0

foreach ($imgName in $catalogImages) {
    if ($diskMap.ContainsKey($imgName)) {
        $resolvedDisk++
        $filePath = $diskMap[$imgName]
        $item = Get-Item $filePath
        $totalBytes += $item.Length
        if ($item.Length -lt 100) {
            $corruptDisk += "$imgName is abnormally small ($($item.Length) bytes)"
        } else {
            $bytes = [System.IO.File]::ReadAllBytes($filePath)
            if ($bytes.Length -lt 3 -or $bytes[0] -ne 0xFF -or $bytes[1] -ne 0xD8 -or $bytes[2] -ne 0xFF) {
                $corruptDisk += "$imgName failed JPEG magic byte check"
            }
        }
    } else {
        $missingDisk += $imgName
    }
}

Write-Host "   Physical JPEGs resolved: $resolvedDisk / $catalogCount"
Write-Host "   Missing on disk: $($missingDisk.Count)"
Write-Host "   Corrupt JPEGs: $($corruptDisk.Count)"
Write-Host "   Total size: $([math]::Round($totalBytes / 1GB, 3)) GB"

# --- 3. Atomic Checkpoint Forensic Verification ---
Write-Host "3. Auditing scripts\ingest_checkpoint_jmol.json..."
$rawCheckpoint = Get-Content -Path $checkpointPath -Raw -Encoding UTF8
$checkpoint = ConvertFrom-Json $rawCheckpoint

$cpNotebooks = $checkpoint.notebook_ids
$cpCompleted = @($checkpoint.completed_notebooks)
$cpUploaded = $checkpoint.uploaded_sources
$cpSourceKeys = @($cpUploaded.PSObject.Properties.Name)

$uuidRegex = "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
$invalidNbUuids = @()
foreach ($prop in $cpNotebooks.PSObject.Properties) {
    if ($prop.Value -notmatch $uuidRegex) {
        $invalidNbUuids += "$($prop.Name): $($prop.Value)"
    }
}

$invalidSourceUuids = @()
$sourceTimestamps = @()
foreach ($k in $cpSourceKeys) {
    $entry = $cpUploaded.$k
    if ($entry.source_id -notmatch $uuidRegex) {
        $invalidSourceUuids += "${k}: $($entry.source_id)"
    }
    $sourceTimestamps += $entry.timestamp
}

$missingInCp = @()
foreach ($img in $catalogImages) {
    if (-not $cpUploaded.PSObject.Properties[$img]) {
        $missingInCp += $img
    }
}

$extraInCp = @()
foreach ($k in $cpSourceKeys) {
    if ($catalogImages -notcontains $k) {
        $extraInCp += $k
    }
}

Write-Host "   Checkpoint notebooks: $(@($cpNotebooks.PSObject.Properties).Count) (Completed: $($cpCompleted.Count))"
Write-Host "   Checkpoint uploaded sources: $($cpSourceKeys.Count)"
Write-Host "   Missing in checkpoint: $($missingInCp.Count)"
Write-Host "   Extra in checkpoint: $($extraInCp.Count)"
Write-Host "   Invalid source UUIDs: $($invalidSourceUuids.Count)"

# --- 4. Verification Report Forensic Verification ---
Write-Host "4. Auditing scripts\verification_report_jmol.json..."
$rawReport = Get-Content -Path $reportPath -Raw -Encoding UTF8
$report = ConvertFrom-Json $rawReport

$reportNotebooks = $report.notebooks
$reportOverall = $report.overall_status

$reportFailures = @()
$totalActual = 0
$totalReady = 0
$totalExpected = 0

foreach ($prop in $reportNotebooks.PSObject.Properties) {
    $nbData = $prop.Value
    $totalActual += $nbData.actual_count
    $totalReady += $nbData.ready_count
    $totalExpected += $nbData.expected_count
    if ($nbData.status -ne "PASS") {
        $reportFailures += "$($prop.Name) status is $($nbData.status)"
    }
    if ($nbData.missing_count -gt 0) {
        $reportFailures += "$($prop.Name) missing $($nbData.missing_count)"
    }
    if ($nbData.ready_count -ne $nbData.expected_count) {
        $reportFailures += "$($prop.Name) ready_count $($nbData.ready_count) != expected $($nbData.expected_count)"
    }
}

Write-Host "   Report overall_status: $reportOverall"
Write-Host "   Total actual: $totalActual, Total ready: $totalReady, Total expected: $totalExpected"
Write-Host "   Report failures: $($reportFailures.Count)"

$finalResults = [PSCustomObject]@{
    timestamp = (Get-Date).ToString("o")
    catalog = [PSCustomObject]@{
        total_records = $catalogCount
        unique_images = $uniqueCatalogImages.Count
        l28_compliant = $l28Compliant
        l28_violations = $l28Violations
        discrepancies = $catalogDiscrepancies
    }
    disk = [PSCustomObject]@{
        resolved = $resolvedDisk
        missing = $missingDisk.Count
        corrupt = $corruptDisk.Count
        total_gb = [math]::Round($totalBytes / 1GB, 3)
    }
    checkpoint = [PSCustomObject]@{
        notebooks_count = @($cpNotebooks.PSObject.Properties).Count
        completed_count = $cpCompleted.Count
        sources_count = $cpSourceKeys.Count
        missing_count = $missingInCp.Count
        extra_count = $extraInCp.Count
        invalid_source_uuids = $invalidSourceUuids.Count
        invalid_notebook_uuids = $invalidNbUuids.Count
    }
    report = [PSCustomObject]@{
        overall_status = $reportOverall
        total_expected = $totalExpected
        total_actual = $totalActual
        total_ready = $totalReady
        failures = $reportFailures
    }
}

$finalResults | ConvertTo-Json -Depth 5 | Set-Content -Path $outReportPath -Encoding UTF8
Write-Host "Results saved to $outReportPath"
