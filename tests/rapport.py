"""Writes docs/TEST-REPORT.md and docs/STYLE-CATALOG.md from the results, never by hand."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'docs' / 'preuves'
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding='utf-8')


def j(path):
    f = P / path
    return json.loads(f.read_text(encoding='utf-8')) if f.exists() else None


def cell(x):
    return str(x).replace('|', '/').replace('\n', ' ')


def link(path):
    return f'[{path}](preuves/{path})' if (P / path).exists() else '—'


def report():
    out = ['# Rapport de tests', '', 'Généré par `tests/rapport.py` à partir des exécutions réelles. Machine : Windows 11, i5-1240P, NVIDIA T550.', '',
           'PASS : exécuté et vérifié. PARTIAL : la route est juste et quelque chose a tourné, mais pas toute la demande. BLOCKED : il manque un service, un asset ou un consentement. NOT TESTED : non exécuté.', '',
           '> Le contrôle automatique ne juge ni le goût ni l\'écoute : les planches ont été regardées, et seules les voix FR et ES ont été validées à l\'oreille.', '']
    extra = j('extras.json') or {}
    out += ['## Tests unitaires', '', f"{extra.get('unit', 'NOT TESTED')}", '', '## Non-régression des moteurs', '', '| Test | Statut | Détail |', '|---|---|---|']
    for r in j('regression.json') or []:
        out.append(f"| {cell(r['test'])} | **{r['status']}** | {cell(r['detail'])} |")
    out += ['', '## Démonstrateurs', '', '| Démonstrateur | Statut | Alertes | Preuves |', '|---|---|---|---|']
    names = {'personnage': 'Personnage 3D réutilisable qui parle et gesticule', 'explainer': 'Infographie sur données sourcées (NOAA)', 'montage': 'Montage de médias de test (clips, photos, logo, voix, musique)', 'presentation': 'Présentation de services : HTML interactif + film', 'glb': 'Import GLB CC0, animations, repli sans bouche', 'cinema': 'Scène 3D look cinéma', 'hybride': 'Rushes + personnage 3D', 'personnage-fr': 'Personnage 3D, voix française (ElevenLabs)', 'personnage-es': 'Personnage 3D, voix espagnole (ElevenLabs)', 'explainer-fr': 'Infographie, narration française (ElevenLabs)', 'explainer-es': 'Infographie, narration espagnole (ElevenLabs)'}
    names.update({'film-style': 'Film écrit en code, style Risograph, son synthétisé en local', 'effets': 'Deux effets sur un clip sans personne',
                  'personnage-kokoro-fr': 'Personnage 3D, voix française locale (Kokoro)', 'personnage-kokoro-es': 'Personnage 3D, voix espagnole locale (Kokoro)'})
    demos = j('demos.json') or {}
    for k, label in names.items():
        r = demos.get(k)
        if not r:
            out.append(f'| {label} | NOT TESTED | | |')
            continue
        folder = r.get('proofs', '').replace('\\', '/').split('preuves/')[-1]
        out.append(f"| {label} | **{'PASS' if r.get('pass') else 'FAIL'}** | {len(r.get('warnings') or [])} | {link(folder + '/planche.jpg') if folder else '—'} |")
    out += ['', 'Tous les effets vidéo, sur un clip sans personne :', '', '| Format | Effets | Images produites | Statut | Preuve | Limite |', '|---|---|---|---|---|---|']
    for framing in ('vertical', 'paysage'):
        fx = j(f'effects/resultats-{framing}.json')
        out.append(f"| {framing} | {fx['effets']} | {fx['images']} | **{'PASS' if fx['pass'] else 'FAIL'}** | {link(f'effects/planche-{framing}.jpg')} | {cell(fx['limite'])} |" if fx else f'| {framing} | | | NOT TESTED | | |')
    vo = j('voix-locale/resultats.json')
    if vo:
        out += ['', 'Voix locale Kokoro et transcription, sans service payant :', '', '| Langue | Voix | Durée | Texte retrouvé par la transcription | Écart aux pauses | Texte écrit conservé | Statut |', '|---|---|---|---|---|---|---|']
        out += [f"| {r['langue']} | {r['voix']} | {r['duree_s']} s | {round(r['texte_retrouve'] * 100)} % | {r['ecart_pauses_s']} s | {'oui' if r['texte_ecrit_conserve'] else 'non'} | **{'PASS' if r['pass'] else 'FAIL'}** |" for r in vo['voix']]
        out += ['', cell(vo['limite'])]
    el = j('elevenlabs.json')
    if el:
        out += ['', 'Voix ElevenLabs, appels payants accordés le 2026-11-03 :', '', '| Texte | Langue | Voix | Durée | Caractères facturés |', '|---|---|---|---|---|']
        out += [f"| {r['demo']} | {r['langue']} | {r['voix']} | {r['duree']} s | {r['caracteres']} |" for r in el['voix']]
        out += ['', f"Total facturé par l'API : {el['total']} caractères, {el['compteur']}. Tout rendu suivant lit le cache `out/cache-voix` sans frais."]
    out += ['', 'Interactions réelles de la présentation (Chromium, Playwright) :', '', '| Interaction | Statut |', '|---|---|']
    for r in j('presentation/interactions.json') or []:
        out.append(f"| {cell(r['name'])} | **{r['status']}** |")
    ph = j('phrases-naturelles.json')
    if ph:
        out += ['', '## Comprendre une demande en langage courant', '', 'Sans aucun mot technique, FR, ES et EN. Le routeur ne reconnaît que des mots : comprendre revient à Claude, le routeur doit surtout avouer quand il devine.', '',
                '| Série | Phrases | Justes | Avoue ne pas savoir | Fausses sans le dire |', '|---|---|---|---|---|']
        for label, key in (('Ayant servi au réglage', 'reglage'), ('Nouvelles, jamais vues au réglage : le vrai chiffre', 'nouvelles'), ('Vidéo fournie, liste écrite avant tout essai', 'video')):
            if key not in ph:
                continue
            r = ph[key]
            out.append(f"| {label} | {r['phrases']} | {r['justes']} | {sum(1 for d in r['detail'] if d['avoue'])} | **{r['fausses_sans_le_dire']}** |")
        out += ['', 'Avant ce travail, sur la première série : 19 justes sur 36 et 17 fausses sans le dire.', '',
                'Vidéo fournie : à la première mesure, 22 justes sur 23 et **une fausse sans le dire** (« Transforme mon podcast d\'une heure en petits extraits pour TikTok », lu comme un changement de style). '
                'Le défaut a été corrigé, d\'où le 23 sur 23 ci-dessus : cette liste est désormais connue et ne mesure plus des phrases neuves.']
    tr = j('traitements/resultats.json')
    if tr:
        out += ['', '## Vidéo fournie : les traitements, exécutés pour de vrai', '',
                f"Vidéo d'essai : {tr['source']}, {'une voix française de synthèse locale' if tr['voix'] else 'sans voix'}. Là où le kit attend un lecteur, le script joue Claude.", '',
                '| Cas | Demande | Attendu | Obtenu | Statut |', '|---|---|---|---|---|']
        for r in tr['cas']:
            out.append(f"| {cell(r['cas'])} | {cell(r['demande'])} | {cell(r['attendu'])} | {cell(r['obtenu'])}{' · ' + cell(' '.join(r['notes'])) if r['notes'] else ''} | **{r['statut']}** |")
        out += ['', f"Images des sous-titres, de la traduction, de la chaîne complète et d'un extrait : {link('traitements/planche.jpg')}.", '', cell(tr['limite']), '',
                'Avant ce travail, ces demandes sortaient toutes une vidéo de 3,5 s déclarée livrée : voir `docs/AUDIT-2026-11-09.md`. '
                'Le décalage progressif entre l\'image et le son après de nombreuses coupes, et l\'échec au-delà d\'une centaine de coupes, ont été trouvés par ces essais puis corrigés.']
    az = j('assistant/resultats.json')
    if az:
        out += ['', '## Assistant : détection, premier lancement, vérification, réparation, désinstallation', '',
                f"Exécuté le {az['date']} sur : {cell(' · '.join(az['machine'].values()))}.", '', '| Essai | Statut | Détail |', '|---|---|---|']
        out += [f"| {cell(r['test'])} | **{r['status']}** | {cell(r['detail'])} |" for r in az['tests']]
        out += ['', 'Bilan rendu par la vérification complète :', '', '| Élément | Niveau | État | Version | Détail |', '|---|---|---|---|---|']
        out += [f"| {cell(r['title'])} | {r['level']} | **{r['status']}** | {r['version'] or ''} | {cell(r['detail'])} |" for r in az['bilan']]
        out += ['', f"Mascotte rendue par Blender : {link('assistant/mascotte-blender.jpg')}.", '', 'Versions fixées et dernières publiées (lecture seule, rien n\'est mis à jour) :', '',
                '| Paquet | Où | Fixée | Dernière | Écart |', '|---|---|---|---|---|']
        out += [f"| {r['name']} | {r['where']} | {r['pinned']} | {r['latest'] or 'non lue'} | {r['change']} |" for r in az['versions']]
        out += ['', 'L\'installation de ce qui manque n\'est pas dans ce tableau : sur cette machine, rien ne manquait. Elle est essayée sur le kit décompressé à neuf, section « Installation, portabilité, paquet », '
                'et par `tests/test_onboarding.py` avec des doublures.']
    tk = j('tokens.json')
    if tk:
        out += ['', '## Économie de tokens (estimations)', '', f"Méthode : {tk['methode']}. Explications : `docs/TOKEN-ECONOMY.md`. Mesure : `python tests/tokens.py`.", '',
                '| Ce que Claude lit | Taille | ≈ tokens |', '|---|---|---|']
        a = tk['toujours_charge']
        out.append(f"| `CLAUDE.md` et les descriptions des {a['skills']} skills, à chaque requête | {a['caracteres']} caractères | {a['tokens']} |")
        for name, flow in tk.get('parcours', {}).items():
            out.append(f"| Skills lues pour : {name} | {flow['caracteres']} caractères | {flow['tokens']} |")
        st = tk['start']
        out.append(f"| Réponse de `start`, kit prêt, sans skill d'installation | {st['kit_pret']['caracteres']} caractères | {st['kit_pret']['tokens']} |")
        r = tk['route']
        out.append(f"| Fiche de routage (le manifeste complet en ferait {r['manifeste_complet']['tokens']}) | {r['fiche_lue_par_claude']['caracteres']} caractères | {r['fiche_lue_par_claude']['tokens']} |")
        out.append(f"| Réponse de `run` | {tk['run']['sortie']['caracteres']} caractères | {tk['run']['sortie']['tokens']} |")
        if 'planche' in tk:
            p = tk['planche']
            out.append(f"| Planche de 10 images en {p['taille']} (les 10 images une à une en feraient {p['tokens_si_10_images_en_1280x720']}) | une image | {p['tokens']} |")
        tr = tk.get('transcription', {})
        if 'facteur' in tr:
            out.append(f"| Transcription lisible (les mots minutés en feraient {round(tr['mots_minutes_json'] / 3.6)}) | {tr['texte_lu_par_claude']} caractères | {round(tr['texte_lu_par_claude'] / 3.6)} |")
    out += ['', '## Routage', '', 'Chaque cas a son manifeste validé, sa fiche et sa preuve dans `docs/preuves/routage/<cas>/`.', '', '| Cas | Intentions | Moteurs | Questions | Accords requis | Statut | Détail |', '|---|---|---|---|---|---|---|']
    for r in j('routage/resultats.json') or []:
        out.append(f"| {cell(r.get('cas'))} | {', '.join(r.get('intent', []))} | {', '.join(r.get('engines', []))} | {r.get('questions', '')} | {r.get('approvals', '')} | **{r['status']}** | {cell(r.get('detail', ''))} |")
    out += ['', '## Presets démonstrateurs', '', '| Preset | Composition | Statut | Preuve |', '|---|---|---|---|']
    for r in j('presets/resultats.json') or []:
        out.append(f"| {r['id']} | {r.get('composition') or 'HTML'} | **{r['status']}** | {cell(r.get('detail', ''))} |")
    out += ['', '## Installation, portabilité, paquet', '', '| Test | Statut | Détail |', '|---|---|---|']
    three = j('three-studio/resultat.json')
    for r in [*extra.get('install', []), *([three] if three else [])]:
        out.append(f"| {cell(r['test'])} | **{r['status']}** | {cell(r['detail'])} |")
    out += ['', '## Non testé ou bloqué', '', '| Capacité | Statut | Raison |', '|---|---|---|',
            '| Vrai restylage de vidéo, caricature d\'une personne | **BLOCKED** | Aucun fournisseur, budget et consentement requis. Aperçu par filtres seulement |',
            '| Photoréalisme, acteur humain | **BLOCKED** | Modèles et matières réalistes absents : Blender rend ce qu\'on lui fournit. Look cinéma stylisé en repli |',
            '| Génération d\'images ou de vidéos | **BLOCKED** | Aucun fournisseur configuré, appels payants |',
            '| ElevenLabs : musique et effets | **NOT TESTED** | Payant, non demandé |',
            '| Suivi d\'un vrai visage : éléments derrière une personne, recadrage qui suit le visage | **NOT TESTED** | Demande une vidéo d\'une personne d\'accord. Les effets ont tourné sur un clip sans personne, le recadrage sur des trajectoires simulées |',
            '| Naturel de la voix Kokoro en français et en espagnol | **PARTIAL** | Texte et minutage mesurés. Écoutée par le créateur du kit, qui l\'a jugée perfectible : elle reste l\'option gratuite, ElevenLabs l\'option payante |',
            '| Contrôle de design sur le texte dessiné sur un canvas | **NOT TESTED** | Impeccable ne lit que HTML et CSS : aucune alerte sur une page de film ne prouve rien |',
            '| Comportement de Claude dans une nouvelle conversation | **NOT TESTED** | Consignes écrites (`CLAUDE.md`, `kit-onboarding`, `universal-motion-director`, `video-workflows`), non mesurées dans une session vierge. Le code qu\'elles pilotent est testé |',
            '| Installer un outil de l\'ordinateur avec winget ou Homebrew | **NOT TESTED** | Logique testée avec des doublures. Sur la machine d\'essai tout était déjà présent : aucune installation réelle |',
            '| macOS | **NOT TESTED** | Aucune machine. L\'assistant prévoit Homebrew et les emplacements de Blender |',
            '| Assistant en fenêtre avec quelqu\'un qui répond au clavier | **NOT TESTED** | Les réponses sont jouées dans les tests ; le lancement sans question est essayé sur le paquet |',
            '| Vidéo fournie de plus de 20 minutes | **NOT TESTED** | Essayé jusqu\'à 20 minutes et 343 coupes. Une heure n\'a pas été lancée |',
            '| Sous-titres sur une vraie voix, avec du bruit ou de la musique | **NOT TESTED** | Essayé sur une voix de synthèse propre. La relecture avant incrustation reste obligatoire |',
            '| Plusieurs personnes à l\'image, plusieurs voix | **NOT TESTED** | Le recadrage suit un seul visage, les voix ne sont pas séparées |',
            '| Effets imitant Instagram, iMessage, iPhone | **PARTIAL** | Rendus sur le clip de test, usage réel soumis à accord : marques et interfaces de tiers |',
            '| 65 styles Opuscar sur 66 | **NOT TESTED** | Recette et moteur présents, aucun film de preuve. Seul Risograph a été rendu |',
            '| Instruments échantillonnés, styles 3D Opuscar | **NOT TESTED** | Paquets à télécharger avec accord |',
            '| Synchronisation labiale phonétique en FR et ES | **NOT TESTED** | La bouche suit les lettres minutées, pas des phonèmes : suffisant pour un personnage stylisé |',
            '| VRM avec `@pixiv/three-vrm` | **NOT TESTED** | Non installé |',
            '| Personnage articulé dans Blender (Rigify) | **NOT TESTED** | Seule la mascotte procédurale est rendue, voir la section de l\'assistant |',
            '| FBX | **NOT TESTED** | Le routeur demande une conversion en GLB |',
            '| Blocs HyperFrames du catalogue | **NOT TESTED** | Noms vérifiés contre 0.8.164, un seul installé. Non rendus |',
            '| Herk Edit Kit | **NOT TESTED** | Optionnel, commit fixé vérifié, outil non lancé |',
            '| Option `-ConSkillsTerceros` | **NOT TESTED** | Écrirait dans `~/.claude/skills`, non lancée ici |',
            '| Rendu 4K | **NOT TESTED** | Profil présent, non lancé |',
            '| Rendu sans aucune connexion réseau | **NOT TESTED** | Polices et médias locaux, mais la coupure réseau n\'a pas été simulée |',
            '| Écoute humaine des mixages anglais, du montage, de la musique et du film Risograph | **NOT TESTED** | Niveaux mesurés seulement. Voix FR et ES acceptées par le créateur du kit le 2026-11-03 |', '']
    (ROOT / 'docs' / 'TEST-REPORT.md').write_text('\n'.join(out), encoding='utf-8', newline='\n')


def catalog():
    from universal.catalog import load
    data = load('style-catalog.json')
    out = ['# Catalogue de styles', '', 'Généré depuis `presets/`. Recherche : `python -m universal.cli catalog <mots>`, `--category <catégorie>`, `--presets`.', '', '## Statuts', '']
    out += [f'- **{k}** : {v}' for k, v in data['statuts'].items()]
    out += ['', '## Directions artistiques', '', 'Axes combinables : dimension, réalisme, cadrage, lumière, caméra, narration. Le style n\'est pas un moteur.', '', '| Direction | Dimension | Réalisme | Atteignable en local | Limites |', '|---|---|---|---|---|']
    for a in load('art-directions.json')['directions']:
        out.append(f"| **{a['id']}** | {a['dimension']} | {a['realisme']} | {cell(a['atteignable_en_local'])} | {cell(a['limites'])} |")
    out += ['', '## Démonstrateurs', '', '| Preset | Nom | Moteur | Composition |', '|---|---|---|---|']
    for d in load('demonstrators.json')['demonstrators']:
        out.append(f"| **{d['id']}** | {d['nom']} | {d['moteur']} | {d['composition'] or 'HTML'} |")
    out += ['', '## Styles', '']
    cats = sorted({s['categorie'] for s in data['styles']})
    for c in cats:
        out += [f'### {c}', '', '| Style | Moteurs | Intensité | Durée | Contrainte | Statut | Blocs HyperFrames |', '|---|---|---|---|---|---|---|']
        for s in data['styles']:
            if s['categorie'] == c:
                out.append(f"| **{s['nom']}** `{s['id']}` | {', '.join(s['moteurs'])} | {s['intensite']} | {s['duree']} | {cell(s['contraintes'])} | {s['statut']} | {', '.join(s['blocs_hyperframes']) or '—'} |")
        out.append('')
    out += ['Tous les styles acceptent 16:9, 9:16, 1:1 et 4:5. Une durée est une indication, pas une règle.', '']
    (ROOT / 'docs' / 'STYLE-CATALOG.md').write_text('\n'.join(out), encoding='utf-8', newline='\n')


def sanitize():
    """Proofs travel with the kit: they must not carry this machine's paths or user name."""
    root = str(ROOT)
    home = str(Path.home())
    pairs = [(root.replace('\\', '\\\\'), '<kit>'), (root.replace('\\', '/'), '<kit>'), (root, '<kit>'),
             (home.replace('\\', '\\\\'), '<home>'), (home.replace('\\', '/'), '<home>'), (home, '<home>')]
    count = 0
    for f in P.rglob('*'):
        if f.suffix in ('.json', '.txt') and f.is_file():
            text = f.read_text(encoding='utf-8')
            clean = text
            for a, b in pairs:
                clean = clean.replace(a, b)
            # Whatever the edition of Windows, it says something about where the kit was built and proves nothing
            clean = re.sub(r'Windows (\d+) [A-Z][A-Za-zé]+(?= ?[(,·|]|$)', r'Windows \1', clean, flags=re.M)
            if clean != text:
                f.write_text(clean, encoding='utf-8', newline='\n')
                count += 1
    print('nettoyés:', count)


if __name__ == '__main__':
    sanitize()
    report()
    catalog()
    print('ok')
