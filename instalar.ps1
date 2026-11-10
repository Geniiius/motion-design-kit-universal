<#
  MOTION DESIGN KIT UNIVERSAL STUDIO — instalación (Windows 10 / 11)

  Lo más fácil: doble clic en INSTALAR.bat.
  O abre esta carpeta en Claude Code y di «instala el kit»: Claude hace lo mismo, hablando contigo.

  Este script no instala nada sin preguntar:
    1. Busca Python, que hace funcionar el asistente. Si falta, te pregunta antes de instalarlo.
    2. Lanza el asistente del kit: mira tu equipo, te enseña una tabla, pregunta por cada elemento que falta,
       instala solo lo que aceptas, comprueba cada parte y hace dos vídeos de prueba.
    3. ElevenLabs (opcional, de pago): guarda tu API key sin mostrarla.

  Lo que ya está instalado y funciona se reconoce y no se vuelve a instalar.
  Todo se instala en la carpeta del kit, salvo las herramientas del equipo (Python, Node.js, FFmpeg), que el asistente nombra una a una.

  Opciones:
    -Idioma fr|es|en        idioma del asistente (por defecto, el de Windows)
    -Aprobar "a,b,c"        instala solo esos elementos, sin hacer preguntas (pruebas automáticas). Ver: python -m universal.cli setup plan
    -SoloElevenLabs         solo el paso de la API key
    -SinElevenLabs          sin el paso de la API key
    -ConHerk                Herk Edit Kit (montaje de cara a cámara, commit auditado)
    -ConSkillsTerceros      skills de Remotion, HyperFrames, GSAP, LottieFiles, ElevenLabs en ~/.claude/skills
                            (global; los repositorios no están fijados, ver docs/THIRD-PARTY.md)
#>
param(
  [string]$Idioma = "",
  [string]$Aprobar = "",
  [switch]$SoloElevenLabs,
  [switch]$SinElevenLabs,
  [switch]$ConHerk,
  [switch]$ConSkillsTerceros,
  [switch]$SinRequisitos,  # sin efecto desde la 3.1: el asistente pregunta por cada elemento
  [switch]$SinProyectos,   # junto con -SinRequisitos equivale a -SoloElevenLabs, como antes
  [switch]$SinSkills,      # sin efecto: se conserva para no romper guiones antiguos
  [switch]$SinHerk         # sin efecto: Herk ya es opcional
)
$ErrorActionPreference = "Continue"   # npm / git / ffmpeg escriben su progreso en stderr
$Kit = $PSScriptRoot
$env:NO_COLOR = "1"
$env:HYPERFRAMES_SKIP_SKILLS = "1"
$env:HYPERFRAMES_NO_TELEMETRY = "1"
$env:HYPERFRAMES_NO_UPDATE_CHECK = "1"
$env:DO_NOT_TRACK = "1"
$env:PYTHONUTF8 = "1"
if ($SinRequisitos -and $SinProyectos) { $SoloElevenLabs = $true }
$interactivo = [Environment]::UserInteractive -and $Host.Name -eq "ConsoleHost" -and -not $Aprobar

