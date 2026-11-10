"""Chapters of a long video, as the text a video platform reads in a description. The video itself is not changed.

First run: the transcript is written and the run stops. The agent reads it and writes the chapters in
props.workflow.chapters = [{"t": 0, "title": "Introduction"}, ...]. Second run: the list is checked and written.
"""
from __future__ import annotations
from . import NeedsInput, Track, tools, transcript

ID = 'chapters'
ORDER = 50
TITLE = {'fr': 'Chapitres', 'es': 'Capítulos', 'en': 'Chapters'}
WORDS = ['chapitr', 'capitulos?', 'chapters?']
NEEDS = ['ffmpeg']
MIN_GAP_S = 10


def check(chapters, total: float) -> list[str]:
    if not isinstance(chapters, list) or len(chapters) < 3:
        return ['il faut au moins 3 chapitres, chacun avec "t" en secondes et "title"']
    problems, last = [], None
    for i, c in enumerate(chapters, 1):
        try:
            t, title = float(c['t']), str(c['title']).strip()
        except (KeyError, TypeError, ValueError):
            problems.append(f'chapitre {i} : "t" et "title" sont obligatoires')
            continue
        if not title:
            problems.append(f'chapitre {i} : titre vide')
        if i == 1 and t != 0:
            problems.append('le premier chapitre doit commencer à 0')
        if last is not None and t - last < MIN_GAP_S:
            problems.append(f'chapitre {i} : moins de {MIN_GAP_S} s après le précédent')
        if t >= total:
            problems.append(f'chapitre {i} : après la fin de la vidéo')
        last = t
    return problems


def text(chapters: list[dict]) -> str:
    return '\n'.join(f"{transcript.stamp(float(c['t']), tenths=False)} {str(c['title']).strip()}" for c in chapters) + '\n'


def run(ctx, track: Track) -> list[Track]:
    meta = tools.info(track.video)
    chapters = ctx.options.get(ID)
    if not chapters:
        if not meta['audio'] or transcript.missing():
            raise RuntimeError(transcript.missing() or 'Chapitres : cette vidéo n\'a pas de son. Indique les chapitres toi-même dans props.workflow.chapters.')
        words = transcript.words_of(track.video, ctx.out_dir / f'{ctx.name}{track.suffix}.mots.json', ctx.opt('captions', 'spoken'))['words']
        script = transcript.write_text(words, ctx.out_dir / f'{ctx.name}{track.suffix}.transcription.txt', f"Durée : {meta['duration']:.1f} s. Les temps sont en secondes.")
        raise NeedsInput(f'Chapitres : la transcription est dans {script}. Lis-la, repère où le sujet change, puis écris props.workflow.chapters, '
                         'par exemple [{"t": 0, "title": "Introduction"}, {"t": 95, "title": "..."}], et relance.', script)
    problems = check(chapters, meta['duration'])
    if problems:
        raise ValueError('Chapitres : ' + ' ; '.join(problems))
    out = ctx.out_dir / f'{ctx.name}{track.suffix}.chapitres.txt'
    out.write_text(text(chapters), encoding='utf-8')
    ctx.notes.append(f'Chapitres : {len(chapters)} écrits dans {out.name}, à coller dans la description de la vidéo.')
    return [Track(track.video, track.suffix, track.files + [out], track.expected_s, track.changed)]
