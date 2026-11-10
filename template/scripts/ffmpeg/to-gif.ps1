<#
  Convierte un vídeo en GIF optimizado (paleta generada) — para emails, documentación, Slack.
  Ejemplo: .\scripts\ffmpeg\to-gif.ps1 out\Logo-Square.mp4 -Ancho 480 -Fps 15
#>
param(
  [Parameter(Mandatory)] [string]$Video,
  [int]$Ancho = 480,
  [int]$Fps = 15,
  [string]$Salida = ""
)
$ErrorActionPreference = "Continue"  # ffmpeg escribe su progreso en stderr
if (-not $Salida) { $Salida = [IO.Path]::ChangeExtension($Video, ".gif") }
ffmpeg -y -i $Video -vf "fps=$Fps,scale=${Ancho}:-1:flags=lanczos,split[a][b];[a]palettegen=stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=4" $Salida
if ($LASTEXITCODE -ne 0) { throw "ffmpeg ha fallado (código $LASTEXITCODE)" }
Write-Host "OK $Salida" -ForegroundColor Green
