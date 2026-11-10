# Tiers : licences, versions, décisions

Le code propre au kit est publié sous licence MIT, © 2026 Geniiius (fichier `LICENSE`). Les éléments ci-dessous gardent leur propre licence.

## Dépendances utilisées

| Élément | Version | Licence | Note |
|---|---|---|---|
| Remotion et `@remotion/*` | 4.0.540 exact | **Licence Remotion** | Gratuit pour une personne, une entreprise jusqu'à 3 salariés, une association. **Au-delà : licence entreprise payante.** À vérifier avant un usage commercial |
| three | 0.180.0 exact | MIT | |
| `@react-three/fiber` | 9.3.0 exact | MIT | |
| zod | 4.6.7 exact | MIT | Version exigée par Remotion 4.0.540 |
| GSAP | 3.15.0 exact | Licence « no charge » de GreenSock | Gratuit, pas open source : voir gsap.com/standard-license |
| Motion, lottie-web | exacts | MIT | |
| Playwright | 1.64.1 exact | Apache-2.0 | |
| `@fontsource/inter`, `@fontsource/space-grotesk` | 5.3.0 exact | OFL-1.1 | Polices locales |
| HyperFrames | 0.8.164 fixé, téléchargé par `npx` | Apache-2.0 | Registre fixé sur `v0.8.164` |
| FFmpeg | installé par winget | LGPL/GPL selon la version | Programme externe, non redistribué |
| Herk Edit Kit | commit `10511e5`, optionnel | Voir son `LICENSE` | Non testé ici |
| Effets vidéo (`modules/video-effects`) | Commit `93140a9` de `Vibha-Ramprakash/claude-video-effects`, corrigé | MIT © 2026 Vibha Ramprakash | Corrections listées dans son `UPSTREAM.md` |
| YuNet, MediaPipe Selfie Segmenter | Modèles copiés, empreintes vérifiées contre leurs sources | MIT, Apache-2.0 | Détection du visage et détourage, en local |
| Styles et moteur Opuscar (`modules/opuscar`) | Commit `bebbbe1` de `lemomo-ai/lemo-opuscar`, partie légère, corrigée | MIT © 2026 LemoLab | Corrections listées dans son `UPSTREAM.md`. Films de démonstration : CC BY 4.0, non inclus |
| Kokoro-82M, `kokoro-onnx` 0.6.1 | Modèle téléchargé avec accord, SHA-256 vérifié | Apache-2.0 | Voix locale. Corpus d'entraînement dont SIWIS (CC BY 4.0) |
| faster-whisper 1.2.1, modèle `Systran/faster-whisper-base` | Révision `ebe41f7`, téléchargée avec accord | MIT | Transcription locale |
| Échantillons d'instruments | Paquets à télécharger avec accord, SHA-256 vérifiés | CC0 surtout ; piano Salamander CC BY 3.0 et batterie MuldjordKit CC BY 4.0 **à citer** | `modules/opuscar/core/audio/INSTRUMENTS.md` |
| mediapipe, opencv, numpy, scipy, numba et leurs dépendances | Versions et empreintes dans `modules/requirements/` | Licences libres, voir chaque paquet | Roues précompilées seulement : aucun script d'installation ne tourne |
| CLI `skills` | 1.7.4, optionnelle | MIT | Les dépôts qu'elle installe ne sont pas fixés : d'où l'option désactivée par défaut |

## Outils que l'assistant peut installer, avec accord

L'assistant n'ajoute aucune dépendance au kit : il n'utilise que la bibliothèque standard de Python. Voici ce qu'il propose d'installer sur l'ordinateur quand un outil manque. Chaque installation demande un « oui » pour l'outil nommé, et la mention de sa licence fait partie de la question.

| Outil | Paquet winget | Formule Homebrew | Licence |
|---|---|---|---|
| Python 3.13 | `Python.Python.3.13` | `python@3.13` | PSF |
| Node.js LTS | `OpenJS.NodeJS.LTS` | `node` | MIT |
| FFmpeg | `Gyan.FFmpeg` | `ffmpeg` | GPL pour cette compilation |
| Git | `Git.Git` | `git` | GPL-2.0 |
| uv | `astral-sh.uv` | `uv` | MIT ou Apache-2.0 |
| Blender | `BlenderFoundation.Blender` | `--cask blender` | GPL |

