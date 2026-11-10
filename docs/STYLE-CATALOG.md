# Catalogue de styles

Généré depuis `presets/`. Recherche : `python -m universal.cli catalog <mots>`, `--category <catégorie>`, `--presets`.

## Statuts

- **demontre** : rendu dans ce kit, preuve dans docs/preuves
- **recette** : moteur et méthode présents, pas d'échantillon dédié
- **bloc-hf** : bloc HyperFrames 0.8.164 existant, non rendu ici
- **externe** : exige des assets ou un logiciel absents

## Directions artistiques

Axes combinables : dimension, réalisme, cadrage, lumière, caméra, narration. Le style n'est pas un moteur.

| Direction | Dimension | Réalisme | Atteignable en local | Limites |
|---|---|---|---|---|
| **cinematic-hollywood** | 3d | realistic | Scène 3D PBR, bandes 2,39:1, étalonnage | Pas de qualité blockbuster automatique, pas d'acteurs réalistes |
| **stylized-3d** | 3d | stylized | Personnages et objets procéduraux, GLB licenciés | Pas de génération 3D depuis un texte |
| **cartoon-caricature** | 2d | stylized | Personnage original, aperçu par filtres d'une vidéo | Vrai restylage de rushes : fournisseur externe et accord |
| **photorealistic-commercial** | 3d | photoreal | Non atteint : look PBR stylisé en repli | Exige Blender et un modèle soigné, ou un fournisseur |
| **hybrid-live-action-cgi** | hybrid | semi-realistic | Personnage composé sur un rush | Pas de suivi de caméra ni d'ombres automatiques sur la scène réelle |
| **educational-3d** | 3d | schematic | Scènes procédurales et étiquettes | Une anatomie exacte exige un modèle vérifié |
| **cinematic-logo-reveal** | 2d | stylized | Logo-* avec un PNG ou SVG fourni | Le logo n'est jamais redessiné sans accord |
| **animated-photo** | 2.5d | realistic | Encadrement vivant, parallaxe si plans séparés | Une photo plate n'a pas d'information 3D |
| **documentary-premium** | live-action | realistic | Montage et graphiques sourcés | Une séquence lente ou sans CTA est correcte si déclarée |
| **immersive-5d-inspired** | 2.5d | stylized | Parallaxe 2.5D, scène 3D, HTML interactif | Stéréo, VR et effets physiques exigent matériel et pipeline dédiés |

## Démonstrateurs

| Preset | Nom | Moteur | Composition |
|---|---|---|---|
| **agency-saas-launch** | Lancement SaaS d'agence | remotion-2d | Promo-Landscape |
| **premium-service-presentation** | Présentation premium de services | remotion-2d | Promo-Square |
| **scientific-explainer** | Explainer scientifique | remotion-2d | Explainer-Landscape |
| **animated-infographic** | Infographie animée verticale | remotion-2d | Explainer-Reel |
| **3d-character-presenter** | Présentateur 3D | remotion-3d | Personaje-Nodo-Landscape |
| **3d-product-showcase** | Vitrine produit 3D | remotion-3d | Escena3D-Square |
| **interactive-services-deck** | Présentation interactive | html-deck | HTML |
| **cinematic-hybrid** | Hybride cinématographique | remotion-3d | Hibrido-Landscape |

## Styles

### 3d

| Style | Moteurs | Intensité | Durée | Contrainte | Statut | Blocs HyperFrames |
|---|---|---|---|---|---|---|
| **3D stylisée cartoon** `stylized-3d-cartoon` | remotion-3d | moyenne | 5-60 s | Lumière d'environnement obligatoire | demontre | — |
| **Personnages et mascottes** `character-mascot` | remotion-3d | moyenne | 5-90 s | Fiche de personnage, continuité entre plans | demontre | — |
| **Produit CGI** `product-cgi` | remotion-3d, hyperframes | moyenne | 4-20 s | Un modèle fourni donne un meilleur résultat | demontre | product-turntable |
| **Photoréalisme contrôlé** `controlled-photoreal` | blender | faible | 4-20 s | Blender et assets nécessaires, non atteint par le moteur local | externe | — |
| **Architecture et espaces** `architecture` | remotion-3d, blender | faible | 8-30 s | Modèle à fournir | externe | — |
| **Caméra 3D** `camera-3d` | remotion-3d, hyperframes | moyenne | 4-20 s | Piste caméra séparée du décor | demontre | camera-dolly-zoom, frost-sequence-camera-orbit |
| **Vue éclatée** `exploded-view` | hyperframes | moyenne | 4-15 s | Non construit en Remotion, bloc HyperFrames | bloc-hf | exploded-stack |
| **Simulations légères** `light-simulation` | hyperframes | moyenne | 4-15 s | Graine fixe, tiré du temps | bloc-hf | water, ripples, nebula |

