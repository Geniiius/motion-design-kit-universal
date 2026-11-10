<#
  Recodifica un vídeo con las especificaciones de una plataforma (H.264, yuv420p, AAC, faststart)
  y normaliza el volumen a -14 LUFS.
  Ejemplos:
    .\scripts\ffmpeg\social-export.ps1 out\Promo-Reel.mp4 -Plataforma instagram
    .\scripts\ffmpeg\social-export.ps1 out\Promo-Landscape.mp4 -Plataforma youtube
  Plataformas: instagram | tiktok | youtube | linkedin | x | web
#>
param(
  [Parameter(Mandatory)] [string]$Video,
  [ValidateSet("instagram", "tiktok", "youtube", "linkedin", "x", "web")] [string]$Plataforma = "instagram",
  [string]$Salida = ""
)
$ErrorActionPreference = "Continue"  # ffmpeg escribe su progreso en stderr

# CRF bajo = mejor calidad. maxrate limita el bitrate para evitar una recompresión agresiva.
$specs = @{
  instagram = @{ crf = 18; maxrate = 8;  audio = "192k" }
  tiktok    = @{ crf = 18; maxrate = 10; audio = "192k" }
  youtube   = @{ crf = 16; maxrate = 16; audio = "320k" }
  linkedin  = @{ crf = 20; maxrate = 6;  audio = "192k" }
  x         = @{ crf = 20; maxrate = 6;  audio = "128k" }
  web       = @{ crf = 24; maxrate = 3;  audio = "128k" }
}
$s = $specs[$Plataforma]
if (-not $Salida) { $Salida = [IO.Path]::ChangeExtension($Video, $null).TrimEnd('.') + "-$Plataforma.mp4" }

# Añade una pista muda si el vídeo no tiene audio (algunas plataformas la exigen)
$hasAudio = [bool](ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 $Video)
$audioIn = if ($hasAudio) { @() } else { @("-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo") }
# Volumen estándar de redes sociales: -14 LUFS, picos por debajo de -1,5 dB
$audioFx = if ($hasAudio) { @("-af", "loudnorm=I=-14:TP=-1.5:LRA=11") } else { @() }

ffmpeg -y -i $Video @audioIn @audioFx `
  -map 0:v:0 -map "$(if ($hasAudio) { '0:a:0' } else { '1:a:0' })" -shortest `
  -vf "scale=out_range=tv,format=yuv420p" -color_range tv -c:v libx264 -preset slow -profile:v high -pix_fmt yuv420p -crf $s.crf -maxrate "$($s.maxrate)M" -bufsize "$($s.maxrate * 2)M" `
  -r 30 -c:a aac -b:a $s.audio -ar 48000 -movflags +faststart $Salida

if ($LASTEXITCODE -ne 0) { throw "ffmpeg ha fallado (código $LASTEXITCODE)" }
Write-Host "OK $Salida" -ForegroundColor Green
