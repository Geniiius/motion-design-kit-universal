# Sur demande uniquement : télécharge les sources tierces dans des dossiers isolés.
# Ne copie pas les skills dans ~/.claude, ne lance pas d'installation externe.
param([switch]$Confirmer)
$ErrorActionPreference = 'Stop'
if (-not $Confirmer) { Write-Host 'Mode aperçu. Utiliser -Confirmer pour cloner les dépôts tiers après lecture de docs/THIRD-PARTY.md.'; exit 0 }
$dest = Join-Path $PSScriptRoot 'vendors'
New-Item -ItemType Directory -Force $dest | Out-Null
$repos = @(
  @{ url='https://github.com/cblain100-prog/motion-design-claude-code.git'; dir='motion-design-claude-code' },
  @{ url='https://github.com/heygen-com/hyperframes.git'; dir='hyperframes' }
)
foreach ($r in $repos) {
  $target = Join-Path $dest $r.dir
  if (Test-Path $target) { Write-Warning "Dossier déjà présent, inchangé: $target"; continue }
  git clone --depth 1 -- $r.url $target
  git -C $target rev-parse HEAD
}
Write-Host 'Sources disponibles dans integrations/vendors/. Audit manuel des licences/scripts requis avant utilisation.'
