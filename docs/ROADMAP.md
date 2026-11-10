# Feuille de route

Ce qui reste, par ordre d'utilité. Rien ici n'est annoncé comme existant.

## Dépend d'une décision ou d'un accès

| Sujet | Bloqué par | Note |
|---|---|---|
| Une voix française gratuite plus naturelle | Écoute humaine, extrait de voix consenti | Kokoro reste l'option gratuite, jugée perfectible à l'écoute par le créateur du kit ; ElevenLabs l'option payante. Chatterbox, essayé sans extrait français, n'a pas fait mieux aux mesures : voir `THIRD-PARTY.md` |
| Suivi d'un vrai visage, pour les effets et le recadrage | Une vidéo d'une personne d'accord | Les 51 effets tournent sur un clip sans personne, et le recadrage est prouvé sur des trajectoires simulées. Sans visage filmé, ni l'un ni l'autre n'est prouvé |
| Vrai restylage de vidéo | Fournisseur, budget, consentement | Aujourd'hui : aperçu par filtres seulement |
| Génération d'images et de vidéos | Fournisseur et budget | Adaptateurs optionnels à écrire, jamais imposés |
| Photoréalisme | Modèles, matières et décors réalistes, avec leurs droits | Blender est reconnu et `character3d` rend une mascotte procédurale (essayé avec Blender 5.2.3). Il ne rend que ce qu'on lui fournit |
| Musique jouée par de vrais instruments | Accord pour télécharger les échantillons (78 à 416 Mo par banque) | Musique synthétisée et bruitages locaux déjà fonctionnels. ElevenLabs reste possible en payant |
| Un fournisseur de vidéo générée (Arcads ou autre) | Choix, compte, budget | Évalué et écarté du kit de base, voir `THIRD-PARTY.md`. Possible plus tard comme option payante limitée |

## À construire

| Sujet | Valeur | Détail |
|---|---|---|
| Retirer les hésitations et les prises ratées | Haute | Les silences se coupent et les extraits tombent sur des fins de mots. Les « euh » et les reprises restent : Herk Edit Kit en option |
| Plusieurs personnes à l'image | Moyenne | Le recadrage suit un seul visage ; à deux, il faut le fond flou ou la coupe au centre. Aucune séparation des voix |
| Prouver d'autres styles Opuscar | Haute | Seul Risograph a un film de preuve. Viser d'abord un style 3D et un style documentaire |
| Styles personnels | Moyenne | Changer un style et le garder dans `perfil/`, d'après `MY-STYLES.md` d'Opuscar, non copié |
| `ExplodedView`, `MapScene` dans Remotion | Moyenne | Passent aujourd'hui par les blocs HyperFrames |
| VRM | Moyenne | `@pixiv/three-vrm` 3.5.5 demande `three >=0.137` : ajout possible, à tester avec un avatar libre |
| Un GLB fourni comme héros de `Escena3D` | Moyenne | Le héros est procédural aujourd'hui |
| Suivi de caméra pour `Hibrido` | Moyenne | Sans lui, seules les prises fixes s'intègrent bien |
| Bouche phonétique pour FR et ES | Moyenne | Aujourd'hui la bouche suit les lettres minutées, pas les phonèmes |
| Comparaison visuelle automatique entre plans d'un personnage | Moyenne | La continuité repose sur une fiche unique et un contrôle à l'œil |
| Rendu partiel et reprise après échec | Moyenne | Chaque scène est relancée en entier aujourd'hui |
| Sous-agents par scène pour films longs | Moyenne | Méthode décrite dans `docs/STORYBOARD-AGENCY.md`, non outillée |
| Masquage et séparation de plans depuis une photo | Basse | Exige un modèle de segmentation local |
| Sorties Lottie, Rive, APNG | Basse | Seul le GIF passe par `to-gif.ps1` |

## Compréhension et mémoire

- **Vidéo fournie, liste neuve de 23 demandes** écrite avant tout essai : 22 comprises à la première mesure et **une mal comprise sans le dire** (« Transforme mon podcast en petits extraits » lu comme un changement de style). Corrigé, puis 23 sur 23. La liste est maintenant connue : elle ne mesure plus des phrases neuves.
- **Le routeur seul ne comprend pas tout** : 22 phrases nouvelles sur 30, et il avoue les 8 autres. Comprendre revient à Claude, guidé par `universal-motion-director`. Ce comportement n'a pas été mesuré dans une session vierge.
- **Le kit retient seul** le format habituel, la qualité de chaque entrega, la marque et les règles. Le reste des goûts dépend de `motion-memoria`, donc de Claude.

## Dette connue

- `hyperframes-starter` charge GSAP depuis un CDN : son rendu dépend du réseau.
- Les skills tiers (option `-ConSkillsTerceros`) ne sont pas fixés par commit : la CLI ne le permet pas telle qu'elle est utilisée. Option désactivée par défaut.
- HyperFrames reste en 0.8.164 alors que 0.9.28 existe (lu par `updates` le 10 novembre 2026) : à réévaluer si un bloc récent devient nécessaire. Remotion, Playwright, three, React, Impeccable et mediapipe ont aussi une version plus récente : aucune n'est adoptée sans essai.
- `modules/three-studio` n'a pas de fichier de verrouillage : l'assistant ne le propose pas.
- La validation du manifeste couvre les mots-clés JSON Schema utilisés, pas toute la norme.
- Le contrôle qualité ne vérifie pas lui-même que le texte reste dans les zones sûres : il produit une image pour le contrôle visuel.

## Assistant et installation

| Sujet | État | Note |
|---|---|---|
| Installer un outil de l'ordinateur avec winget ou Homebrew | Logique testée, **jamais exécuté pour de vrai** | Sur la machine d'essai, tout était déjà présent. Ces outils arrivent dans la dernière version publiée par leur éditeur, puis le minimum est vérifié |
| macOS | **Non essayé** | L'assistant prévoit Homebrew et les emplacements de Blender |
| Linux | Essayé en partie sous WSL | Tests unitaires et assistant. FFmpeg absent de WSL : aucun rendu lancé |
| Mettre à jour le kit lui-même | Manuel | `updates.source` est vide : le kit se remplace dossier contre dossier, en recopiant `perfil/`, `out/` et les réglages |
| Appliquer une mise à jour de dépendance | Non prévu | `updates` compare et n'écrit rien : une version plus récente s'adopte avec une nouvelle version du kit |
| Désinstaller un outil de l'ordinateur | Manuel | Le kit liste ce qu'il a installé et dit comment l'enlever. Il ne le fait pas lui-même |
| Comportement de Claude dans une conversation vierge | Non mesuré | Le premier lancement, la reprise et la réparation sont testés au niveau du code, pas en conversation réelle |