if (-not $Idioma) { $Idioma = (Get-Culture).TwoLetterISOLanguageName }
if ($Idioma -notin "fr", "es", "en") { $Idioma = "es" }
$T = @{
  es = @{ falta = "El kit necesita Python para funcionar: es gratuito y ocupa unos 30 MB."; pregunta = "¿Instalo Python 3.13 con winget? La instalación acepta por ti su licencia (PSF). [s/N]";
          manual = "Instala Python 3.13 desde https://www.python.org/downloads/ (marca «Add python.exe to PATH») y vuelve a abrir INSTALAR.bat.";
          reabrir = "Python está instalado, pero esta ventana aún no lo ve: ciérrala y vuelve a abrir INSTALAR.bat."; nada = "No se ha instalado nada.";
          fin = "Siguiente paso: abre esta carpeta en Claude Code y di qué vídeo quieres." }
  fr = @{ falta = "Le kit a besoin de Python pour fonctionner : il est gratuit et pèse environ 30 Mo."; pregunta = "J'installe Python 3.13 avec winget ? L'installation accepte pour toi sa licence (PSF). [o/N]";
          manual = "Installe Python 3.13 depuis https://www.python.org/downloads/ (coche « Add python.exe to PATH ») puis rouvre INSTALAR.bat.";
          reabrir = "Python est installé, mais cette fenêtre ne le voit pas encore : ferme-la et rouvre INSTALAR.bat."; nada = "Rien n'a été installé.";
          fin = "Étape suivante : ouvre ce dossier dans Claude Code et dis quelle vidéo tu veux." }
  en = @{ falta = "The kit needs Python to run: it is free and takes about 30 MB."; pregunta = "Install Python 3.13 with winget? Installing accepts its licence (PSF) for you. [y/N]";
          manual = "Install Python 3.13 from https://www.python.org/downloads/ (tick 'Add python.exe to PATH') and open INSTALAR.bat again.";
          reabrir = "Python is installed, but this window cannot see it yet: close it and open INSTALAR.bat again."; nada = "Nothing was installed.";
          fin = "Next step: open this folder in Claude Code and say which video you want." }
}[$Idioma]

function Existe($cmd) { [bool](Get-Command $cmd -ErrorAction SilentlyContinue) }
function Recargar-Path {
  $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
}
function Buscar-Python {
  # El alias de la Microsoft Store responde sin ser Python: solo cuenta el que dice su versión
  foreach ($c in "python", "py", "python3") {
    if (-not (Existe $c)) { continue }
    $v = ""
    try { $v = (& $c --version 2>&1 | Out-String) } catch { }
    if ($v -match "Python 3\.(\d+)" -and [int]$Matches[1] -ge 10) { return $c }
  }
  return $null
}

Push-Location $Kit
$codigo = 0

# ---------------------------------------------------------------- 1 y 2. Python y el asistente
if (-not $SoloElevenLabs) {
  $py = Buscar-Python
  if (-not $py) {
    Write-Host "`n  $($T.falta)" -ForegroundColor Yellow
    $si = $false
    if ($interactivo -and (Existe "winget")) { $si = (Read-Host "  $($T.pregunta)") -match '^\s*(s|si|sí|o|oui|y|yes)\s*$' }
    if ($si) {
      winget install --id Python.Python.3.13 -e --silent --accept-source-agreements --accept-package-agreements
      Recargar-Path
      $py = Buscar-Python
      if (-not $py) { Write-Host "`n  $($T.reabrir)" -ForegroundColor Yellow; Pop-Location; exit 1 }
    } else {
      Write-Host "  $($T.nada) $($T.manual)" -ForegroundColor Yellow
      Pop-Location
      exit 1
    }
  }
  $argumentos = @("-m", "universal.cli", "setup", "wizard", "--language", $Idioma)
  if ($Aprobar) {
    $argumentos += "--no-questions"
    foreach ($id in ($Aprobar -split "[,; ]+" | Where-Object { $_ })) { $argumentos += @("--approve", $id) }
  } elseif (-not $interactivo) {
    $argumentos += "--no-questions"   # nadie puede responder: no se instala nada, solo se comprueba
  }
  & $py @argumentos
  $codigo = $LASTEXITCODE
}

# ---------------------------------------------------------------- Opcional: Herk Edit Kit
if ($ConHerk -and (Existe "git") -and (Existe "npm")) {
  Write-Host "`n=== Herk Edit Kit ===" -ForegroundColor Cyan
  $herk = Join-Path $Kit "workspaces\herk-edit-kit"
  New-Item -ItemType Directory -Force (Split-Path $herk) | Out-Null
  # Commit auditado: para actualizarlo, revísalo y cambia este valor (ver docs/THIRD-PARTY.md)
  $herkCommit = "10511e5af86fc47756ea89803b397422e2d89284"
  if (-not (Test-Path (Join-Path $herk ".git"))) {
    git init -q $herk 2>&1 | Out-Null
    git -C $herk remote add origin https://github.com/nateherkai/herk-edit-kit 2>&1 | Out-Null
  }
  if ((git -C $herk rev-parse HEAD 2>$null) -ne $herkCommit) {
    git -C $herk fetch --depth 1 -q origin $herkCommit 2>&1 | Out-Null
    git -C $herk checkout -q FETCH_HEAD 2>&1 | Out-Null
  }
  if (Test-Path (Join-Path $herk "package.json")) {
    Push-Location $herk
    npm install --no-fund --no-audit 2>&1 | Out-Null
    Pop-Location
    Write-Host "  [OK] Herk Edit Kit -> workspaces\herk-edit-kit" -ForegroundColor Green
  } else { Write-Host "  [ERROR] Descarga de nateherkai/herk-edit-kit" -ForegroundColor Red; $codigo = 1 }
} elseif ($ConHerk) { Write-Host "  [ERROR] Herk Edit Kit necesita Git y Node.js" -ForegroundColor Red; $codigo = 1 }

