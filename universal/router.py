"""Universal router: request + real inventory -> intents, art direction, deliverables, engines.

Look and engine are separate decisions. The soberest engine that can do the job wins:
no 3D chain for a simple cut, no paid call without an approval listed in the manifest.
"""
from __future__ import annotations
import json
import re
import unicodedata
from pathlib import Path
from .capabilities import detect

ROOT = Path(__file__).resolve().parents[1]
INTENTS = ('CREATE_FROM_SCRATCH', 'ANIMATE_LOGO', 'ANIMATE_IMAGES', 'EDIT_FOOTAGE', 'RESTYLE_FOOTAGE', 'HYBRID_COMPOSITE',
           'CHARACTER_ANIMATION', 'DATA_EXPLAINER', 'INTERACTIVE_PRESENTATION', 'REVISE_EXISTING_PROJECT', 'EXPORT_CONVERT')
FORMATS = {'16:9': (1920, 1080), '9:16': (1080, 1920), '1:1': (1080, 1080), '4:5': (1080, 1350)}
# Effects drawn around a person: only with a real video among the inputs
FACE_WORDS = ['talking.?head', 'face.?cam', 'face (a|à) (la )?camera', 'de cara a (la )?camara', 'derriere (ma|la|sa|ta) tete', 'detras de (mi|la|su|tu) cabeza', 'behind (my|the|his|her|their|your) head',
              'derriere moi', 'detras de mi', 'behind me', 'autour de (moi|ma tete)', 'alrededor de (mi|mi cabeza)', 'around (me|my head)', 'quand je parle', 'mientras hablo', 'while i (talk|speak)',
              'suivi du visage', 'suit (mon|le|son) visage', 'seguimiento (de la cara|del rostro)', 'face track', '/effects', 'effets? video', 'efectos? de video', 'video effects?']