### cartoon et anime

| Style | Moteurs | Intensité | Durée | Contrainte | Statut | Blocs HyperFrames |
|---|---|---|---|---|---|---|
| **1930s Rubber Hose Cartoon** `rubber-hose` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **80s Cel Anime** `cel-anime-80s` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Mid-century Cartoon** `midcentury-toon` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Sci-Fi Sitcom Toon** `scifi-toon` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |

### cinema

| Style | Moteurs | Intensité | Durée | Contrainte | Statut | Blocs HyperFrames |
|---|---|---|---|---|---|---|
| **Profondeur cinématographique** `cinematic-depth` | remotion-3d | moyenne | 4-30 s | Look stylisé : pas de photoréalisme local | demontre | rack-focus, lens-flare, vfx-anamorphic-flare |
| **Rushes + 3D / VFX** `live-action-vfx` | remotion-3d, ffmpeg-edit | moyenne | 5-60 s | Pas de suivi de caméra automatique | demontre | light-leak, godrays |

### cinéma et époques

| Style | Moteurs | Intensité | Durée | Contrainte | Statut | Blocs HyperFrames |
|---|---|---|---|---|---|---|
| **1920s Silent Film** `silent-film` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Liminal Found Footage** `backrooms` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |

### dessin et peinture

| Style | Moteurs | Intensité | Durée | Contrainte | Statut | Blocs HyperFrames |
|---|---|---|---|---|---|---|
| **Chalkboard** `chalkboard` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Chinese Ink Wash** `ink-wash` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Crayon Picture Book** `crayon-book` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Impasto Oil Painting** `impasto` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **One-line Drawing** `one-line` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Urban Sketch · Pen & Wash** `urban-sketch` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Watercolor Brush** `watercolor` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Whiteboard Explainer** `whiteboard-opuscar` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |

### donnees

| Style | Moteurs | Intensité | Durée | Contrainte | Statut | Blocs HyperFrames |
|---|---|---|---|---|---|---|
| **Graphiques et tableaux de bord** `charts-dashboard` | remotion-2d, hyperframes | faible | 10-60 s | Axes et unités visibles | demontre | data-chart, bar-chart-race, heatmap, mk-progress-stat |
| **Cartes** `maps` | hyperframes | moyenne | 8-30 s | Frontières à vérifier selon le sujet | bloc-hf | world-map, us-map, spain-map, nyc-paris-flight |
| **Frises chronologiques** `timelines` | remotion-2d | faible | 10-40 s | Dates sourcées | demontre | — |

### films de preuves

| Style | Moteurs | Intensité | Durée | Contrainte | Statut | Blocs HyperFrames |
|---|---|---|---|---|---|---|
| **Archive Light Table** `archive-lighttable` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Data Physicalization** `data-physical` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Engineering Briefing Board** `briefing-board` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Exploded Teardown** `teardown` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **LiDAR Survey** `lidar-survey` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Microscope Story** `microscope` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Projection on White Model** `white-model` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Satellite Briefing** `satellite-briefing` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |

### genre

| Style | Moteurs | Intensité | Durée | Contrainte | Statut | Blocs HyperFrames |
|---|---|---|---|---|---|---|
| **Tutoriel** `tutorial` | remotion-2d | faible | 30-180 s | Curseur exact sur l'élément cité | recette | code-typing, notes-reveal |
| **Podcast, interview** `podcast-interview` | ffmpeg-edit, herk-edit-kit | faible | toute durée | Ne pas couper une phrase, Herk Edit Kit en option | recette | lt-clean-bar |
| **Film d'événement** `event-film` | ffmpeg-edit | moyenne | 30-180 s | Consentement des personnes, chronologie si demandée | demontre | — |
| **Documentaire** `documentary` | ffmpeg-edit, remotion-2d | faible | 60 s et plus | Rythme lent assumé, pas de CTA imposé | recette | freeze-frame-dressing |
| **Narration multilingue** `multilingual-narration` | remotion-2d, elevenlabs | faible | toute durée | Voix locale en-US seulement sur ce PC, autre langue : voix fournie ou accord payant | recette | — |
| **Motion comics** `motion-comics` | remotion-2d | moyenne | 20-120 s | Planches par calques | recette | — |
| **Vidéo musicale au beat** `beat-music-video` | hyperframes | forte | 15-60 s | Grille vérifiée sur les vrais temps | bloc-hf | beat-freeze-cut, waveform |
| **Présentation de services** `service-presentation` | html-deck, remotion-2d | faible | libre | Tarifs et bénéfices vérifiés, jamais inventés | demontre | — |

