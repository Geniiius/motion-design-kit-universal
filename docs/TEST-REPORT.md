# Rapport de tests

Généré par `tests/rapport.py` à partir des exécutions réelles. Machine : Windows 11, i5-1240P, NVIDIA T550.

PASS : exécuté et vérifié. PARTIAL : la route est juste et quelque chose a tourné, mais pas toute la demande. BLOCKED : il manque un service, un asset ou un consentement. NOT TESTED : non exécuté.

> Le contrôle automatique ne juge ni le goût ni l'écoute : les planches ont été regardées, et seules les voix FR et ES ont été validées à l'oreille.

## Tests unitaires

**PASS** : Ran 195 tests in 75.783s, via `python -m unittest discover -s tests -p "test_*.py"`.

## Non-régression des moteurs

| Test | Statut | Détail |
|---|---|---|
| TypeScript du modèle Remotion | **PASS** | 21 s  |
| Compositions listées | **PASS** | 37 compositions |
| Versions Remotion cohérentes | **PASS** | All packages have the correct version. |
| npm audit (production) | **PASS** | {'info': 0, 'low': 0, 'moderate': 0, 'high': 0, 'critical': 0, 'total': 0} |
| Modèle 2D existant : Promo-Landscape | **PASS** | 12 s |
| Modèle 2D existant : Kinetic-Reel | **PASS** | 13 s |
| Modèle 2D existant : Showcase-Landscape | **PASS** | 13 s |
| Vidéo 2D existante rendue : Logo-Square | **PASS** | 17 s, yuv420p, QC OK |
| Repli CPU pour la 3D (swangle) | **PASS** | 15 s |
| Prompt Motion : rendu | **PASS** | 6 s |
| HyperFrames 0.8.164 : check du starter | **PASS** | 28 s, sortie 0 |
| HyperFrames : bloc du registre fixé (data-chart) | **PASS** | 5 s, compositions/data-chart.html créé |
| HyperFrames : rendu du starter | **PASS** | 45 s, MP4 créé |

## Démonstrateurs

| Démonstrateur | Statut | Alertes | Preuves |
|---|---|---|---|
| Personnage 3D réutilisable qui parle et gesticule | **PASS** | 0 | [personnage/planche.jpg](preuves/personnage/planche.jpg) |
| Infographie sur données sourcées (NOAA) | **PASS** | 0 | [explainer/planche.jpg](preuves/explainer/planche.jpg) |
| Montage de médias de test (clips, photos, logo, voix, musique) | **PASS** | 0 | [montage/planche.jpg](preuves/montage/planche.jpg) |
| Présentation de services : HTML interactif + film | **PASS** | 0 | [presentation/planche.jpg](preuves/presentation/planche.jpg) |
| Import GLB CC0, animations, repli sans bouche | **PASS** | 0 | [modele-glb/planche.jpg](preuves/modele-glb/planche.jpg) |
| Scène 3D look cinéma | **PASS** | 0 | [cinema/planche.jpg](preuves/cinema/planche.jpg) |
| Rushes + personnage 3D | **PASS** | 0 | [hybride/planche.jpg](preuves/hybride/planche.jpg) |
| Personnage 3D, voix française (ElevenLabs) | **PASS** | 0 | [personnage-fr/planche.jpg](preuves/personnage-fr/planche.jpg) |
| Personnage 3D, voix espagnole (ElevenLabs) | **PASS** | 0 | [personnage-es/planche.jpg](preuves/personnage-es/planche.jpg) |
| Infographie, narration française (ElevenLabs) | **PASS** | 0 | [explainer-fr/planche.jpg](preuves/explainer-fr/planche.jpg) |
| Infographie, narration espagnole (ElevenLabs) | **PASS** | 0 | [explainer-es/planche.jpg](preuves/explainer-es/planche.jpg) |
| Film écrit en code, style Risograph, son synthétisé en local | **PASS** | 0 | [film-style/planche.jpg](preuves/film-style/planche.jpg) |
| Deux effets sur un clip sans personne | **PASS** | 2 | [effects-demo/planche.jpg](preuves/effects-demo/planche.jpg) |
| Personnage 3D, voix française locale (Kokoro) | **PASS** | 0 | [personnage-kokoro-fr/planche.jpg](preuves/personnage-kokoro-fr/planche.jpg) |
| Personnage 3D, voix espagnole locale (Kokoro) | **PASS** | 0 | [personnage-kokoro-es/planche.jpg](preuves/personnage-kokoro-es/planche.jpg) |

