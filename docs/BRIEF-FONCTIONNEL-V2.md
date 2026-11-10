# Prompt maître V2 — Motion Design Kit Universal Studio

**Objectif central : studio audiovisuel multi-entrées, multi-styles et multi-sorties.** Le point de départ peut être un brief seul, un logo, des images, des rushes vidéo, des audios, des documents, un modèle 3D, un projet existant, ou une combinaison de ces éléments. Il faut traiter création, montage, modification et transformation comme des tâches distinctes.

> **Utilisation :** ouvrir Claude Code à la racine de `Motion-Design-Kit/`, puis coller l'intégralité du prompt ci-dessous. Le prompt est conçu pour auditer et améliorer le dépôt existant sans le détruire. Les URLs sont des sources à inspecter, pas des scripts à exécuter aveuglément.

## Rôle et mission

Agis comme **Principal Creative Technologist, Motion Design Director, 3D Technical Artist, Video Pipeline Engineer et Software Architect**. Ta mission consiste à transformer mon projet existant `Motion-Design-Kit/` en **Motion Design Kit Universal Studio**, un système modulaire de production audiovisuelle piloté par Claude Code. Il doit créer des vidéos de qualité professionnelle et, si demandé, des expériences réellement interactives, du storyboard à l'export, avec mémoire des marques, personnages persistants, prévisualisation et contrôle qualité.

**IMPORTANT :** tu dois travailler sur MON code existant, pas repartir de zéro. Commence par découvrir et lire `CLAUDE.md`, `LEEME.md`, les skills, `instalar.ps1`, `template/`, `prompt-motion/`, `hyperframes-starter/`, `perfil-plantilla/` et tous les manifestes. Déduis les capacités réelles du code et des commandes testées ; ne considère pas une promesse de README comme une fonction déjà installée. Distingue **existant / partiel / absent / incompatible**.

## Sources externes à auditer et intégrer proprement

1. `https://github.com/cblain100-prog/motion-design-claude-code` — surtout `patterns/PATTERNS.md`, `patterns/STORYBOARD-CRAFT.md`, les dix lois de mise en scène, les modèles `DIRECTIONS`/`STORYBOARD`, les styleframes, le minutage mot par mot avec Whisper, les objets-ponts entre scènes, les décors et caméras communs, les contrôles de couture, les exemples de film et le dispatch par séquence. Réutilise ou adapte les mécanismes pertinents selon licences et provenance ; ne copie pas les films, marques, musiques ou médias tiers comme si j'en possédais les droits.
2. `https://github.com/heygen-com/hyperframes` — l'API et la documentation compatibles avec la version installée, les quatre skills principaux (`hyperframes`, `hyperframes-cli`, `hyperframes-registry`, `media-use`), les skills optionnels `slideshow`, `figma` et `remotion-to-hyperframes`, ainsi que son catalogue de composants : titres, transitions, 3D, charts, maps, caméras, overlays, captions, product demos. Identifier les changements de version avant toute migration. **Ne pas exécuter automatiquement de mise à jour globale des skills ni de publish cloud.**
3. Évaluer techniquement, et adopter uniquement si utile : `@remotion/three`, React Three Fiber, Three.js, Drei, `@pixiv/three-vrm`, Blender + Python + Rigify, Motion Canvas, Manim Community, Reveal.js, Rive, GSAP et FFmpeg. Pour chaque outil : apport réel, compatibilité, licence, maintenance, impact CPU/GPU, preuve de fonctionnement, stratégie de fallback. Ne pas installer toutes ces bibliothèques par réflexe.

## Contraintes non négociables

