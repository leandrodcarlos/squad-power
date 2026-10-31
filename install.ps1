# Instalador do Squad Power (Windows). Roda no PowerShell 5.1 ou 7.
# Mensagens em ASCII: o PowerShell 5.1 le este arquivo sem BOM como ANSI.
param(
    [string]$Destino = "$HOME\.claude",
    [switch]$SemPlugins,
    [switch]$SemPython
)
$ErrorActionPreference = 'Stop'
$Raiz = Split-Path -Parent $MyInvocation.MyCommand.Path
$RaizFwd = $Raiz.Replace([char]92, [char]47)
$Utf8SemBom = New-Object System.Text.UTF8Encoding($false)
$Avisos = New-Object System.Collections.ArrayList

function Copiar-ComRaiz([string]$Origem, [string]$Alvo) {
    # Escreve sem BOM: BOM antes do --- quebra o frontmatter do agente.
    $txt = [IO.File]::ReadAllText($Origem, $Utf8SemBom).Replace('{{SQUAD_ROOT}}', $RaizFwd)
    [IO.File]::WriteAllText($Alvo, $txt, $Utf8SemBom)
}

$Agentes = @(Get-ChildItem (Join-Path $Raiz 'agents') -Filter '*-fran.md')
if ($Agentes.Count -eq 0) { throw "Nenhum agente em $Raiz\agents" }
New-Item -ItemType Directory -Force (Join-Path $Destino 'agents') | Out-Null
foreach ($a in $Agentes) { Copiar-ComRaiz $a.FullName (Join-Path $Destino "agents\$($a.Name)") }

$Skills = @(Get-ChildItem (Join-Path $Raiz 'skills') -Directory | Where-Object { Test-Path (Join-Path $_.FullName 'SKILL.md') })
foreach ($s in $Skills) {
    $dest = Join-Path $Destino "skills\$($s.Name)"
    New-Item -ItemType Directory -Force $dest | Out-Null
    Copiar-ComRaiz (Join-Path $s.FullName 'SKILL.md') (Join-Path $dest 'SKILL.md')
}
Write-Host "OK  $($Agentes.Count) agentes e $($Skills.Count) skills instalados em $Destino (base em $RaizFwd)"

if (-not $SemPython) {
    $py = Get-Command python -ErrorAction SilentlyContinue
    if ($py -and $py.Source -notlike '*WindowsApps*') {
        $ErrorActionPreference = 'Continue'
        & python -m pip install --quiet --disable-pip-version-check -r (Join-Path $Raiz 'requirements.txt') 2>&1 | Out-Null
        $codigo = $LASTEXITCODE
        $ErrorActionPreference = 'Stop'
        if ($codigo -eq 0) { Write-Host "OK  bibliotecas Python instaladas" }
        else { [void]$Avisos.Add("Bibliotecas Python nao instalaram. Rode: python -m pip install -r requirements.txt") }
    } else { [void]$Avisos.Add("Python nao encontrado. Instale: winget install Python.Python.3.11  (depois rode este instalador de novo)") }
    if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
        [void]$Avisos.Add("ffmpeg nao encontrado (so faz falta para transcrever audio). Instale: winget install Gyan.FFmpeg")
    }
}

if (-not $SemPlugins) {
    # Versoes fixas: plugin roda com a permissao da usuaria e nao deve mudar sozinho.
    $Plugins = @(
        @{ Repo = 'https://github.com/thedotmack/claude-mem.git#v10.6.2'; Id = 'claude-mem@thedotmack'; Uso = 'memoria entre conversas' },
        @{ Repo = 'https://github.com/nextlevelbuilder/ui-ux-pro-max-skill.git#v2.15.0'; Id = 'ui-ux-pro-max@ui-ux-pro-max-skill'; Uso = 'design de sites e propostas' },
        @{ Repo = 'https://github.com/anthropics/skills.git'; Id = 'document-skills@anthropic-agent-skills'; Uso = 'Word, PowerPoint, Excel e PDF' }
    )
    if (Get-Command claude -ErrorAction SilentlyContinue) {
        $ErrorActionPreference = 'Continue'
        foreach ($pl in $Plugins) {
            & claude plugin marketplace add $pl.Repo 2>&1 | Out-Null
            & claude plugin install $pl.Id -y 2>&1 | Out-Null
            & claude plugin enable $pl.Id 2>&1 | Out-Null
            $lista = (& claude plugin list 2>&1 | Out-String)
            $i = $lista.IndexOf($pl.Id)
            if ($i -ge 0 -and $lista.Substring($i, [Math]::Min(160, $lista.Length - $i)) -match 'enabled') {
                Write-Host "OK  plugin $($pl.Id) ($($pl.Uso))"
            } else { [void]$Avisos.Add("Plugin $($pl.Id) nao ficou ativo. Rode: claude plugin install $($pl.Id)") }
        }
        $ErrorActionPreference = 'Stop'
    } else { [void]$Avisos.Add("Comando claude nao encontrado: instale o Claude Code e rode este instalador de novo.") }
}

if ($Avisos.Count -gt 0) {
    Write-Host ""
    Write-Host "O squad funciona, mas falta resolver:"
    foreach ($m in $Avisos) { Write-Host "  - $m" }
}
Write-Host ""
Write-Host "Pronto. Feche e abra o Claude Code, depois digite: /squad-power"
