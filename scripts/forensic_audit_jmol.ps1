# Forensic Audit Script for San Juan del Molinillo Corpus
# Auditor: auditor_jmol_1

$ErrorActionPreference = "Stop"

$baseDir = "c:\TRABAJOS\personal\genealo"
$catalogPath = Join-Path $baseDir "catalogo_corpus.json"
$checkpointPath = Join-Path $baseDir "scripts\ingest_checkpoint_jmol.json"
$reportPath = Join-Path $baseDir "scripts\verification_report_jmol.json"
$outJsonPath = Join-Path $baseDir ".agents\teamwork\auditor_jmol_1\forensic_audit_evidence.json"

Write-Host "=== STARTING FORENSIC AUDIT (auditor_jmol_1) ==="

$targets = @(
    "JMOL-BAUT-01", "JMOL-BAUT-02", "JMOL-BAUT-03", "JMOL-BAUT-04", "JMOL-BAUT-05", "JMOL-INDICE-BAUT",
    "JMOL-MATR-01", "JMOL-MATR-02", "JMOL-MATR-03", "JMOL-MIXTO-04",
    "JMOL-DIFU-01", "JMOL-DIFU-02", "JMOL-DIFU-03", "JMOL-DIFU-04", "JMOL-DIFU-05", "JMOL-DIFU-06",
    "JMOL-DIFU-PARVULOS", "JMOL-INDICE-DIFU"
)

$expectedCounts = @{
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

# 1. Catalog analysis
Write-Host "1. Parsing catalogo_corpus.json..."
$rawCatalog = Get-Content $catalogPath -Raw -Encoding UTF8
$catalog = ConvertFrom-Json $rawCatalog
$jmolRecords = @($catalog | Where-Object { $targets -contains $_.cuaderno_asignado_id })
$catalogCount = $jmolRecords.Count
$catalogImages = @($jmolRecords | ForEach-Object { $_.id_imagen })
$uniqueCatalogImages = @($catalogImages | Select-Object -Unique)

$l28Regex = "^\d{9}_\d{5}\.jpg$"
$l28Pass = 0
$l28Fail = 0
foreach ($img in $catalogImages) {
    if ($img -match $l28Regex) { $l28Pass++ } else { $l28Fail++ }
}

$perNotebookCatalogCounts = @{}
foreach ($t in $targets) {
    $c = @($jmolRecords | Where-Object { $_.cuaderno_asignado_id -eq $t }).Count
    $perNotebookCatalogCounts[$t] = $c
}

Write-Host "   Catalog JMOL records: $catalogCount (Unique: $($uniqueCatalogImages.Count))"

# 2. Physical File Integrity Analysis
Write-Host "2. Verifying physical disk images..."
$searchDirs = @(
    "$baseDir\imagenes\rollo 004298570",
    "$baseDir\imagenes\rollo 004298571",
    (Get-Item "$baseDir\San Juan Bautista. Bautismos enero de 1801*").FullName,
    (Get-Item "$baseDir\San Juan Bautista. Bautismos julio de 1752*").FullName
)

$diskFilesMap = @{}
$orphanFiles = @()
$zeroByteCount = 0
$corruptJpegCount = 0
$totalBytes = 0

foreach ($dir in $searchDirs) {
    if (Test-Path $dir) {
        $files = Get-ChildItem -Path $dir -Filter "*.jpg" -File
        foreach ($f in $files) {
            $diskFilesMap[$f.Name] = $f.FullName
        }
    }
}

Write-Host "   Total JPEGs discovered across 4 target folders: $($diskFilesMap.Count)"

# Check every catalog image on disk
$resolvedCount = 0
$missingOnDisk = @()
$jpegMagicBytesValid = 0

foreach ($imgName in $catalogImages) {
    if ($diskFilesMap.ContainsKey($imgName)) {
        $resolvedCount++
        $fpath = $diskFilesMap[$imgName]
        $fileInfo = Get-Item $fpath
        $fsize = $fileInfo.Length
        $totalBytes += $fsize
        if ($fsize -eq 0) {
            $zeroByteCount++
        }
        # Check JPEG header 0xFF 0xD8 0xFF
        $bytes = [System.IO.File]::ReadAllBytes($fpath)
        if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xFF -and $bytes[1] -eq 0xD8 -and $bytes[2] -eq 0xFF) {
            $jpegMagicBytesValid++
        } else {
            $corruptJpegCount++
        }
    } else {
        $missingOnDisk += $imgName
    }
}

# Check for orphan files (files in those folders not in JMOL catalog records)
$catalogSet = New-Object System.Collections.Generic.HashSet[string]
foreach ($img in $catalogImages) { [void]$catalogSet.Add($img) }

foreach ($k in $diskFilesMap.Keys) {
    if (-not $catalogSet.Contains($k)) {
        $orphanFiles += $k
    }
}

Write-Host "   Resolved: $resolvedCount / $catalogCount | Missing on disk: $($missingOnDisk.Count) | Zero-byte: $zeroByteCount | Corrupt JPEGs: $corruptJpegCount | Orphans: $($orphanFiles.Count)"

# 3. Checkpoint Integrity Analysis
Write-Host "3. Parsing scripts\ingest_checkpoint_jmol.json..."
$rawCheckpoint = Get-Content $checkpointPath -Raw -Encoding UTF8
$checkpoint = ConvertFrom-Json $rawCheckpoint

