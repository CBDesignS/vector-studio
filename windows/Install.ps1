# Per-user setup. No administrator rights or permanent policy changes required.
[CmdletBinding()]
param(
    [string]$InstallDirectory = (Join-Path $env:LOCALAPPDATA 'VectorStudioCuttingLab'),
    [switch]$CheckOnly
)
$ErrorActionPreference = 'Stop'

function Confirm-Step([string]$Question) {
    return (Read-Host "$Question [y/N]") -match '^(y|yes)$'
}

function Test-Python([string]$Executable) {
    if (-not $Executable -or -not (Test-Path -LiteralPath $Executable -PathType Leaf)) { return $false }
    # Ignore Store aliases, which can open the Store instead of running Python.
    if ($Executable -like '*\Microsoft\WindowsApps\*') { return $false }
    try {
        $result = & $Executable -c "import sys,struct,venv,ensurepip; print('VECTOR_PY_OK' if sys.version_info[:2] in ((3,11),(3,12)) and struct.calcsize('P') == 8 else 'NO')" 2>$null
        return $LASTEXITCODE -eq 0 -and $result -contains 'VECTOR_PY_OK'
    } catch { return $false }
}

function Find-Python {
    $candidates = [System.Collections.Generic.List[string]]::new()
    foreach ($version in @('3.12','3.11')) {
        $suffix = $version.Replace('.', '')
        $candidates.Add((Join-Path $env:LOCALAPPDATA "Programs\Python\Python$suffix\python.exe"))
        $candidates.Add((Join-Path $env:ProgramFiles "Python$suffix\python.exe"))
        foreach ($hive in @('HKCU:','HKLM:')) {
            $key = "$hive\Software\Python\PythonCore\$version\InstallPath"
            try {
                if (Test-Path $key) {
                    $location = (Get-Item $key).GetValue('')
                    if ($location) { $candidates.Add((Join-Path $location 'python.exe')) }
                }
            } catch { } # Restricted accounts can still use the other discovery methods.
        }
        $py = Get-Command py.exe -ErrorAction SilentlyContinue
        if ($py -and $py.Source -notlike '*\Microsoft\WindowsApps\*') {
            try {
                $found = & $py.Source "-$version" -c 'import sys; print(sys.executable)' 2>$null
                if ($LASTEXITCODE -eq 0 -and $found) { $candidates.Add([string]($found | Select-Object -Last 1)) }
            } catch { }
        }
    }
    $pythonCommand = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($pythonCommand) { $candidates.Add($pythonCommand.Source) }
    foreach ($candidate in ($candidates | Select-Object -Unique)) {
        if (Test-Python $candidate) { return $candidate }
    }
    return $null
}

function Test-AppDependencies([string]$Executable) {
    if (-not (Test-Python $Executable)) { return $false }
    try {
        & $Executable -c "from importlib.metadata import version; import flask,PIL,vtracer; assert version('vtracer') == '0.6.15'; assert (3,1) <= tuple(map(int,version('Flask').split('.')[:2])) < (4,0); assert 11 <= int(version('Pillow').split('.')[0]) < 13" 2>$null | Out-Null
        if ($LASTEXITCODE -ne 0) { return $false }
        & $Executable -m pip check 2>$null | Out-Null
        return $LASTEXITCODE -eq 0
    } catch { return $false }
}