def norm(text: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFD', text.lower()) if unicodedata.category(c) != 'Mn')


def has(text: str, words) -> bool:
    return any(re.search(r'(?<![a-z0-9])' + w, text) for w in words)


KW = {
    'INTERACTIVE_PRESENTATION': ['interacti', 'cliquable', 'cliquer', 'clickable', 'clicable', 'hacer clic', 'can click', 'navigable', 'hotspot', 'boutons?', 'botones', 'catalogue de services', 'catalogo de servicios', 'presentation html', 'deck'],
    'DATA_EXPLAINER': ['infographi', 'infografi', 'explainer', 'explicati', 'explicativ', 'donnees', 'datos', 'chiffres', 'cifras', 'statisti', 'estadisti', 'graphique', 'grafico', 'chart', 'pedagogi', 'scientifi', 'cientifi', 'tutoriel', 'tutorial'],
    'CHARACTER_ANIMATION': ['personnage', 'personaje', 'character', 'mascott?e', 'mascota', 'mascot', 'avatar', 'presentateur 3d', 'presentador 3d', 'lip.?sync', 'bonhomme', 'munequito', 'muneco', 'quelqu.un qui parle', 'alguien que hable', 'someone (who )?(talks|speaks)'],
    'RESTYLE_FOOTAGE': ['restyl', 'caricatur', 'cartooni', 'transforme.* en', 'convierte.* en', 'turn .* into', 'style anime', 'version cartoon'],
    'ANIMATE_LOGO': ['logo reveal', 'anime.* logo', 'animer .*logo', 'intro de logo', 'intro logo', 'outro', 'animar .*logo', 'revelado de logo'],
    'ANIMATE_IMAGES': ['diaporama', 'slideshow', 'photo vivante', 'photos? anime', 'anime.* photo', 'anima.* foto', 'fotos? animad', 'parallax'],
    'EDIT_FOOTAGE': ['monte ', 'monter', 'montage', 'montaje', 'monta ', 'rushes', 'best.?of', 'couper', 'cortar', 'edit my', 'cut my', 'raccourci', 'acorta', 'shorten'],
    'HYBRID_COMPOSITE': ['hybrid', 'hibrid', 'live.?action', 'vfx', 'compositing', 'incrust'],
    'REVISE_EXISTING_PROJECT': ['projet existant', 'proyecto existente', 'modifie le projet', 'corrige le', 'nouvelle version', 'existing project'],
    'EXPORT_CONVERT': ['convertis', 'convierte', 'compresse', 'comprime', 'en gif', 'to gif', 'exporte', 'exporta', 'recadre', 'recorta'],
}

GENERIC_RESTYLE = ['transforme.* en', 'convierte.* en', 'turn .* into']

# Art direction: combinable axes, then the preset that best names them
ART = [
    ('immersive-5d-inspired', ['5 ?d', 'immersi']), ('cartoon-caricature', ['caricatur', 'cartoon', 'dessin anime', 'dibujos animados']),
    ('photorealistic-commercial', ['photoreal', 'fotorreal', 'cgi produit', 'produit cgi', 'realiste', 'realista', 'realistic']),
    ('cinematic-hollywood', ['hollywood', 'blockbuster', 'cinemato', 'cinematogra', 'cinematic', 'cinematique', 'cinema', 'film noir', 'trailer', 'bande.?annonce']),
    ('hybrid-live-action-cgi', ['hybrid', 'hibrid', 'live.?action']), ('educational-3d', ['3d (pedagogi|educati|cientifi|scientifi)', 'anatomi']),
    ('stylized-3d', ['3d styl', '3d estiliz', 'stylized 3d', 'clay', 'low.?poly', 'cartoon 3d', '3d']), ('cinematic-logo-reveal', ['logo reveal', 'logo premium', 'intro de logo', 'intro logo']),
    ('animated-photo', ['photo vivante', 'photos? anime', 'fotos? animad', 'parallax', '2[.,]5 ?d']), ('documentary-premium', ['documentaire', 'documental', 'documentary', 'reportage']),
]
REALISM = [('photoreal', ['photoreal', 'fotorreal']), ('realistic', ['realiste', 'realista', 'realistic', 'hollywood', 'documentaire']),
           ('semi-realistic', ['semi.?real']), ('schematic', ['schema', 'esquema', 'infographi', 'infografi', 'diagramm'])]
DIMENSION = [('2.5d', ['2[.,]5 ?d', 'parallax']), ('3d', ['3d', 'cgi']), ('live-action', ['rushes', 'montage', 'montaje', 'interview'])]
NARRATIVE = [('ad', ['pub', 'anuncio', ' ad ', 'promo']), ('teaser', ['teaser']), ('brand-film', ['film de marque', 'pelicula de marca', 'brand film']),
             ('tutorial', ['tutoriel', 'tutorial']), ('service-demo', ['services', 'servicios']), ('event', ['evenement', 'evento', 'mariage', 'boda', 'best.?of']),
             ('documentary', ['documentaire', 'documental']), ('explainer', ['infographi', 'infografi', 'explainer', 'explicati', 'pedagogi', 'scientifi']), ('fiction', ['court.?metrage', 'cortometraje', 'fiction'])]
# The first match wins: « feed » before « instagram », which alone means vertical, and « short » before « youtube »
PLATFORMS = [('1:1', ['1:1', 'carre', 'cuadrado', 'square']), ('4:5', ['4:5', 'feed']),
             ('9:16', ['9:16', 'reel', 'tiktok', 'short', 'story', 'stories', 'vertical', 'instagram']),
             ('16:9', ['16:9', 'youtube', 'linkedin', 'horizontal', 'paysage'])]


def _language(text: str, fallback: str = 'es') -> str:
    t = f' {norm(text)} '
    score = {'fr': len(re.findall(r" (je|le|les|des|une|avec|pour|dans|mon|mes|et|du|ma|sur|fais|ajoute|ces|cette) ", t)),
             'es': len(re.findall(r" (el|los|las|una|con|para|en|mi|mis|y|del|que) ", t)),
             'en': len(re.findall(r" (the|with|for|my|and|of|an|to|from) ", t))}
    best = max(score, key=score.get)
    return best if score[best] else fallback


def detect_intents(brief: str, inputs: list[dict]) -> list[str]:
    t = f' {norm(brief)} '
    found = [i for i, words in KW.items() if has(t, words)]
    kinds = {k: [x for x in inputs if x['type'] == k and x['exists']] for k in ('image', 'video', 'audio', '3d', 'document', 'data', 'project', 'url')}
    logos = [x for x in kinds['image'] if x['role'] == 'logo']
    photos = [x for x in kinds['image'] if x['role'] != 'logo']
    if len(kinds['image']) == 1 and not logos and has(t, ['logo']):
        kinds['image'][0]['role'] = 'logo'
        logos, photos = kinds['image'], []
    # « Transforme mon podcast en extraits » changes the form, not the look: only a named look makes it a restyle
    if 'RESTYLE_FOOTAGE' in found and workflow_words(brief) and not has(t, [w for w in KW['RESTYLE_FOOTAGE'] if w not in GENERIC_RESTYLE]) and not film_style_named(brief):
        found.remove('RESTYLE_FOOTAGE')
    specific = 'RESTYLE_FOOTAGE' in found
    if kinds['project']:
        found.append('REVISE_EXISTING_PROJECT')
    if kinds['video'] and not specific and 'INTERACTIVE_PRESENTATION' not in found:
        found.append('EDIT_FOOTAGE')
        if logos or photos or kinds['3d']:
            found.append('HYBRID_COMPOSITE')
    if logos and not kinds['video'] and not photos:
        found.append('ANIMATE_LOGO')
    if photos and not kinds['video'] and not specific and 'INTERACTIVE_PRESENTATION' not in found:
        found.append('ANIMATE_IMAGES')
    if kinds['document'] or kinds['data']:
        found.append('DATA_EXPLAINER')
    if kinds['3d'] and not kinds['video']:
        found.append('CHARACTER_ANIMATION')
    if not any(x['exists'] for x in inputs) and not ({'INTERACTIVE_PRESENTATION', 'DATA_EXPLAINER'} & set(found)):
        found.append('CREATE_FROM_SCRATCH')
    return [i for i in INTENTS if i in found] or ['CREATE_FROM_SCRATCH']


def film_style_named(brief: str, explicit: str | None = None) -> dict | None:
    """A film style only when it is named: by its id with --style, or by a name in the brief."""
    t = f' {norm(brief)} '
    pool = [x for x in _load('style-catalog.json')['styles'] if x.get('source') == 'opuscar']
    if explicit:
        wanted = norm(explicit)
        for x in pool:
            if wanted in (x['opuscar'], x['id'], norm(x['nom'])):
                return x
    # The longest name that matches wins: « gravure sur bois » is not just any « gravure »
    hits = [(len(m.group(0)), x) for x in pool for a in x['alias'] for m in [re.search(r'(?<![a-z0-9])' + a, t)] if m]
    return max(hits, key=lambda h: h[0])[1] if hits else None


def effects_named(brief: str) -> bool:
    """Asked for by the kind of work or by an effect's own name, which alone can be an ordinary word."""
    t = f' {norm(brief)} '
    if has(t, FACE_WORDS):
        return True
    names = [x['id'] for x in _load('video-effects.json')['effects']]
    return any(re.search(r'(effet|efecto|effect|/effects)s? (de |d.|the )?' + re.escape(n) + r'(?![a-z0-9-])', t) for n in names) or any(has(t, [re.escape(n)]) for n in names if '-' in n)


def detect_style(brief: str, explicit: str | None = None) -> dict:
    t = f' {norm(brief)} {norm(explicit or "")} '
    preset = next((name for name, words in ART if has(t, words)), None)
    named = film_style_named(brief, explicit)
    return {'preset': preset,
            'dimension': next((d for d, w in DIMENSION if has(t, w)), '2d'),
            'realism_level': next((r for r, w in REALISM if has(t, w)), 'stylized'),
            'narrative': next((n for n, w in NARRATIVE if has(t, w)), 'unspecified'),
            'art_direction': (named['nom'] if named else None) or explicit or preset or 'à définir', 'references': [], 'negative_constraints': [], 'continuity': {},
            'film_style': named['opuscar'] if named else None}


def shape(item: dict | None) -> tuple[int, int]:
    """Width and height of a video as it is displayed: a phone clip stored sideways counts upright."""
    meta = (item or {}).get('metadata') or {}
    w, h = int(meta.get('width') or 1920), int(meta.get('height') or 1080)
    return (h, w) if abs(int(meta.get('rotation') or 0)) in (90, 270) else (w, h)


def one_video(inputs: list[dict]) -> dict | None:
    """The single video someone hands over to be worked on, as opposed to several clips or photos to be cut together."""
    videos = [x for x in inputs if x['type'] == 'video' and x['exists']]
    stills = [x for x in inputs if x['type'] == 'image' and x['exists'] and x['role'] not in ('logo', 'cover')]
    return videos[0] if len(videos) == 1 and not stills else None


def workflow_words(brief: str) -> list[str]:
    from . import workflows
    t = f' {norm(brief)} '
    return [m.ID for m in workflows.registry().values() if has(t, m.WORDS)]


def workflow_named(brief: str, inputs: list[dict]) -> list[str]:
    """Treatments of a provided video that the request names: captions, silences, reframing, clips, chapters."""
    return workflow_words(brief) if one_video(inputs) else []


def detect_deliverables(brief: str, intents: list[str], language: str, fmt: str | None = None, duration: float | None = None, source: dict | None = None) -> list[dict]:
    t = f' {norm(brief)} '
    fmt = fmt or next((f for f, w in PLATFORMS if has(t, w)), '16:9')
    m = re.search(r'(\d+(?:[.,]\d+)?) ?(s|sec|secondes?|segundos?|seconds?)(?![a-z])', t)
    m2 = re.search(r'(\d+) ?(min|minutes?|minutos?)(?![a-z])', t)
    dur = duration or (float(m.group(1).replace(',', '.')) if m else float(m2.group(1)) * 60 if m2 else None)
    w, h = FORMATS[fmt] if fmt in FORMATS else shape(source)
    out = []
    if 'INTERACTIVE_PRESENTATION' in intents:
        out.append({'kind': 'html', 'format': 'responsive', 'language': language, 'interactive': True})
    if 'INTERACTIVE_PRESENTATION' not in intents or has(t, ['film', 'mp4', 'video lineaire', 'recapitulatif', 'recapitulativ']):
        out.append({'kind': 'video', 'container': 'mp4', 'format': fmt, 'width': w, 'height': h, 'duration_s': dur, 'language': language, 'interactive': False})
    if has(t, ['gif']):
        out.append({'kind': 'gif', 'format': fmt, 'language': language})
    if has(t, ['transparen', 'alpha']):
        out.append({'kind': 'video-alpha', 'container': 'webm', 'format': fmt, 'language': language})
    return out


def _load(name: str) -> dict:
    return json.loads((ROOT / 'presets' / name).read_text(encoding='utf-8'))


def uses_film_style(intents: list[str], style: dict) -> bool:
    return bool(style.get('film_style')) and not {'RESTYLE_FOOTAGE', 'INTERACTIVE_PRESENTATION', 'REVISE_EXISTING_PROJECT', 'EXPORT_CONVERT'} & set(intents)


def select_engines(intents: list[str], style: dict, inputs: list[dict], caps: dict, effects: bool = False, steps: list | None = None) -> dict:
    """Engines with their reason, plus what is missing and the honest fallback."""
    e, missing, approvals, notes, questions = [], [], [], [], []
    used = set()

    def add(engine: str, why: str):
        if engine not in used:
            used.add(engine)
            e.append({'id': engine, 'why': why, 'available': caps['engines'].get(engine, False)})

    ok = set(intents)
    want_photoreal = style['realism_level'] in ('photoreal', 'realistic') and style['preset'] in ('photorealistic-commercial', 'cinematic-hollywood')
    models = [x for x in inputs if x['type'] == '3d' and x['exists']]
    if 'INTERACTIVE_PRESENTATION' in ok:
        add('html-deck', 'Navigation réelle au clic, au clavier et au tactile : un MP4 ne contient pas de vrais boutons.')
    if effects:
        add('video-effects', 'Effets posés autour de la personne, visage suivi et texte derrière la tête, en local.')
        notes.append('Effets : le texte et les chiffres affichés viennent du plan, aucun n\'est inventé. Ceux qui imitent Instagram, iMessage ou iPhone demandent un accord.')
        approvals.append({'what': 'Consentement des personnes filmées', 'why': 'Suivi et détourage du visage et du corps, en local.'})
        if not caps['engines'].get('video-effects'):
            notes.append('Option « effects » absente (gratuite, environ 450 Mo) : demander l\'accord, puis python -m universal.cli setup apply --approve effects')
    elif steps:
        add('video-workflow', 'Traitement de la vidéo fournie, gardée en entier : ' + ', '.join(steps) + '.')
    elif uses_film_style(intents, style):
        add('film-style', f"Film écrit en code à partir de la recette du style {style['film_style']} : modules/opuscar/styles/{style['film_style']}/STYLE.md.")
        notes.append('Style écrit en code : 30 à 60 minutes et beaucoup de tokens pour un film complet, selon la source. Le premier passage se regarde sur des images fixes.')
        if not caps['engines'].get('film-style'):
            notes.append('Option « film-styles » absente (gratuite, environ 400 Mo) : demander l\'accord, puis python -m universal.cli setup apply --approve film-styles')
    if ('EDIT_FOOTAGE' in ok or 'EXPORT_CONVERT' in ok) and not effects and not steps and not uses_film_style(intents, style):
        add('ffmpeg-edit', 'Montage et transformation de médias existants : pas besoin de moteur de génération.')
    written = uses_film_style(intents, style) or effects or bool(steps)
    if 'HYBRID_COMPOSITE' in ok and models:
        add('remotion-3d', 'Élément 3D à composer sur les rushes.')
    if 'ANIMATE_LOGO' in ok and not written:
        add('remotion-2d', 'Logo fourni animé en couches, proportions et couleurs conservées.')
    if 'ANIMATE_IMAGES' in ok and not written:
        add('remotion-2d', 'Photos mises en mouvement par plans (parallaxe 2.5D), piloté par image pour rester reproductible.')
    if 'DATA_EXPLAINER' in ok and not written:
        add('remotion-2d', 'Graphiques pilotés par les données et le temps.')
    if 'CHARACTER_ANIMATION' in ok and not written:
        add('remotion-3d', 'Vrais objets et caméra en volume, personnage et gestes pilotés par image.')
    if 'CREATE_FROM_SCRATCH' in ok and not written:
        three = style['dimension'] == '3d' or want_photoreal
        add('remotion-3d' if three else 'remotion-2d', 'Scène 3D procédurale locale.' if three else 'Motion graphics procédural local, sans média à générer.')
    if 'RESTYLE_FOOTAGE' in ok:
        add('ffmpeg-edit', "Aperçu local par filtres seulement : ce n'est pas un vrai restylage.")
        missing.append({'need': 'Service de restylage image/vidéo', 'fallback': "Aperçu par filtres FFmpeg : look posterisé, sans suivi d'identité.", 'blocking': True})
        approvals.append({'what': 'Consentement des personnes filmées et droits sur la vidéo', 'why': 'Transformation de visages ou de personnes réelles.'})
        approvals.append({'what': 'Fournisseur externe et budget', 'why': "Aucun fournisseur de restylage n'est configuré, tout appel serait payant."})
    if style['dimension'] == '3d' and any(x['type'] == 'image' and x['exists'] for x in inputs) and not models and 'ANIMATE_IMAGES' in ok:
        notes.append("Une photo ne contient pas de 3D : ce sera un effet de profondeur. Pour un objet qui tourne vraiment, il faut un modèle 3D de l'objet.")
    if want_photoreal:
        # Blender renders what it is given: installed or not, realism still needs real models, materials and sets
        need = ('Modèles, matières et décors réalistes avec leurs droits : Blender est installé, mais il ne rend que ce qu\'on lui fournit' if caps['tools'].get('blender')
                else 'Blender et assets réalistes (ou génération vidéo externe)')
        missing.append({'need': need, 'fallback': 'Scène 3D PBR éclairée en environnement : look cinématographique stylisé, pas photoréaliste.', 'blocking': False})
        notes.append("« Hollywood » se traduit ici en critères réalisables : cadrage, lumière motivée, caméra, étalonnage, son et montage. Ce n'est pas une promesse de qualité blockbuster.")
    if style['preset'] == 'immersive-5d-inspired':
        notes.append("« 5D » n'est pas un format vidéo standard. Options réelles : parallaxe 2.5D, vraie scène 3D, expérience 3D interactive, 360/VR si le matériel suit.")
        questions.append({'id': 'forme-5d', 'text': 'Pour le « 5D », quelle forme finale ?', 'options': ['Vidéo parallaxe 2.5D + son (recommandé)', 'Vraie scène 3D', 'Expérience HTML interactive'], 'default': 'Vidéo parallaxe 2.5D + son (recommandé)'})
    for m in models:
        meta = m['metadata']
        if meta.get('needs_conversion'):
            missing.append({'need': f"Conversion de {Path(m['path']).name} en GLB", 'fallback': 'Demander un GLB ou installer Blender.', 'blocking': True})
        if meta.get('vrm') and not caps['tools'].get('three_vrm'):
            missing.append({'need': '@pixiv/three-vrm pour ce modèle VRM', 'fallback': 'Lecture comme GLB simple, sans expressions VRM.', 'blocking': False})
    voices = [x for x in inputs if x['type'] == 'audio' and x['role'] == 'voice' and x['exists']]
    if voices:
        approvals.append({'what': 'Droits et consentement sur la voix fournie', 'why': 'Réutilisation de la voix dans un film.'})
    if ok == {'REVISE_EXISTING_PROJECT'}:
        notes.append("Projet existant : lire d'abord son état et ses versions, travailler sur une copie, garder la version précédente.")
    if not e and ok != {'REVISE_EXISTING_PROJECT'}:
        add('remotion-2d', 'Moteur par défaut pour un film sans média.')
    if e and not any(x['available'] for x in e):
        notes.append('Moteur absent : demander l\'accord, puis l\'installer avec python -m universal.cli setup apply --approve <élément> (voir setup plan).')
    return {'engines': e, 'missing': missing, 'approval_required': approvals, 'notes': notes, 'questions': questions[:3]}


def adapter_for(intents: list[str], style: dict, deliverable: dict, inputs: list[dict], effects: bool = False, steps: list | None = None) -> dict:
    """The concrete command `run` will execute. Every target here exists in the kit."""
    fmt = deliverable.get('format', '16:9')
    suffix = {'16:9': 'Landscape', '9:16': 'Reel', '1:1': 'Square', '4:5': 'Feed'}.get(fmt, 'Landscape')
    ok = set(intents)
    if deliverable['kind'] == 'html':
        return {'engine': 'html-deck'}
    if ok == {'REVISE_EXISTING_PROJECT'}:
        return {'engine': 'revision', 'note': 'Inspecter le projet et modifier une copie : la demande dit quoi changer.'}
    if 'RESTYLE_FOOTAGE' in ok:
        return {'engine': 'ffmpeg-edit', 'mode': 'restyle-preview'}
    if effects:
        return {'engine': 'video-effects'}
    if steps:
        return {'engine': 'video-workflow', 'steps': list(steps)}
    if uses_film_style(intents, style):
        return {'engine': 'film-style', 'style': style['film_style']}
    if 'EDIT_FOOTAGE' in ok or 'EXPORT_CONVERT' in ok:
        return {'engine': 'ffmpeg-edit', 'mode': 'edl'}
    if 'CHARACTER_ANIMATION' in ok:
        glb = any(x['type'] == '3d' and x['exists'] for x in inputs)
        return {'engine': 'remotion', 'composition': f"Personaje-GLB-{suffix}" if glb else f"Personaje-Nodo-{suffix}"}
    if 'DATA_EXPLAINER' in ok:
        return {'engine': 'remotion', 'composition': f'Explainer-{suffix}'}
    if 'ANIMATE_LOGO' in ok:
        return {'engine': 'remotion', 'composition': f'Logo-{suffix}'}
    if 'ANIMATE_IMAGES' in ok or style['preset'] == 'immersive-5d-inspired':
        return {'engine': 'remotion', 'composition': f'Parallaxe-{suffix}'}
    if style['realism_level'] in ('photoreal', 'realistic') or style['dimension'] == '3d':
        return {'engine': 'remotion', 'composition': f'Escena3D-{suffix}'}
    return {'engine': 'remotion', 'composition': 'Kinetic-Square' if fmt == '1:1' else 'Kinetic-Feed' if fmt == '4:5' else 'Kinetic-Reel' if fmt == '9:16' else f'Promo-{suffix}'}


def understanding(brief: str, inputs: list[dict], decided: bool) -> dict:
    """Where the route comes from. A guess must say so: keywords cannot understand a person, the agent can."""
    if decided:
        return {'source': 'agent', 'certain': True}
    t = f' {norm(brief)} '
    words = [i for i, w in KW.items() if has(t, w)] or (['VIDEO_EFFECTS'] if effects_named(brief) else []) or workflow_named(brief, inputs)
    style = bool(film_style_named(brief))
    if words or style:
        return {'source': 'mots', 'certain': True, 'indices': words}
    present = {x['type'] for x in inputs if x['exists']}
    if present and present != {'video'}:
        return {'source': 'fichiers', 'certain': True}
    # Footage alone says nothing about what to do with it, and with no file at all only the request can decide
    return {'source': 'defaut', 'certain': False, 'consigne': 'Rien dans la demande ne désigne un travail précis : ce choix est un défaut, et il ne sera pas exécuté tel quel. Comprends le besoin toi-même, puis relance avec --intent, --workflow, --style ou --effects, ou pose une question.'}


def route(brief: str, inputs: list[dict], *, name: str = 'projet', language: str | None = None, style: str | None = None,
          fmt: str | None = None, duration: float | None = None, intent: list[str] | None = None, caps: dict | None = None,
          force_effects: bool = False, profile: dict | None = None, workflow: list[str] | None = None) -> dict:
    caps = caps or detect()
    profile = profile or {}
    lang = language or _language(brief, profile.get('idioma_por_defecto') or 'es')
    intents = intent or detect_intents(brief, inputs)
    st = detect_style(brief, style)
    t = f' {norm(brief)} '
    single = one_video(inputs)
    if workflow and not single:
        raise ValueError('Un traitement de vidéo fournie s\'applique à une seule vidéo. Pour plusieurs clips, c\'est un montage.')
    effects = (force_effects or effects_named(brief)) and any(x['type'] == 'video' and x['exists'] for x in inputs) and 'RESTYLE_FOOTAGE' not in intents
    steps = [] if effects or 'RESTYLE_FOOTAGE' in intents else list(workflow or workflow_named(brief, inputs))
    habitual, habit = None, profile.get('formato_habitual')
    asked = bool(fmt) or any(has(t, w) for _, w in PLATFORMS)
    if not asked and single and 'RESTYLE_FOOTAGE' not in intents:
        fmt = 'source'  # a provided video keeps its own shape unless another one is asked for
    elif not asked and habit:
        fmt = habitual = habit
    deliverables = detect_deliverables(brief, intents, lang, fmt, duration, single)
    sel = select_engines(intents, st, inputs, caps, effects, steps)
    for d in deliverables:
        d['adapter'] = adapter_for(intents, st, d, inputs, effects, steps)
    seen = understanding(brief, inputs, bool(intent or style or force_effects or workflow))
    if not seen['certain']:
        sel['notes'].insert(0, seen['consigne'])
    if habitual:
        sel['notes'].append(f'Format {habitual} repris de tes dernières vidéos.')
    if fmt == 'source' and habit:
        sel['notes'].append(f'La vidéo fournie garde sa forme d\'origine. Tes dernières vidéos étaient en {habit} : proposer ce format si c\'est utile.')
    if not single and sum(1 for i in inputs if i['type'] == 'video' and i['exists']) > 1:
        later = [s for s in workflow_words(brief) if s != 'reframe']
        if later:
            sel['notes'].append(f"Demandé aussi : {', '.join(later)}. Ces traitements s'appliquent à une seule vidéo : monter d'abord les clips, puis traiter le film monté.")
    props = None
    if 'captions' in steps:
        from .workflows.captions import languages_in
        named = languages_in(norm(brief))
        if named:
            props = {'workflow': {'captions': {'languages': named}}}
    if profile.get('marca'):
        sel['notes'].append(f"Marque : {profile['marca']}, fiche perfil/marcas/{profile['marca']}.md à appliquer.")
    for rule in profile.get('reglas') or []:
        sel['notes'].append(f'Règle apprise : {rule}')
    for problem in profile.get('problemas_recurrentes') or []:
        sel['notes'].append(f'Défaut déjà vu plusieurs fois, à prévenir : {problem}')
    return {
        'schema_version': '1.0', 'name': name,
        'request': {'brief': brief, 'language': lang},
        'intent': intents, 'inputs': inputs, 'style': st, 'deliverables': deliverables, 'understanding': seen,
        'timeline': {'fps': 30, 'scenes': [], 'edl': []}, 'characters': [], 'scene_assets': [],
        'engines': sel['engines'], 'missing': sel['missing'], 'questions': sel['questions'], 'notes': sel['notes'],
        'quality': {'profile': 'draft', 'exceptions': []},
        'cost_ceiling': {'amount': 0, 'currency': 'EUR'},
        'approval_required': sel['approval_required'], 'status': 'blocked' if any(m['blocking'] for m in sel['missing']) else 'planned',
        **({'props': props} if props else {}),
    }


LABELS = {
    'fr': dict(assets='Assets détectés', intent='Intention', style='Direction artistique', engine='Pipeline', missing='Manque et repli', out='Livrable', cost='Coût', approve='À valider', tests='Tests', none='aucun', local='0, tout est local'),
    'es': dict(assets='Recursos detectados', intent='Intención', style='Dirección artística', engine='Pipeline', missing='Falta y alternativa', out='Entregable', cost='Coste', approve='Por validar', tests='Pruebas', none='ninguno', local='0, todo es local'),
    'en': dict(assets='Detected assets', intent='Intent', style='Art direction', engine='Pipeline', missing='Missing and fallback', out='Deliverable', cost='Cost', approve='To approve', tests='Tests', none='none', local='0, all local'),
}


def summary(p: dict) -> str:
    """Short card returned for every request, in the language of the request."""
    t = LABELS.get(p['request']['language'], LABELS['fr'])
    assets = ', '.join(f"{Path(x['path']).name} ({x['type']}/{x['role']})" for x in p['inputs']) or t['none']
    engines = ' + '.join(f"{e['id']}{'' if e['available'] else ' (absent)'}" for e in p['engines'])
    miss = '; '.join(f"{m['need']} -> {m['fallback']}" for m in p['missing']) or t['none']
    out = ', '.join(d['kind'] + (f" {d['format']}" if d.get('format') else '') for d in p['deliverables'])
    approve = '; '.join(a['what'] for a in p['approval_required']) or t['none']
    cost = t['local'] if not any('externe' in a['what'] or 'Fournisseur' in a['what'] for a in p['approval_required']) else 'non estimé, sans tarif documenté'
    return '\n'.join((f"{t['assets']}: {assets}", f"{t['intent']}: {', '.join(p['intent'])}", f"{t['style']}: {p['style']['art_direction']} · {p['style']['dimension']} · {p['style']['realism_level']}",
                      f"{t['engine']}: {engines}", f"{t['missing']}: {miss}", f"{t['out']}: {out}", f"{t['cost']}: {cost}", f"{t['approve']}: {approve}",
                      f"{t['tests']}: python -m universal.cli qc"))