$cpNotebookIds = $checkpoint.notebook_ids
$cpCompletedNotebooks = @($checkpoint.completed_notebooks)
$cpUploadedSources = $checkpoint.uploaded_sources
$cpSourceKeys = @($cpUploadedSources.psobject.properties.Name)
$cpSourceUUIDs = @()
$uuidRegex = "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
$invalidUUIDs = @()
$timestamps = @()
$cpNotebookIdMismatches = @()

foreach ($prop in $cpUploadedSources.psobject.properties) {
    $entry = $prop.Value
    $uuid = $entry.source_id
    $nbId = $entry.notebook_id
    $ts = $entry.timestamp
    $cpSourceUUIDs += $uuid
    $timestamps += $ts
    if ($uuid -notmatch $uuidRegex) {
        $invalidUUIDs += @{ Name = $prop.Name; UUID = $uuid }
    }
}

$uniqueUUIDs = @($cpSourceUUIDs | Select-Object -Unique)

# Bijective check Catalog <-> Checkpoint
$missingInCheckpoint = @()
$extraInCheckpoint = @()
$cpSet = New-Object System.Collections.Generic.HashSet[string]
foreach ($k in $cpSourceKeys) { [void]$cpSet.Add($k) }

foreach ($img in $catalogImages) {
    if (-not $cpSet.Contains($img)) { $missingInCheckpoint += $img }
}
foreach ($k in $cpSourceKeys) {
    if (-not $catalogSet.Contains($k)) { $extraInCheckpoint += $k }
}

# Check timestamp realism
$sortedTimestamps = @($timestamps | Sort-Object)
$minTimestamp = $sortedTimestamps[0]
$maxTimestamp = $sortedTimestamps[$sortedTimestamps.Count - 1]
$uniqueTimestampsCount = @($timestamps | Select-Object -Unique).Count

Write-Host "   Uploaded sources in checkpoint: $($cpSourceKeys.Count)"
Write-Host "   Unique UUIDs: $($uniqueUUIDs.Count) (Invalid format: $($invalidUUIDs.Count))"
Write-Host "   Missing in checkpoint: $($missingInCheckpoint.Count) | Extra: $($extraInCheckpoint.Count)"
Write-Host "   Timestamps span: $minTimestamp to $maxTimestamp ($uniqueTimestampsCount unique timestamps)"

# 4. Verification Report Cross-Check
Write-Host "4. Parsing scripts\verification_report_jmol.json..."
$rawReport = Get-Content $reportPath -Raw -Encoding UTF8
$report = ConvertFrom-Json $rawReport
$reportOverallStatus = $report.overall_status
$reportNotebooks = $report.notebooks

$reportTotalExpected = 0
$reportTotalActual = 0
$reportTotalReady = 0
$reportTotalMissing = 0

foreach ($prop in $reportNotebooks.psobject.properties) {
    $nbMeta = $prop.Value
    $reportTotalExpected += $nbMeta.expected_count
    $reportTotalActual += $nbMeta.actual_count
    $reportTotalReady += $nbMeta.ready_count
    $reportTotalMissing += $nbMeta.missing_count
}

Write-Host "   Report Status: $reportOverallStatus | Expected: $reportTotalExpected | Actual: $reportTotalActual | Ready: $reportTotalReady | Missing: $reportTotalMissing"

# 5. Compile Evidence Object
$evidence = @{
    audit_timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    auditor = "auditor_jmol_1"
    catalog = @{
        total_records = $catalogCount
        unique_images = $uniqueCatalogImages.Count
        l28_regex_compliant = $l28Pass
        l28_regex_violations = $l28Fail
        per_notebook_counts = $perNotebookCatalogCounts
    }
    physical_disk = @{
        resolved_count = $resolvedCount
        missing_count = $missingOnDisk.Count
        zero_byte_count = $zeroByteCount
        corrupt_jpeg_count = $corruptJpegCount
        jpeg_magic_bytes_valid = $jpegMagicBytesValid
        orphan_files_count = $orphanFiles.Count
        total_bytes = $totalBytes
        total_gigabytes = [Math]::Round($totalBytes / 1GB, 3)
    }
    checkpoint = @{
        uploaded_sources_count = $cpSourceKeys.Count
        unique_source_uuids = $uniqueUUIDs.Count
        invalid_uuids_count = $invalidUUIDs.Count
        missing_in_checkpoint_count = $missingInCheckpoint.Count
        extra_in_checkpoint_count = $extraInCheckpoint.Count
        notebooks_count = ($cpNotebookIds.psobject.properties.Name).Count
        completed_notebooks_count = $cpCompletedNotebooks.Count
        min_timestamp = $minTimestamp
        max_timestamp = $maxTimestamp
        unique_timestamps = $uniqueTimestampsCount
    }
    verification_report = @{
        overall_status = $reportOverallStatus
        total_expected = $reportTotalExpected
        total_actual = $reportTotalActual
        total_ready = $reportTotalReady
        total_missing = $reportTotalMissing
    }
    bijective_integrity = @{
        catalog_vs_checkpoint_diff = ($missingInCheckpoint.Count + $extraInCheckpoint.Count)
        catalog_vs_disk_diff = $missingOnDisk.Count
        disk_orphans = $orphanFiles.Count
        uuid_collisions = ($cpSourceUUIDs.Count - $uniqueUUIDs.Count)
    }
}

$evidenceJson = $evidence | ConvertTo-Json -Depth 6
[System.IO.File]::WriteAllText($outJsonPath, $evidenceJson, [System.Text.Encoding]::UTF8)
Write-Host "=== FORENSIC EVIDENCE WRITTEN TO $outJsonPath ==="