- Sauvegarde et branche Git dédiées avant mutation. **Jamais d'écrasement de mes templates, compositions, assets, profils, presets, API keys, configuration ou projets.** Changements incrémentaux, avec commits explicites et retour arrière documenté.
- Ne jamais afficher, copier dans les logs ou committer de clés/API tokens. Les appels payants et la génération d'assets payants nécessitent mon accord explicite. Mode local/offline par défaut lorsque possible.
- Auditer tout code tiers, scripts d'installation, hooks, commandes et skill instructions **avant** exécution ; vérifier les licences, la provenance et le SHA/versions. Privilégier les dépendances pinées et les skills **locaux au projet**, non le remplacement silencieux des skills globaux. Ne jamais utiliser `@latest` sans audit ni consentement.
- Réconcilier les versions déjà présentes ; éviter les doublons entre Remotion, HyperFrames, Prompt Motion et les packages d'animation. Les modules restent isolés et communiquent par des interfaces stables.
- Conserver l'usage Windows/PowerShell et rendre les pipelines portables Linux/WSL quand c'est pertinent. Détecter CPU/GPU et prévoir un mode léger.
- Respecter les contraintes de licence, de marque, de consentement pour les voix/visages et les droits sur modèles 3D, musiques et vidéos. Ne jamais prétendre reproduire un visage ou une voix fidèle sans assets et droits appropriés.
- Le kit doit répondre dans la langue choisie par l'utilisateur (français, espagnol, anglais ; espagnol mexicain possible pour les voix) ; migrer proprement la règle actuelle « toujours en espagnol » vers une préférence configurable, sans perdre les profils existants.
- Les résultats doivent être reproductibles : animation calculée à partir du temps/frame (`seek`), seeds fixées pour les effets procéduraux, timeline et manifeste d'assets par projet, aucune dépendance réseau non contrôlée pendant le rendu.

## A0. Analyse universelle des entrées et des demandes — PRIORITÉ ABSOLUE

**N'impose jamais un workflow "texte -> storyboard -> vidéo" à toutes les demandes.** À l'ouverture de chaque mission, exécute le routage dans cet ordre :

1. **Détecte l'intention** : `CREATE_FROM_SCRATCH`, `ANIMATE_LOGO`, `ANIMATE_IMAGES`, `EDIT_FOOTAGE`, `RESTYLE_FOOTAGE`, `HYBRID_COMPOSITE`, `CHARACTER_ANIMATION`, `DATA_EXPLAINER`, `INTERACTIVE_PRESENTATION`, `REVISE_EXISTING_PROJECT`, `EXPORT_CONVERT` ; autoriser plusieurs intentions par projet.
2. **Inventorie réellement les assets** (sans altérer les originaux) : `logo`, images, clips, musique, voix off, texte/script, PDF/présentation, données, URL de site, modèles `.glb/.gltf/.vrm/.fbx`, sous-titres, projet éditable. Déduis les formats, dimensions, durée, cadence, rotation, codecs, canaux audio, alpha, langues, colorimétrie, qualité, droits et usages autorisés lorsque disponibles. Génère une planche-contact/timeline de repérage à partir des images et rushes. Ne présume pas qu'un logo JPEG est vectoriel, qu'une vidéo est exploitable sans conversion ou qu'une photo contient des informations 3D complètes.
3. **Choisis le traitement des assets** : réutiliser, nettoyer, détourer, vectoriser prudemment, reconstituer, recadrer, mettre en mouvement, enrichir, transformer, synchroniser, monter, remplacer ou générer les médias manquants. Préserve et référence les originaux ; toute transformation destructive doit créer une copie.
4. **Lis l'intention visuelle** séparément du type de tâche : stylisé 2D, cartoon 3D, caricature, anime, claymation, stop-motion, 2.5D, isométrique, CGI produit, photoréalisme, look film hollywoodien (sans copier des éléments protégés), documentaire réaliste, film noir, science-fiction, esthétique luxueuse, comédie, publicité, motion typographique, infographic, autre ou mélange explicité.
5. **Définis les contraintes de sortie** : linéaire MP4/WebM, GIF, image, animation transparente, expérience HTML interactive, projet éditable, découpage multi-formats ; durée, langue, ratio, résolution, niveau de qualité, budget de calcul/API et date de livraison.
6. **Route vers un ou plusieurs moteurs** en justifiant pourquoi chacun est nécessaire ; ne jamais lancer une chaîne lourde de génération 3D pour une simple coupe vidéo, ni réécrire des rushes filmés quand l'utilisateur demande seulement un montage. En cas d'absence d'assets, distinguer ce qui est réalisable par création procédurale locale de ce qui nécessite un service de génération visuelle ou des assets achetés/fournis.
7. **Pose au plus trois questions réellement bloquantes** ; si l'utilisateur demande « fais-le directement », propose les meilleures hypothèses et commence. La validation des dépenses/API, de l'utilisation des voix/visages et de toute publication reste obligatoire.

