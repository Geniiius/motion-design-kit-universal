# Architecture

Une seule entrée, plusieurs moteurs. Le moteur le plus sobre qui suffit est choisi : pas de 3D pour une coupe, pas de génération quand un montage suffit.

```
premier message d'une conversation
   │
   ▼
onboarding.py  start : premier lancement, reprise, réparation, ou « prêt » en une demi-seconde
   │           (diagnostic.py regarde, state.py se souvient, logs.py tient le journal)
   ▼
demande + fichiers
   │
   ▼
inventory.py   lit les fichiers (ffprobe, en-têtes GLB, CSV) sans les modifier
   ▼
router.py      intentions · direction artistique · livrables · moteurs · manques · accords
   ▼
project.json   manifeste validé (schema/project.schema.json, manifest.py)
   ▼
run.py ──► video-workflow workflows/    traitements d'une vidéo fournie, gardée entière
       ──► ffmpeg-edit   render.py     montage de médias existants
       ──► remotion      remotion.py   compositions 2D et 3D de template/
       ──► html-deck     present.py    présentation interactive
   ▼
qc.py          défauts bloquants / alertes / déclarés / signaux esthétiques, planches
```

## Modules

| Module | Rôle | Interface |
|---|---|---|
| `universal/inventory.py` | Types, dimensions, durée, cadence, rotation, codecs, alpha, couleur, audio, squelette et morphs d'un GLB, lignes d'un CSV, sous-titres, projet | `inspect()`, `contact_sheet()` |
| `universal/router.py` | 11 intentions FR/ES/EN, axes de style, choix des moteurs | `route()`, `summary()` |
| `universal/manifest.py` | Validation du contrat, sans dépendance | `validate()`, `save()`, `load()` |
| `universal/render.py` | Plan de montage FFmpeg | `edit()`, `render()`, `restyle_preview()` |
| `universal/remotion.py` | Publie les médias, lance une composition, GPU puis CPU | `render()` |
| `universal/present.py` | HTML autonome, interactif et film | `presentation()`, `infographic()` |
| `universal/voice.py` | Voix locale, marques de mots et de visèmes, SRT | `synthesize()`, `to_srt()` |
| `universal/voice_elevenlabs.py` | Voix payante avec minutage, accord obligatoire, cache, plafond | `synthesize()`, `balance()` |
| `universal/datos.py` | Données sourcées vers explainer | `facts()`, `build_props()` |
| `universal/voice_kokoro.py` | Voix locale FR, ES, EN et transcription, après téléchargement accordé | `synthesize()`, `transcribe()` |
| `universal/modules.py` | Modules optionnels : un environnement local, versions et empreintes fixées, téléchargements sur accord | `install()`, `status()` |
| `universal/effects.py` | Effets autour d'une personne filmée, accord pour les interfaces de marque | `render()`, `check()`, `catalog()` |
| `universal/film_style.py` | Films écrits en code d'après une recette, sans gabarit | `new()`, `stills()`, `render()`, `master()` |
| `modules/video-effects/`, `modules/opuscar/` | Code tiers fixé par commit et corrigé, voir leur `UPSTREAM.md` | appelés par ligne de commande |
| `universal/design_check.py` | Contrôle de design des pages HTML livrées, automatique, en conseil seulement | `check()` |
| `universal/perfil.py` | Ce que le kit retient : formato habitual, historial de calidad, marca, reglas. Lu avant le routage, écrit après chaque entrega | `context()`, `remember_delivery()` |
| `universal/qc.py` | Contrôle qualité | `qc()` |
| `universal/capabilities.py` | Les moteurs disponibles, et Blender trouvé jusque dans son dossier d'installation | `detect()`, `find_blender()` |
| `universal/workflows/` | Traitements d'une vidéo fournie : un fichier par traitement, trouvé tout seul par le registre | `registry()`, `run_steps()`, `NeedsInput` |
| `universal/onboarding.py` | Assistant : proposition, installation sur accord nommé, vérification réelle, réparation, désinstallation, mises à jour | `start()`, `plan()`, `apply()`, `verify()`, `repair()`, `uninstall()`, `updates()`, `wizard()` |
| `universal/diagnostic.py` | La machine mesurée, en lecture seule : système, processeur, mémoire, cartes graphiques, disque, versions, conflits, encodeurs essayés | `full()`, `machine()`, `software()`, `conflicts()`, `test_encoders()` |
| `universal/state.py` | État de l'installation sur cette machine, avec une empreinte qui le remet à zéro ailleurs | `load()`, `save()` |
| `universal/config.py` | Réglages : `kit.config.json` livré, `kit.config.local.json` pour l'utilisateur | `get()`, `set_local()` |
| `universal/logs.py` | Journal technique nettoyé de toute donnée sensible | `write()`, `scrub()`, `tail()` |
| `universal/character.py` | Mascotte procédurale rendue par Blender, réglages d'usine, erreur claire si le rendu échoue | `build()` |
| `universal/catalog.py` | Styles, directions, démonstrateurs | `search()` |
| `universal/demos.py` | Démonstrateurs complets | `ALL` |
| `template/src/universal/` | Compositions et pièces Remotion | identifiants `Explainer-*`, `Personaje-*`, `Parallaxe-*`, `Escena3D-*`, `Hibrido-*` |

