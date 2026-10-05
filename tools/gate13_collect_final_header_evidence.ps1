param(
    [Parameter(Mandatory=$true)]
    [string]$SourceZip,

    [string]$RepoRoot,

    [string]$OutputDirectory = (Join-Path $env:TEMP "fm2001-gate13-final-header-evidence")
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$ExpectedArchiveSha = "677dcbc859109818d22599f34890ca7873393aea5adbf1f1f1a32d1a76f8a8a4"
$ExpectedExeSha = "833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3"

$SourceZip = (Resolve-Path $SourceZip).Path
if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
} else {
    $RepoRoot = (Resolve-Path $RepoRoot).Path
}

$archiveHash = (Get-FileHash -Algorithm SHA256 $SourceZip).Hash.ToLowerInvariant()
if ($archiveHash -ne $ExpectedArchiveSha) {
    throw "Authorized source ZIP SHA-256 mismatch: $archiveHash"
}

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$work = Join-Path $OutputDirectory $stamp
$stage = Join-Path $work "stage"
$inventory = Join-Path $work "gate13-final-header-inventory.json"
$trace = Join-Path $work "gate13-final-header-trace.json"
$assetBundle = Join-Path $work "gate13-final-header-assets-base64.json"

New-Item -ItemType Directory -Force -Path $stage | Out-Null

$inventoryTool = Join-Path $RepoRoot "reconstruction\gate13_source_inventory.py"
$traceTool = Join-Path $RepoRoot "reconstruction\gate13_management_header_source_trace.py"

$paths = @(
    "footballmanager.exe",
    "FM2001_Art/Generic/Background_buttons/back_4.444",
    "FM2001_Art/Generic/Background_buttons/back_4_anim.444",
    "Fonts/Zurich_XCn_BT_24pixel.fnt"
)

$args = @(
    $inventoryTool,
    $SourceZip,
    "--deep",
    "--extract-candidates-to", $stage,
    "--only-explicit",
    "--require-all-explicit",
    "--hash-source",
    "--output", $inventory
)
foreach ($path in $paths) {
    $args += @("--extract-path", $path)
}

& python @args
if ($LASTEXITCODE -ne 0) {
    throw "Exact-path source extraction failed with exit code $LASTEXITCODE"
}

$exe = Join-Path $stage "footballmanager.exe"
if (-not (Test-Path $exe)) {
    throw "Canonical disc-root footballmanager.exe was not staged"
}
$exeHash = (Get-FileHash -Algorithm SHA256 $exe).Hash.ToLowerInvariant()
if ($exeHash -ne $ExpectedExeSha) {
    throw "Staged footballmanager.exe SHA-256 mismatch: $exeHash"
}

& python $traceTool $exe --source-root $stage --disassemble --output $trace
if ($LASTEXITCODE -ne 0) {
    throw "Read-only management-header trace failed with exit code $LASTEXITCODE"
}

$traceHash = (Get-FileHash -Algorithm SHA256 $trace).Hash.ToLowerInvariant()

# Emit only the three exact Gate-13 resources approved for repository import.
# The canonical executable remains private and is deliberately excluded.
$assetPaths = @(
    "FM2001_Art/Generic/Background_buttons/back_4.444",
    "FM2001_Art/Generic/Background_buttons/back_4_anim.444",
    "Fonts/Zurich_XCn_BT_24pixel.fnt"
)
$assetRecords = @()
foreach ($relativePath in $assetPaths) {
    $fullPath = Join-Path $stage ($relativePath -replace "/", "\")
    if (-not (Test-Path $fullPath)) {
        throw "Expected staged Gate-13 asset is missing: $relativePath"
    }
    $bytes = [System.IO.File]::ReadAllBytes($fullPath)
    $assetRecords += [ordered]@{
        source_path = $relativePath
        size_bytes = $bytes.Length
        sha256 = (Get-FileHash -Algorithm SHA256 $fullPath).Hash.ToLowerInvariant()
        base64 = [Convert]::ToBase64String($bytes)
    }
}
$bundlePayload = [ordered]@{
    format_version = 1
    source_archive_sha256 = $archiveHash
    canonical_executable_sha256 = $exeHash
    note = "Temporary private transfer bundle for the three exact Gate-13 source assets; do not commit this JSON."
    assets = $assetRecords
}
$bundlePayload | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 $assetBundle
$bundleHash = (Get-FileHash -Algorithm SHA256 $assetBundle).Hash.ToLowerInvariant()

Write-Host ""
Write-Host "Gate-13 final-header evidence collected read-only."
Write-Host "Archive SHA-256 : $archiveHash"
Write-Host "Executable SHA-256: $exeHash"
Write-Host "Inventory        : $inventory"
Write-Host "Trace            : $trace"
Write-Host "Trace SHA-256    : $traceHash"
Write-Host "Asset bundle     : $assetBundle"
Write-Host "Bundle SHA-256   : $bundleHash"
Write-Host ""
Write-Host "No repository files or original source files were modified."
Write-Host "The asset bundle contains only the three exact source assets approved for Gate-13 import; it excludes footballmanager.exe."