Tous les effets vidéo, sur un clip sans personne :

| Format | Effets | Images produites | Statut | Preuve | Limite |
|---|---|---|---|---|---|
| vertical | 51 | 51 | **PASS** | [effects/planche-vertical.jpg](preuves/effects/planche-vertical.jpg) | Clip sans personne : le suivi du visage et le passage derrière la tête ne sont pas prouvés ici. |
| paysage | 51 | 51 | **PASS** | [effects/planche-paysage.jpg](preuves/effects/planche-paysage.jpg) | Clip sans personne : le suivi du visage et le passage derrière la tête ne sont pas prouvés ici. |

Voix locale Kokoro et transcription, sans service payant :

| Langue | Voix | Durée | Texte retrouvé par la transcription | Écart aux pauses | Texte écrit conservé | Statut |
|---|---|---|---|---|---|---|
| fr | ff_siwis | 7.941 s | 92 % | 0.179 s | oui | **PASS** |
| es | ef_dora | 7.612 s | 100 % | 0.223 s | oui | **PASS** |
| en | af_bella | 8.318 s | 100 % | 0.15 s | oui | **PASS** |

Le texte entendu et le minutage sont mesurés. Le naturel de la voix ne se juge qu'à l'oreille.

Voix ElevenLabs, appels payants accordés le 2026-11-03 :

| Texte | Langue | Voix | Durée | Caractères facturés |
|---|---|---|---|---|
| Explainer | es | Matilda | 25.867 s | 318 |
| Explainer | fr | Matilda | 27.771 s | 364 |
| Personnage | es | Sarah | 14.443 s | 207 |
| Personnage | fr | Sarah | 13.282 s | 220 |

Total facturé par l'API : 1109 caractères, le compteur du compte a augmenté de 1111 caractères pendant ces appels. Tout rendu suivant lit le cache `out/cache-voix` sans frais.

Interactions réelles de la présentation (Chromium, Playwright) :

| Interaction | Statut |
|---|---|
| menu visible au chargement | **PASS** |
| vrai clic: ouvre un service et met à jour l'adresse | **PASS** |
| démo par étapes: chaque clic révèle l'étape suivante | **PASS** |
| clavier: flèche droite passe au service suivant | **PASS** |
| point interactif: le clic affiche sa note | **PASS** |
| Échap: retour au menu et focus rendu au bon bouton | **PASS** |
| chapitres: le bouton courant est signalé | **PASS** |
| avant/après: le curseur répond au clavier | **PASS** |
| lien direct: #service-4 ouvre le bon service | **PASS** |
| Tab atteint les commandes, focus visible | **PASS** |
| toucher + téléphone: pas de défilement horizontal, cibles de 44 px | **PASS** |
| mouvement réduit: animations coupées | **PASS** |
| aucune requête réseau, aucune erreur JavaScript | **PASS** |

## Comprendre une demande en langage courant

Sans aucun mot technique, FR, ES et EN. Le routeur ne reconnaît que des mots : comprendre revient à Claude, le routeur doit surtout avouer quand il devine.

| Série | Phrases | Justes | Avoue ne pas savoir | Fausses sans le dire |
|---|---|---|---|---|
| Ayant servi au réglage | 36 | 36 | 0 | **0** |
| Nouvelles, jamais vues au réglage : le vrai chiffre | 30 | 22 | 8 | **0** |
| Vidéo fournie, liste écrite avant tout essai | 23 | 23 | 0 | **0** |

Avant ce travail, sur la première série : 19 justes sur 36 et 17 fausses sans le dire.