Les modules communiquent par `project.json` et par ligne de commande. Remotion, HyperFrames et Prompt Motion gardent leurs dépendances dans leur propre dossier.

## Intentions

`CREATE_FROM_SCRATCH`, `ANIMATE_LOGO`, `ANIMATE_IMAGES`, `EDIT_FOOTAGE`, `RESTYLE_FOOTAGE`, `HYBRID_COMPOSITE`, `CHARACTER_ANIMATION`, `DATA_EXPLAINER`, `INTERACTIVE_PRESENTATION`, `REVISE_EXISTING_PROJECT`, `EXPORT_CONVERT`. Plusieurs peuvent coexister.

## Manifeste

Champs : `request`, `intent[]`, `inputs[]` (chemin, type, rôle, métadonnées, droits, provenance, traitement, alertes), `style` (`art_direction`, `dimension`, `realism_level`, `references`, `negative_constraints`, `continuity`), `deliverables[]` (avec l'adaptateur), `timeline`, `characters`, `scene_assets`, `engines[]` (avec le motif), `missing`, `questions`, `notes`, `quality` (avec `exceptions`), `cost_ceiling`, `approval_required`, `status`.

## Moteurs

| Moteur | Sert à | État |
|---|---|---|
| `video-workflow` | Vidéo fournie : silences, extraits, recadrage, sous-titres et traductions, chapitres | testé, sauf le suivi d'un vrai visage |
| `ffmpeg-edit` | Coupes, fondus, photos en mouvement, logo, voix sur musique, sous-titres, -14 LUFS | testé |
| `remotion-2d` | Motion graphics, logos, données, parallaxe | testé |
| `remotion-3d` | Personnages, scènes en volume, rushes + 3D | testé |
| `html-deck` | Présentation interactive, sans réseau | testé |
| `prompt-motion` | Look showreel, film d'une présentation | testé |
| `hyperframes` 0.8.164 | Blocs (cartes, transitions, titres), HTML/GSAP | `check` et rendu testés, les blocs du catalogue non |
| `voice` locale | Voix Windows avec visèmes | testé, en-US seulement sur cette machine |
| `voice_elevenlabs` | Voix FR, ES et autres, minutage par caractère | testé en FR et ES, appel payant soumis à accord |
| `herk-edit-kit` | Montage face caméra | optionnel, non testé |
| ElevenLabs : musique, effets | Musique et bruitages | optionnel, payant, non appelé |
| `blender` | Mascotte procédurale | optionnel, testé avec Blender 5.2.3. Pas de réalisme sans modèles et matières fournis |
| Fournisseur de restylage ou de génération | Transformation d'images et de vidéos | aucun adaptateur |

## Profils de rendu

| Profil | FFmpeg (largeur) | Remotion (échelle) | CRF | Usage |
|---|---|---|---|---|
| `draft` | 640 | 0,5 | 28 | essais |
| `review` | 960 | 0,75 | 23 | validation |
| `final` | 1920 | 1 | 17 | livraison |
| `4k` | 3840 | 2 | 17 | si le disque et le temps suivent |

Formats : 16:9, 9:16, 1:1, 4:5. Une vidéo fournie sans format demandé garde sa propre forme (`source`). GPU par ANGLE, repli automatique sur `swangle` (CPU).
L'encodage final est logiciel (libx264), qui sert de référence. Un encodeur matériel n'est utilisé que pour une vidéo longue, et seulement s'il a produit un fichier lors de la vérification de cette machine.

## Reproductibilité

- Chaque image est calculée depuis le temps : pas d'état entre images, pas de `Math.random` sans graine.
- Versions exactes et `package-lock` dans `template/` et `prompt-motion/`.
- Polices et médias locaux : le rendu ne dépend pas du réseau.
- Empreinte sha256 et provenance de chaque média dans le manifeste.

## Langue

`perfil/preferencias.json` (`idioma_respuesta`, `idioma_video`, `acento_voz`). `auto` suit la langue de la demande. `acento_voz`, `modo_local_primero` et `aprobar_antes_de_gastar` sont des consignes lues par Claude, pas par le code. Les libellés de la fiche et de la présentation existent en FR, ES et EN.

## Assistant

`start` est l'unique entrée. Il ne lance rien quand le kit est configuré : il lit `kit-state.json` et regarde si les fichiers attendus sont toujours là.

| Étape | Fonction | Change quelque chose ? |
|---|---|---|
| Regarder | `diagnostic.full()` | Non |
| Proposer | `onboarding.plan()` : chaque élément, son état, son niveau, son poids, ce qui serait fait | Non |
| Installer | `onboarding.apply(ids)` : uniquement les éléments nommés | Oui, et seulement eux |
| Vérifier | `onboarding.verify(deep=True)` : chaque moteur lancé, deux vidéos d'essai, encodeurs essayés | Écrit l'état et le bilan |

- **Accord.** `apply` sans identifiant ne fait rien. Un outil de l'ordinateur passe par winget ou Homebrew avec la mention de sa licence ; sous Linux, la ligne `sudo` est rendue à la personne. Une option gratuite absente lève `ConsentRequired` au lieu de s'installer (`consent.free_modules: ask`).
- **Préserver.** Un élément présent et utilisable répond `already` : rien n'est refait. Seule une réparation demandée réinstalle, et jamais un outil de l'ordinateur.
- **Reprise.** Chaque étape est notée `running`, `done` ou `failed` dans l'état. Un `running` retrouvé au lancement est une installation interrompue.
- **Verdict.** `READY`, `WARNING`, `FAILED`, `OPTIONAL` par élément. Le kit n'est « configuré » qu'après une vérification complète sans `FAILED` sur un élément indispensable. Un indispensable refusé par la personne est un `WARNING`, pas une panne.
- **Partir.** `uninstall` ne connaît que les dossiers générés par le kit, dans le kit. `perfil/`, `out/` et les réglages ne figurent pas dans cette liste : ils ne peuvent pas être supprimés par ce chemin.
- **Rester à jour.** `updates` lit les registres publics et compare. Il n'écrit rien.

## Traitements d'une vidéo fournie

Un traitement est un fichier de `universal/workflows/` qui déclare `ID`, `ORDER`, `TITLE`, `WORDS`, `NEEDS` et `run(ctx, track) -> [Track]`. En ajouter un, c'est ajouter un fichier : le registre le trouve, le routeur apprend ses mots, la chaîne l'exécute à son rang.

- Les étapes vont de fichier en fichier avec un intermédiaire presque sans perte ; un seul encodage final décide de la qualité livrée.
- Une étape qui a besoin d'une lecture ou d'un choix lève `NeedsInput` : le texte transcrit se relit avant d'être incrusté, les extraits et les chapitres se choisissent en lisant la transcription, les traductions s'écrivent à partir du fichier relu. Aucun service externe.
- `run` répond `delivered`, `needs-input`, `unchanged` (aucun traitement n'a rien changé : aucun fichier n'est écrit) ou `failed`.
- Une demande que le routeur n'a pas comprise (`understanding.certain: false`) n'est pas exécutée.

## Fichiers d'état et de réglage

| Fichier | Contenu | Partagé |
|---|---|---|
| `kit.config.json` | Réglages par défaut : seuils, accord, niveau sonore, encodeur, traitements, journal | Oui |
| `kit.config.local.json` | Les mêmes clés, changées par l'utilisateur | Non |
| `kit-state.json` | Accords donnés, étapes faites, dernier bilan, encodeurs vérifiés, ce que le kit a installé | Non |
| `logs/` | Journal en lignes JSON et `dernier-rapport.md` | Non |
