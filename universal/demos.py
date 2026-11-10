"""Demonstrators that really run. Output goes to out/demos, the small proofs to docs/preuves.

Nothing here uses a paid service, a third-party face or a third-party voice. The local voice
is the Windows one; its language is reported, not assumed.
"""
from __future__ import annotations
import json
import re
import shutil
import subprocess
from pathlib import Path
from . import effects, film_style, fixtures, manifest, present, remotion
from . import voice_elevenlabs, voice_kokoro
from .datos import _sentence_starts, build_props, facts, narration, read_series
from .inventory import inspect
from .qc import qc
from .render import edit, run
from .router import route
from .voice import amplitude_envelope, synthesize, to_srt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'out' / 'demos'
PROOFS = ROOT / 'docs' / 'preuves'
CSV = ROOT / 'examples' / 'datos' / 'co2_annmean_mlo.csv'
GLB = ROOT / 'examples' / 'modelos' / 'RobotExpressive' / 'RobotExpressive.glb'


def master(src: Path, dst: Path, lufs: float = -14.0) -> Path:
    """Audio to the delivery level with a closing fade; the picture is left as rendered."""
    d = float(run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', src]).strip())
    run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', src, '-af', f'loudnorm=I={lufs}:TP=-1.5:LRA=11,aresample=48000,afade=t=out:st={max(0, d - .4):.3f}:d=0.4',
         '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', dst])
    return dst


