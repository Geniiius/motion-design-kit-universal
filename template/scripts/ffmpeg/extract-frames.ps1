<#
  Extrae N fotogramas repartidos por el vídeo para revisarlo visualmente (control de calidad).
  Ejemplo: .\scripts\ffmpeg\extract-frames.ps1 out\Promo-Reel.mp4 -Cantidad 8
#>
param(
  [Parameter(Mandatory)] [string]$Video,
  [int]$Cantidad = 8,
  [string]$Carpeta = "frames"
)
$ErrorActionPreference = "Continue"  # ffmpeg escribe su progreso en stderr
New-Item -ItemType Directory -Force $Carpeta | Out-Null
$duracion = [double](ffprobe -v error -show_entries format=duration -of csv=p=0 $Video)
$nombre = [IO.Path]::GetFileNameWithoutExtension($Video)
for ($i = 0; $i -lt $Cantidad; $i++) {
  $t = [math]::Round($duracion * ($i + 0.5) / $Cantidad, 2)
  ffmpeg -v error -y -ss $t -i $Video -frames:v 1 -vf "scale=540:-2" "$Carpeta/$nombre-$('{0:D2}' -f $i)-${t}s.png"
}
if ($LASTEXITCODE -ne 0) { throw "ffmpeg ha fallado (código $LASTEXITCODE)" }
Write-Host "OK $Cantidad fotogramas en $Carpeta" -ForegroundColor Green
