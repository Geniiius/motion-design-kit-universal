# Origine et corrections

Source : [Vibha-Ramprakash/claude-video-effects](https://github.com/Vibha-Ramprakash/claude-video-effects), commit `93140a976dcd1c78bda8819fa432ca7b4f260bf7`. Code MIT © 2026 Vibha Ramprakash (`LICENSE`).

## Modifié pour ce kit

- **Aucun texte ni chiffre par défaut qui se ferait passer pour vrai.** Les noms, comptes, titres et audiences de l'auteur ont été retirés. Ce qui est nécessaire à l'écran passe par `need()` : sans la valeur, l'effet s'arrête avant le suivi.
- **Chiffres écrits en dur retirés** : `reel-frame`, `glass-widgets`. Le texte de remplissage de `match-cut` est un lorem ipsum.
- **Pas de code chargé depuis un fichier optionnel** : le `exec()` de `fx_private.py` est supprimé.
- **Pas d'installation à l'exécution** : `words.py` n'appelle plus `pip`. Les versions et les empreintes sont fixées dans `modules/requirements/`.
- **Windows et langues** : plans lus en UTF-8, installation écrite en Python à la place de `setup.sh`.
- **Honnêteté du suivi** : `fx.py` écrit combien d'images ont vraiment trouvé un visage. Le kit le rapporte et prévient si c'est faible.
- **`--check`** vérifie les options sans vidéo.
- **Polices** : texte complet de l'OFL ajouté pour Anton et Montserrat, avec le copyright lu dans les fichiers de police.

## Retiré

`SKILL.md`, `README.md`, `assets/preview.jpg`, `scripts/setup.sh`. Le kit a son propre skill : `.claude/skills/video-effects/`.

## Modèles

`models/yunet.onnx` : SHA-256 identique à la version d'[opencv_zoo](https://github.com/opencv/opencv_zoo) (MIT). `models/selfie_segmenter.tflite` : MD5 identique à la version publiée par Google (Apache-2.0). Vérifié le 2026-11-03.
