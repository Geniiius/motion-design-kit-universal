<#
  Añade (o sustituye) el audio: música de fondo y/o voz en off, con fundidos y ducking.
  Ideal para la voz y la música generadas con ElevenLabs.
  Ejemplos:
    .\scripts\ffmpeg\add-audio.ps1 out\Promo-Reel.mp4 -Musica public\audio\musica\pista.mp3
    .\scripts\ffmpeg\add-audio.ps1 out\Promo-Reel.mp4 -Musica public\audio\musica\pista.mp3 -Voz public\audio\voz\locucion.mp3
#>
param(
  [Parameter(Mandatory)] [string]$Video,
  [string]$Musica = "",
  [string]$Voz = "",
  [double]$VolumenMusica = 0.5,
  [string]$Salida = ""
)
$ErrorActionPreference = "Continue"  # ffmpeg escribe su progreso en stderr
if (-not $Musica -and -not $Voz) { throw "Indica -Musica y/o -Voz" }
if (-not $Salida) { $Salida = [IO.Path]::ChangeExtension($Video, $null).TrimEnd('.') + "-audio.mp4" }
$d = [double](ffprobe -v error -show_entries format=duration -of csv=p=0 $Video)
$fadeOut = [math]::Max(0, $d - 1.5)

if ($Musica -and $Voz) {
  # La música baja automáticamente cuando habla la voz (sidechain ducking)
  $filtro = "[1:a]volume=$VolumenMusica,afade=t=in:d=0.5,afade=t=out:st=${fadeOut}:d=1.5[m];" +
            "[2:a]apad,asplit=2[v][vk];[m][vk]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=300[md];" +
            "[md][v]amix=inputs=2:duration=first:normalize=0[a]"
  ffmpeg -y -i $Video -stream_loop -1 -i $Musica -i $Voz -filter_complex $filtro -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -t $d -movflags +faststart $Salida
} else {
  $src = if ($Musica) { $Musica } else { $Voz }
  $vol = if ($Musica) { $VolumenMusica } else { 1 }
  $loop = if ($Musica) { @("-stream_loop", "-1") } else { @() }
  ffmpeg -y -i $Video @loop -i $src -filter_complex "[1:a]volume=$vol,afade=t=in:d=0.5,afade=t=out:st=${fadeOut}:d=1.5[a]" -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -t $d -movflags +faststart $Salida
}
if ($LASTEXITCODE -ne 0) { throw "ffmpeg ha fallado (código $LASTEXITCODE)" }
Write-Host "OK $Salida" -ForegroundColor Green
