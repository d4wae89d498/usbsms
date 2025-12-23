# -------------------------------
# Save original directory (UNC OK)
# -------------------------------
$OrigDir = Get-Location
Write-Host "CUR PATH IS $PSScriptRoot"
Pause

# -------------------------------
# Self-elevate if needed
# -------------------------------
$IsAdmin = ([Security.Principal.WindowsPrincipal] `
    [Security.Principal.WindowsIdentity]::GetCurrent()
).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $IsAdmin) {
    Write-Host "Requesting administrative privileges..."
    Start-Process powershell `
        -Verb RunAs `
        -ArgumentList "-ExecutionPolicy Bypass -File `"$PSCommandPath`""
    exit
}

# -------------------------------
# Restore original directory
# -------------------------------
Set-Location $OrigDir

$DoUsb = Read-Host "Setup USB to WSL passthrough? (y/N)"

if ($DoUsb -match '^(y|yes)$') {

    # -------------------------------
    # List USB devices
    # -------------------------------
    usbipd list
    Write-Host ""

    # -------------------------------
    # Ask BUSID
    # -------------------------------
    $BusId = Read-Host "Enter BUSID to attach"

    # -------------------------------
    # Bind & attach
    # -------------------------------
    usbipd bind --busid $BusId
    usbipd attach --wsl --busid $BusId
}


# -------------------------------
# Convert Windows path → WSL path
# -------------------------------
$ScriptDir = $PSScriptRoot.ToString()
Write-Host $ScriptDir

if ($ScriptDir.StartsWith("\\wsl.localhost\", [System.StringComparison]::OrdinalIgnoreCase)) {
    # \\wsl.localhost\Ubuntu\home\user\dir
    $parts = $ScriptDir -split '\\'

    # parts:
    # [0] ""
    # [1] ""
    # [2] "wsl.localhost"
    # [3] "Ubuntu"
    # [4] "home"
    # ...

    $WslDir = "/" + ($parts[4..($parts.Length - 1)] -join "/")
}
else {
    # Normal Windows path (C:\...)
    $WslDir = (wsl wslpath "$ScriptDir").Trim()
}


Write-Host ""
Write-Host "Running script from:"
Write-Host "  Source dir: $ScriptDir"
Write-Host "  WSL dir:     $WslDir"
Write-Host ""

# -------------------------------
# Run script in WSL
# -------------------------------

$DoUsb = Read-Host "Run bash launch.sh? (y/N)"

if ($DoUsb -match '^(y|yes)$') {

wsl -d Ubuntu -- bash -lc "cd '$WslDir' && bash launch.sh"

}

Pause