- Ces outils ne sont pas redistribués par le kit. Ils arrivent dans **la dernière version publiée par leur éditeur** : c'est la seule exception à la règle des versions fixées, elle est dite à la personne, et le minimum exigé est vérifié après l'installation.
- Sous Linux, l'assistant n'exécute rien qui demande le mot de passe administrateur : il rend la ligne à taper.
- Ces installations n'ont pas été exécutées pour de vrai sur la machine d'essai, où tout était déjà présent.

## Sources et contenus

| Élément | Origine | Droits | Usage |
|---|---|---|---|
| `docs/STORYBOARD-AGENCY.md` | Méthode de `cblain100-prog/motion-design-claude-code` @`a89fc54` | MIT © 2026 Colin Blain | Résumé adapté. Aucun film, marque, musique ni média de ce dépôt |
| `presets/hyperframes-0.8.164.json` | Noms de blocs de `heygen-com/hyperframes` @`v0.8.164` | Apache-2.0 | Noms seulement |
| `examples/modelos/RobotExpressive/` | three.js r180, Tomás Laulhé (Quaternius), modifications Don McCurdy | CC0 1.0 | Test d'import GLB, voir `LICENCE.txt` |
| `examples/datos/co2_annmean_mlo.csv` | NOAA GML | Libre, citation demandée | Démonstrateur explainer, voir `SOURCE.txt` |
| Nodo, décors, logo de test, médias de test | Créés par code pour ce kit | Sans tiers | `universal/fixtures.py`, `nodo.json` |
| Voix anglaises des démos | Voix système de Windows (Zira) | Soumise aux conditions de Windows : à vérifier avant une diffusion publique | Démonstration uniquement |
| Voix FR et ES des démos | ElevenLabs, voix génériques Sarah et Matilda, `eleven_multilingual_v2`, compte du créateur du kit | Conditions d'ElevenLabs selon le forfait : à vérifier avant une diffusion commerciale | Non incluses dans le ZIP |

`ejemplos/*.mp4` sont des rendus du moteur Prompt Motion du kit.

## Outils évalués

Rien n'a été installé par réflexe. « Preuve » indique ce qui a tourné ici.