### Matrice des modes d'entrée à implémenter et tester

| Entrées | Sous-pipeline principal | Exemple de résultat | Contrôle spécifique |
|---|---|---|---|
| Seulement une idée/texte | concept -> script -> assets disponibles/procéduraux -> scènes -> montage | publicité, film narratif, animation explicative | identifier les médias réellement générables sans service externe |
| Logo uniquement | nettoyage/alpha -> animation vectorielle ou scène 3D -> compositing | logo reveal, intro/outro premium | respecter le logo exact, ses proportions et couleurs |
| Une ou plusieurs photos | recadrage, masquage, séparation en plans si faisable -> profondeur/parallaxe -> scène | photo vivante, diaporama cinématique, image animée | garder l'identité/le contenu sauf demande de transformation explicite |
| Rushes vidéo | ingest -> repérage -> sélection -> edit -> étalonnage -> audio -> export | montage clips, publicité, interview, best-of | respecter chronologie si demandé, éviter les coupures de phrases |
| Rushes + photos + logo + voix | story edit -> motion graphics -> compositing -> mix | vidéo hybride de marque | continuité audio/visuelle entre médias hétérogènes |
| Image/vidéo à restyler | vérifier droits/consentement -> transformation stylistique -> suivi et stabilisation -> QC | look cartoon, stylisé, cinematic | identité cohérente, moins de flicker, signaler limites du restylage |
| PDF, texte, chiffres, documents | extraction fidèle -> storyboard pédagogique -> graphiques -> voix | vidéo explainer ou infographie scientifique | ne pas inventer faits, chiffres, unités, sources |
| Personnage fourni/3D | importer -> rig/retarget -> animation/lipsync -> caméra/lumière | personnage présentateur ou court-métrage | cohérence personnage d'une scène à l'autre |
| Projet déjà créé | inspecter état/versions -> modification ciblée -> regression tests | montage corrigé, nouveau format, nouveau look | ne pas effacer la version antérieure |
| Présentation de services | scènes + branchements cliquables -> HTML et/ou film linéaire | catalogue de services interactif | vrais clics dans HTML ; aucun faux bouton annoncé sur MP4 |

### Contrat d'entrée unifié

Crée un manifeste par projet `project.json`, typé et validé (Zod ou JSON Schema), incluant au minimum : `request`, `intent[]`, `inputs[]` (path, type, metadata, rights, provenance), `style` (art_direction, realism_level, references, negative_constraints, continuity), `deliverables[]`, `timeline`, `characters`, `scene_assets`, `engines[]`, `quality`, `cost_ceiling`, `approval_required`, `status`. Le routeur doit fonctionner sur des cas mélangés (ex. logo + 10 clips + script + modèle 3D) et sur un brief sans fichier.

## A0bis. Bibliothèque de directions artistiques et cinématiques

Ne confonds pas **type d'image** et **niveau de réalisme**. Catalogue des axes combinables :

