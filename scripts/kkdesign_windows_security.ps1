# Shared Windows cache trust checks. No policy or ACL changes to existing data.
[CmdletBinding()]
param([string]$Path, [switch]$Recurse, [string]$UserHome = $env:USERPROFILE)
# A PowerShell 7 executor may pass its incompatible module search path to 5.1.
# Select only this native host's built-in modules in this child process.
$env:PSModulePath = [IO.Path]::Combine($PSHOME, 'Modules')
$ErrorActionPreference = 'Stop'

function Assert-PrivatePath([string]$Target, [string]$HomePath, [switch]$Tree) {
    $sid = [Security.Principal.WindowsIdentity]::GetCurrent().User.Value
    $homeFull = [IO.Path]::GetFullPath($HomePath).TrimEnd('\')
    $full = [IO.Path]::GetFullPath($Target)
    if (-not ($full.Equals($homeFull, [StringComparison]::OrdinalIgnoreCase) -or
        $full.StartsWith($homeFull + '\', [StringComparison]::OrdinalIgnoreCase))) {
        throw 'Executable cache must be inside the user home'
    }
    $cursor = $full
    while ($cursor) {
        if (Test-Path -LiteralPath $cursor) {
            $entry = Get-Item -LiteralPath $cursor -Force
            if ($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Reparse point in cache ancestry; preserve and inspect it' }
            if ($cursor.Equals($homeFull, [StringComparison]::OrdinalIgnoreCase) -or
                $cursor.StartsWith($homeFull + '\', [StringComparison]::OrdinalIgnoreCase)) {
                Assert-PrivateEntry $entry $sid
            }
        }
        $parent = [IO.Directory]::GetParent($cursor)
        if ($null -eq $parent) { break }
        $cursor = $parent.FullName
    }
    if ($Tree -and (Test-Path -LiteralPath $full)) {
        # Walk explicitly: never traverse a junction before rejecting it.
        $pending = New-Object 'Collections.Generic.Stack[string]'
        $pending.Push($full)
        while ($pending.Count) {
            $directory = $pending.Pop()
            foreach ($entry in Get-ChildItem -LiteralPath $directory -Force) {
                Assert-PrivateEntry $entry $sid
                if ($entry.PSIsContainer) { $pending.Push($entry.FullName) }
            }
        }
    }
}

function Assert-PrivateEntry($Entry, [string]$Sid) {
    if ($Entry.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Reparse point in cache; preserve and inspect it' }
    $acl = Get-Acl -LiteralPath $Entry.FullName
    # Windows may assign Administrators as owner to an elevated user's new
    # files. These authorities already have permitted write access below.
    $trusted = @($Sid, 'S-1-5-18', 'S-1-5-32-544')
    if ($acl.GetOwner([Security.Principal.SecurityIdentifier]).Value -notin $trusted) { throw 'Cache has another owner; preserve and inspect it' }
    # A missing DACL grants everyone access. Deny entries need not grant trust.
    $raw = New-Object Security.AccessControl.RawSecurityDescriptor($acl.Sddl)
    if ($null -eq $raw.DiscretionaryAcl) { throw 'Cache has no protective DACL' }
    foreach ($rule in $acl.GetAccessRules($true, $true, [Security.Principal.SecurityIdentifier])) {
        if ($rule.AccessControlType -eq [Security.AccessControl.AccessControlType]::Allow -and
            ([long]$rule.FileSystemRights -band 0x500D0156) -and
            $rule.IdentityReference.Value -notin $trusted) {
            throw ('Cache is writable by another account; preserve and inspect its ACL: ' + $Entry.FullName + ' (' + $rule.IdentityReference.Value + ')')
        }
    }
}

function New-PrivateDirectory([string]$Target) {
    # Create with its private inheritable DACL atomically, rather than opening
    # an inherited writable directory then attempting to repair it.
    $sid = [Security.Principal.WindowsIdentity]::GetCurrent().User
    $acl = New-Object Security.AccessControl.DirectorySecurity
    $acl.SetOwner($sid)
    $acl.SetAccessRuleProtection($true, $false)
    foreach ($identity in @($sid.Value, 'S-1-5-18', 'S-1-5-32-544')) {
        $rule = New-Object Security.AccessControl.FileSystemAccessRule(
            (New-Object Security.Principal.SecurityIdentifier($identity)), 'FullControl',
            'ContainerInherit, ObjectInherit', 'None', 'Allow')
        $acl.AddAccessRule($rule)
    }
    $directory = New-Object IO.DirectoryInfo($Target)
    # Windows PowerShell 5.1/.NET Framework supports atomic ACL creation.
    $directory.Create($acl)
}

if ($MyInvocation.InvocationName -ne '.') {
    try {
        Assert-PrivatePath $Path $UserHome -Tree:$Recurse
    } catch {
        [Console]::Error.WriteLine($_.Exception.Message)
        exit 1
    }
}
