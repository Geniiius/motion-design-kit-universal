# Origine et corrections

Source : [lemomo-ai/lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar), commit `bebbbe1aa92a3cb4bb6f83500e61b23a17d1aa00`. Code et documentation MIT © 2026 LemoLab (`LICENSE`). Les films de démonstration sont sous CC BY 4.0 et ne sont pas dans ce kit.

## Copié

Les 66 recettes (`styles/<style>/STYLE.md`, `style.json`), `DIRECTOR.md`, `TECHNIQUE.md`, et dans `core/` : le moteur de rendu, `lib.js`, les passes d'image, les outils audio et la voix Kokoro.

## Modifié pour ce kit

- **Installation** : plus de `setup.sh`. Il remettait le code sur la branche principale à chaque lancement et écrivait dans le dossier de l'utilisateur. Ici, tout reste dans le kit, en versions fixées avec empreintes : `python -m universal.cli modules install`. Le commit source est fixé dans `universal/modules.py`.
- **`DIRECTOR.md`, section 13** : les règles imposant une représentation politique de territoires disputés sont retirées. Un kit universel n'a pas à trancher : sans frontières si le film n'en parle pas, sinon la source est choisie par l'utilisateur et citée.
- **`mux.sh` remplacé** par `film-style master` (Python) : il ne demande pas de shell POSIX sous Windows, et il garde les couleurs de la page. Il écrit toujours du BT.709.
- **`tts_zh.py` retiré** : il appelle un service en ligne. Le kit reste local, ou payant avec un accord explicite.
- **Dépendances exactes** : `playwright-core` 1.64.1 (celle du kit, dans la plage demandée par la source) et `three` 0.170.0.
- **Commandes des guides** réécrites vers `python -m universal.cli`.

## Non copié

Les films et leurs sources (`styles/*/demo`, récupérables au même commit avec `film-style demo <style>`), la galerie, `AGENTS.md`, `MY-STYLES.md`, `MAINTAINING.md`, le plugin, les textures et modèles 3D (`film-style assets3d`), les modèles et les échantillons (`modules install`).

## Paquets téléchargeables

Empreintes SHA-256 dans `tools/assets.json`. Licences des échantillons : `core/audio/INSTRUMENTS.md`. Le piano Salamander (CC BY 3.0) et la batterie MuldjordKit (CC BY 4.0) exigent une mention dans les crédits. Kokoro-82M : Apache-2.0, entraîné notamment sur le corpus SIWIS (CC BY 4.0).