try {
    Write-Host "`nVector Studio Cutting Lab - Experimental Windows Setup`n" -ForegroundColor Green
    if (-not [Environment]::Is64BitOperatingSystem) { throw 'This setup requires 64-bit Windows 10 or Windows 11.' }
    $sourceDirectory = Split-Path -Parent $PSScriptRoot
    foreach ($required in @('app.py','launcher.py','Run.cmd','requirements.txt','templates\index.html','static\app.js','static\style.css','static\cutting.css','static\icons\app.ico','static\theme.js','static\theme.css')) {
        if (-not (Test-Path -LiteralPath (Join-Path $sourceDirectory $required))) {
            throw "Missing $required. Extract the entire ZIP before running Install.cmd."
        }
    }
    $python = Find-Python
    $destination = [IO.Path]::GetFullPath($InstallDirectory)
    $venvPython = Join-Path $destination '.venv\Scripts\python.exe'
    Write-Host "Install folder: $destination"
    if ($python) { Write-Host "Compatible Python found: $python" }
    else { Write-Host 'Python 3.11 or 3.12 (64-bit, with venv) was not found.' }
    $dependenciesReady = Test-AppDependencies $venvPython
    Write-Host "App dependencies ready: $dependenciesReady"
    if ($CheckOnly) {
        Write-Host 'Check complete. Nothing was installed or changed.'
        return
    }
    if (-not $python) {
        if (-not (Confirm-Step 'Install Python 3.12 from the Python Software Foundation using Windows Package Manager?')) {
            throw 'Python installation declined. Install 64-bit Python 3.11 or 3.12 from python.org, then rerun setup.'
        }
        $winget = Get-Command winget.exe -ErrorAction SilentlyContinue
        if (-not $winget) {
            throw 'Windows Package Manager is unavailable. Install Python 3.12 from https://www.python.org/downloads/windows/ (include pip), then rerun setup.'
        }
        # Leave package/source agreement prompts visible for the user to review.
        & $winget.Source install --id Python.Python.3.12 --exact --source winget --scope user --architecture x64
        if ($LASTEXITCODE -notin @(0, 3010)) { throw 'Python installation did not complete. Review the Windows Package Manager message above.' }
        $python = Find-Python
        if (-not $python) { throw 'Python was not found after installation. Restart this setup, or install Python 3.12 from python.org.' }
    }
    if (-not (Confirm-Step "Set up Vector Studio in $destination and create a desktop shortcut? Existing app source files there will be updated")) {
        throw 'Setup cancelled. No app files were copied.'
    }
    if (-not $dependenciesReady) {
        if (-not (Confirm-Step 'Download and install Flask, Pillow, and VTracer plus their dependencies into a private app environment? Internet access is required')) {
            throw 'Dependency installation declined.'
        }
    }
    New-Item -ItemType Directory -Path $destination -Force | Out-Null
    # Explicit allowlist avoids copying uploads, caches, or the development environment.
    $files = @('app.py','launcher.py','Run.cmd','Install.cmd','README.md','INSTALL.md','requirements.txt',
               '.gitignore','windows\Install.ps1','templates\index.html',
               'static\app.js','static\style.css','static\cutting.css','static\theme.js','static\theme.css','static\icons\app.ico',
               'static\icons\favicon.ico','static\icons\icon.svg',
               'static\icons\app-192.png','static\icons\app-512.png','tests\test_app.py')
    foreach ($relative in $files) {
        $from = Join-Path $sourceDirectory $relative
        $to = Join-Path $destination $relative
        if ((Test-Path -LiteralPath $from) -and ([IO.Path]::GetFullPath($from) -ne [IO.Path]::GetFullPath($to))) {
            New-Item -ItemType Directory -Path (Split-Path -Parent $to) -Force | Out-Null
            Copy-Item -LiteralPath $from -Destination $to -Force
        }
    }
    if (-not (Test-Python $venvPython)) {
        Write-Host 'Creating the private Python environment...'
        & $python -m venv (Join-Path $destination '.venv')
        if ($LASTEXITCODE -ne 0) { throw 'Could not create the app environment. Check that your Python installation includes pip and venv.' }
    }
    if (-not $dependenciesReady) {
        & $venvPython -m pip install --only-binary=:all: -r (Join-Path $destination 'requirements.txt')
        if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed. Check your internet connection, then run setup again.' }
    }
    if (-not (Test-AppDependencies $venvPython)) { throw 'Dependency verification failed. Run setup again to repair the installation.' }
    Write-Host 'Checking the installed app (including a real VTracer conversion)...'
    Push-Location $destination
    try {
        & $venvPython -m unittest discover -s tests -v
        if ($LASTEXITCODE -ne 0) { throw 'The installed app did not pass its checks. No shortcut was created.' }
    } finally { Pop-Location }
    $desktop = [Environment]::GetFolderPath('DesktopDirectory')
    if (-not $desktop) { throw 'Windows could not locate your desktop. You can still start the app with Run.cmd in the install folder.' }
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut((Join-Path $desktop 'Vector Studio Cutting Lab.lnk'))
    $shortcut.TargetPath = $env:ComSpec
    $shortcut.Arguments = '/d /c ""' + (Join-Path $destination 'Run.cmd') + '""'
    $shortcut.WorkingDirectory = $destination
    $shortcut.Description = 'Start the experimental Vector Studio Cutting Lab'
    $shortcut.IconLocation = (Join-Path $destination 'static\icons\app.ico') + ',0'
    $shortcut.Save()
    Write-Host "`nInstalled successfully. Open Vector Studio Cutting Lab from your desktop." -ForegroundColor Green
    Write-Host 'Keep its console window open while using the app; close it to stop.'
    Write-Host 'To remove the app: close it, delete the install folder and the desktop shortcut. Python is kept for other apps.'
} catch {
    Write-Host "`nSetup stopped: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
