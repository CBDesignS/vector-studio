[CmdletBinding()]
param([switch]$CheckOnly)
$ErrorActionPreference = 'Stop'
$appId = 'cutting-lab'
$appFolder = 'VectorStudioCuttingLab'
$appName = 'Vector Studio Cutting Lab'
. (Join-Path $PSScriptRoot 'AppMaintenance.ps1')

try {
    $target = Get-AppTarget (Join-Path $env:LOCALAPPDATA $appFolder) $appFolder
    $state = Get-AppInstallState $target $appId
    Write-Host "`nUninstall $appName`nFolder: $target`nState: $state"
    if ($CheckOnly) { Write-Host 'Check only: nothing was changed.'; return }
    if ($state -eq 'Absent') {
        Remove-AppShortcuts $target $appName
        Write-Host 'The app folder is already absent. Matching shortcuts were removed.'
        return
    }
    Assert-NoAppLinks $target
    Assert-AppStopped $target
    Write-Host 'This permanently removes this app folder, its private environment, and matching shortcuts.'
    Write-Host 'Any personal files saved INSIDE that folder will also be removed. Move them elsewhere first.'
    Write-Host 'Python, the other Vector Studio edition, browser preferences, and files outside this folder are kept.'
    if ((Read-Host 'Remove this installation? [y/N]') -notmatch '^(y|yes)$') {
        Write-Host 'Cancelled. Nothing was removed.'
        return
    }
    Set-Location -LiteralPath $env:TEMP
    Remove-AppFolder $target $appFolder $appId
    Remove-AppShortcuts $target $appName
    Write-Host "`n$appName has been removed." -ForegroundColor Green
} catch {
    Write-Host "`nUninstall stopped: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host 'If Windows reported locked files, close the app and rerun Uninstall.cmd from an extracted ZIP.'
    exit 1
}
