[CmdletBinding()]
param(
    [string]$Python = 'python',
    [switch]$SkipInstall,
    [switch]$OneDir
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$root = $PSScriptRoot
$originalLayout = $env:DEVMODE_BUILD_LAYOUT
Push-Location -LiteralPath $root
try {
    if ($SkipInstall) {
        $buildPython = (Get-Command $Python -ErrorAction Stop).Source
    } else {
        & $Python -m venv .venv-build
        if ($LASTEXITCODE -ne 0) { throw 'Creating build environment failed.' }
        $buildPython = Join-Path $root '.venv-build/Scripts/python.exe'
        & $buildPython -m pip install --disable-pip-version-check -r requirements-lock.txt
        if ($LASTEXITCODE -ne 0) { throw 'Installing build dependencies failed.' }
    }
    & $buildPython -m unittest discover -s tests -v
    if ($LASTEXITCODE -ne 0) { throw 'Tests failed.' }
    & $buildPython packaging/collect_notices.py
    if ($LASTEXITCODE -ne 0) { throw 'Collecting notices/source archives failed.' }
    $env:DEVMODE_BUILD_LAYOUT = if ($OneDir) { 'onedir' } else { 'onefile' }
    $layout = $env:DEVMODE_BUILD_LAYOUT
    & $buildPython -m PyInstaller --noconfirm --distpath "dist/$layout" --workpath "build/$layout" packaging/helper.spec
    if ($LASTEXITCODE -ne 0) { throw 'Packaging failed.' }
    $exe = if ($OneDir) { Join-Path $root 'dist/onedir/iOS-Developer-Mode-Helper/iOS-Developer-Mode-Helper.exe' } else { Join-Path $root 'dist/onefile/iOS-Developer-Mode-Helper.exe' }
    if (-not $OneDir) {
        & $buildPython packaging/check_privacy.py $exe
        if ($LASTEXITCODE -ne 0) { throw 'Packaged privacy check failed.' }
    }
    $result = Join-Path $root "build/$layout/frozen-self-test.json"
    if (Test-Path -LiteralPath $result) { Remove-Item -LiteralPath $result }
    $proc = Start-Process -FilePath $exe -ArgumentList @('--self-test','--output',('"' + $result + '"')) -WindowStyle Hidden -PassThru
    if (-not $proc.WaitForExit(60000)) { $proc.Kill(); throw 'Frozen runtime test timed out.' }
    if ($proc.ExitCode -ne 0 -or -not (Test-Path -LiteralPath $result)) { throw 'Frozen runtime test failed.' }
    $report = Get-Content -LiteralPath $result -Raw | ConvertFrom-Json
    if (-not $report.ok) { throw 'Frozen runtime test reported a failure.' }
    $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $exe).Hash.ToLowerInvariant()
    "$hash  $([IO.Path]::GetFileName($exe))" | Set-Content -LiteralPath "$exe.sha256" -Encoding ascii
    Write-Output "Built and smoke-tested: $exe"
} finally {
    $env:DEVMODE_BUILD_LAYOUT = $originalLayout
    Pop-Location
}