Vidéo fournie : à la première mesure, 22 justes sur 23 et **une fausse sans le dire** (« Transforme mon podcast d'une heure en petits extraits pour TikTok », lu comme un changement de style). Le défaut a été corrigé, d'où le 23 sur 23 ci-dessus : cette liste est désormais connue et ne mesure plus des phrases neuves.

## Vidéo fournie : les traitements, exécutés pour de vrai

Vidéo d'essai : 17.8 s, 1920x1080, une voix française de synthèse locale. Là où le kit attend un lecteur, le script joue Claude.

| Cas | Demande | Attendu | Obtenu | Statut |
|---|---|---|---|---|
| logo | Ajoute mon logo à cette vidéo | 17.8 s, entière, avec le logo | t-logo.mp4 17.8 s 640x360 ; médias entiers, dans l'ordre | **PASS** |
| silences | Enlève les silences de ma vidéo | plus courte, la durée annoncée tenue | t-silences.mp4 10.3 s 640x360 · Silences : 4 coupes, 7.5 s retirées sur 17.8 s. | **PASS** |
| vertical | Mets ma vidéo au format TikTok | 360x640, entière ; sans visage, image gardée sur fond flou | t-vertical.mp4 17.8 s 360x640 · Recadrage : aucun visage suivi de façon fiable, l'image entière est gardée sur un fond flou. | **PASS** |
| vertical, centre | Mets ma vidéo au format TikTok (coupe au centre choisie) | 360x640 | t-vertical.mp4 17.8 s 360x640 · Recadrage : coupe au centre. | **PASS** |
| rien à changer | Enlève les silences de ma vidéo (vidéo sans silence) | « unchanged », aucun fichier écrit | unchanged, 0 fichier · Silences : aucun silence notable trouvé, la vidéo reste telle quelle. | **PASS** |
| demande floue | Ça fait pas assez pro, améliore | refus : rien n'est livré au hasard | refusée | **PASS** |
| sous-titres | Ajoute des sous-titres à ma vidéo | arrêt pour relecture, puis incrustés | t-sous-titres.mp4 17.8 s 640x360 ; deux arrêts avant ; transcrit : Bonjour et bienvenue dans cette vidéo. / Aujourd'hui, je vous montre / comment préparer un bon café. / Merci d'avoir regardé et à bientôt. · Sous-titres : fr, incrustés dans l'image. | **PASS** |
| traductions | Sous-titre ma vidéo en anglais et en espagnol | arrêt tant que les traductions manquent, puis une vidéo par langue | t-traduction-en.mp4, t-traduction-es.mp4 ; traduction écrite par le script · Sous-titres : en, es, incrustés dans l'image. | **PASS** |
| extraits | Fais 3 extraits courts de cette vidéo pour Instagram | arrêt pour le choix, puis 3 fichiers verticaux | t-extraits-1.mp4 3.8 s 360x640 ; t-extraits-2.mp4 3.3 s 360x640 ; t-extraits-3.mp4 3.4 s 360x640 · Extraits : 3 coupés sur des fins de mots. Recadrage : aucun visage suivi de façon fiable, l'image entière est gardée sur un fond flou. | **PASS** |
| chapitres | Écris les chapitres de cette vidéo pour YouTube | arrêt pour la lecture, puis un texte, aucune vidéo réencodée | t-chapitres.chapitres.txt ; 0 vidéo · Chapitres : 3 écrits dans t-chapitres.chapitres.txt, à coller dans la description de la vidéo. | **PASS** |
| chaîne complète | Enlève les silences, ajoute des sous-titres et mets-la en vertical pour TikTok | trois traitements, un seul fichier vertical, plus court | t-tout.mp4 10.3 s 360x640 · Silences : 4 coupes, 7.5 s retirées sur 17.8 s. Recadrage : aucun visage suivi de façon fiable, l'image entière est gardée sur un fond flou. Sous-titres : 1 passage(s) se lisent vite parce que la personne parle vite. Condenser le texte de t-tout.fr.srt si la lecture gêne. Sous-titres : fr, incrustés dans l'image. | **PASS** |
| vidéo de 20 minutes | Enlève les silences de ma vidéo (343 silences) | livrée, image et son de même durée | t-longue.mp4 596.8 s 320x180 ; écart image-son 0.085 s · Silences : 343 coupes, 603.3 s retirées sur 1200.0 s. | **PASS** |

Images des sous-titres, de la traduction, de la chaîne complète et d'un extrait : [traitements/planche.jpg](preuves/traitements/planche.jpg).

Les chiffres mesurent des durées, des formes et des nombres de fichiers. Le texte des sous-titres, le choix des extraits et des chapitres sont joués par ce script à la place de Claude. Le recadrage qui suit un visage n'est pas essayé ici : la vidéo d'essai ne montre personne.

Avant ce travail, ces demandes sortaient toutes une vidéo de 3,5 s déclarée livrée : voir `docs/AUDIT-2026-11-09.md`. Le décalage progressif entre l'image et le son après de nombreuses coupes, et l'échec au-delà d'une centaine de coupes, ont été trouvés par ces essais puis corrigés.

## Assistant : détection, premier lancement, vérification, réparation, désinstallation

Exécuté le 2026-11-10 sur : Windows 11 (10.0.22631), AMD64 · 12th Gen Intel(R) Core(TM) i5-1240P (12 cœurs, 16 fils) · 39,7 Go · Intel(R) Iris(R) Xe Graphics (2,0 Go) ; NVIDIA T550 Laptop GPU (4,0 Go) · 71,1 Go libres sur 474,7.

| Essai | Statut | Détail |
|---|---|---|
| Machine mesurée | **PASS** | Windows 11 (10.0.22631), AMD64 · 12th Gen Intel(R) Core(TM) i5-1240P (12 cœurs, 16 fils) · 39,7 Go · Intel(R) Iris(R) Xe Graphics (2,0 Go) ; NVIDIA T550 Laptop GPU (4,0 Go) · 71,1 Go libres sur 474,7 · 16.3 s |
| Logiciels et versions lus | **PASS** | python 3.14.4, node 24.14.1, npm 11.11.0, ffmpeg 9.0.2, git 2.55.0, uv 0.12.10, blender 5.2.3 · gestionnaire : winget |
| Conflits signalés | **PASS** | aucun sur cette machine |
| Encodeurs matériels essayés pour de vrai | **PASS** | h264_nvenc : échoue, h264_qsv : fonctionne, h264_amf : échoue |
| Premier lancement : ce qui est déjà installé est reconnu | **PASS** | 15 éléments déjà là sur 15, 0 à proposer, 0 à faire à la main |
| Demander à installer ce qui est déjà là ne refait rien | **PASS** | 15 éléments, tous laissés tels quels |
| Vérification complète | **PASS** | READY en 104 s : 17 READY, 0 WARNING, 0 FAILED, 0 OPTIONAL |
| Essai vidéo : montage | **PASS** | vidéo de 3.0 s faite et contrôlée en 5 s · essai-montage.mp4 640x360 |
| Essai vidéo : création | **PASS** | vidéo de 3.2 s faite et contrôlée en 48 s · essai-creation.mp4 540x960 |
| Kit déjà configuré : contrôle de santé sans rien relancer | **PASS** | phase ready en 0.16 s, 12 usages prêts |
| Diagnostic de réparation | **PASS** | 0 élément(s) à réparer ; rien n'est réparé sans accord |
| Désinstallation : liste seule | **PASS** | 8 groupes, 2388 Mo ; jamais supprimés : perfil, out ; hors du kit : 3 élément(s) listés |
| Comparaison des versions, sans rien mettre à jour | **PASS** | 12 versions fixées comparées le 2026-11-10 ; plus récentes : remotion 4.0.540 → 4.0.542 (corrective); three 0.180.0 → 0.187.0 (majeure); react 19.1.0 → 19.3.1 (mineure); playwright 1.64.1 → 1.65.0 (mineure); playwright-core 1.64.1 → 1.65.0 (mineure); impeccable 4.8.0 → 4.8.2 (corrective); hyperframes 0.8.164 → 0.9.30 (majeure); mediapipe 1.2.0 → 1.2.2 (corrective) |
| Journal et état sans donnée sensible | **PASS** | 2 fichier(s) de journal lus : ni dossier personnel, ni nom d'utilisateur, ni clé |
| Blender 5.2.3 trouvé hors du PATH, mascotte rendue | **PASS** | 2.0 s, 960x540, en 273 s |

Bilan rendu par la vérification complète :

| Élément | Niveau | État | Version | Détail |
|---|---|---|---|---|
| Python | required | **READY** | 3.14.4 | version suffisante |
| FFmpeg | required | **READY** | 9.0.2 | une vidéo d'essai encodée puis relue ; une vidéo d'essai rendue pour de vrai |
| Node.js | required | **READY** | 24.14.1 | exécute du code |
| Moteur de création | required | **READY** | 4.0.540 | fichiers présents à la version fixée ; une vidéo d'essai rendue pour de vrai |
| Sous-titres automatiques | recommended | **READY** |  | le modèle se charge et transcrit hors ligne |
| Voix off gratuite | optional | **READY** |  | une phrase d'essai prononcée hors ligne |
| Effets autour d'une personne | optional | **READY** |  | détection chargée (OpenCV 5.0.0) |
| Styles de films | optional | **READY** | 1.64.1 | une image du film d'exemple rendue |
| Interfaces animées | optional | **READY** | 1.64.1 | le navigateur de rendu démarre |
| HyperFrames | optional | **READY** | 0.8.164 | version fixée déjà en cache |
| Contrôle de design | optional | **READY** |  | empreinte du détecteur vérifiée |
| Blender | optional | **READY** | 5.2.3 | trouvé dans son dossier d'installation |
| Git | optional | **READY** | 2.55.0 | présent |
| uv | optional | **READY** | 0.12.10 | présent |
| ElevenLabs (payant) | optional | **READY** |  | clé présente, valeur jamais lue. Service payant : chaque appel demande ton accord |
| Essai vidéo : montage | required | **READY** |  | vidéo de 3.0 s faite et contrôlée en 5 s |
| Essai vidéo : création | required | **READY** |  | vidéo de 3.2 s faite et contrôlée en 48 s |

Mascotte rendue par Blender : [assistant/mascotte-blender.jpg](preuves/assistant/mascotte-blender.jpg).

Versions fixées et dernières publiées (lecture seule, rien n'est mis à jour) :

| Paquet | Où | Fixée | Dernière | Écart |
|---|---|---|---|---|
| remotion | template | 4.0.540 | 4.0.542 | corrective |
| three | template | 0.180.0 | 0.187.0 | majeure |
| react | template | 19.1.0 | 19.3.1 | mineure |
| playwright | prompt-motion | 1.64.1 | 1.65.0 | mineure |
| playwright-core | modules/opuscar | 1.64.1 | 1.65.0 | mineure |
| impeccable | modules/design-check | 4.8.0 | 4.8.2 | corrective |
| hyperframes | cache de npm | 0.8.164 | 0.9.30 | majeure |
| mediapipe | option effects | 1.2.0 | 1.2.2 | corrective |
| opencv-python | option effects | 5.0.0.93 | 5.0.0.93 | à jour |
| faster-whisper | option transcribe | 1.2.1 | 1.2.1 | à jour |
| onnxruntime | option transcribe | 1.31.1 | 1.31.1 | à jour |
| kokoro-onnx | option voice | 0.6.1 | 0.6.1 | à jour |

L'installation de ce qui manque n'est pas dans ce tableau : sur cette machine, rien ne manquait. Elle est essayée sur le kit décompressé à neuf, section « Installation, portabilité, paquet », et par `tests/test_onboarding.py` avec des doublures.

## Économie de tokens (estimations)

Méthode : caractères / 3,6 pour le texte, largeur x hauteur / 750 pour une image. Explications : `docs/TOKEN-ECONOMY.md`. Mesure : `python tests/tokens.py`.

| Ce que Claude lit | Taille | ≈ tokens |
|---|---|---|
| `CLAUDE.md` et les descriptions des 21 skills, à chaque requête | 12449 caractères | 3458 |
| Skills lues pour : kit prêt, vidéo fournie à traiter | 14127 caractères | 3924 |
| Skills lues pour : création à partir d'une idée | 16264 caractères | 4518 |
| Skills lues pour : premier lancement | 6541 caractères | 1817 |
| Réponse de `start`, kit prêt, sans skill d'installation | 1516 caractères | 421 |
| Fiche de routage (le manifeste complet en ferait 896) | 259 caractères | 72 |
| Réponse de `run` | 1522 caractères | 423 |
| Planche de 10 images en 1600x360 (les 10 images une à une en feraient 12290) | une image | 768 |
| Transcription lisible (les mots minutés en feraient 901) | 602 caractères | 167 |

## Routage

Chaque cas a son manifeste validé, sa fiche et sa preuve dans `docs/preuves/routage/<cas>/`.

| Cas | Intentions | Moteurs | Questions | Accords requis | Statut | Détail |
|---|---|---|---|---|---|---|
| Brief sans aucun média | CREATE_FROM_SCRATCH | remotion-2d | 0 | 0 | **PASS** | 960x540, 10.5 s, bloquants: 0, alertes: 0 |
| Logo PNG seul | ANIMATE_LOGO | remotion-2d | 0 | 0 | **PASS** | 960x540, 3.0 s, bloquants: 0, alertes: 0 |
| Lot de photos | ANIMATE_IMAGES | remotion-2d | 0 | 0 | **PASS** | 960x540, 15.0 s, bloquants: 0, alertes: 0 |
| Trois clips à monter | EDIT_FOOTAGE | ffmpeg-edit | 0 | 0 | **PASS** | 640x360, 14.2 s, bloquants: 0, alertes: 1 |
| Logo + photos + vidéos + voix | EDIT_FOOTAGE, HYBRID_COMPOSITE | ffmpeg-edit | 0 | 1 | **PASS** | 640x360, 13.8 s, bloquants: 0, alertes: 0 |
| Restylage caricatural | RESTYLE_FOOTAGE | ffmpeg-edit | 0 | 2 | **PARTIAL** | Aperçu par filtres seulement. Le vrai restylage exige un fournisseur, un budget et le consentement : BLOCKED sans eux. 640x360, 4.0 s, bloquants: 0, alertes: 1 |
| Création 3D stylisée | CREATE_FROM_SCRATCH | remotion-3d | 0 | 0 | **PASS** | 960x540, 8.0 s, bloquants: 0, alertes: 0 |
| Scène réaliste cinématographique | CREATE_FROM_SCRATCH | remotion-3d | 0 | 0 | **PARTIAL** | Look cinéma en 3D PBR. Le photoréalisme n'est pas atteint : il demande des modèles et des matières réalistes, que le kit ne fournit pas. 960x540, 8.0 s, bloquants: 0, alertes: 0 |
| Demande ambiguë « 5D » | CREATE_FROM_SCRATCH | remotion-2d | 1 | 0 | **PASS** | 960x540, 8.0 s, bloquants: 0, alertes: 0 |
| Présentation HTML interactive | INTERACTIVE_PRESENTATION | html-deck | 0 | 0 | **PASS** | 13 interactions réelles réussies dans Chromium |
| Fichier de données | DATA_EXPLAINER | remotion-2d | 0 | 0 | **PASS** | 960x540, 34.6 s, bloquants: 0, alertes: 0 |
| Personnage fourni en GLB | CHARACTER_ANIMATION | remotion-3d | 0 | 0 | **PASS** | 960x540, 6.0 s, bloquants: 0, alertes: 0 |
| Projet déjà créé | REVISE_EXISTING_PROJECT |  | 0 | 0 | **ROUTE OK, NOT TESTED** | La modification dépend de la demande : route et inspection testées, pas de rendu. |

## Presets démonstrateurs

| Preset | Composition | Statut | Preuve |
|---|---|---|---|
| agency-saas-launch | Promo-Landscape | **PASS** | docs\preuves\presets\agency-saas-launch.png |
| premium-service-presentation | Promo-Square | **PASS** | docs\preuves\presets\premium-service-presentation.png |
| scientific-explainer | Explainer-Landscape | **PASS** | docs\preuves\presets\scientific-explainer.png |
| animated-infographic | Explainer-Reel | **PASS** | docs\preuves\presets\animated-infographic.png |
| 3d-character-presenter | Personaje-Nodo-Landscape | **PASS** | docs\preuves\presets\3d-character-presenter.png |
| 3d-product-showcase | Escena3D-Square | **PASS** | docs\preuves\presets\3d-product-showcase.png |
| interactive-services-deck | HTML | **PASS** | Voir le cas 10-interactif |
| cinematic-hybrid | Hibrido-Landscape | **PASS** | docs\preuves\presets\cinematic-hybrid.png |

## Installation, portabilité, paquet

| Test | Statut | Détail |
|---|---|---|
| ZIP créé par empaquetar.ps1 | **PASS** | 14.9 Mo |
| empaquetar refuse d'écraser un ZIP sans -Sobrescribir | **PASS** | refus constaté |
| Pas de perfil, de projets, de node_modules, de .git, d'état ni de journal | **PASS** | 799 entrées |
| Aucune clé d'API | **PASS** | 467 fichiers lus |
| Aucun terme personnel | **PASS** | liste fournie à l'exécution |
| Premier lancement reconnu : moteur de création proposé, pas installé | **PASS** | phase first-launch, à accepter : engine-remotion |
| Rien ne s'installe sans accord nommé | **PASS** | setup apply sans --approve est refusé |
| instalar.ps1 sur le paquet extrait : trois éléments acceptés, installés, vérifiés | **PASS** | 109 s, code 0, 0 FAILED.  |
| Deux vidéos d'essai faites pendant la vérification | **PASS** | out\essai-installation |
| Après la vérification complète, le kit se dit prêt sans rien relancer | **PASS** | phase ready, verdict READY |
| Les options non acceptées restent proposées, pas installées | **PASS** | sous-titres, voix et effets : sur demande |
| Journal technique écrit, sans nom d'utilisateur ni clé | **PASS** | logs\ : 2 fichier(s) |
| Profil vierge créé à l'installation | **PASS** | perfil\ ne contient que le modèle |
| Skills globaux inchangés par l'installation | **PASS** | empreinte de ~/.claude/skills identique avant et après |
| Montage depuis le paquet | **PASS** | route + run + QC |
| Personnage 3D depuis le paquet | **PASS** | composition Personaje-Nodo |
| Présentation interactive depuis le paquet | **PASS** | 13 interactions réelles |
| Contrôle de design accepté, installé et lancé depuis le paquet | **PASS** | empreinte vérifiée, 1 défaut(s) à juger |
| Rien d'Impeccable hors du kit | **PASS** | aucun dossier créé chez l'utilisateur |
| Modules présents dans le paquet | **PASS** | 66 styles, 51 effets, sans modèle ni environnement |
| Moteur des styles depuis le paquet | **PASS** | npm ci puis une image du film Risograph |
| Pas de téléchargement sans accord | **PASS** | le modèle de voix demande --approve-download |
| Tests unitaires depuis le paquet | **PASS** | Ran 195 tests in 69.550s |
| WSL Ubuntu, Python 3 : tests unitaires | **PASS** | Ran 195 tests in 28.299s OK (skipped=28) |
| WSL : montage et rendu | **NOT TESTED** | FFmpeg absent de WSL : tests de rendu sautés, pipeline non exécuté sous Linux |
| Compositions sans police ni média réseau (lecture du code) | **PASS** | template\src |
| Aperçu 3D interactif optionnel (modules/three-studio) | **PASS** | npm install, vite build, ouverture dans Chromium, boutons Saluer et Tourner cliqués, 0 erreur. Mascotte en formes simples : aperçu, pas un personnage fini. Commande : node tests/three_studio.mjs <copie> <image> |

## Non testé ou bloqué

| Capacité | Statut | Raison |
|---|---|---|
| Vrai restylage de vidéo, caricature d'une personne | **BLOCKED** | Aucun fournisseur, budget et consentement requis. Aperçu par filtres seulement |
| Photoréalisme, acteur humain | **BLOCKED** | Modèles et matières réalistes absents : Blender rend ce qu'on lui fournit. Look cinéma stylisé en repli |
| Génération d'images ou de vidéos | **BLOCKED** | Aucun fournisseur configuré, appels payants |
| ElevenLabs : musique et effets | **NOT TESTED** | Payant, non demandé |
| Suivi d'un vrai visage : éléments derrière une personne, recadrage qui suit le visage | **NOT TESTED** | Demande une vidéo d'une personne d'accord. Les effets ont tourné sur un clip sans personne, le recadrage sur des trajectoires simulées |
| Naturel de la voix Kokoro en français et en espagnol | **PARTIAL** | Texte et minutage mesurés. Écoutée par le créateur du kit, qui l'a jugée perfectible : elle reste l'option gratuite, ElevenLabs l'option payante |
| Contrôle de design sur le texte dessiné sur un canvas | **NOT TESTED** | Impeccable ne lit que HTML et CSS : aucune alerte sur une page de film ne prouve rien |
| Comportement de Claude dans une nouvelle conversation | **NOT TESTED** | Consignes écrites (`CLAUDE.md`, `kit-onboarding`, `universal-motion-director`, `video-workflows`), non mesurées dans une session vierge. Le code qu'elles pilotent est testé |
| Installer un outil de l'ordinateur avec winget ou Homebrew | **NOT TESTED** | Logique testée avec des doublures. Sur la machine d'essai tout était déjà présent : aucune installation réelle |
| macOS | **NOT TESTED** | Aucune machine. L'assistant prévoit Homebrew et les emplacements de Blender |
| Assistant en fenêtre avec quelqu'un qui répond au clavier | **NOT TESTED** | Les réponses sont jouées dans les tests ; le lancement sans question est essayé sur le paquet |
| Vidéo fournie de plus de 20 minutes | **NOT TESTED** | Essayé jusqu'à 20 minutes et 343 coupes. Une heure n'a pas été lancée |
| Sous-titres sur une vraie voix, avec du bruit ou de la musique | **NOT TESTED** | Essayé sur une voix de synthèse propre. La relecture avant incrustation reste obligatoire |
| Plusieurs personnes à l'image, plusieurs voix | **NOT TESTED** | Le recadrage suit un seul visage, les voix ne sont pas séparées |
| Effets imitant Instagram, iMessage, iPhone | **PARTIAL** | Rendus sur le clip de test, usage réel soumis à accord : marques et interfaces de tiers |
| 65 styles Opuscar sur 66 | **NOT TESTED** | Recette et moteur présents, aucun film de preuve. Seul Risograph a été rendu |
| Instruments échantillonnés, styles 3D Opuscar | **NOT TESTED** | Paquets à télécharger avec accord |
| Synchronisation labiale phonétique en FR et ES | **NOT TESTED** | La bouche suit les lettres minutées, pas des phonèmes : suffisant pour un personnage stylisé |
| VRM avec `@pixiv/three-vrm` | **NOT TESTED** | Non installé |
| Personnage articulé dans Blender (Rigify) | **NOT TESTED** | Seule la mascotte procédurale est rendue, voir la section de l'assistant |
| FBX | **NOT TESTED** | Le routeur demande une conversion en GLB |
| Blocs HyperFrames du catalogue | **NOT TESTED** | Noms vérifiés contre 0.8.164, un seul installé. Non rendus |
| Herk Edit Kit | **NOT TESTED** | Optionnel, commit fixé vérifié, outil non lancé |
| Option `-ConSkillsTerceros` | **NOT TESTED** | Écrirait dans `~/.claude/skills`, non lancée ici |
| Rendu 4K | **NOT TESTED** | Profil présent, non lancé |
| Rendu sans aucune connexion réseau | **NOT TESTED** | Polices et médias locaux, mais la coupure réseau n'a pas été simulée |
| Écoute humaine des mixages anglais, du montage, de la musique et du film Risograph | **NOT TESTED** | Niveaux mesurés seulement. Voix FR et ES acceptées par le créateur du kit le 2026-11-03 |