### graphisme et typographie

| Style | Moteurs | Intensité | Durée | Contrainte | Statut | Blocs HyperFrames |
|---|---|---|---|---|---|---|
| **60s Spy Title Sequence** `spy-titles` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **ASCII / CRT Terminal** `ascii-crt` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Art Deco** `art-deco` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Blueprint** `blueprint` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Pictogram Motion** `pictogram-motion` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Stained Glass** `stained-glass` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Swiss Motion Graphics** `swiss-motion` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |

### illustration

| Style | Moteurs | Intensité | Durée | Contrainte | Statut | Blocs HyperFrames |
|---|---|---|---|---|---|---|
| **Flat 2D** `flat-2d` | remotion-2d | moyenne | 10-60 s | Palette réduite | recette | blob, stripes |
| **Collage** `collage` | remotion-2d, hyperframes | moyenne | 10-40 s | Droits de chaque image à vérifier | recette | gallery-tunnel |

### impression et gravure

| Style | Moteurs | Intensité | Durée | Contrainte | Statut | Blocs HyperFrames |
|---|---|---|---|---|---|---|
| **Copperplate Engraving** `engraving` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Halftone Dossier** `halftone-dossier` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Printed Long Take** `printed-long-take` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Risograph Print** `risograph` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Silkscreen Travel Poster** `silkscreen-poster` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Woodcut Print** `woodcut` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |

### information et keynote

| Style | Moteurs | Intensité | Durée | Contrainte | Statut | Blocs HyperFrames |
|---|---|---|---|---|---|---|
| **Circuit Board** `circuit-board` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Dark Tech Keynote** `dark-keynote` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Data Storytelling** `dataviz` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Isometric Infographic** `iso-infographic` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Isometric Picture Book** `isometric-picture-book` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Living Screencast** `living-screencast` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Sci-fi Hologram HUD** `hologram-hud` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Transit Map** `transit-map` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |

### interface

| Style | Moteurs | Intensité | Durée | Contrainte | Statut | Blocs HyperFrames |
|---|---|---|---|---|---|---|
| **HUD futuriste** `futuristic-hud` | prompt-motion, hyperframes | forte | 5-20 s | Densité d'information maîtrisée | demontre | hologram |
| **Néon** `neon` | hyperframes | forte | 5-20 s | Contraste à contrôler | bloc-hf | lt-neon-border, thin-film |
| **Glassmorphism** `glassmorphism` | hyperframes | moyenne | 5-20 s | Lisibilité du texte sur le flou | bloc-hf | glass-hero, ios26-liquid-glass, vfx-liquid-glass |
| **Motion UI** `motion-ui` | prompt-motion, remotion-2d | moyenne | 5-30 s | 150-350 ms par transition | recette | liquid-glass-widgets |
| **Démo produit SaaS** `saas-demo` | remotion-2d, prompt-motion, hyperframes | moyenne | 30-90 s | Reconstruire l'interface, curseur sur l'élément nommé | recette | app-showcase, code-typing |

### jeux vidéo

| Style | Moteurs | Intensité | Durée | Contrainte | Statut | Blocs HyperFrames |
|---|---|---|---|---|---|---|
| **16-bit Pixel RPG** `pixel-rpg` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Game Show Flat** `game-show` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **HD-2D** `hd-2d` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Microgame Frenzy** `microgame` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |

### marque

| Style | Moteurs | Intensité | Durée | Contrainte | Statut | Blocs HyperFrames |
|---|---|---|---|---|---|---|
| **Logo reveal** `logo-reveal` | remotion-2d, hyperframes | moyenne | 3-8 s | Logo exact, proportions et couleurs conservées | demontre | logo-outro, extruded-logo, yt-logo-intro |
| **Lower thirds** `lower-thirds` | hyperframes, remotion-2d | faible | 3-6 s | Hors zone couverte par la plateforme | bloc-hf | lt-clean-bar, lt-kicker-name, yt-lower-third, lower-third-bild |
| **Sous-titres cinétiques** `kinetic-captions` | remotion-2d, hyperframes | moyenne | toute durée | Calés sur les marques réelles de la voix | demontre | — |

### matières et volume

| Style | Moteurs | Intensité | Durée | Contrainte | Statut | Blocs HyperFrames |
|---|---|---|---|---|---|---|
| **Brick Toy** `brick-toy` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Desktop Flythrough** `desktop-flythrough` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Glass Product Render** `glass-product` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Low-poly Isometric Island** `lowpoly-island` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Memphis Diorama** `memphis-diorama` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Paper Pop-up Book** `paper-popup` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Tilt-Shift Miniature** `tilt-shift` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |

