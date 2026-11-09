# Internal marketplace Setup, Windows PowerShell 5.1. Never change execution policy.
[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$PackageRoot, [switch]$Consent,
      [string]$Helper,
      [Parameter(ValueFromRemainingArguments=$true)][string[]]$HelperArguments)
# A PowerShell 7 executor may pass its incompatible module search path to 5.1.
# Select only this native host's built-in modules in this child process.
$env:PSModulePath = [IO.Path]::Combine($PSHOME, 'Modules')
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2
$stage = $null
$lock = $null
$environment = @{}

function Emit($Value) { $Value | ConvertTo-Json -Compress -Depth 8 }
function Digest([string]$File) { (Get-FileHash -LiteralPath $File -Algorithm SHA256).Hash.ToLowerInvariant() }
function Inventory([string]$Directory) {
    $items = @(Get-ChildItem -LiteralPath (Join-Path $Directory 'python') -Recurse -Force | Sort-Object FullName)
    $lines = foreach ($entry in $items) {
        if ($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Unexpected acquired reparse point' }
        $name = $entry.FullName.Substring($Directory.Length + 1).Replace('\', '/')
        if ($entry.PSIsContainer) { 'directory ' + $name } else { (Digest $entry.FullName) + ' ' + $name }
    }
    return ($lines -join "`n")
}
function Download([string]$Url, [string]$Destination) {
    Add-Type -AssemblyName System.Net.Http
    $handler = New-Object Net.Http.HttpClientHandler
    $handler.AllowAutoRedirect = $false
    $client = New-Object Net.Http.HttpClient($handler)
    $client.Timeout = [TimeSpan]::FromSeconds(240)
    try {
        for ($redirect = 0; $redirect -lt 8; $redirect++) {
            $uri = [Uri]$Url
            if ($uri.Scheme -ne 'https') { throw 'Only HTTPS runtime acquisition is allowed' }
            $response = $client.GetAsync($uri).GetAwaiter().GetResult()
            try {
                if ([int]$response.StatusCode -in @(301,302,303,307,308)) {
                    $Url = ([Uri]::new($uri, $response.Headers.Location)).AbsoluteUri
                    continue
                }
                $response.EnsureSuccessStatusCode() | Out-Null
                $stream = [IO.File]::Open($Destination, [IO.FileMode]::CreateNew)
                try { $response.Content.CopyToAsync($stream).GetAwaiter().GetResult() } finally { $stream.Dispose() }
                return
            } finally { $response.Dispose() }
        }
        throw 'Too many runtime download redirects'
    } finally { $client.Dispose(); $handler.Dispose() }
}

try {
    if ($PSBoundParameters.ContainsKey('Helper') -and -not $Helper) { throw 'Missing helper name' }
    if ($HelperArguments -and -not $Helper) { throw 'Helper arguments require a helper name' }
    if ($Helper -and $Consent) { throw 'Helper invocation cannot provision; choose Setup separately' }
    if ($env:OS -ne 'Windows_NT' -or $PSVersionTable.PSEdition -ne 'Desktop' -or $PSVersionTable.PSVersion -lt [version]'5.1') {
        throw 'Use the native Windows PowerShell 5.1 host; no WSL, Git Bash or alternate installer is required'
    }
    if (-not [IO.Path]::IsPathRooted($PackageRoot) -or $PackageRoot -notmatch '^[A-Za-z]:[\\/]') { throw 'An explicit absolute local package root is required' }
    $PackageRoot = [IO.Path]::GetFullPath($PackageRoot).TrimEnd('\')
    foreach ($name in @('SKILL.md', 'scripts\kkdesign_setup.py', 'scripts\kkdesign_windows_security.ps1')) {
        if (-not (Test-Path -LiteralPath (Join-Path $PackageRoot $name) -PathType Leaf)) { throw 'Invalid package root' }
    }
    . (Join-Path $PackageRoot 'scripts\kkdesign_windows_security.ps1')
    # OS architecture, not the architecture of a possibly emulated process.
    $architecture = (Get-ItemProperty -LiteralPath 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Environment').PROCESSOR_ARCHITECTURE
    switch ($architecture) {
        'AMD64' { $target = 'x86_64'; $digest = '2d670beb3b930d30e3a13cc909923a001dbdfcb5537692d5da40b6b41643ce1c' }
        'ARM64' { $target = 'aarch64'; $digest = 'd708734581e8cb03f4cf95f39f17ea331bc4761dfdad99b6b738a245444c9c54' }
        default { throw 'No pinned Windows Python artifact for this CPU' }
    }
    $tar = Join-Path ([Environment]::GetFolderPath('Windows')) 'System32\tar.exe'
    if (-not (Test-Path -LiteralPath $tar -PathType Leaf)) { throw 'Setup requires the native Windows tar tool (Windows 10 1803 or newer)' }
    $userHome = $env:USERPROFILE
    if ($userHome -notmatch '^[A-Za-z]:[\\/]') { throw 'An absolute local user profile is required' }
    $base = Join-Path $userHome '.kkdesign-kit'
    $root = Join-Path $base 'bootstrap'
    $cache = Join-Path $root ('cpython-3.12.12-20251014-' + $target + '-pc-windows-msvc')
    Assert-PrivatePath $cache $userHome
    if ($Helper -and -not (Test-Path -LiteralPath $cache -PathType Container)) { throw 'Setup required: managed bootstrap is missing; choose Setup in the installed skill' }
    if (-not (Test-Path -LiteralPath $cache) -and -not $Consent) {
        [Console]::Error.WriteLine("Setup needs pinned CPython 3.12.12 from Astral python-build-standalone release 20251014 over HTTPS and requirements.txt dependencies from the package index. Storage: $cache and $base\runtimes. Network, private user-cache writes and local execution are required; no admin, system Python, PATH or policy changes. Obtain explicit consent before -Consent.")
        Emit @{plugin='loaded'; runtime='setup-required'; externalTools='unverified'; status='consent-required'; phase='consent-required'}
        exit 0
    }
    foreach ($directory in @($base, $root)) {
        if (-not (Test-Path -LiteralPath $directory)) { New-PrivateDirectory $directory }
        Assert-PrivatePath $directory $userHome
    }
    # Exclusive open, no stale-lock deletion or recovery of another transaction.
    $lockPath = Join-Path $root 'setup.lock'
    $lock = [IO.File]::Open($lockPath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    if (-not (Test-Path -LiteralPath $cache)) {
        Emit @{phase='downloading-python'; runtime='setup-required'; externalTools='unverified'}
        $stage = Join-Path $root ('.preparing.' + [Guid]::NewGuid().ToString('N'))
        New-PrivateDirectory $stage
        $archive = Join-Path $stage 'archive.tar.gz'
        $artifact = "cpython-3.12.12%2B20251014-$target-pc-windows-msvc-install_only.tar.gz"
        Download "https://github.com/astral-sh/python-build-standalone/releases/download/20251014/$artifact" $archive
        if ((Digest $archive) -ne $digest) { throw 'Downloaded Python checksum mismatch; nothing was executed' }
        & $tar -xzf $archive -C $stage
        if ($LASTEXITCODE -ne 0) { throw 'Python extraction failed' }
        Assert-PrivatePath $stage $userHome -Tree
        [IO.File]::WriteAllText((Join-Path $stage 'inventory.sha256'), (Inventory $stage))
        [IO.Directory]::Move($stage, $cache)
        $stage = $null
    }
    Assert-PrivatePath $cache $userHome -Tree
    if ((Digest (Join-Path $cache 'archive.tar.gz')) -ne $digest) { throw 'Cached artifact checksum mismatch; preserve and inspect it' }
    if ((Inventory $cache) -cne [IO.File]::ReadAllText((Join-Path $cache 'inventory.sha256'))) { throw 'Cached Python tree changed; preserve and inspect it' }
    $python = Join-Path $cache 'python\python.exe'
    if (-not (Test-Path -LiteralPath $python -PathType Leaf)) { throw 'Managed bootstrap interpreter is missing' }
    foreach ($name in @('PYTHONHOME','PYTHONPATH','PYTHONSTARTUP')) {
        $environment[$name] = [Environment]::GetEnvironmentVariable($name, 'Process')
        [Environment]::SetEnvironmentVariable($name, $null, 'Process')
    }
    $arguments = @('-I','-B', (Join-Path $PackageRoot 'scripts\kkdesign_setup.py'), '--package-root', $PackageRoot)
    if ($Helper) {
        $arguments = @('-I','-B', (Join-Path $PackageRoot 'scripts\kkdesign_run.py'), '--package-root', $PackageRoot, $Helper) + $HelperArguments
    } elseif ($Consent) { $arguments += '--consent' }
    & $python @arguments
    if ($Helper) { exit $LASTEXITCODE }
    if ($LASTEXITCODE -ne 0) { throw 'Runtime execution or helper verification failed' }
} catch {
    [Console]::Error.WriteLine($_.Exception.Message + '. Restore approved network access, user-cache writes or local execution with the administrator; do not bypass policy or use another installer. Existing caches are preserved.')
    Emit @{plugin='loaded'; runtime='error'; externalTools='unverified'; status='error'; phase='failed'}
    exit 1
} finally {
    foreach ($name in $environment.Keys) { [Environment]::SetEnvironmentVariable($name, $environment[$name], 'Process') }
    if ($stage) { Remove-Item -LiteralPath $stage -Recurse -Force }
    if ($lock) { $lock.Dispose(); Remove-Item -LiteralPath $lockPath -Force }
}
