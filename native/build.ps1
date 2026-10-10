<#
.SYNOPSIS
    Builds sm64-mario.dll, the native Mario library, from a libsm64 checkout plus the overlays in native/.

.DESCRIPTION
    This script downloads nothing. You get libsm64 yourself (commands below), it checks that the checkout is the
    commit this mod was written against, applies the overlays to copies of a few files (your checkout is not
    modified) and compiles with zig.

    One time setup, from the repository root:

        git clone https://github.com/libsm64/libsm64.git native/libsm64
        git -C native/libsm64 checkout fd11813208272b4271d92bd92feb8f3fdbe61be5
        cd native/libsm64
        python import-mario-geo.py          # libsm64's own step: downloads Mario's model from n64decomp/sm64
        cd ../..

    You also need zig 0.17.0 (https://ziglang.org/download/ - a plain zip, nothing to install) and Python 3.

    Then:

        native\build.ps1 -Zig C:\tools\zig-0.17.0\zig.exe -Output dist\native\sm64-mario.dll

    The result exports everything the mod needs in every mode (including the optional carry feature), so one
    DLL is all there is. Your ROM is not needed to build; it is only read when the game starts.

.PARAMETER Zig
    Path to zig.exe.

.PARAMETER Output
    Where to write sm64-mario.dll (the launcher looks in dist/native/).

.PARAMETER Source
    The libsm64 checkout. Default: native/libsm64.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Zig,
    [Parameter(Mandatory = $true)][string]$Output,
    [string]$Source = ''
)
$ErrorActionPreference = 'Stop'
# Windows PowerShell 5.1 leaves $PSScriptRoot empty in parameter defaults, so the default is set here.
if (-not $Source) { $Source = Join-Path $PSScriptRoot 'libsm64' }

$manifest = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'libsm64-source.json') -Raw | ConvertFrom-Json
$setup = @"

To get the source (nothing here downloads it for you):

    git clone $($manifest.repository).git native/libsm64
    git -C native/libsm64 checkout $($manifest.commit)
    cd native/libsm64
    python import-mario-geo.py
    cd ../..

"@

function Stop-Build([string]$Message, [string]$Help = '') {
    Write-Host "`nBuild stopped: $Message" -ForegroundColor Red
    if ($Help) { Write-Host $Help }
    exit 1
}

# zig
if (-not (Test-Path -LiteralPath $Zig -PathType Leaf)) {
    Stop-Build "zig.exe not found at '$Zig'." "Get zig $($manifest.zig) from https://ziglang.org/download/ (the Windows x86_64 zip), unpack it anywhere and pass the path to zig.exe."
}
$zigVersion = (& $Zig version).Trim()
if ($zigVersion -ne $manifest.zig) {
    Write-Host "Warning: zig $zigVersion found, this mod was built with zig $($manifest.zig). Other versions may not compile it." -ForegroundColor Yellow
}

# python
$python = $null
foreach ($candidate in @('python', 'py')) {
    $found = Get-Command $candidate -ErrorAction SilentlyContinue
    if ($found) { $python = $found.Source; break }
}
if (-not $python) { Stop-Build 'Python 3 was not found on PATH.' 'Install Python 3 from https://www.python.org/downloads/ (the build script and libsm64''s import step are Python).' }

# libsm64 checkout
if (-not (Test-Path -LiteralPath (Join-Path $Source 'src/libsm64.c'))) {
    Stop-Build "No libsm64 checkout at '$Source'." $setup
}
$gitDir = Join-Path $Source '.git'
if ((Test-Path -LiteralPath $gitDir) -and (Get-Command git -ErrorAction SilentlyContinue)) {
    $head = (& git -C $Source rev-parse HEAD).Trim()
    if ($head -ne $manifest.commit) {
        Stop-Build "The checkout is at $head, not $($manifest.commit)." "Run:  git -C `"$Source`" checkout $($manifest.commit)  and then python import-mario-geo.py again."
    }
}
if (-not (Test-Path -LiteralPath (Join-Path $Source 'src/decomp/mario/geo.inc.c'))) {
    Stop-Build 'Mario''s model files are missing (src/decomp/mario).' "Run libsm64's own step once:  cd `"$Source`"; python import-mario-geo.py   (it downloads the model from the n64decomp/sm64 repository)."
}

$outDir = Split-Path -Parent ([IO.Path]::GetFullPath($Output))
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
$arguments = @((Join-Path $PSScriptRoot 'scripts/build_native.py'), '--source', (Resolve-Path -LiteralPath $Source).Path,
    '--zig', (Resolve-Path -LiteralPath $Zig).Path, '--output', ([IO.Path]::GetFullPath($Output)))
& $python @arguments
if ($LASTEXITCODE -ne 0) { Stop-Build "build_native.py failed (exit $LASTEXITCODE)." }
if (-not (Test-Path -LiteralPath $Output)) { Stop-Build 'The compiler reported success but no DLL was written.' }
Write-Host "`nsm64-mario.dll is ready: $Output" -ForegroundColor Green