### montage et documentaire

| Style | Moteurs | Intensité | Durée | Contrainte | Statut | Blocs HyperFrames |
|---|---|---|---|---|---|---|
| **1920s Newsreel** `newsreel` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Broadcast News Package** `news-package` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Caption News** `caption-news` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Constructivist Montage** `kino-montage` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Live Countdown Split-screen** `countdown` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Sports Telestrator** `telestrator` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Time-lapse Symphony** `city-symphony` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Visual Investigation** `visual-investigation` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |

### pedagogie

| Style | Moteurs | Intensité | Durée | Contrainte | Statut | Blocs HyperFrames |
|---|---|---|---|---|---|---|
| **Tableau blanc pédagogique** `whiteboard` | hyperframes | faible | 30-120 s | Calme, une idée par étape | bloc-hf | hw-scribble-transition, hw-frame, hw-path-text |
| **Infographie pédagogique** `educational-infographic` | remotion-2d | faible | 20-90 s | Source, unité et date visibles, aucun chiffre inventé | demontre | data-chart |
| **Maths et sciences** `math-science` | remotion-2d | faible | 30-120 s | Manim non installé : courbes pilotées par données | recette | mk-line-graph |
| **Diagramme de flux** `flow-diagram` | remotion-2d, hyperframes | faible | 10-40 s | Sens de lecture unique | demontre | flowchart, flowchart-vertical, hw-pipeline |
| **Avant / après** `before-after` | remotion-2d, html-deck, hyperframes | moyenne | 5-20 s | Mêmes cadrage et unité des deux côtés | demontre | — |

### profondeur

| Style | Moteurs | Intensité | Durée | Contrainte | Statut | Blocs HyperFrames |
|---|---|---|---|---|---|---|
| **2.5D parallaxe** `parallax-25d` | remotion-2d | moyenne | 4-20 s | Profondeur simulée : ce n'est pas de la 3D | demontre | camera-dolly-zoom |
| **Isométrique** `isometric` | hyperframes, remotion-3d | moyenne | 8-30 s | Caméra orthographique à régler | recette | cuboid-carousel |

### publicite

| Style | Moteurs | Intensité | Durée | Contrainte | Statut | Blocs HyperFrames |
|---|---|---|---|---|---|---|
| **Publicités sociales** `social-ads` | remotion-2d, hyperframes | forte | 6-30 s | Accroche en 2 s, zones sûres | demontre | instagram-follow, tiktok-follow |
| **Lancement de produit** `product-launch` | remotion-2d, hyperframes | forte | 30-80 s | Un seul bouton en fin de film si CTA | recette | app-showcase, logo-outro |

### traditions est-asiatiques

| Style | Moteurs | Intensité | Durée | Contrainte | Statut | Blocs HyperFrames |
|---|---|---|---|---|---|---|
| **Paper-cut Lightbox** `paper-lantern` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Red Paper-cut** `papercut-red` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Shadow Puppetry** `shadow-puppet` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |
| **Ukiyo-e** `ukiyoe` | film-style | selon le récit | 20-120 s | Film écrit en code par scène, 30 à 60 min et beaucoup de tokens selon la source. | recette | — |

### typographie

| Style | Moteurs | Intensité | Durée | Contrainte | Statut | Blocs HyperFrames |
|---|---|---|---|---|---|---|
| **Typographie cinétique** `kinetic-type` | remotion-2d, hyperframes | forte | 8-30 s | Texte ≥ 5 % de la hauteur sur mobile | demontre | hw-title, yt-prism-title, glass-shard-title |
| **Éditorial corporate** `editorial-corporate` | remotion-2d, hyperframes | faible | 20-90 s | Pas de rebonds, rythme posé | recette | canopy-part-title, lt-clean-bar |
| **Minimal premium** `minimal-premium` | remotion-2d, prompt-motion | faible | 10-40 s | Une seule couleur d'accent | recette | flash-through-white, rack-focus |
| **Typographie massive** `bold-type` | remotion-2d, hyperframes | forte | 6-20 s | Lisible sans le son | recette | hw-write-title, editorial-flash-overlay |
| **Rétro VHS** `retro` | hyperframes | moyenne | 6-30 s | Grain et aberration avec parcimonie | bloc-hf | camcorder-hud, glitch |
| **Paper UI** `paper-ui` | prompt-motion | moyenne | 5-20 s | Fond papier gris chaud | demontre | — |

Tous les styles acceptent 16:9, 9:16, 1:1 et 4:5. Une durée est une indication, pas une règle.