- **Dimension / technique** : flat 2D, motion vectoriel, 2.5D/parallaxe, 3D géométrique, 3D personnage, CGI photoréaliste, VFX, prises de vue réelles, génération vidéo conditionnelle et compositing hybride.
- **Style artistique** : cartoon expressif, caricature originale, anime, comic book, illustration, clay, low-poly, jeu vidéo, film d'animation familial, documentaire, luxe minimal, cyberpunk, science-fiction, vintage, film noir, blockbuster/héroïque, horreur, documentaire réaliste, reportage, corporate premium.
- **Direction cinématographique** : cadrages, plans larges/moyens/serrés, profondeur de champ, focales et perspective cohérentes, lighting motivated, volumétrie si possible, dolly/tracking, arc/orbit, crane, handheld volontaire, transitions par continuité, match cuts, color grading et sound design.
- **Intensité / degré de réalisme** : schématique, stylisé, semi-réaliste, réaliste, photoréaliste ; disponibilité des assets, GPU, moteur et budget conditionnent la qualité atteignable.
- **Narration** : publicité courte, teaser, film de marque, tutoriel, démonstration de service, montage événementiel, miniature documentaire, infographie pédagogique, récit fictionnel, présentation navigable.

**Traitement du terme « Hollywood » :** traduire en critères réalisables — composition cinématographique, éclairage, mouvements de caméra, color grading, conception sonore, storytelling, VFX et cohérence de production — et non en promesse automatique de qualité blockbuster. Définir des presets `cinematic-hollywood`, `stylized-3d`, `cartoon-caricature`, `photorealistic-commercial`, `hybrid-live-action-cgi`, `educational-3d`, `cinematic-logo-reveal`, `animated-photo`, `documentary-premium` et `immersive-5d-inspired`.

**Traitement de « 5D » :** ce n'est pas une technique de rendu vidéo standard. Proposer explicitement selon le besoin : animation 2.5D/parallaxe, vraie scène 3D, expérience interactive 3D, projection stéréoscopique/VR/360 si matériel et pipeline adaptés, ou ambiance multisensorielle simulée (son, caméra, effets). Ne jamais décrire une vidéo ordinaire comme 5D native.

**Personnages et médias fournis :** préserver l'identité et les traits visuels des personnages autorisés, les tenues et accessoires si précisés, la continuité des visages, couleurs, vêtements et proportions entre plans. Utiliser une bible de personnage et une planche de référence par personnage. Pour une transformation stylisée, chercher une cohérence visuelle et noter les limites techniques ; ne pas promettre une ressemblance parfaite. Pour un vrai acteur/visage/voix, vérifier le consentement aux usages de synthèse, éviter la confusion trompeuse et conserver la provenance des médias.

**Éviter une uniformisation :** les directions artistiques doivent différer réellement par le cadrage, la narration, le langage d'animation et les matériaux, pas seulement par la palette. Autoriser un film mêlant plusieurs styles, mais documenter les transitions et l'intention de ce mélange.

## A0ter. Moteurs, capacités, fallback et dépenses

Distinguer **édition de médias existants** (FFmpeg, pipeline NLE si disponible), **génération de motion graphisme** (Remotion, HyperFrames, Prompt Motion, GSAP), **3D rendue** (Three.js/Blender/Remotion Three), **génération d'assets** (outils locaux ou providers externes avec accès, tarifs et droits), **restylage de vidéo** (techniques adaptées et limites temporelles), **narration/audio** (source fournie, ElevenLabs autorisé ou outil local) et **interactivité** (HTML/React, non MP4).

Pour chaque requête, retourne brièvement : **assets détectés**, **intention**, **direction artistique**, **pipeline sélectionné**, **éléments manquants et fallback**, **livrable**, **coût potentiel**, **tests**. Le moteur doit traiter chaque tâche avec les outils les plus sobres, d'abord montage/transformation locale quand cela suffit. Les providers externes éventuels (génération d'image, texte-vers-vidéo, vidéo-vers-vidéo, lip-sync) sont des **adaptateurs optionnels**, jamais des obligations implicites. Pas d'appel payant sans approbation et estimation fondée ; pas d'affirmation qu'une API est disponible sans vérification.

## A. Audit initial et architecture cible

Créer `docs/AUDIT-AS-IS.md` comprenant : arborescence, versions, dépendances, inventaire des skills, fonctions réelles, moteurs opérationnels, scripts, problèmes, fonctionnalités absentes, risques de sécurité/licence/performance, commandes de validation et priorités. Corriger ou signaler les incohérences documentaires, notamment le nombre de skills intégrés, la distinction entre ressources du ZIP et ressources installées dynamiquement, et les capacités des moteurs.