| Outil | Apport réel | Compatibilité | Licence | Maintenance | CPU/GPU | Preuve | Repli | Décision |
|---|---|---|---|---|---|---|---|---|
| `@remotion/three` + React Three Fiber | Vraie 3D pilotée image par image | Déjà en place | Remotion / MIT | Active | GPU, lent en CPU | Démos personnage, GLB, cinéma | `swangle` testé | **Adopté** |
| Three.js | Base de la 3D, chargeur GLTF, environnement | Déjà en place | MIT | Active | GPU | Idem | `swangle` | **Adopté** |
| FFmpeg | Montage, contrôle, audio | Déjà en place | LGPL/GPL | Active | CPU | Démo montage, QC | Aucun : requis | **Adopté** |
| GSAP | Chronologies, film HTML | Déjà en place | No charge | Active | Léger | Composition Showcase | CSS, fonctions du temps | **Conservé**, inutile pour la présentation |
| Drei | Raccourcis R3F | Compatible en 10.7.9 | MIT | Active | — | Non installé | Code Three direct | **Écarté** : caméra, environnement et ombres couverts en quelques lignes |
| `@pixiv/three-vrm` | Avatars VRM, expressions, visèmes | Compatible en théorie (`three >=0.137`) | MIT | Active | GPU | **Non testé** | Lecture GLB sans expressions | **Reporté** : adopter avec un avatar libre à tester |
| Blender + Rigify | Modélisation, rigging, rendu réaliste | Absent de cette machine | GPL | Active | Lourd, 4 Go de VRAM limitent | `character3d` **non testé** | Remotion 3D stylisé | **Optionnel** |
| Motion Canvas | Animation pédagogique par code | Second moteur à apprendre | MIT | Active | Léger | Non installé | Pièces Remotion | **Écarté** : aucune valeur démontrée face à `Explainer-*` |
| Manim Community | Mathématiques animées | Python, LaTeX, Cairo à installer | MIT | Active | CPU | Non installé | `DataChart` | **Reporté** : utile seulement pour des démonstrations de formules |
| Reveal.js | Présentations web | Compatible | MIT | Active | Léger | Non installé | `present.py` | **Écarté** : `present.py` couvre le besoin, sans dépendance. HyperFrames `slideshow` reste possible |
| claude-video-effects | Visage suivi, éléments derrière la personne, 51 effets | Windows après correction | MIT | Active | CPU | Les 51 effets sur un clip sans personne. **Suivi d'un vrai visage non testé** | Effets Remotion sans suivi | **Adopté, corrigé** : valeurs par défaut de l'auteur et interfaces de marque encadrées |
| lemo-opuscar | 66 recettes de style, musique et bruitages locaux, voix Kokoro | Windows après remplacement de `setup.sh` et `mux.sh` | MIT, films CC BY | Active | CPU, WebGL | Film Risograph complet, audio synthétisé. **65 autres styles sans film de preuve** | Styles du catalogue | **Adopté en partie** : le plugin et sa mise à jour automatique sont écartés |
| Impeccable (`detect` seulement) | Contrôle automatique du design des pages HTML | Windows, moteur compilé de 20 Mo | Apache-2.0 | Active | CPU, moins d'une seconde | 14 alertes justes sur 17 sur les pages du kit, voir `modules/design-check/UPSTREAM.md` | Regard sur la page | **Adopté en conseil** : ne bloque jamais, moteur non recompilé mais empreinte vérifiée |
| Chatterbox | Voix locale, 23 langues, reprise d'une voix à partir d'un extrait | Python 3.13 après ajout de `setuptools`, sans `gradio` ni `pykakasi` | MIT, code et modèle ; filigrane inaudible sur chaque fichier | Active | CPU : 9 à 15 fois la durée de l'audio | Essayé hors du kit, [mesures](preuves/chatterbox/resultats.json) : en français, moins de mots retrouvés que Kokoro | Kokoro, ElevenLabs | **Écarté pour l'instant** : 4,7 Go pour une voix intégrée pensée pour l'anglais. À revoir avec un enregistrement français consenti |
| Arcads | Restylage et vidéo générée, service payant | Instructions et serveur distant, aucun code local | Pas de fichier de licence, manifeste MIT | Active | Service distant | Non installé | Aperçu par filtres | **Écarté du kit de base** : dépenses sans accord dans certains skills, copie de publicités de concurrents, envoi des médias au service |
| Rive | Animations interactives vectorielles | Exige l'éditeur Rive | MIT (runtime) | Active | Léger | Non installé | Lottie, HTML | **Écarté** pour l'instant : besoin de fichiers `.riv` |

## Sécurité

- `npm audit --omit=dev` dans `template/` : voir [TEST-REPORT.md](TEST-REPORT.md).
- Rendu sans réseau pour les compositions Universal : polices et médias locaux.
- Clés : seule l'existence de `ELEVENLABS_API_KEY` est lue, jamais sa valeur.
- Aucune installation globale, publication ni média payant sans demande explicite.

## Polices

| Polices | Où | Licence |
|---|---|---|
| Huit polices du moteur Opuscar (`f0` à `f7`) | `modules/opuscar/core/fonts/` | SIL Open Font License, texte dans `OFL.md` |
| Anton, Archivo Black, Instrument Serif, Inter, Montserrat, Playfair Display, Space Mono | `modules/video-effects/fonts/` | SIL Open Font License, un fichier `OFL-*.txt` par famille |
| Permanent Marker | `modules/video-effects/fonts/` | Apache-2.0, `LICENSE-PermanentMarker.txt` |
| Inter, Space Grotesk (`@fontsource`) | `template/node_modules`, installées par npm | OFL-1.1 |

## Inspirations

Écrites avec les mots du kit, sans copie de texte :
- `motion-fundamentals` s'inspire du « Motion Design Skill » de LottieFiles ;
- `ui-microinteractions`, des principes publiés sur le motion design d'interface ;
- `video-storyboard`, des skills de HyperFrames.

Le moteur et la skill « Prompt Motion » reprennent un style visuel observé sur prompt-motion.com : ni code, ni média, ni marque de ce site ne sont inclus.

## Marques et indépendance

Claude est une marque d'Anthropic. Remotion, HyperFrames (HeyGen), ElevenLabs, YouTube, TikTok, Instagram, iMessage, iPhone et LinkedIn appartiennent à leurs propriétaires. Les plateformes ne sont citées que pour nommer leurs formats ; les effets qui imitent leurs interfaces demandent un accord avant tout usage réel.

Le kit est un projet indépendant : il n'est ni affilié à ces entreprises, ni approuvé par elles.
