<#
  Le kit tel qu'une nouvelle personne le reçoit : ZIP créé, extrait ailleurs, installé, testé.
  Écrit docs\preuves\extras.json. Aucune écriture hors du dossier temporaire et de ce fichier.
    powershell -ExecutionPolicy Bypass -File tests\paquet.ps1 -Termes "mot1|mot2"
  -Termes : mots qui ne doivent apparaître nulle part dans le paquet.
#>
param([string]$Termes = "", [string]$Temp = "")
$ErrorActionPreference = "Continue"
$Kit = Split-Path $PSScriptRoot -Parent
$base = if ($Temp) { $Temp } else { Join-Path $env:TEMP "mdk-paquet" }
if (Test-Path $base) { Remove-Item $base -Recurse -Force }
New-Item -ItemType Directory -Force $base | Out-Null
$lignes = [System.Collections.Generic.List[object]]::new()
function Note($test, $ok, $detail, $statut = "") {
  $s = if ($statut) { $statut } elseif ($ok) { "PASS" } else { "FAIL" }
  $lignes.Add([ordered]@{ test = $test; status = $s; detail = "$detail" })
  Write-Host "$s  $test : $detail"
}

# 1. Paquet
$zip = Join-Path $base "kit.zip"
powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $Kit "empaquetar.ps1") -Destino $zip | Out-Null
$mb = if (Test-Path $zip) { [math]::Round((Get-Item $zip).Length / 1MB, 1) } else { 0 }
Note "ZIP créé par empaquetar.ps1" (Test-Path $zip) "$mb Mo"
$refus = (powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $Kit "empaquetar.ps1") -Destino $zip 2>&1 | Out-String)
Note "empaquetar refuse d'écraser un ZIP sans -Sobrescribir" ($refus -match "Ya existe") "refus constaté"

