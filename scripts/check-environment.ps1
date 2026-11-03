# Windows PowerShell 5.1 ou PowerShell 7; nenhuma instalacao automatica.
[CmdletBinding()]
param(
    [ValidateSet('all', 'dev', 'core', 'analysis')]
    [string]$Profile = 'all',
    [string]$Distribution,
    [string]$CorePython,
    [switch]$RequireDocker,
    [switch]$Native
)
$ErrorActionPreference = 'Stop'
$repoPath = Split-Path -Parent $PSScriptRoot
$report = Join-Path $repoPath ('build\environment-' + $Profile + '.json')
$extraArgs = @()
if ($CorePython) { $extraArgs += @('--core-python', $CorePython) }
if ($RequireDocker) { $extraArgs += '--require-docker' }

if (-not $Native) {
    if (-not (Get-Command wsl.exe -ErrorAction SilentlyContinue)) {
        Write-Error 'WSL nao encontrado. Use Linux/VM/laboratorio ou prepare WSL conforme docs/AMBIENTE.md. -Native permite apenas diagnosticar o Windows.'
        exit 1
    }
    $wslArgs = @()
    if ($Distribution) { $wslArgs = @('-d', $Distribution) }
    # wslpath tambem confirma que a distribuicao pode executar comandos.
    $pathOutput = & wsl.exe @wslArgs -- wslpath -a -u $repoPath
    if ($LASTEXITCODE -ne 0) {
        Write-Error 'Nao foi possivel acessar a distribuicao WSL. Confira wsl --list --verbose e docs/AMBIENTE.md.'
        exit 1
    }
    $linuxRepo = ($pathOutput -join "`n").Trim()
    & wsl.exe @wslArgs -- bash "$linuxRepo/scripts/check-environment.sh" --profile $Profile --json "build/environment-$Profile.json" @extraArgs
    exit $LASTEXITCODE
}

if ($Distribution) {
    Write-Error '-Distribution nao pode ser combinado com -Native.'
    exit 2
}
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { $python = Get-Command py -ErrorAction SilentlyContinue }
if (-not $python) {
    Write-Error 'Python nao encontrado. Instale Python >= 3.10 ou execute o diagnostico no Linux/WSL.'
    exit 1
}
& $python.Source -c 'import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)'
if ($LASTEXITCODE -ne 0) {
    Write-Error 'Python >= 3.10 precisa estar disponivel; aliases da Microsoft Store nao bastam.'
    exit 1
}
& $python.Source (Join-Path $PSScriptRoot 'check_environment.py') --profile $Profile --json $report @extraArgs
exit $LASTEXITCODE
