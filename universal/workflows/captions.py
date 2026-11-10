"""Captions burned into the picture, or delivered as files, in the spoken language and in translations.

The kit transcribes offline. A transcription mishears names and words that sound alike, so the text is never burned unread:
the first run writes the caption file and stops, the agent corrects the text, then the second run burns it.
Translations are written by the agent from the corrected file, with the same numbers and times: no outside service.
"""
from __future__ import annotations
import re
import shutil
from pathlib import Path
from .. import config
from ..qc import check_srt
from ..voice import to_srt
from . import NeedsInput, Track, tools, transcript

ID = 'captions'
ORDER = 40
TITLE = {'fr': 'Sous-titres et traductions', 'es': 'Subtítulos y traducciones', 'en': 'Captions and translations'}
WORDS = ['sous.?titr', 'subtitul', 'subtitles?', 'captions?', 'traduis', 'traduc', 'traduce', 'translat']
NEEDS = ['ffmpeg', 'transcription-locale']
LANGUAGES = {'fr': ['francais', 'frances', 'french'], 'es': ['espagnol', 'espanol', 'castellano', 'spanish'], 'en': ['anglais', 'ingles', 'english'],
             'de': ['allemand', 'aleman', 'german'], 'it': ['italien', 'italiano', 'italian'], 'pt': ['portugais', 'portugues', 'portuguese'],
             'nl': ['neerlandais', 'holandes', 'dutch'], 'ar': ['arabe', 'arabic'], 'zh': ['chinois', 'chino', 'chinese'], 'ja': ['japonais', 'japones', 'japanese']}


def languages_in(text: str) -> list[str]:
    """Languages named in a request already lowered and stripped of accents, in the order they are named."""
    hits = [(m.start(), code) for code, names in LANGUAGES.items() for name in names for m in [re.search(r'(?<![a-z])' + name + r'(?![a-z])', text)] if m]
    return list(dict.fromkeys(code for _, code in sorted(hits)))


def cues(path: Path) -> list[tuple[float, float, str]]:
    to_s = lambda h, m, s, ms: int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
    out = []
    for block in re.split(r'\n\s*\n', Path(path).read_text(encoding='utf-8-sig', errors='replace').replace('\r', '').strip()):
        m = re.search(r'(\d+):(\d+):(\d+)[,.](\d+) --> (\d+):(\d+):(\d+)[,.](\d+)\n?(.*)', block, re.S)
        if m:
            out.append((to_s(*m.groups()[:4]), to_s(*m.groups()[4:8]), m.group(9).strip()))
    return out


def compare(source: Path, translated: Path) -> list[str]:
    """A translation keeps the numbers and the times of the corrected file: only the text changes."""
    if not translated.exists():
        return [f'le fichier {translated.name} manque']
    a, b = cues(source), cues(translated)
    if len(a) != len(b):
        return [f'{len(b)} sous-titres au lieu de {len(a)}']
    problems = [f'sous-titre {i} : horaires différents du fichier d\'origine' for i, (x, y) in enumerate(zip(a, b), 1) if abs(x[0] - y[0]) > .06 or abs(x[1] - y[1]) > .06]
    problems += [f'sous-titre {i} : texte vide' for i, y in enumerate(b, 1) if not y[2]]
    return problems[:6]


def burn(ctx, video: Path, srt: Path, tall: bool) -> Path:
    local = ctx.work / f'st{ctx.counter + 1}.srt'  # a plain name beside the command: Windows paths and filter escaping do not mix
    shutil.copy(srt, local)
    # Sizes are in 288ths of the height. On a vertical feed the lowest quarter is covered by the platform's own texts and buttons: captions sit above it.
    style = f"FontName=Arial,FontSize={13 if tall else 15},Outline=1,Shadow=0,MarginV={70 if tall else 14},Bold=1"
    out = ctx.temp('sous-titres')
    tools.ffmpeg(['-i', video, '-vf', f"subtitles={local.name}:force_style='{style}'"] + tools.INTERMEDIATE + [out], cwd=ctx.work)
    return out


def run(ctx, track: Track) -> list[Track]:
    meta = tools.info(track.video)
    if not meta['audio']:
        raise ValueError('Sous-titres : cette vidéo n\'a pas de son à transcrire.')
    name = ctx.name + track.suffix
    opts = ctx.options.get(ID) or {}
    data = transcript.words_of(track.video, ctx.out_dir / f'{name}.mots.json', opts.get('spoken'))
    spoken = opts.get('spoken') or data.get('language') or ctx.deliverable.get('language', 'fr')
    tall = ctx.frame[1] > ctx.frame[0]
    source = ctx.out_dir / f'{name}.{spoken}.srt'
    if data['fresh'] or not source.exists():
        to_srt(data['words'], source, config.get('workflows.captions.max_chars_tall' if tall else 'workflows.captions.max_chars_wide'))
        raise NeedsInput(f'Sous-titres : le texte transcrit est dans {source}. La transcription se trompe sur les noms propres et les mots qui se ressemblent : '
                         'relis-le et corrige le texte sans toucher aux numéros ni aux horaires. Puis mets props.workflow.captions.reviewed à true et relance.',
                         source, reset=(ID, 'reviewed'))
    if not opts.get('reviewed'):
        raise NeedsInput(f'Sous-titres : {source} attend ta relecture. Corrige le texte, puis mets props.workflow.captions.reviewed à true et relance.', source)
    wanted = list(dict.fromkeys(opts.get('languages') or [spoken]))
    files, out = [], []
    for lang in wanted:
        srt = source if lang == spoken else ctx.out_dir / f'{name}.{lang}.srt'
        # a last caption may stay up to a second after the last word so that it can be read
        problems = (compare(source, srt) if lang != spoken else []) or check_srt(srt, meta['duration'] + 1.1)
        if lang == spoken:
            # Word-for-word captions cannot be slower than the person speaks: a fast passage is told, it does not block.
            # A translation is the agent's own text: that one can and must be shortened.
            fast = [p for p in problems if p.startswith('lecture trop rapide')]
            problems = [p for p in problems if p not in fast]
            if fast:
                ctx.notes.append(f"Sous-titres : {len(fast)} passage(s) se lisent vite parce que la personne parle vite. Condenser le texte de {srt.name} si la lecture gêne.")
        if problems:
            todo = (f'Traduction « {lang} » : écris {srt} à partir de {source}, avec les mêmes numéros et les mêmes horaires, seul le texte change.' if not srt.exists()
                    else f'Sous-titres « {lang} » à corriger dans {srt} : ' + ' ; '.join(problems) + '. Raccourcis le texte quand il se lit trop vite.')
            raise NeedsInput(todo, srt)
        files.append(srt)
        if opts.get('mode', 'burn') == 'burn':
            out.append(Track(burn(ctx, track.video, srt, tall), track.suffix + (f'-{lang}' if len(wanted) > 1 else ''), track.files + [srt], track.expected_s, changed=True))
    ctx.notes.append(f"Sous-titres : {', '.join(wanted)}" + (', incrustés dans l\'image.' if out else ', livrés en fichiers à côté de la vidéo.'))
    return out or [Track(track.video, track.suffix, track.files + files, track.expected_s, track.changed)]
