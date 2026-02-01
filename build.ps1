# Build script for poetry-fill-blank
# Uses pyinstaller to build and optimize the executable

param(
    [switch]$Clean,
    [switch]$NoUPX,
    [string]$Name = "poetry-fill-blank"
)

$ErrorActionPreference = "Stop"

function Write-Info($msg) { Write-Host "[+] $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "[!] $msg" -ForegroundColor Yellow }
function Write-Err($msg) { Write-Host "[X] $msg" -ForegroundColor Red }
function Write-Step($msg) { Write-Host "`n[*] $msg" -ForegroundColor Cyan }

function Check-PyInstaller {
    $pyi = Get-Command pyinstaller -ErrorAction SilentlyContinue
    if (-not $pyi) {
        Write-Err "pyinstaller not found"
        Write-Warn "Install with: pip install pyinstaller"
        exit 1
    }
    Write-Info "pyinstaller found: $($pyi.Source)"
}

function Check-UPX {
    $upx = Get-Command upx -ErrorAction SilentlyContinue
    if ($upx) {
        Write-Info "UPX found: $($upx.Source), compression enabled"
        return $true
    } else {
        Write-Warn "UPX not found, skipping extra compression"
        Write-Warn "Download from: https://github.com/upx/upx/releases"
        return $false
    }
}

function Clean-Build {
    Write-Step "Cleaning old build files..."
    $dirs = @("build", "dist", "__pycache__")
    foreach ($dir in $dirs) {
        if (Test-Path $dir) {
            Remove-Item -Recurse -Force $dir
            Write-Info "Removed: $dir"
        }
    }
    Get-ChildItem -Recurse -Filter "*.pyc" -ErrorAction SilentlyContinue | Remove-Item -Force
    Get-ChildItem -Recurse -Filter "__pycache__" -Directory -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
    Write-Info "Clean complete"
}

function Generate-Spec {
    param($UseUPX, $ExeName)
    
    Write-Step "Generating optimized spec file..."
    
    $upxFlag = "False"
    if ($UseUPX -and -not $NoUPX) {
        $upxFlag = "True"
    }
    
    $specContent = @"
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('data/format_prompt.md', 'data'),
        ('data/reference-original.json', 'data'),
        ('config.json', '.'),
    ],
    hiddenimports=[
        'rich',
        'rich.console',
        'rich.panel',
        'rich.table',
        'rich.progress',
        'requests',
        'urllib3',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'PIL',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
        'tkinter',
        'unittest',
        'pytest',
        'pydoc',
    ],
    noarchive=False,
    optimize=2,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='$ExeName',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=$upxFlag,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"@
    
    $specFile = "build_temp.spec"
    $specContent | Out-File -FilePath $specFile -Encoding UTF8
    Write-Info "Spec file generated: $specFile"
    return $specFile
}

function Build-Executable {
    param($SpecFile)
    
    Write-Step "Building executable..."
    Write-Warn "This may take a few minutes..."
    
    pyinstaller $SpecFile --clean --noconfirm
    
    if ($LASTEXITCODE -ne 0) {
        Write-Err "Build failed!"
        exit 1
    }
    
    Write-Info "Build complete"
}

function Copy-Dependencies {
    param($ExeName)
    
    Write-Step "Copying dependencies to dist..."
    
    $distDir = "dist\$ExeName"
    if (-not (Test-Path $distDir)) {
        $distDir = "dist"
    }
    
    if (Test-Path "data") {
        if (Test-Path "$distDir\data") {
            Remove-Item -Recurse -Force "$distDir\data"
        }
        Copy-Item -Recurse -Force "data" "$distDir\data"
        Write-Info "Copied: data -> $distDir\data"
    }
    
    $exePath = "$distDir\$ExeName.exe"
    if (Test-Path $exePath) {
        $size = (Get-Item $exePath).Length / 1MB
        Write-Info ("Executable size: {0:N2} MB" -f $size)
    }
}

function Show-Result {
    param($ExeName)
    
    Write-Step "Build Result"
    
    $distPath = Resolve-Path "dist"
    Write-Info "Output directory: $distPath"
    
    Get-ChildItem "dist" -Recurse | ForEach-Object {
        $size = ""
        if ($_.PSIsContainer) { 
            $size = "<DIR>" 
        } else { 
            $size = ("{0:N2} MB" -f ($_.Length / 1MB))
        }
        $relPath = $_.FullName.Replace($distPath, "")
        Write-Host "    $relPath  $size"
    }
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  Build Complete!" -ForegroundColor Green
    Write-Host "  Run: .\dist\$ExeName\$ExeName.exe" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
}

# Main
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Poetry Generator - Build Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Check-PyInstaller
$hasUPX = Check-UPX

if ($Clean) {
    Clean-Build
}

$specFile = Generate-Spec -UseUPX $hasUPX -ExeName $Name
Build-Executable -SpecFile $specFile
Copy-Dependencies -ExeName $Name
Show-Result -ExeName $Name

if (Test-Path $specFile) {
    Remove-Item $specFile
}

Write-Host ""
Write-Host "Press any key to exit..." -NoNewline
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