Définir un **routeur intelligent** de production (une seule interface utilisateur et plusieurs backends) : `creative-director`, `style-registry`, `storyboard-engine`, `asset-manager`, `character-studio`, `scene-engine`, `audio-engine`, `render-engine`, `interactive-experience`, `quality-gates`, `brand-memory`. Utiliser le moteur adapté au plan, pas quatre moteurs pour chaque vidéo. Formats de sortie : MP4/WebM, GIF/APNG si pertinent, images/stills, séquences PNG alpha, Lottie/rive si pertinent, et HTML interactif pour les expériences navigables. Fournir un schéma de projet machine-readable validé (JSON Schema/Zod) avec scènes, transitions, assets, couches, camera, timings, audio, aspect ratios, langues, droits, moteurs et rendus.

## B. Fusion de la grammaire visuelle et de tous les styles utiles

Importer le SAVOIR-FAIRE des deux dépôts dans une bibliothèque maintenable sans écraser les presets existants. Prévoir un catalogue searchable `styles/`, `patterns/`, `presets/`, `recipes/`, des métadonnées (nom, catégorie, tags, moteur, intensité, duration, formats, contraintes, référence source, licence, sample image/video). Inclure des catégories :

- typography cinétique, editorial/corporate, minimal premium, bold, rétro, paper UI, flat 2D, collage, whiteboard/dessin pédagogique, infographie éducative, math/science, diagrammes de flux, comparatif avant/après, charts/dashboards, cartes et timelines ;
- 2.5D parallax, isométrique, HUD futuriste, néon, glassmorphism, motion UI, product demo SaaS, publicités réseaux sociaux, lancement de produit, logo reveal, lower thirds, subtitres cinétiques ;
- 3D stylisée/cartoon, personnages humains ou mascottes, objets produits CGI, photoréalisme contrôlé, architecture/espaces, caméra 3D, assemblages/exploded views, simulations légères, profondeur cinématique, éléments filmés + 3D/VFX ;
- tutoriels, podcasts/interviews, vidéos d'événement, films documentaires ou narration, narration multi-langue, motion comics/storytelling, vidéos musicales calées sur le beat et présentations de services.

Adapter les règles « caméra vivante », « élément-pont », « un sujet visuel à la fois », « rythme en événements » et « calage image/voix » **au genre** ; ne pas imposer des mouvements rapides, des sous-titres omniprésents ou un CTA commercial à une vidéo scientifique, institutionnelle ou à un exposé calme.

Produire au minimum des presets démonstrateurs utilisables : `agency-saas-launch`, `premium-service-presentation`, `scientific-explainer`, `animated-infographic`, `3d-character-presenter`, `3d-product-showcase`, `interactive-services-deck` et `cinematic-hybrid`.

## C. Vraie 3D et personnages réutilisables

Créer `character-studio` avec import de `.glb/.gltf/.vrm/.fbx` quand les outils le permettent, vérification de licence, bibliothèque de personnages persistants, rig/armature, expressions, animations (idle, parler, pointer, marcher, réaction), éclairage, caméras et décors. Choisir `@remotion/three`/React Three Fiber + Three.js pour les scènes 3D adaptées au moteur Remotion ; `@pixiv/three-vrm` pour les avatars VRM ; Blender/Rigify pour la modélisation, le rigging avancé et le rendu plus réaliste. Utiliser les blocs 3D HyperFrames lorsque leur contrat de rendu est respecté.

Ajouter un pipeline de synchronisation labiale **à partir d'une piste voix et de timestamps/visèmes réels**, avec fallback simple si le modèle n'expose pas les blendshapes nécessaires. Ajouter cadrage, regards, gestes narratifs et contrôle de continuité du personnage entre scènes. Prévoir des avatars 3D stylisés et un mode CGI photoréaliste si les assets et la capacité de rendu le permettent. **Ne pas promettre qu'une simple bibliothèque Three.js génère magiquement un humain photoréaliste depuis du texte : elle affiche et anime des modèles.** Prévoir les imports/licences et la fabrication d'assets comme étapes distinctes.

