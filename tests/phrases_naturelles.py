"""What the router understands when someone simply says what they need, with no technical word.

The agent's understanding comes first: the router is its safety net. This measures that net, and above all
that it admits when it does not know instead of guessing silently. python tests/phrases_naturelles.py"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding='utf-8')

from universal.router import route  # noqa: E402

CAPS = {'tools': {'blender': False, 'three_vrm': False}, 'engines': {k: True for k in ('ffmpeg-edit', 'html-deck', 'remotion-2d', 'remotion-3d', 'film-style', 'video-effects')}}


def item(kind, role='source', name='x'):
    return {'path': f'{name}.bin', 'type': kind, 'role': role, 'exists': True, 'metadata': {}, 'rights': {'status': 'unknown'}, 'provenance': {}, 'warnings': [], 'treatment': []}


VIDEO, PHOTO, LOGO, CSV = item('video', name='moi'), item('image', name='photo'), item('image', 'logo', 'logo'), item('data', name='ventes')
# phrase, files, what a person would expect: an engine, or None when asking is the right answer
CASES = [
    ("Je veux un truc qui claque pour mes réseaux", [], 'remotion-2d'),
    ("Fais-moi une petite pub pour ma boulangerie", [], 'remotion-2d'),
    ("Il me faut quelque chose pour présenter ma boîte à des clients", [], None),
    ("J'ai besoin d'une vidéo pour Instagram sur mes nouveaux produits", [], 'remotion-2d'),
    ("Quelque chose de joli pour annoncer mon mariage", [], 'remotion-2d'),
    ("Explique aux gens comment marche mon appli", [], 'remotion-2d'),
    ("Mes ventes ont doublé, je veux le montrer de façon sympa", [], 'remotion-2d'),
    ("Mets ça en valeur", [PHOTO], 'remotion-2d'),
    ("Donne vie à cette image", [PHOTO], 'remotion-2d'),
    ("Rends mon logo vivant", [LOGO], 'remotion-2d'),
    ("Enlève les blancs et les silences de ma vidéo", [VIDEO], 'video-workflow'),
    ("Raccourcis cette vidéo à 30 secondes", [VIDEO], 'ffmpeg-edit'),
    ("Mets ma vidéo au format TikTok", [VIDEO], 'video-workflow'),
    ("Ajoute des sous-titres", [VIDEO], 'video-workflow'),
    ("Écris un mot géant derrière moi quand je parle", [VIDEO], 'video-effects'),
    ("Fais apparaître mes chiffres autour de moi", [VIDEO], 'video-effects'),
    ("Rends ma vidéo plus dynamique, un peu comme les gros créateurs", [VIDEO], None),
    ("Je veux que ça ressemble à une vieille gravure", [], 'film-style'),
    ("Un petit film comme une peinture pour raconter mon village", [], 'film-style'),
    ("Un dessin animé à l'ancienne sur mon café", [], 'film-style'),
    ("Comme un vieux jeu vidéo", [], 'film-style'),
    ("Un petit bonhomme qui présente mon service", [], 'remotion-3d'),
    ("Quelqu'un qui parle à l'écran pour expliquer, mais pas moi", [], 'remotion-3d'),
    ("Une page où mes clients peuvent cliquer pour voir mes offres", [], 'html-deck'),
    ("Montre ce fichier sous forme de graphique animé", [CSV], 'remotion-2d'),
    ("Fais que mon produit tourne en 3D", [PHOTO], 'remotion-2d'),
    ("Quiero algo chulo para mis redes", [], 'remotion-2d'),
    ("Una cosita para anunciar la apertura de mi tienda", [], 'remotion-2d'),
    ("Que parezca una pintura antigua", [], 'film-style'),
    ("Escribe una palabra enorme detrás de mí mientras hablo", [VIDEO], 'video-effects'),
    ("Quítale los silencios a mi vídeo", [VIDEO], 'video-workflow'),
    ("Un muñequito que explique mi servicio", [], 'remotion-3d'),
    ("Something eye-catching for my socials", [], 'remotion-2d'),
    ("Make it look like an old painting", [], 'film-style'),
    ("Put big text behind me while I talk", [VIDEO], 'video-effects'),
    ("Cut the boring parts out of my video", [VIDEO], 'ffmpeg-edit'),
]
# Written after the router was tuned, and never tuned on: the honest measure. Includes traps.
HOLDOUT = [
    ("Je tiens un salon de coiffure, il me faudrait de quoi attirer du monde", [], None),
    ("Pub pour mon entreprise de peinture en bâtiment", [], 'remotion-2d'),
    ("Vidéo pour ma salle de jeux vidéo", [], 'remotion-2d'),
    ("Je voudrais raconter l'histoire de ma grand-mère", [], None),
    ("Montre aux investisseurs que notre croissance est solide", [CSV], 'remotion-2d'),
    ("J'aimerais un truc façon vieux film en noir et blanc muet", [], 'film-style'),
    ("Dans le style des estampes japonaises, mon voyage à Kyoto", [], 'film-style'),
    ("Un film tout en papier découpé pour Noël", [], 'film-style'),
    ("Peux-tu ajouter ma musique sur cette vidéo ?", [VIDEO], 'ffmpeg-edit'),
    ("Enlève le début, il est trop long", [VIDEO], 'ffmpeg-edit'),
    ("Je parle face caméra, je voudrais des trucs qui bougent autour de ma tête", [VIDEO], 'video-effects'),
    ("Que mon prénom apparaisse derrière ma tête", [VIDEO], 'video-effects'),
    ("Transforme cette vidéo en dessin animé", [VIDEO], 'ffmpeg-edit'),
    ("Mets du mouvement sur ces photos de vacances", [PHOTO, PHOTO], 'remotion-2d'),
    ("Fais une intro avec mon logo", [LOGO], 'remotion-2d'),
    ("Un robot sympa qui accueille les visiteurs de mon site", [], 'remotion-3d'),
    ("Un mini site où on clique pour découvrir mes tarifs", [], 'html-deck'),
    ("Convertis ça en GIF", [VIDEO], 'ffmpeg-edit'),
    ("Ça fait pas assez pro, améliore", [VIDEO], None),
    ("Refais pareil que la dernière fois", [], None),
    ("Necesito algo para vender más en mi tienda", [], None),
    ("Un vídeo tipo película antigua sobre mi pueblo", [], 'film-style'),
    ("Haz que mi nombre salga detrás de mi cabeza", [VIDEO], 'video-effects'),
    ("Corta las partes aburridas", [VIDEO], 'ffmpeg-edit'),
    ("Pon mi logo a moverse", [LOGO], 'remotion-2d'),
    ("Un personajito simpático que salude a mis clientes", [], 'remotion-3d'),
    ("I need something to show my boss", [], None),
    ("Make my photos come alive", [PHOTO, PHOTO], 'remotion-2d'),
    ("A little animated guy who explains my product", [], 'remotion-3d'),
    ("Remove the silences", [VIDEO], 'video-workflow'),
]

# Requests about one provided video, written on 2026-11-09 after the treatments existed and before any run: never tuned on.
# The five expectations above that name silences, captions or a vertical format were moved to 'video-workflow' the same day,
# because the right answer changed when the kit learned those treatments.
VIDEO_HOLDOUT = [
    ("Mets des sous-titres sur ma vidéo", [VIDEO], 'video-workflow'),
    ("Je veux que les gens puissent lire ce que je dis", [VIDEO], None),
    ("Coupe les moments où je ne dis rien", [VIDEO], None),
    # First measure: 22 right out of 23. This one was read as a change of look and failed in silence; the defect it revealed was then fixed.
    ("Transforme mon podcast d'une heure en petits extraits pour TikTok", [VIDEO], 'video-workflow'),
    ("Passe cette vidéo en vertical", [VIDEO], 'video-workflow'),
    ("Découpe la vidéo en chapitres", [VIDEO], 'video-workflow'),
    ("Traduis ma vidéo en anglais", [VIDEO], 'video-workflow'),
    ("Ajoute mon logo en haut à droite", [VIDEO, LOGO], 'ffmpeg-edit'),
    ("Rends le son plus fort", [VIDEO], None),
    ("Sous-titres en espagnol et en allemand, s'il te plaît", [VIDEO], 'video-workflow'),
    ("Ponle subtítulos a mi vídeo", [VIDEO], 'video-workflow'),
    ("Quita las pausas largas", [VIDEO], 'video-workflow'),
    ("Hazme clips cortos para Reels", [VIDEO], 'video-workflow'),
    ("Pásalo a formato vertical", [VIDEO], 'video-workflow'),
    ("Tradúcelo al inglés", [VIDEO], 'video-workflow'),
    ("Divide el vídeo en capítulos", [VIDEO], 'video-workflow'),
    ("Add captions to my video", [VIDEO], 'video-workflow'),
    ("Make it vertical for TikTok", [VIDEO], 'video-workflow'),
    ("Pull the best moments out of this interview", [VIDEO], 'video-workflow'),
    ("Translate the subtitles into French", [VIDEO], 'video-workflow'),
    ("Add chapters for YouTube", [VIDEO], 'video-workflow'),
    ("Tighten it up, there's too much dead air", [VIDEO], 'video-workflow'),
    ("Monte ces deux clips avec des sous-titres", [VIDEO, VIDEO], 'ffmpeg-edit'),
]


def measure(cases, label):
    rows, right, honest = [], 0, 0
    for phrase, files, expected in cases:
        p = route(phrase, list(files), caps=CAPS)
        got = [e['id'] for e in p['engines']]
        known = (p.get('understanding') or {}).get('source') != 'defaut'
        ok = expected in got if expected else not known
        right += ok
        honest += ok or not known
        rows.append({'phrase': phrase, 'attendu': expected, 'obtenu': got, 'source': (p.get('understanding') or {}).get('source'), 'juste': ok, 'avoue': not known and not ok})
        print(f"{'OK ' if ok else ('?  ' if not known else 'FAUX')} {phrase[:58]:58} -> {','.join(got)} (attendu {expected})")
    print(f"\n{label} : {right} justes sur {len(cases)} ; {len(cases) - honest} fausses sans le dire\n")
    return {'phrases': len(cases), 'justes': right, 'fausses_sans_le_dire': len(cases) - honest, 'detail': rows}


def main() -> int:
    report = {'reglage': measure(CASES, 'Phrases de réglage'), 'nouvelles': measure(HOLDOUT, 'Phrases nouvelles'), 'video': measure(VIDEO_HOLDOUT, 'Vidéo fournie, phrases nouvelles')}
    out = ROOT / 'docs/preuves/phrases-naturelles.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding='utf-8')
    return 0


if __name__ == '__main__':
    sys.exit(main())