def _proofs(name: str, video: Path | None, report: dict, project: dict | None = None) -> dict:
    target = PROOFS / name
    target.mkdir(parents=True, exist_ok=True)
    for key, value in report.get('proofs', {}).items():
        shutil.copy(value, target / Path(value).name)
    (target / 'qc.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    if project:
        (target / 'project.json').write_text(json.dumps(project, ensure_ascii=False, indent=2), encoding='utf-8')
    return {'demo': name, 'video': str(video) if video else None, 'pass': report['pass'], 'blocking': report['blocking'], 'warnings': report['warnings'], 'proofs': str(target)}


def _cue(words: list[dict], word: str, nth: int = 1, off: float = 0.0) -> float:
    hits = [w for w in words if re.sub(r'\W', '', w['text']).lower() == word.lower()]
    return round(hits[nth - 1]['start'] + off, 3) if len(hits) >= nth else 0.0


# Generic ElevenLabs voices any account has. Paid: see `voiced`.
VOICES = {'character': 'EXAVITQu4vr4xnSDxMaL', 'narrator': 'XrExE9yKIg1WjnnlVkGX'}  # Sarah, Matilda: verified in fr and es

NODO = {
    'en': dict(text="Hello! I'm Nodo, and I was built entirely from code. Watch my mouth: it follows the real sounds of this voice. I can wave, point at what matters, and react. And in every shot, I stay the same character.",
               hello='Hello', built='built', code='code', mouth='mouth', wave='wave', point='point', matters='matters', react='react', same='same'),
    'fr': dict(text="Bonjour ! Je suis Nodo, et je suis entièrement fait de code. Regarde ma bouche : elle suit les vrais sons de cette voix. Je peux saluer, montrer ce qui compte, et réagir. Et dans chaque plan, je reste le même personnage.",
               hello='Bonjour', built='entièrement', code='code', mouth='bouche', wave='saluer', point='montrer', matters='compte', react='réagir', same='même'),
    'es': dict(text="¡Hola! Soy Nodo, y estoy hecho completamente de código. Mira mi boca: sigue los sonidos reales de esta voz. Puedo saludar, señalar lo importante y reaccionar. Y en cada plano, sigo siendo el mismo personaje.",
               hello='Hola', built='completamente', code='código', mouth='boca', wave='saludar', point='señalar', matters='importante', react='reaccionar', same='mismo'),
}


def voiced(text: str, out: Path, language: str, role: str, approved: bool, provider: str = 'auto') -> dict:
    """English: the free local voice. Other languages: ElevenLabs, only with approval (or from its cache). Kokoro when asked for."""
    if provider == 'kokoro':
        return voice_kokoro.synthesize(text, out, language)
    if language == 'en':
        return synthesize(text, out, 'en')
    return voice_elevenlabs.synthesize(text, out.with_suffix('.mp3'), language, VOICES[role], approved=approved)


def _audio_path(path: Path, language: str) -> Path:
    return path if language == 'en' else path.with_suffix('.mp3')


def demo_personnage(profile: str = 'review', fmt: str = 'Landscape', language: str = 'en', approved: bool = False, provider: str = 'auto') -> dict:
    """Reusable 3D character who speaks and gestures from timed mouth shapes."""
    suffix = '' if language == 'en' else f'-{language}'
    local = provider == 'kokoro'
    name = f"personnage{'-kokoro' if local else ''}{suffix}"
    work = OUT / name
    work.mkdir(parents=True, exist_ok=True)
    t = NODO[language]
    wav = work / 'voz.wav'
    marks = voiced(t['text'], wav, language, 'character', approved, provider)
    audio = wav if local else _audio_path(wav, language)
    (work / 'marcas.json').write_text(json.dumps(marks, ensure_ascii=False, indent=1), encoding='utf-8')
    w = marks['words']
    st = _sentence_starts(w)
    props = {
        'duracion': round(marks['duration'] + .9, 2), 'voz': remotion.publish(audio, name), 'words': w, 'visemas': marks['visemes'],
        'envolvente': amplitude_envelope(audio),
        'gestos': [{'tipo': 'saludar', 'inicio': max(.05, _cue(w, t['hello'], off=-.2)), 'fin': _cue(w, t['hello']) + 1.5, 'lado': 1},
                   {'tipo': 'asentir', 'inicio': _cue(w, t['built'], off=-.1), 'fin': _cue(w, t['code'], off=.5)},
                   {'tipo': 'senalar', 'inicio': _cue(w, t['mouth'], off=-.5), 'fin': _cue(w, t['mouth'], off=.9), 'lado': -1},
                   {'tipo': 'saludar', 'inicio': _cue(w, t['wave'], off=-.25), 'fin': _cue(w, t['wave'], off=.9), 'lado': -1},
                   {'tipo': 'senalar', 'inicio': _cue(w, t['point'], off=-.2), 'fin': _cue(w, t['matters'], off=.45), 'lado': 1},
                   {'tipo': 'reaccionar', 'inicio': _cue(w, t['react'], off=-.2), 'fin': _cue(w, t['react'], off=.95)},
                   {'tipo': 'saltar', 'inicio': _cue(w, t['same'], off=-.2), 'fin': _cue(w, t['same'], off=.75)}],
        'cortes': [st[2], st[-1]],
    }
    raw, final = work / f'{name}-brut.mp4', work / f'{name}.mp4'
    composition = f'Personaje-Nodo-{fmt}'
    project = route('Personnage 3D stylisé qui parle et gesticule', [], name=name, style='stylized-3d', language='fr', intent=['CHARACTER_ANIMATION'])
    project['characters'] = [{'id': 'nodo', 'ficha': 'template/src/universal/personajes/nodo.json', 'licence': 'créé par code pour ce kit'}]
    project['props'] = {'composition': composition, 'voice': {k: marks.get(k) for k in ('voice', 'culture', 'timing', 'duration', 'language_match', 'engine', 'visemes_source')}, 'visemes': len(marks['visemes']), 'words': len(w)}
    if language != 'en' and not local:
        project['approval_required'].append({'what': 'Voix ElevenLabs payante', 'why': f"{len(t['text'])} caractères, accordé pour cette démo"})
    manifest.validate(project)
    remotion.render(project, composition, raw, profile, props=props)
    master(raw, final)
    srt = to_srt(w, work / f'{name}.srt')
    report = qc(final, work / 'preuves', subtitles=srt)
    return _proofs(name, final, report, project)


def demo_explainer(profile: str = 'review', fmt: str = 'Landscape', language: str = 'en', approved: bool = False) -> dict:
    """Infographic film from a sourced public dataset: every figure is computed from the file."""
    suffix = '' if language == 'en' else f'-{language}'
    name = f'explainer{suffix}'
    work = OUT / name
    work.mkdir(parents=True, exist_ok=True)
    series = read_series(CSV)
    f = facts(series)
    wav = work / 'voz.wav'
    marks = voiced(narration(f, language), wav, language, 'narrator', approved)
    audio = _audio_path(wav, language)
    props = build_props(series, CSV, marks, language, remotion.publish(audio, name))
    (work / 'props.json').write_text(json.dumps(props, ensure_ascii=False, indent=1), encoding='utf-8')
    raw, final = work / f'{name}-brut.mp4', work / f'{name}.mp4'
    project = route('Infographie scientifique à partir de données sourcées', [inspect({'path': str(CSV), 'rights': {'status': 'licensed', 'note': 'NOAA GML, usage libre, citation demandée'}, 'source': props['_provenance']['url']})],
                    name=name, language='fr', style='scientific-explainer')
    project['props'] = {'provenance': props['_provenance']}
    project['quality']['exceptions'] = [{'type': 'freeze', 'from': 0, 'to': 1e9, 'reason': 'Lecture de graphiques : tenues voulues pour un film pédagogique calme.'}]
    remotion.render(project, f'Explainer-{fmt}', raw, profile, props=props)
    master(raw, final)
    srt = to_srt(marks['words'], work / f'{name}.srt')
    report = qc(final, work / 'preuves', subtitles=srt, exceptions=project['quality']['exceptions'])
    result = _proofs(name, final, report, project)
    if language == 'en':
        # Same data, other languages on screen, without a voice: proof that the language is a setting
        for lang, frame in (('es', 500), ('fr', 500)):
            still = PROOFS / 'explainer' / f'ecran-{lang}.png'
            localized = build_props(series, CSV, marks, lang, '')
            localized['words'] = []
            remotion.render(project, f'Explainer-{fmt}', still, 'draft', still_frame=frame, props=localized)
    return result


def demo_montage(profile: str = 'review') -> dict:
    """Editing supplied media: three unlike clips, stills, logo, voice over ducked music."""
    made = fixtures.build()
    work = OUT / 'montage'
    work.mkdir(parents=True, exist_ok=True)
    text = 'Three different clips, two photographs and one logo. Cut together locally, with this voice above the music.'
    wav = work / 'voz.wav'
    marks = synthesize(text, wav, 'en')
    clips, photos = made['clips'], made['fotos']
    edl = [{'src': str(clips[0]), 'in': .5, 'seconds': 2.4}, {'src': str(photos[0]), 'seconds': 2, 'transition': 'fade'}, {'src': str(clips[1]), 'in': 1, 'seconds': 2.2, 'transition': 'cut'},
           {'src': str(clips[2]), 'in': .4, 'seconds': 2, 'transition': 'fade'}, {'src': str(photos[1]), 'seconds': 2.2, 'transition': 'fade'}]
    inputs = [inspect({'path': str(p), 'rights': {'status': 'generated-locally'}}) for p in [*clips, *photos[:2], made['logo'], made['musica'], wav]]
    project = route('Monte ces clips avec le logo et la voix', inputs, name='montage', language='fr')
    project['timeline']['edl'] = edl
    final, srt = work / 'montage.mp4', to_srt(marks['words'], work / 'montage.srt')
    edit(edl, ROOT, final, profile=profile, logo=made['logo'], voice=wav, music=made['musica'], subtitles=srt)
    report = qc(final, work / 'preuves', subtitles=srt)
    return _proofs('montage', final, report, project)


SERVICES = ROOT / 'examples' / 'universal' / 'services.json'


def demo_presentation(profile: str = 'review') -> dict:
    """Two separate outputs: a deck with real buttons, and a linear recap film without them."""
    work = OUT / 'presentation'
    work.mkdir(parents=True, exist_ok=True)
    spec = json.loads(SERVICES.read_text(encoding='utf-8'))
    deck = work / 'services.html'
    present.presentation(spec, deck)
    tests = subprocess.run(['node', str(ROOT / 'tests' / 'deck.spec.mjs'), str(deck), str(PROOFS / 'presentation')], capture_output=True, text=True, encoding='utf-8', errors='replace')
    film = work / 'services-film.mp4'
    subprocess.run(['node', 'render.mjs', str(deck), '--out', str(film)], cwd=ROOT / 'prompt-motion', capture_output=True, check=True)
    report = qc(film, work / 'preuves', exceptions=[{'type': 'no-audio'}], audio_target=None)
    result = _proofs('presentation', film, report)
    result['deck'] = str(deck)
    result['interaction_tests_exit'] = tests.returncode
    result['interaction_tests'] = tests.stdout[-1800:] + tests.stderr[-400:]
    if tests.returncode:
        result['pass'] = False
    return result


def demo_glb(profile: str = 'review') -> dict:
    """Imported licensed model: real skeleton clips and morphs; no mouth shapes, so a head fallback."""
    work = OUT / 'modele-glb'
    work.mkdir(parents=True, exist_ok=True)
    text = "This model came from a file. It has a skeleton and animations, but no mouth shapes, so its head moves with the voice instead."
    wav = work / 'voz.wav'
    marks = synthesize(text, wav, 'en')
    d = round(marks['duration'] + .8, 2)
    props = {'modelo': remotion.publish(GLB, 'modele-glb'), 'duracion': d, 'voz': remotion.publish(wav, 'modele-glb'), 'words': marks['words'], 'envolvente': amplitude_envelope(wav), 'escala': .5, 'altura': -1.26,
             'clips': [{'nombre': 'Walking', 'inicio': 0, 'fin': d * .25}, {'nombre': 'Wave', 'inicio': d * .25, 'fin': d * .55, 'expresion': 'Surprised'}, {'nombre': 'Yes', 'inicio': d * .55, 'fin': d * .8}, {'nombre': 'ThumbsUp', 'inicio': d * .8, 'fin': d}]}
    model = inspect({'path': str(GLB), 'rights': {'status': 'cc0', 'note': 'Tomás Laulhé (Quaternius), modifications Don McCurdy, CC0 1.0, via three.js r180'}, 'source': 'three.js r180'})
    project = route('Personnage importé en GLB, sans bouche animable', [model], name='modele-glb', language='fr')
    raw, final = work / 'glb-brut.mp4', work / 'modele-glb.mp4'
    remotion.render(project, 'Personaje-GLB-Landscape', raw, profile, props=props)
    master(raw, final)
    report = qc(final, work / 'preuves')
    return _proofs('modele-glb', final, report, project)


def demo_cinema(profile: str = 'review') -> dict:
    project = route('Scène cinématographique réaliste façon Hollywood', [], name='cinema', language='fr')
    final = OUT / 'cinema' / 'cinema.mp4'
    remotion.render(project, 'Escena3D-Landscape', final, profile, props={'titulo': 'Une scène en volume', 'subtitulo': 'Lumière, caméra et étalonnage. Pas de photoréalisme.', 'cinemascope': True})
    exceptions = [{'type': 'no-audio', 'reason': 'Démonstrateur image'}, {'type': 'black', 'from': 0, 'to': 1e9, 'reason': 'Scène volontairement sombre et bandes cinéma'}]
    report = qc(final, OUT / 'cinema' / 'preuves', exceptions=exceptions, audio_target=None)
    return _proofs('cinema', final, report, project)


def demo_hybride(profile: str = 'review') -> dict:
    made = fixtures.build()
    project = route('Film hybride : rushes et personnage 3D', [inspect({'path': str(made['clips'][0]), 'rights': {'status': 'generated-locally'}})], name='hybride', language='fr', style='hybrid-live-action-cgi')
    final = OUT / 'hybride' / 'hybride.mp4'
    remotion.render(project, 'Hibrido-Landscape', final, profile, props={'clip': remotion.publish(made['clips'][0], 'hybride'), 'titulo': 'Rushes et 3D', 'subtitulo': 'Vidéo filmée, personnage calculé'})
    report = qc(final, OUT / 'hybride' / 'preuves', exceptions=[{'type': 'no-audio', 'reason': 'Démonstrateur image'}], audio_target=None)
    return _proofs('hybride', final, report, project)


def demo_film_style(profile: str = 'review') -> dict:
    """A film written in code from the Risograph recipe, with a score synthesized locally."""
    work = OUT / 'riso'
    work.mkdir(parents=True, exist_ok=True)
    project = route('Film promo de 14 secondes en risographie pour une boulangerie fictive', [], name='riso', language='fr')
    project['quality']['exceptions'] = [{'type': 'freeze', 'from': 11.5, 'to': 14, 'reason': 'Titre tenu jusqu\'à la coupe finale, seule la vapeur bouge.'}]
    final = work / 'du-pain-chaud.mp4'
    result = film_style.render(ROOT / 'examples/film-style/riso-pain', final, profile=profile, grain=0)
    reading = film_style.reading_check(ROOT / 'examples/film-style/riso-pain', profile=profile)
    report = qc(final, work / 'preuves', exceptions=project['quality']['exceptions'])
    out = _proofs('film-style', final, report, project)
    (PROOFS / 'film-style' / 'lecture.txt').write_text(reading, encoding='utf-8')
    return {**out, 'size': result['size'], 'style': 'risograph'}


def demo_effects(profile: str = 'review') -> dict:
    """Effects on a synthetic clip with nobody in it: the pipeline runs, face tracking is not proven here."""
    made = fixtures.build()
    work = OUT / 'effets-demo'
    work.mkdir(parents=True, exist_ok=True)
    plan = [{'fx': 'backdrop-word', 'start': .2, 'end': 2.2, 'text': 'ÉTÉ'}, {'fx': 'spotlight', 'start': 2.4, 'end': 4.6, 'text': 'Niño'}]
    final = work / 'effets.mp4'
    project = route('Ajoute un effet backdrop-word et un effet spotlight sur cette vidéo', [inspect({'path': str(made['clips'][0]), 'rights': {'status': 'generated-locally'}})], name='effets', language='fr')
    project['props'] = {'effects': plan}
    result = effects.render(made['clips'][0], plan, final, profile=profile)
    report = qc(final, work / 'preuves', audio_target=None)
    out = _proofs('effects-demo', final, report, project)
    return {**out, 'tracking': result['tracking'], 'warnings': out['warnings'] + result['warnings']}


def _kokoro(language):
    return lambda profile='review': demo_personnage(profile, language=language, provider='kokoro')


def _paid(fn, language):
    return lambda profile='review', approved=False: fn(profile, 'Landscape', language, approved)


# Need approved=True the first time (ElevenLabs), then read from out/cache-voix at no cost
PAID = {'personnage-fr': _paid(demo_personnage, 'fr'), 'personnage-es': _paid(demo_personnage, 'es'), 'explainer-fr': _paid(demo_explainer, 'fr'), 'explainer-es': _paid(demo_explainer, 'es')}
ALL = {'personnage': demo_personnage, 'explainer': demo_explainer, 'montage': demo_montage, 'presentation': demo_presentation, 'glb': demo_glb, 'cinema': demo_cinema, 'hybride': demo_hybride, 'film-style': demo_film_style, 'effets': demo_effects, 'personnage-kokoro-fr': _kokoro('fr'), 'personnage-kokoro-es': _kokoro('es')}
