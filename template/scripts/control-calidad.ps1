<#
  Control de calidad automático de un vídeo terminado.
  Mide imagen y audio, los compara con los objetivos para redes sociales y guarda el resultado
  en perfil/calidad.jsonl (historial que el kit usa para mejorar vídeo tras vídeo).

  Ejemplo:
    .\scripts\control-calidad.ps1 out\mi-video-linkedin.mp4 -Proyecto "MiVideo" -Plataforma linkedin
#>
param(
  [Parameter(Mandatory)] [string]$Video,
  [string]$Proyecto = "",
  [string]$Plataforma = ""
)
$ErrorActionPreference = "Continue"  # ffmpeg escribe sus medidas en stderr
$kit = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$historial = Join-Path $kit "perfil\calidad.jsonl"
if (-not (Test-Path $Video)) { throw "No encuentro el vídeo: $Video" }

# ---------- Medidas ----------
$v = (ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,codec_name,pix_fmt -of json $Video | ConvertFrom-Json).streams[0]
$duracion = [double](ffprobe -v error -show_entries format=duration -of csv=p=0 $Video)
$tieneAudio = [bool](ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 $Video)
$fpsParts = $v.r_frame_rate -split '/'; $fps = [math]::Round([double]$fpsParts[0] / [double]$fpsParts[1], 2)

$lufs = $null; $tp = $null; $lra = $null; $silencioInicio = 0; $silencioFinal = 0
if ($tieneAudio) {
  $ebu = (ffmpeg -hide_banner -nostats -i $Video -af "ebur128=peak=true" -f null - 2>&1) -join "`n"
  $resumen = $ebu.Substring([Math]::Max(0, $ebu.LastIndexOf("Summary:")))
  if ($resumen -match "I:\s+(-?[\d\.]+) LUFS") { $lufs = [double]$Matches[1] }
  if ($resumen -match "LRA:\s+(-?[\d\.]+) LU") { $lra = [double]$Matches[1] }
  if ($resumen -match "True peak:\s+Peak:\s+(-?[\d\.]+|-inf) dBFS") { $tp = if ($Matches[1] -eq "-inf") { -99 } else { [double]$Matches[1] } }
  elseif ($resumen -match "Peak:\s+(-?[\d\.]+) dBFS") { $tp = [double]$Matches[1] }
  $sil = (ffmpeg -hide_banner -nostats -i $Video -af "silencedetect=n=-45dB:d=0.4" -f null - 2>&1) -join "`n"
  $starts = [regex]::Matches($sil, "silence_start: (-?[\d\.]+)") | ForEach-Object { [double]$_.Groups[1].Value }
  $ends = [regex]::Matches($sil, "silence_end: ([\d\.]+)") | ForEach-Object { [double]$_.Groups[1].Value }
  if ($starts.Count -gt 0 -and $starts[0] -le 0.05 -and $ends.Count -gt 0) { $silencioInicio = [math]::Round($ends[0], 2) }
  if ($starts.Count -gt $ends.Count) { $silencioFinal = [math]::Round($duracion - $starts[-1], 2) }
}
$neg = (ffmpeg -hide_banner -nostats -i $Video -vf "blackdetect=d=0.3:pix_th=0.08" -an -f null - 2>&1) -join "`n"
$negros = [regex]::Matches($neg, "black_start:([\d\.]+) black_end:([\d\.]+)") | ForEach-Object { "{0}-{1}s" -f $_.Groups[1].Value, $_.Groups[2].Value }

# ---------- Comparación con los objetivos ----------
$problemas = [System.Collections.Generic.List[string]]::new()
$filas = [System.Collections.Generic.List[object]]::new()
function Fila($medida, $valor, $objetivo, $ok, $consejo) {
  $filas.Add([pscustomobject]@{ Medida = $medida; Valor = $valor; Objetivo = $objetivo; Estado = $(if ($ok) { "OK" } else { "MEJORAR" }) })
  if (-not $ok) { $problemas.Add($consejo) }
}
Fila "Resolución" "$($v.width)x$($v.height)" "1080x1920 / 1080x1350 / 1080x1080 / 1920x1080" (@("1080x1920","1080x1350","1080x1080","1920x1080") -contains "$($v.width)x$($v.height)") "Resolución no estándar: renderiza en uno de los formatos del kit."
Fila "Fotogramas/s" $fps "30" ($fps -eq 30) "Usa 30 fps para redes sociales."
Fila "Códec / píxeles" "$($v.codec_name) / $($v.pix_fmt)" "h264 / yuv420p" ($v.codec_name -eq "h264" -and $v.pix_fmt -eq "yuv420p") "Exporta con social-export.ps1 (H.264 + yuv420p)."
Fila "Audio" $(if ($tieneAudio) { "sí" } else { "no" }) "sí (voz y/o música)" $tieneAudio "El vídeo no tiene sonido: añade voz o música con ElevenLabs."
if ($tieneAudio) {
  Fila "Volumen (LUFS)" $lufs "-14 ± 1" ($lufs -ne $null -and [math]::Abs($lufs + 14) -le 1) "Volumen fuera de -14 LUFS: exporta con social-export.ps1 (lo normaliza)."
  Fila "Pico (dBFS)" $tp "≤ -1" ($tp -ne $null -and $tp -le -1) "Picos demasiado altos (riesgo de saturación): baja efectos o música."
  Fila "Rango dinámico (LU)" $lra "≤ 11" ($lra -ne $null -and $lra -le 11) "Diferencias de volumen muy grandes: acerca el volumen de música, voz y efectos."
  Fila "Silencio al inicio (s)" $silencioInicio "≤ 1" ($silencioInicio -le 1) "Más de 1 s de silencio al empezar: el sonido debe arrancar enseguida (hook)."
}
Fila "Fotogramas negros" $(if ($negros) { $negros -join ", " } else { "ninguno" }) "ninguno" (-not $negros) "Hay tramos negros: revisa el inicio, las transiciones y el final."
Fila "Duración (s)" ([math]::Round($duracion, 1)) "según plataforma" $true ""

Write-Host "`nControl de calidad: $([IO.Path]::GetFileName($Video))" -ForegroundColor Cyan
$filas | Format-Table -AutoSize
if ($problemas.Count) {
  Write-Host "A mejorar:" -ForegroundColor Yellow
  $problemas | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
} else { Write-Host "Todo dentro de los objetivos." -ForegroundColor Green }

# ---------- Historial ----------
New-Item -ItemType Directory -Force (Split-Path $historial) | Out-Null
$registro = [ordered]@{
  fecha = (Get-Date).ToString("yyyy-MM-dd HH:mm"); proyecto = $Proyecto; plataforma = $Plataforma
  archivo = [IO.Path]::GetFileName($Video); resolucion = "$($v.width)x$($v.height)"; fps = $fps; duracion = [math]::Round($duracion, 2)
  lufs = $lufs; pico = $tp; lra = $lra; silencio_inicio = $silencioInicio; negros = @($negros); problemas = @($problemas)
}
Add-Content -Path $historial -Value ($registro | ConvertTo-Json -Compress -Depth 3) -Encoding UTF8
Write-Host "`nGuardado en el historial: perfil\calidad.jsonl" -ForegroundColor Gray
