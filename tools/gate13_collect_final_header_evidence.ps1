param(
    [Parameter(Mandatory=$true)]
    [string]$SourceZip,

    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,

    [string]$OutputDirectory = (Join-Path $env:TEMP "fm2001-gate13-final-header-evidence")
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$ExpectedArchiveSha = "677dcbc859109818d22599f34890ca7873393aea5adbf1f1f1a32d1a76f8a8a4"
$ExpectedExeSha = "833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3"

$SourceZip = (Resolve-Path $SourceZip).Path
$RepoRoot = (Resolve-Path $RepoRoot).Path

$archiveHash = (Get-FileHash -Algorithm SHA256 $SourceZip).Hash.ToLowerInvariant()
if ($archiveHash -ne $ExpectedArchiveSha) {
    throw "Authorized source ZIP SHA-256 mismatch: $archiveHash"
}

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$work = Join-Path $OutputDirectory $stamp
$stage = Join-Path $work "stage"
$inventory = Join-Path $work "gate13-final-header-inventory.json"
$trace = Join-Path $work "gate13-final-header-trace.json"

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

Write-Host ""
Write-Host "Gate-13 final-header evidence collected read-only."
Write-Host "Archive SHA-256 : $archiveHash"
Write-Host "Executable SHA-256: $exeHash"
Write-Host "Inventory        : $inventory"
Write-Host "Trace            : $trace"
Write-Host "Trace SHA-256    : $traceHash"
Write-Host ""
Write-Host "No repository files or original source files were modified."
