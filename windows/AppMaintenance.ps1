# Shared safety checks for setup and uninstall. No actions run when dot-sourced.
function Get-AppTarget([string]$Directory, [string]$Folder) {
    if (-not $env:LOCALAPPDATA) { throw 'Windows did not report a local application-data folder.' }
    $root = [IO.Path]::GetFullPath($env:LOCALAPPDATA).TrimEnd('\','/')
    $expected = [IO.Path]::GetFullPath((Join-Path $root $Folder)).TrimEnd('\','/')
    $target = [IO.Path]::GetFullPath($Directory).TrimEnd('\','/')
    if (-not $target.Equals($expected, [StringComparison]::OrdinalIgnoreCase) -or $target.Equals($root, [StringComparison]::OrdinalIgnoreCase)) {
        throw "For safety, this setup only manages $expected."
    }
    return $target
}

function Assert-NoAppLinks([string]$Target) {
    if (-not (Test-Path -LiteralPath $Target)) { return }
    # Walk one directory at a time; never traverse junctions or symbolic links.
    $pending = [Collections.Generic.Stack[string]]::new()
    $pending.Push($Target)
    while ($pending.Count -gt 0) {
        $path = $pending.Pop()
        $item = Get-Item -LiteralPath $path -Force
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            throw "A link or junction was found at $path. Automatic removal is disabled for this folder."
        }
        if ($item.PSIsContainer) {
            foreach ($child in (Get-ChildItem -LiteralPath $path -Force)) {
                if ($child.Attributes -band [IO.FileAttributes]::ReparsePoint) {
                    throw "A link or junction was found at $($child.FullName). Automatic removal is disabled for this folder."
                }
                if ($child.PSIsContainer) { $pending.Push($child.FullName) }
            }
        }
    }
}

function Get-AppInstallState([string]$Target, [string]$AppId) {
    if (-not (Test-Path -LiteralPath $Target)) { return 'Absent' }
    if (-not (Test-Path -LiteralPath $Target -PathType Container)) { throw 'The installation path is not a folder.' }
    $marker = Join-Path $Target '.vector-studio-install.json'
    if (Test-Path -LiteralPath $marker) {
        $record = Get-Content -LiteralPath $marker -Raw | ConvertFrom-Json
        if ($record.app_id -ne $AppId -or -not ([IO.Path]::GetFullPath([string]$record.install_directory)).TrimEnd('\','/').Equals($Target, [StringComparison]::OrdinalIgnoreCase)) {
            throw 'The installation record belongs to a different app or folder. No files will be removed.'
        }
        return 'Managed'
    }
    if ((Test-Path -LiteralPath (Join-Path $Target 'app.py')) -and
        ((Test-Path -LiteralPath (Join-Path $Target 'Run.cmd')) -or (Test-Path -LiteralPath (Join-Path $Target 'windows\Run.cmd'))) -and
        (Test-Path -LiteralPath (Join-Path $Target '.venv\pyvenv.cfg'))) { return 'Legacy' }
    if (@(Get-ChildItem -LiteralPath $Target -Force).Count -eq 0) { return 'Empty' }
    throw 'The target contains unrecognized files and no valid installation record. No files will be removed.'
}

function Assert-AppStopped([string]$Target) {
    $lock = Join-Path $Target '.vector-studio-running.lock'
    if (Test-Path -LiteralPath $lock) {
        try {
            $stream = [IO.File]::Open($lock, [IO.FileMode]::Open, [IO.FileAccess]::ReadWrite, [IO.FileShare]::None)
            $stream.Dispose()
        } catch { throw 'Vector Studio is running (or its lock file is unavailable). Close its console window and try again.' }
    }
    # Also detect older launchers, which did not create a running marker.
    $processes = @()
    try { $processes = @(Get-CimInstance Win32_Process -Filter "Name = 'python.exe' OR Name = 'pythonw.exe'" -ErrorAction Stop) }
    catch { Write-Host 'Windows could not check older Python processes. Make sure all app console windows are closed.' }
    $prefix = $Target.TrimEnd('\','/') + [IO.Path]::DirectorySeparatorChar
    foreach ($process in $processes) {
        if ($process.ExecutablePath -and ([string]$process.ExecutablePath).StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) {
            throw 'Vector Studio is running. Close its console window and try again.'
        }
    }
}

function Remove-AppFolder([string]$Directory, [string]$Folder, [string]$AppId) {
    $target = Get-AppTarget $Directory $Folder
    $state = Get-AppInstallState $target $AppId
    if ($state -eq 'Absent') { return }
    Assert-NoAppLinks $target
    Assert-AppStopped $target
    # The resolved absolute target was checked against this app's exact user folder.
    Remove-Item -LiteralPath $target -Recurse -Force
}

function Remove-AppShortcuts([string]$Target, [string]$Name) {
    $desktop = [Environment]::GetFolderPath('DesktopDirectory')
    $programs = [Environment]::GetFolderPath('Programs')
    $shell = New-Object -ComObject WScript.Shell
    $links = @()
    if ($desktop) { $links += (Join-Path $desktop "$Name.lnk") }
    $menu = $null
    if ($programs) {
        $menu = Join-Path $programs $Name
        $links += (Join-Path $menu "$Name.lnk")
        $links += (Join-Path $menu "Uninstall $Name.lnk")
    }
    foreach ($path in $links) {
        if (Test-Path -LiteralPath $path -PathType Leaf) {
            $link = $shell.CreateShortcut($path)
            if ($link.WorkingDirectory.TrimEnd('\','/').Equals($Target, [StringComparison]::OrdinalIgnoreCase) -or $link.Arguments.IndexOf($Target, [StringComparison]::OrdinalIgnoreCase) -ge 0) {
                Remove-Item -LiteralPath $path -Force
            }
        }
    }
    if ($menu -and (Test-Path -LiteralPath $menu) -and @(Get-ChildItem -LiteralPath $menu -Force).Count -eq 0) {
        Remove-Item -LiteralPath $menu
    }
}
