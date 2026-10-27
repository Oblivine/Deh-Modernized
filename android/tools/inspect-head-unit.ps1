<#
.SYNOPSIS
  Collect a read-only Android head-unit inventory using an already-authorized ADB connection.
.DESCRIPTION
  Saves Android and hardware properties, memory, WebView information, package names,
  and launchable activities. Package and app names may be private; review the report
  before sharing it. No serial numbers or network addresses are included intentionally.
  This helper does not connect, pair, change settings, install, root, or flash a device.
.EXAMPLE
  .\inspect-head-unit.ps1 -AdbPath 'C:\platform-tools\adb.exe' -ReportPath '.\head-unit-report.txt'
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)] [string] $ReportPath,
    [string] $AdbPath = 'adb'
)

$ErrorActionPreference = 'Stop'
$adbCommand = Get-Command $AdbPath -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $adbCommand) { throw 'ADB was not found. Supply -AdbPath pointing to the official Android platform-tools adb executable.' }
$adbExecutable = $adbCommand.Source

# Do not put device-list output in the report: it contains serial numbers or addresses.
$deviceOutput = @(& $adbExecutable devices 2>&1)
if ($LASTEXITCODE -ne 0) { throw 'ADB could not list devices. Start or repair ADB, then retry.' }
$entries = @($deviceOutput | ForEach-Object { [string]$_ } | Where-Object { $_ -match '^\S+\s+(device|offline|unauthorized|no permissions)\s*$' })
if ($entries.Count -ne 1 -or $entries[0] -notmatch '^\S+\s+device\s*$') {
    throw 'Exactly one connected and authorized ADB device is required. No connection or authorization is attempted by this script.'
}

$lines = [System.Collections.Generic.List[string]]::new()
$lines.Add('DEH Modernized - read-only Android inventory')
$lines.Add('Contains installed package and app-component names. Review before sharing.')
$lines.Add('These values are reported by Android and may not reflect the true underlying hardware.')
$lines.Add('')

function Add-AdbSection {
    param([string] $Title, [string[]] $Arguments, [string] $Include = '.*')
    $lines.Add('--- ' + $Title + ' ---')
    try {
        $result = @(& $adbExecutable @Arguments 2>&1)
        if ($LASTEXITCODE -ne 0) { $lines.Add('Unavailable (ADB command failed).') }
        else {
            $filtered = @($result | ForEach-Object { [string]$_ } | Where-Object { $_ -match $Include })
            if ($filtered.Count -eq 0) { $lines.Add('Unavailable or no matching information was reported.') }
            else { foreach ($line in $filtered) { $lines.Add($line) } }
        }
    } catch { $lines.Add('Unavailable (ADB command failed).') }
    $lines.Add('')
}

foreach ($entry in @(
    @('Android version', 'ro.build.version.release'),
    @('Android API level', 'ro.build.version.sdk'),
    @('Manufacturer', 'ro.product.manufacturer'),
    @('Model', 'ro.product.model'),
    @('Device product', 'ro.product.name'),
    @('Hardware', 'ro.hardware'),
    @('CPU ABIs', 'ro.product.cpu.abilist')
)) { Add-AdbSection -Title $entry[0] -Arguments @('shell','getprop',$entry[1]) }

# Only include selected keys: some Android kernels expose a hardware serial in cpuinfo.
Add-AdbSection -Title 'CPU details' -Arguments @('shell','cat','/proc/cpuinfo') -Include '^\s*(model name|Hardware|CPU architecture|processor)\s*:'
Add-AdbSection -Title 'Total memory' -Arguments @('shell','cat','/proc/meminfo') -Include '^MemTotal:'
Add-AdbSection -Title 'WebView provider details' -Arguments @('shell','dumpsys','webviewupdate') -Include '(?i)(current webview package|preferred webview package|valid webview package|versionName|versionCode)'
Add-AdbSection -Title 'Installed package names' -Arguments @('shell','pm','list','packages') -Include '^package:[A-Za-z0-9_.]+\s*$'
Add-AdbSection -Title 'Launchable activities (if supported)' -Arguments @('shell','cmd','package','query-activities','--brief','-a','android.intent.action.MAIN','-c','android.intent.category.LAUNCHER') -Include '^[A-Za-z0-9_.]+/[A-Za-z0-9_.$]+\s*$'

$target = [System.IO.Path]::GetFullPath($ReportPath)
$directory = [System.IO.Path]::GetDirectoryName($target)
if (-not (Test-Path -LiteralPath $directory -PathType Container)) { throw 'The report folder does not exist.' }
if (Test-Path -LiteralPath $target) { throw 'The report file already exists. Choose a new report path to avoid overwriting it.' }
[System.IO.File]::WriteAllLines($target, $lines, [System.Text.UTF8Encoding]::new($false))
Write-Host "Read-only report saved to $target"
Write-Host 'Review installed package and activity names before sharing the report.'
