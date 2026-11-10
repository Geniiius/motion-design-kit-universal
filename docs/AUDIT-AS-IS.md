# Audit de départ

État de `Motion-Design-Kit-Universal-V2.zip` avant ce travail, vérifié par exécution le 2026-11-03 sur Windows 11 (i5-1240P, 39,7 Go de RAM, NVIDIA T550 4 Go + Iris Xe, Node 24, Python 3.14, FFmpeg 9.0.2).

## Origine

V2 est le kit d'origine (102 fichiers) auquel un autre outil a ajouté un routeur Python, 7 skills courts, un catalogue et des démos. Ce travail en a retiré tout contenu personnel et a réécrit ce qui ne tenait pas à l'exécution.

## Ce que V2 annonçait et ce que l'exécution a montré

| Point | Constat | Traitement |
|---|---|---|
| Routeur | Décide sur l'extension et un champ `intent`, un seul `workflow` | Réécrit : inventaire réel, intentions multiples, direction artistique séparée du moteur |
| Démo « brief → vidéo » | Texte fixe sur fond uni (3 images extraites identiques) | Passage par Remotion. Le repli FFmpeg a un fond et un texte animés |
| Contrôle qualité | Ne vérifie que la présence d'une piste et le codec | Réécrit : noirs, gels, coupes, mouvement, LUFS, sous-titres, exceptions déclarées |
| Remotion | Jamais compilé par V2 (dépendances absentes) | Compilé et rendu ici |
| `UniversalInfographic` | Non testée, chiffres illustratifs | Retirée, remplacée par l'explainer sur données sourcées |
| Présentation | Testée sur la présence de texte dans le HTML | Testée par 13 interactions réelles dans Chromium |
| Personnage 3D | Blender requis, bouche en boucle sans lien avec la voix | Personnage procédural avec visèmes réels, Blender reste optionnel |
| Skills | Deux copies (`skills/` et `.claude/skills/`) | Une seule : `.claude/skills/` |

## Problèmes trouvés dans le socle

### Sécurité et confidentialité
1. **`empaquetar.ps1` partageait tout sauf `perfil/`**, y compris tout dossier de projets et les médias de `template/public/`. Il écrasait aussi le ZIP existant sans prévenir. Corrigé : exclusions, contrôle final, refus d'écraser sans `-Sobrescribir`.
2. **`instalar.ps1` supprimait les skills globaux sans copie** et installait sans version fixe (`npx -y skills`, `git clone` sans commit). Corrigé : rien de global par défaut, CLI et commit fixés, options explicites.
3. **Télémétrie HyperFrames active**, registre sur la branche `main`. Corrigé : `.claude/settings.json`, registre fixé sur `v0.8.164`.
4. Aucune clé trouvée dans le code ni la documentation.

### Compatibilité
5. **zod 3.22.3 alors que Remotion en exige une autre** : avertissement à chaque rendu, et 11 vulnérabilités `npm audit` (10 hautes). Corrigé : Remotion 4.0.540 et zod 4.6.7, en versions exactes. `npm audit` de production : 0.
6. **Rendu en `yuvj420p`** au lieu de `yuv420p`. Corrigé par `--color-space=bt709` dans l'adaptateur Remotion.
7. **`hyperframes check` échouait** sur le starter (contraste). Corrigé.
8. **Polices chargées depuis internet pendant le rendu** (`@remotion/google-fonts`). Corrigé : `@fontsource` local.
9. **Le starter HyperFrames charge GSAP depuis un CDN**, version fixée. Signalé, non modifié : voir [ROADMAP.md](ROADMAP.md).

### Incohérences documentaires corrigées
« Plus de 70 skills » (17 dans le kit, le reste optionnel) ; « 21 skills HyperFrames » (vrai en 0.8.164, 8 en 0.9.2) ; Three.js absent de la liste des outils alors qu'il est une dépendance directe ; Herk présenté comme inclus alors qu'il est téléchargé ; « toujours en espagnol ».

## HyperFrames : pas de migration

Le kit reste en **0.8.164**. La version 0.9.0 rompt uniquement le rendu distribué (Lambda, Cloud Run), que le kit n'utilise pas. Passer à 0.9.2 n'apporte rien d'indispensable et demanderait de refaire les tests : à décider plus tard, voir [ROADMAP.md](ROADMAP.md).

## Dépôts externes audités, sans exécuter leur code

| Dépôt | Commit | Licence | Repris |
|---|---|---|---|
| `cblain100-prog/motion-design-claude-code` | `a89fc54` | MIT, skills HeyGen en Apache 2.0 | Méthode de storyboard résumée et adaptée au genre, gabarits, idée du contrôle de mouvement. Aucun film, marque, musique ni média tiers |
| `heygen-com/hyperframes` | tag `v0.8.164`, `4d6b5be` | Apache 2.0 | Noms des blocs de cette version dans le catalogue. Rien n'est copié |
