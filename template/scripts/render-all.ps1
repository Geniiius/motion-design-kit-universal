<#
  Renderiza una o varias composiciones en out/.
  Ejemplos:
    .\scripts\render-all.ps1                          # todas las composiciones
    .\scripts\render-all.ps1 -Filtro Promo            # todas las Promo-*
    .\scripts\render-all.ps1 -Filtro Promo -Props props\cliente.json
#>
param(
  [string]$Filtro = "",
  [string]$Props = "",
  [string]$Salida = "out"
)
$ErrorActionPreference = "Continue"  # ffmpeg/npx escriben su progreso en stderr
Set-Location (Split-Path $PSScriptRoot -Parent)
New-Item -ItemType Directory -Force $Salida | Out-Null

$ids = (npx remotion compositions --quiet 2>$null) -join " " -split '\s+' | Where-Object { $_ -and $_ -match $Filtro }
if (-not $ids) { throw "Ninguna composición coincide con '$Filtro'" }

foreach ($id in $ids) {
  Write-Host "> Renderizando $id" -ForegroundColor Cyan
  $cmd = @("remotion", "render", $id, "$Salida/$id.mp4")
  if ($Props) { $cmd += "--props=$Props" }
  npx @cmd
  if ($LASTEXITCODE -ne 0) { throw "Error al renderizar $id" }
}
Write-Host "OK Terminado -> $Salida" -ForegroundColor Green
