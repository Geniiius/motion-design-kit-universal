<#
  Prepara un vídeo de origen (móvil, grabación de pantalla...) para Remotion:
  recorte al formato, 30 fps, H.264 constante, sin audio -> public/footage/.
  Ejemplos:
    .\scripts\ffmpeg\prepare-footage.ps1 C:\videos\clip.mov -Formato reel
    .\scripts\ffmpeg\prepare-footage.ps1 clip.mp4 -Formato landscape -Inicio 3 -Duracion 6
#>
param(
  [Parameter(Mandatory)] [string]$Video,
  [ValidateSet("reel", "feed", "square", "landscape")] [string]$Formato = "reel",
  [double]$Inicio = 0,
  [double]$Duracion = 0
)
$ErrorActionPreference = "Continue"  # ffmpeg escribe su progreso en stderr
$size = @{ reel = "1080:1920"; feed = "1080:1350"; square = "1080:1080"; landscape = "1920:1080" }[$Formato]
$root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$outDir = Join-Path $root "public/footage"
New-Item -ItemType Directory -Force $outDir | Out-Null
$nombre = [IO.Path]::GetFileNameWithoutExtension($Video)
$out = Join-Path $outDir "$nombre-$Formato.mp4"

$trim = @("-ss", $Inicio)
if ($Duracion -gt 0) { $trim += @("-t", $Duracion) }
# Rellena el encuadre (cover) y recorta al centro
ffmpeg -y @trim -i $Video -vf "scale=${size}:force_original_aspect_ratio=increase,crop=${size},fps=30,setsar=1" `
  -an -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -movflags +faststart $out
if ($LASTEXITCODE -ne 0) { throw "ffmpeg ha fallado (código $LASTEXITCODE)" }
Write-Host "OK $out  -> úsalo con media: 'footage/$nombre-$Formato.mp4'" -ForegroundColor Green