# ---------------------------------------------------------------- Opcional: skills de terceros (globales)
if ($ConSkillsTerceros -and (Existe "npx")) {
  Write-Host "`n=== Skills de terceros en ~/.claude/skills ===" -ForegroundColor Cyan
  New-Item -ItemType Directory -Force (Join-Path $env:USERPROFILE ".claude\skills") | Out-Null
  $paquetes = @(
    @{ repo = "remotion-dev/skills";             skills = @() },
    @{ repo = "heygen-com/hyperframes";          skills = @() },
    @{ repo = "LottieFiles/motion-design-skill"; skills = @() },
    @{ repo = "greensock/gsap-skills";           skills = @() },
    @{ repo = "elevenlabs/skills";               skills = @("text-to-speech", "music", "sound-effects", "speech-to-text", "setup-api-key", "voice-isolator", "dubbing") }
  )
  foreach ($p in $paquetes) {
    $cmd = @("-y", "skills@1.7.4", "add", $p.repo, "-g", "-a", "claude-code", "--copy", "-y")
    foreach ($s in $p.skills) { $cmd += @("-s", $s) }
    $out = (npx @cmd 2>&1 | Out-String)
    if ($out -match "Installed (\d+) skill") { Write-Host "  [OK] $($p.repo)  ($($Matches[1]) skills)" -ForegroundColor Green }
    else { Write-Host "  [ERROR] npx skills add $($p.repo)" -ForegroundColor Red }
  }
}

# ---------------------------------------------------------------- 3. ElevenLabs
if (-not $SinElevenLabs) {
  $actual = [Environment]::GetEnvironmentVariable("ELEVENLABS_API_KEY", "User")
  if ($actual) {
    Write-Host "`n  [OK] API key de ElevenLabs ya configurada (ELEVENLABS_API_KEY)" -ForegroundColor Green
  } elseif ([Environment]::UserInteractive -and $Host.Name -eq "ConsoleHost" -and -not $Aprobar) {
    Write-Host @"

  === ElevenLabs (opcional, de pago) ===
  El kit funciona sin ElevenLabs. Para sus voces, música y efectos, crea una API key:
  https://elevenlabs.io/app/settings/api-keys

  Pega aquí tu API key y pulsa Enter (no se mostrará en pantalla).
  Si no la quieres ahora, pulsa Enter sin escribir nada.
"@
    $seguro = Read-Host "  API key de ElevenLabs" -AsSecureString
    $clave = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($seguro))
    if (-not [string]::IsNullOrWhiteSpace($clave)) {
      $clave = $clave.Trim()
      [Environment]::SetEnvironmentVariable("ELEVENLABS_API_KEY", $clave, "User")
      $env:ELEVENLABS_API_KEY = $clave
      try {
        Invoke-RestMethod -Uri "https://api.elevenlabs.io/v1/models" -Headers @{ "xi-api-key" = $clave } -TimeoutSec 20 | Out-Null
        Write-Host "  [OK] API key de ElevenLabs guardada y verificada" -ForegroundColor Green
      } catch {
        Write-Host "  [AVISO] API key guardada, pero ElevenLabs no la ha aceptado: revísala en https://elevenlabs.io/app/settings/api-keys" -ForegroundColor Yellow
      }
    }
  }
}

Pop-Location
if (-not $SoloElevenLabs) { Write-Host "`n  $($T.fin)`n" }
exit $codigo