Clarifier dans la documentation : la « 2.5D » correspond à une profondeur simulée/parallaxe ; la « 3D » à de vrais objets et caméras en volume ; « 5D » n'est pas un format standard de création vidéo. Traiter les demandes « 5D » comme une expérience cinématique immersive (parallaxe, effets volumétriques, son spatial/interactivité selon les possibilités), et demander éventuellement la forme de livraison finale.

## D. Infographies, explications et données

Créer un moteur explainer où l'utilisateur fournit un texte, un fichier, un jeu de données ou une description et obtient : objectifs pédagogiques, script clair, découpage en étapes, représentation visuelle (diagramme, timeline, carte, chart, anatomie/système 3D, simulation simple), narration, animations progressives, sous-titres et export. Ne jamais inventer de chiffres. Montrer sources/unités, dates, hypothèses et incertitudes. Construire des composants réutilisables `FlowDiagram`, `Timeline`, `ExplodedView`, `Comparison`, `DataChart`, `MapScene`, `ConceptReveal`, `StepByStepExplainer` ; intégrer Motion Canvas ou Manim uniquement pour les cas où ils apportent une valeur démontrée.

## E. Présentations interactives de services

Ajouter **deux sorties explicitement distinctes** : (1) film de présentation MP4, linéaire, et (2) expérience HTML interactive navigable avec boutons, hotspots, navigation libre, chapitres, animations au clic, choix de services, démo avant/après, formulaires ou CTA éventuels. Utiliser la fonction `slideshow` d'HyperFrames et/ou Reveal.js selon le besoin. Prévoir clavier, tactile, focus accessible, mode reduced-motion et responsive. Une vidéo MP4 ne contient pas de vrais boutons cliquables : ne pas présenter une simulation de clic comme de l'interactivité native.

Exemple de recette : présentation de cinq services d'une entreprise avec menu interactif → sélection d'un service → démo/infographie animée → bénéfices/prix vérifiés → retour au menu → option d'export en film récapitulatif.

## F. Pipeline de production universel

Workflow configurable : `brief -> analyser assets/sources -> 3 directions artistiques + styleframes -> validation -> script/storyboard -> voice/timestamps -> produire les scènes -> preview -> QC visuel + technique + audio -> correction ciblée -> livrer les variantes`. Fournir un mode `direct` qui évite les validations non essentielles mais conserve la vérification.

Pour les films longs, permettre des sous-agents par scène avec contrat commun : même design system, palette, typographies, décor, camera/world transform, asset manifest, timestamps, état entrant/sortant et raccord aux frontières. Réutiliser les techniques de handoff et de validation visuelle étudiées dans le dépôt de Colin Blain. Favoriser le cache, le rendu partiel et la reprise sur échec.

Options d'audio : ElevenLabs seulement quand disponible et autorisé, ou médias fournis et outils locaux. Transcription/timing, SFX, musique sous la voix, niveaux loudness, sous-titres SRT/VTT et intégrés, traduction FR/ES/EN. Séparer les coûts API des étapes de développement ; ne jamais générer des médias payants pour une simple vérification d'installation.

## G. Qualité, performance, sécurité et CI

Ajouter : validation Zod/JSON, lint/TypeScript, build et tests unitaires, tests smoke par moteur, preview, tests image à frames clés, planche-contact, détection de frames noires/répétées et de coupures, comparaison visuelle aux styleframes, overscan et safe areas, sous-titres non coupés, cohérence des personnages, validation de la durée/audio/codecs, suivi des perfs CPU/GPU/RAM et cache. Vérifier également le rendu sans internet quand c'est annoncé.

Créer des profils de rendu `draft` (rapide, basse résolution), `review` (qualité moyenne, captures) et `final` (haute qualité), avec support 9:16, 16:9, 4:5, 1:1, 1080p et 4K selon ressources disponibles. Prévoir un fallback CPU si le GPU est insuffisant. Documenter limitations et coûts. Aucun upload automatique. Garder une liste des licences et sources des assets.

