# Recettes de production

**Vous n'avez pas besoin de cette page : dites ce que vous voulez, Claude lance tout.** Elle sert à Claude et aux curieux. Toutes les commandes partent de la racine du kit. Le premier passage en `draft`, la livraison en `final`.

## Premier lancement, santé, réparation
```bash
python -m universal.cli start                                    # à chaque conversation : dit quoi faire
python -m universal.cli setup apply --approve engine-remotion    # seulement ce que la personne a accepté
python -m universal.cli setup verify --deep                      # la seule vérification qui autorise à dire « prêt »
python -m universal.cli repair                                   # ce qui est en panne et ce qui le réparerait
```
Détail dans la skill `kit-onboarding`.

## Une vidéo fournie à travailler
```bash
python -m universal.cli route --brief "Enlève les silences, ajoute des sous-titres et mets-la en vertical pour TikTok" -i video.mp4 --name clip -o out/clip/project.json
python -m universal.cli run out/clip/project.json --profile draft
```
- `needs-input` : le kit a écrit un fichier et attend. Sous-titres : relire `clip.fr.srt`, corriger le texte seul, mettre `props.workflow.captions.reviewed` à `true`, relancer. Extraits et chapitres : lire `clip.transcription.txt`, écrire `props.workflow.clips` ou `props.workflow.chapters`, relancer.
- Traductions : `props.workflow.captions.languages`, puis écrire `clip.en.srt` avec les mêmes numéros et les mêmes horaires que le fichier relu.
- `unchanged` : rien n'était à changer, aucun fichier n'est écrit. Le dire à la personne.
- Si la personne le dit autrement (« coupe quand je ne dis rien »), ajouter `--workflow silence-cut`.

Détail dans la skill `video-workflows`.

## Une idée, aucun fichier
```bash
python -m universal.cli route --brief "Vidéo promo pour une boulangerie. Du pain chaud chaque matin." --name pain -o out/pain/project.json
python -m universal.cli run out/pain/project.json --profile draft
```
Écrire le vrai texte dans `props` du manifeste : au départ, il reprend le brief.

## Un logo
```bash
python -m universal.cli route -i logo.png::logo --name marque -o out/marque/project.json
```
Un PNG sans transparence ou un JPEG déclenche une alerte : le détourer sur une copie.

## Des photos
```bash
python -m universal.cli route -i a.jpg -i b.jpg -i c.jpg --name photos -o out/photos/project.json
```
Encadrement vivant et fondus. Pour une vraie parallaxe, fournir des plans séparés dans `props.capas`.

## Des rushes, un logo, une voix, une musique
```bash
python -m universal.cli contact-sheet a.mp4 b.mp4 -o out/reperage.jpg
python -m universal.cli route --brief "Monte ces clips" -i a.mp4 -i b.mp4 -i logo.png::logo -i voix.wav::voice -i musique.mp3::music --name film -o out/film/project.json
```
Pour choisir les passages, remplir `timeline.edl` : `{"src": "a.mp4", "in": 1.2, "seconds": 3, "transition": "fade"}`.

## Des données
Modèle complet : `universal/datos.py` et `demo_explainer`. Chaque chiffre est calculé depuis le fichier, la source reste à l'écran.

## Un personnage 3D qui parle
Modèle complet : `demo_personnage`. Avec un GLB : `python -m universal.cli route -i modele.glb --name perso -o out/perso/project.json`, après vérification de sa licence.

## Une présentation de services
```bash
python -m universal.cli present -c examples/universal/services.json -o out/services.html
node tests/deck.spec.mjs out/services.html out/preuves
python -m universal.cli film out/services.html -o out/services-film.mp4
```

## Un film dans un style nommé
```bash
python -m universal.cli setup apply --approve film-styles      # une fois, avec l'accord de la personne
python -m universal.cli route --brief "Film de 20 secondes en aquarelle sur la pluie" --name pluie -o out/pluie/project.json
python -m universal.cli film-style new watercolor out/pluie/film --name "La pluie" --seconds 20
```
Écrire `index.html` et `mix.py` d'après `modules/opuscar/styles/watercolor/STYLE.md`, regarder des images fixes avec `film-style still`, puis `run`. Un style est une recette, pas un gabarit : compter 30 à 60 minutes pour un film complet. Exemple complet : `examples/film-style/riso-pain/`.

## Des effets sur une personne filmée
```bash
python -m universal.cli setup apply --approve effects          # une fois, avec l'accord de la personne
python -m universal.cli effects check plan.json
python -m universal.cli effects still video.mp4 --plan plan.json --at 4.5 -o out/essai.png
python -m universal.cli effects render video.mp4 --plan plan.json -o out/final.mp4 --profile final
```
`plan.json` : `{"effects": [{"fx": "backdrop-word", "start": 3, "end": 5, "text": "ÉTÉ"}]}`. Liste : `effects list`. Options obligatoires : `presets/video-effects.json`. Vidéo d'une personne d'accord uniquement.

## Une voix gratuite en français ou en espagnol
```bash
python -m universal.cli setup apply --approve voice-local      # une fois, avec l'accord de la personne
python -m universal.cli voice --provider kokoro --language fr --text "Bonjour" -o out/voix.wav --srt out/voix.srt
```
L'option pèse environ 550 Mo. Avec l'option des sous-titres automatiques (`setup apply --approve captions`, 345 Mo), les mots gardent leur vrai minutage.

## Une voix dans une autre langue (payant)
```bash
python -m universal.cli voice --provider elevenlabs --approve --voice-id <id> --text "Bonjour" --language fr -o out/voix.mp3 --srt out/voix.srt
```
Sans `--approve`, rien n'est envoyé. Un même texte n'est jamais facturé deux fois. Démos FR et ES : `python tests/demos_tous.py review personnage-fr explainer-es --accord`.

## Rejouer tous les démonstrateurs
```bash
python -m universal.cli fixtures
python tests/demos_tous.py review
python tests/routage_preuves.py draft
python tests/effets_tous.py
```