# 2. Extraction et recherche de contenu personnel
$ext = Join-Path $base "x"
Expand-Archive $zip $ext
$racine = (Get-ChildItem $ext -Directory -ErrorAction SilentlyContinue | Select-Object -First 1).FullName
if (-not $racine) {
  # Sans paquet, la suite tournerait dans le vrai dossier du kit : on s'arrête ici, et on le dit
  Note "Paquet extrait" $false "aucun ZIP à extraire : la suite n'a pas été lancée. Raison : $(($refus -split "`n" | Select-Object -First 1))"
  $sortie = [ordered]@{ unit = "**NOT TESTED** : le paquet n'a pas pu être créé."; install = $lignes }
  [IO.File]::WriteAllText((Join-Path $Kit "docs\preuves\extras.json"), ($sortie | ConvertTo-Json -Depth 4), (New-Object Text.UTF8Encoding $false))
  if (Test-Path $base) { Remove-Item $base -Recurse -Force -ErrorAction SilentlyContinue }
  exit 1
}
$noms = Get-ChildItem $racine -Recurse -Force | ForEach-Object { $_.FullName.Substring($racine.Length + 1) }
$perso = $noms | Where-Object { $_ -match '^(perfil|proyectos)(\\|$)|node_modules|\.git(\\|$)|\.venv|\.source|kokoro-v1|voices-v1|whisper-base|instruments\\|^kit-state\.json$|^kit\.config\.local\.json$|^logs(\\|$)' }
Note "Pas de perfil, de projets, de node_modules, de .git, d'état ni de journal" (-not $perso) "$($noms.Count) entrées"
$lisibles = Get-ChildItem $racine -Recurse -File -Force | Where-Object { $_.Extension -in ".md", ".json", ".ps1", ".mjs", ".py", ".ts", ".tsx", ".txt", ".html", ".js", ".sh", ".bat" -and $_.Name -ne "package-lock.json" }
$cles = $lisibles | Select-String -Pattern 'sk_[a-zA-Z0-9]{20,}|xi-api-key"?\s*[:=]\s*"?[a-zA-Z0-9]{10,}' -List
Note "Aucune clé d'API" (-not $cles) "$($lisibles.Count) fichiers lus"
if ($Termes) {
  $trouve = $lisibles | Select-String -Pattern $Termes -List
  Note "Aucun terme personnel" (-not $trouve) $(if ($trouve) { ($trouve | Select-Object -First 5 | ForEach-Object { $_.Path.Substring($racine.Length + 1) }) -join ", " } else { "liste fournie à l'exécution" })
}

# 3. Installation depuis le ZIP (sans winget, sans clé)
Push-Location $racine
$sw = [Diagnostics.Stopwatch]::StartNew()
$globaux = Join-Path $env:USERPROFILE ".claude\skills"
$empreinte = { (Get-ChildItem $globaux -Recurse -File -ErrorAction SilentlyContinue | ForEach-Object { "$($_.FullName)|$($_.Length)|$($_.LastWriteTimeUtc.Ticks)" }) -join "`n" }
$avant = & $empreinte
# Premier lancement : rien n'est installé tant que rien n'est accepté
$debut = (python -m universal.cli start | Out-String | ConvertFrom-Json)
Note "Premier lancement reconnu : moteur de création proposé, pas installé" ($debut.phase -eq "first-launch" -and $debut.to_approve.required -contains "engine-remotion" -and -not (Test-Path template\node_modules)) "phase $($debut.phase), à accepter : $($debut.to_approve.required -join ', ')"
$refusInstall = (python -m universal.cli setup apply 2>&1 | Out-String)
Note "Rien ne s'installe sans accord nommé" ($refusInstall -match "sans accord" -and -not (Test-Path template\node_modules)) "setup apply sans --approve est refusé"
$install = (powershell -NoProfile -ExecutionPolicy Bypass -File .\instalar.ps1 -SinElevenLabs -Idioma fr -Aprobar "engine-remotion,prompt-motion,design-check" 2>&1 | Out-String)
$codeInstall = $LASTEXITCODE
$apres = & $empreinte
$echecs = ([regex]::Matches($install, "(?m)^\s+FAILED")).Count
Note "instalar.ps1 sur le paquet extrait : trois éléments acceptés, installés, vérifiés" ($codeInstall -eq 0 -and $echecs -eq 0) "$([int]$sw.Elapsed.TotalSeconds) s, code $codeInstall, $echecs FAILED. $(($install -split "`n" | Where-Object { $_ -match '^\s+FAILED' } | Select-Object -First 3) -join ' ')"
Note "Deux vidéos d'essai faites pendant la vérification" ((Test-Path out\essai-installation\essai-montage.mp4) -and (Test-Path out\essai-installation\essai-creation.mp4)) "out\essai-installation"
$etat = (python -m universal.cli start | Out-String | ConvertFrom-Json)
Note "Après la vérification complète, le kit se dit prêt sans rien relancer" ($etat.phase -eq "ready") "phase $($etat.phase), verdict $($etat.verdict)"
Note "Les options non acceptées restent proposées, pas installées" ((-not (Test-Path modules\.venv)) -and [bool]($etat.features.sur_demande | Where-Object { $_.quoi -match "Sous-titres" })) "sous-titres, voix et effets : sur demande"
$journal = Get-ChildItem logs -File -ErrorAction SilentlyContinue | Select-String -Pattern ([regex]::Escape($env:USERNAME)), 'sk_[a-zA-Z0-9]{20,}' -List
Note "Journal technique écrit, sans nom d'utilisateur ni clé" ((Test-Path logs\dernier-rapport.md) -and -not $journal) "logs\ : $(@(Get-ChildItem logs -File -ErrorAction SilentlyContinue).Count) fichier(s)"
Note "Profil vierge créé à l'installation" ((Test-Path "perfil\preferencias.json") -and -not (Get-ChildItem "perfil\marcas" -Filter "*.md" | Where-Object Name -ne "_plantilla.md")) "perfil\ ne contient que le modèle"
Note "Skills globaux inchangés par l'installation" ($avant -eq $apres) "empreinte de ~/.claude/skills identique avant et après"

# 4. Un parcours complet, comme un nouvel utilisateur
python -m universal.cli fixtures | Out-Null
python -m universal.cli route --brief "Monte ces clips" -i examples\medios\clip-a.mp4 -i examples\medios\clip-b.mp4 -i examples\medios\logo-demo.png --name essai -o out\essai\project.json | Out-Null
$r1 = $LASTEXITCODE
python -m universal.cli run out\essai\project.json --profile draft | Out-Null
Note "Montage depuis le paquet" ($r1 -eq 0 -and $LASTEXITCODE -eq 0 -and (Test-Path out\essai\essai.mp4)) "route + run + QC"
python -m universal.cli route --brief "Un personnage 3D qui salue" --name perso --language fr -o out\perso\project.json | Out-Null
python -m universal.cli run out\perso\project.json --profile draft | Out-Null
Note "Personnage 3D depuis le paquet" ($LASTEXITCODE -eq 0 -and (Test-Path out\perso\perso.mp4)) "composition Personaje-Nodo"
python -m universal.cli present -c examples\universal\services.json -o out\deck.html | Out-Null
node tests\deck.spec.mjs out\deck.html out\deck-preuves | Out-Null
Note "Présentation interactive depuis le paquet" ($LASTEXITCODE -eq 0) "13 interactions réelles"
$design = (python -m universal.cli design-check out\deck.html | Out-String | ConvertFrom-Json)
Note "Contrôle de design accepté, installé et lancé depuis le paquet" ($design.ran -eq $true) "empreinte vérifiée, $(@($design.defauts).Count) défaut(s) à juger"
Note "Rien d'Impeccable hors du kit" (-not (Test-Path (Join-Path $env:USERPROFILE ".impeccable"))) "aucun dossier créé chez l'utilisateur"
$liste = (python -m universal.cli film-style list | Out-String | ConvertFrom-Json).Count
$fx = (python -m universal.cli effects list | Out-String | ConvertFrom-Json).Count
Note "Modules présents dans le paquet" ($liste -eq 66 -and $fx -eq 51) "$liste styles, $fx effets, sans modèle ni environnement"
python -m universal.cli modules install film | Out-Null
python -m universal.cli film-style still examples\film-style\riso-pain 5 --profile draft --out out\riso | Out-Null
Note "Moteur des styles depuis le paquet" ($LASTEXITCODE -eq 0 -and (Test-Path out\riso\t_5.0.jpg)) "npm ci puis une image du film Risograph"
$refusDl = (python -m universal.cli modules install voice-model 2>&1 | Out-String)
Note "Pas de téléchargement sans accord" ($refusDl -match "approve-download" -and -not (Test-Path modules\opuscar\core\tts\kokoro-v1.0.onnx)) "le modèle de voix demande --approve-download"
$unit = (python -m unittest discover -s tests -p "test_*.py" 2>&1 | Out-String)
Note "Tests unitaires depuis le paquet" ($unit -match "(?m)^OK") (($unit -split "`n" | Where-Object { $_ -match "^Ran " }) -join " ")
Pop-Location

# 5. Linux / WSL : ce qui tourne sans FFmpeg
$wslKit = (wsl -e wslpath -a ($Kit -replace '\\', '/') 2>$null | Out-String).Trim()
if ($wslKit) {
  $w = (wsl -e sh -c "cd '$wslKit' && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' 2>&1 | tail -4" | Out-String)
  Note "WSL Ubuntu, Python 3 : tests unitaires" ($w -match "OK") (($w -split "`n" | Where-Object { $_ -match "Ran |OK|FAILED" }) -join " ")
  $fm = (wsl -e sh -c "command -v ffmpeg" | Out-String).Trim()
  if (-not $fm) { Note "WSL : montage et rendu" $false "FFmpeg absent de WSL : tests de rendu sautés, pipeline non exécuté sous Linux" "NOT TESTED" }
} else { Note "WSL" $false "indisponible" "NOT TESTED" }

# Statique : aucune police ni média réseau dans le rendu
$reseau = Get-ChildItem (Join-Path $Kit "template\src") -Recurse -File | Select-String -Pattern 'google-fonts|https?://[^"'' ]*\.(woff2?|ttf|png|jpg|mp4|mp3|glb)' -List
Note "Compositions sans police ni média réseau (lecture du code)" (-not $reseau) $(if ($reseau) { ($reseau | Select-Object -First 3 | ForEach-Object { $_.Filename }) -join ", " } else { "template\src" })

Push-Location $Kit
$unitKit = (python -m unittest discover -s tests -p "test_*.py" 2>&1 | Out-String)
Pop-Location
$ligne = ($unitKit -split "`n" | Where-Object { $_ -match "^Ran " }) -join ""
$sortie = [ordered]@{ unit = "**$(if ($unitKit -match '(?m)^OK') { 'PASS' } else { 'FAIL' })** : $($ligne.Trim()), via ``python -m unittest discover -s tests -p ""test_*.py""``."; install = $lignes }
[IO.File]::WriteAllText((Join-Path $Kit "docs\preuves\extras.json"), ($sortie | ConvertTo-Json -Depth 4), (New-Object Text.UTF8Encoding $false))
if (Test-Path $base) { Remove-Item $base -Recurse -Force -ErrorAction SilentlyContinue }
