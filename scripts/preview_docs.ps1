<#
.SYNOPSIS
Start a local preview server for this knowledge base.

.DESCRIPTION
Serve the repository root as a static site. The script listens on 127.0.0.1
by default and prefers port 3000. It is intended for the Docsify entry in
this repository.

.PARAMETER HostName
Listener address. Defaults to 127.0.0.1. If you pass 0.0.0.0 the script
binds to all interfaces, but still prints a localhost URL for convenience.

.PARAMETER Port
Specific port to bind. If omitted, the script looks for a free port starting
from 3000.

.PARAMETER Open
Open the preview URL in the default browser after startup.

.EXAMPLE
.\scripts\preview_docs.ps1

.EXAMPLE
.\scripts\preview_docs.ps1 -Open

.EXAMPLE
.\scripts\preview_docs.ps1 -HostName 0.0.0.0 -Port 3010
#>
param(
    [string]$HostName = "127.0.0.1",
    [Nullable[int]]$Port = $null,
    [switch]$Open
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$DefaultPort = 3000
$MaxPortTries = 20

function Get-ListenerStartErrorMessage {
    param(
        [string]$HostName,
        [int]$Port,
        [System.Exception]$Exception
    )

    $prefix = "http://{0}:{1}/" -f $HostName, $Port
    if ($Exception -is [System.Net.HttpListenerException]) {
        switch ($Exception.ErrorCode) {
            5 {
                return "Failed to listen on $prefix. This may be caused by permissions or URL ACL restrictions. Try 127.0.0.1 first, or rerun from an elevated PowerShell session."
            }
            32 {
                return "Failed to listen on $prefix because the port is already in use."
            }
            183 {
                return "Failed to listen on $prefix because the port is already in use."
            }
        }
    }

    return "Failed to listen on $prefix. $($Exception.Message)"
}

function Get-ListenerHost {
    param([string]$HostName)

    if ($HostName -eq "0.0.0.0") {
        return "+"
    }

    return $HostName
}

function Get-DisplayHost {
    param([string]$HostName)

    if ($HostName -eq "0.0.0.0") {
        return "127.0.0.1"
    }

    return $HostName
}

function Start-PreviewListener {
    param(
        [string]$HostName,
        [Nullable[int]]$RequestedPort
    )

    $portsToTry = @()
    if ($null -ne $RequestedPort) {
        $portsToTry += $RequestedPort
    }
    else {
        $portsToTry += ($DefaultPort..($DefaultPort + $MaxPortTries - 1))
    }

    foreach ($candidate in $portsToTry) {
        $listener = [System.Net.HttpListener]::new()
        $prefix = "http://{0}:{1}/" -f (Get-ListenerHost $HostName), $candidate
        $listener.Prefixes.Add($prefix)

        try {
            $listener.Start()
            return @{
                Listener = $listener
                Port = $candidate
            }
        }
        catch {
            $listener.Close()
            $message = Get-ListenerStartErrorMessage -HostName $HostName -Port $candidate -Exception $_.Exception

            if ($null -ne $RequestedPort) {
                throw $message
            }
        }
    }

    throw "No available port found between $DefaultPort and $($DefaultPort + $MaxPortTries - 1)."
}

function Resolve-RequestPath {
    param(
        [string]$RootPath,
        [System.Uri]$Url
    )

    $relativePath = [System.Uri]::UnescapeDataString($Url.AbsolutePath.TrimStart("/"))
    if ([string]::IsNullOrWhiteSpace($relativePath)) {
        $relativePath = "index.html"
    }

    $candidatePath = Join-Path $RootPath ($relativePath -replace "/", [IO.Path]::DirectorySeparatorChar)
    $fullRoot = [IO.Path]::GetFullPath($RootPath)
    $fullCandidate = [IO.Path]::GetFullPath($candidatePath)

    $rootPrefix = $fullRoot
    if (-not $rootPrefix.EndsWith([IO.Path]::DirectorySeparatorChar)) {
        $rootPrefix += [IO.Path]::DirectorySeparatorChar
    }

    if ($fullCandidate -ne $fullRoot -and -not $fullCandidate.StartsWith($rootPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Path traversal is not allowed."
    }

    if ((Test-Path -LiteralPath $fullCandidate) -and (Get-Item -LiteralPath $fullCandidate).PSIsContainer) {
        $fullCandidate = Join-Path $fullCandidate "index.html"
    }

    return $fullCandidate
}

function Get-ContentType {
    param([string]$Path)

    switch ([IO.Path]::GetExtension($Path).ToLowerInvariant()) {
        ".html" { return "text/html; charset=utf-8" }
        ".css" { return "text/css; charset=utf-8" }
        ".js" { return "application/javascript; charset=utf-8" }
        ".json" { return "application/json; charset=utf-8" }
        ".md" { return "text/markdown; charset=utf-8" }
        ".txt" { return "text/plain; charset=utf-8" }
        ".svg" { return "image/svg+xml" }
        ".png" { return "image/png" }
        ".jpg" { return "image/jpeg" }
        ".jpeg" { return "image/jpeg" }
        ".gif" { return "image/gif" }
        ".ico" { return "image/x-icon" }
        default { return "application/octet-stream" }
    }
}

function Write-BytesResponse {
    param(
        [System.Net.HttpListenerResponse]$Response,
        [byte[]]$Bytes,
        [int]$StatusCode,
        [string]$ContentType
    )

    $Response.StatusCode = $StatusCode
    $Response.ContentType = $ContentType
    $Response.ContentLength64 = $Bytes.Length
    $Response.OutputStream.Write($Bytes, 0, $Bytes.Length)
    $Response.OutputStream.Close()
}

function Write-TextResponse {
    param(
        [System.Net.HttpListenerResponse]$Response,
        [string]$Text,
        [int]$StatusCode
    )

    $bytes = [Text.Encoding]::UTF8.GetBytes($Text)
    Write-BytesResponse -Response $Response -Bytes $bytes -StatusCode $StatusCode -ContentType "text/plain; charset=utf-8"
}

function Handle-Request {
    param(
        [System.Net.HttpListenerContext]$Context,
        [string]$RootPath
    )

    try {
        $targetPath = Resolve-RequestPath -RootPath $RootPath -Url $Context.Request.Url

        if (-not (Test-Path -LiteralPath $targetPath) -or (Get-Item -LiteralPath $targetPath).PSIsContainer) {
            Write-TextResponse -Response $Context.Response -Text "Not Found" -StatusCode 404
            return
        }

        $bytes = [IO.File]::ReadAllBytes($targetPath)
        $contentType = Get-ContentType -Path $targetPath
        Write-BytesResponse -Response $Context.Response -Bytes $bytes -StatusCode 200 -ContentType $contentType
    }
    catch {
        Write-TextResponse -Response $Context.Response -Text "Internal Server Error: $($_.Exception.Message)" -StatusCode 500
    }
}

$listenerInfo = Start-PreviewListener -HostName $HostName -RequestedPort $Port
$listener = $listenerInfo.Listener
$actualPort = $listenerInfo.Port
$url = "http://{0}:{1}" -f (Get-DisplayHost $HostName), $actualPort

Write-Host "Preview server started"
Write-Host "Root: $Root"
Write-Host "URL:  $url"
Write-Host "Press Ctrl+C to stop"

if ($Open) {
    Start-Process $url | Out-Null
}

try {
    while ($listener.IsListening) {
        $context = $listener.GetContext()
        Handle-Request -Context $context -RootPath $Root
    }
}
finally {
    if ($listener.IsListening) {
        $listener.Stop()
    }
    $listener.Close()
    Write-Host ""
    Write-Host "Preview server stopped"
}
