<#
  Crea Motion-Design-Kit-Universal.zip listo para compartir: sin node_modules, renders, perfil ni medios de tus proyectos.
  Se detiene antes de crear el ZIP si encuentra un perfil, una carpeta de proyectos o una API key.
  Uso:
    powershell -ExecutionPolicy Bypass -File .\empaquetar.ps1
    powershell -ExecutionPolicy Bypass -File .\empaquetar.ps1 -Destino C:\ruta\prueba.zip
    powershell -ExecutionPolicy Bypass -File .\empaquetar.ps1 -Sobrescribir    (sustituye un ZIP ya existente)
#>
param(
  [string]$Destino = "",
  [switch]$Sobrescribir
)
$ErrorActionPreference = "Stop"
$Kit = $PSScriptRoot
$destino = if ($Destino) { $Destino } else { Join-Path (Split-Path $Kit -Parent) "Motion-Design-Kit-Universal.zip" }
if ((Test-Path $destino) -and -not $Sobrescribir) { throw "Ya existe $destino. Usa -Sobrescribir o elige otro -Destino." }
$tmp = Join-Path $env:TEMP "Motion-Design-Kit-Universal"
if (Test-Path $tmp) { Remove-Item $tmp -Recurse -Force }

# Por nombre (en cualquier nivel) y por ruta exacta. Lo que tú creas (perfil, proyectos, medios, salidas) no se reparte.
$porNombre = @("node_modules", "out", "frames", "renders", "workspaces", ".remotion", ".git", ".hyperframes", "__pycache__", "dist", "vendors", ".venv", ".source", ".release")
$personales = @("perfil", "proyectos", "template\public\universal", "template\public\footage", "template\public\captures", "modules\models", "modules\opuscar\core\audio\instruments", "logs") | ForEach-Object { Join-Path $Kit $_ }
$archivos = @("*.log", "*.pyc", ".env", ".env.*", "kokoro-v1.0.onnx", "voices-v1.0.bin", "*.hdr", "kit-state.json", "kit.config.local.json")
robocopy $Kit $tmp /E /XD @($porNombre + $personales) /XF $archivos /NFL /NDL /NJH /NJS /NP | Out-Null
if ($LASTEXITCODE -ge 8) { throw "Error al copiar los archivos (robocopy $LASTEXITCODE)" }

# Medios del usuario en la plantilla y medios de prueba: se conservan vacías las carpetas y se regeneran con 'fixtures'
foreach ($d in "template\public\images", "template\public\audio\voz", "template\public\audio\musica", "template\public\audio\sfx") {
  Get-ChildItem (Join-Path $tmp $d) -File -Force -ErrorAction SilentlyContinue | Where-Object Name -ne ".gitkeep" | Remove-Item -Force
}
Get-ChildItem (Join-Path $tmp "examples\medios") -Force -ErrorAction SilentlyContinue | Where-Object Name -ne "logo-demo.png" | Remove-Item -Recurse -Force
Get-ChildItem (Join-Path $tmp "modules\opuscar\core\assets\polyhaven") -Force -ErrorAction SilentlyContinue | Where-Object Name -ne "SOURCES.md" | Remove-Item -Recurse -Force
Get-ChildItem (Join-Path $tmp "docs\preuves") -Recurse -File -Filter *.mp4 -ErrorAction SilentlyContinue | Remove-Item -Force

# Control final
$prohibido = Get-ChildItem $tmp -Recurse -Force | Where-Object { $_.FullName.Substring($tmp.Length + 1) -match '^(perfil|proyectos|logs)(\\|$)|^kit-state\.json$|^kit\.config\.local\.json$' }
if ($prohibido) { Remove-Item $tmp -Recurse -Force; throw "Contenido personal en el paquete: $($prohibido[0].FullName)" }
$clave = Get-ChildItem $tmp -Recurse -File -Include *.md, *.json, *.ps1, *.mjs, *.py, *.ts, *.tsx, *.txt, *.html, *.js | Select-String -Pattern 'sk_[a-zA-Z0-9]{20,}' -List
if ($clave) { Remove-Item $tmp -Recurse -Force; throw "Posible API key en: $($clave[0].Path)" }
# Ninguna ruta de este equipo: las pruebas generadas las llevan hasta que tests\rapport.py las limpia
$rutas = @($env:USERPROFILE, $env:USERPROFILE.Replace('\', '\\'), $env:USERPROFILE.Replace('\', '/'))
$equipo = Get-ChildItem $tmp -Recurse -File -Include *.md, *.json, *.txt, *.py, *.ps1, *.mjs, *.html, *.srt, *.js | Select-String -SimpleMatch -Pattern $rutas -List
if ($equipo) { Remove-Item $tmp -Recurse -Force; throw "Ruta de este equipo en: $($equipo[0].Path.Substring($tmp.Length + 1)). Ejecuta 'python tests\rapport.py', que las limpia, y vuelve a empaquetar." }

if (Test-Path $destino) { Remove-Item $destino -Force }
Compress-Archive -Path $tmp -DestinationPath $destino -CompressionLevel Optimal
Remove-Item $tmp -Recurse -Force
$mb = [math]::Round((Get-Item $destino).Length / 1MB, 1)
Write-Host "OK $destino ($mb MB)" -ForegroundColor Green