Distinguer les anomalies bloquantes des préférences esthétiques : une séquence volontairement noire, silencieuse, lente ou sans CTA peut être correcte et doit pouvoir être déclarée comme telle dans le storyboard.

## H. Ordre d'exécution obligatoire et livrables

**Phase 0 :** sauvegarde/branche, analyse du dépôt, versions, état des ressources locales et audit `docs/AUDIT-AS-IS.md` ; ne toucher à aucune configuration externe sans mon accord.

**Phase 1 :** routeur multi-entrées avec matrice testable, architecture modulaire, routeur de projets, registre de styles/patterns, fusion des principes de storyboard de Colin Blain, catalogue HyperFrames compatible, nettoyage des redondances et configuration multilingue. Préserver la compatibilité de l'ancien kit.

**Phase 2 :** implémenter au moins un parcours 3D personnage animé + voix, un explainer/infographie de données et un parcours de présentation de services interactif. Prioriser des démonstrateurs FONCTIONNELS plutôt que des stubs vides.

**Phase 3 :** tests, rendus démonstrateurs, documentation de démarrage Windows et Linux/WSL, contrôle qualité, roadmap restante et rapport de migration.

Créer au minimum :

- `docs/AUDIT-AS-IS.md` ; `docs/ARCHITECTURE.md` ; `docs/STYLE-CATALOG.md` ; `docs/MIGRATION.md` ; `docs/THIRD-PARTY.md` ; `docs/ROADMAP.md` ;
- un manifeste de projet standard et sa validation ; un registre de moteurs/styles documenté ;
- les nouveaux skills/règles de routage (`character-studio`, `infographic-director`, `interactive-presentation`, `cinematic-3d`, `quality-reviewer`) **seulement s'ils correspondent à des capacités exécutables** ;
- au minimum trois démonstrateurs exécutables (dont un montage de médias fournis ou de médias tests, et un cas de création sans asset fourni) et leurs commandes de preview/render ;
- un tableau de tests **PASS / FAIL / NOT TESTED** avec preuves (fichiers/frames/logs) ;
- un résumé des fichiers modifiés, les commandes nécessaires, les éléments encore absents, le coût estimatif des providers externes uniquement si documenté, et la manière de revenir à l'ancienne version.

**Tests de routage supplémentaires obligatoires :** un brief sans aucun média ; un logo PNG seul ; un lot de photos ; trois clips vidéo à monter ; un projet hybride logo + photos + vidéos + voix ; une demande de restylage caricatural ; une création 3D stylisée ; une scène réaliste cinématographique ; une demande ambiguë « 5D » ; une présentation HTML interactive. Pour chaque cas, montrer le manifeste, la sélection du pipeline et au moins une preuve d'exécution locale réalisable ; marquer les tests nécessitant des services ou assets non disponibles comme `BLOCKED` ou `NOT TESTED` et non `PASS`.

**Critères d'acceptation :** (i) une vidéo 2D déjà existante continue de fonctionner ; (ii) une vidéo infographie est produite à partir de données de test sourcées ; (iii) un personnage 3D réutilisable parle/gesticule à partir d'assets licites ; (iv) une présentation HTML contient une véritable navigation interactive ; (v) toutes les sorties passent les checks vérifiables et sont livrées avec les paths ; (vi) aucune installation globale, publication cloud, média payant ni suppression destructive sans autorisation.

**Mode de communication :** donne-moi d'abord l'audit réel et le plan précis, puis exécute les changements locaux raisonnablement faisables de façon incrémentale. À chaque phase, résume clairement ce qui est FAIT, PARTIEL, IMPOSSIBLE dans l'environnement. N'affirme pas qu'un module marche sans test. Si une étape dépend de mon consentement, d'une clé payante, d'un service externe ou d'assets que tu ne possèdes pas, mets-la en attente et continue les autres phases.
