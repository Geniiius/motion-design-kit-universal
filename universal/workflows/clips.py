"""Short clips out of a long video. The kit transcribes and cuts cleanly; which moments are worth keeping is a reader's choice.

First run: the transcript is written and the run stops. The agent reads it, picks the moments and writes them in
props.workflow.clips = [{"in": 12.4, "out": 41.0, "title": "..."}]. Second run: each clip is cut on word boundaries.
"""
from __future__ import annotations
import bisect
from . import NeedsInput, Track, tools, transcript
from .. import config

ID = 'clips'
ORDER = 20
TITLE = {'fr': 'Extraits courts', 'es': 'Extractos cortos', 'en': 'Short clips'}
WORDS = ['extraits?', 'moments forts', 'meilleurs moments', 'extractos?', 'recortes', 'mejores momentos', 'clips? cortos?', 'clips? courts?', 'short clips?', 'highlights?', 'best moments']
NEEDS = ['ffmpeg']


def snap(start: float, end: float, words: list[dict], total: float) -> tuple[float, float]:
    """Moves a cut to the nearest word boundary within reach, with a breath around it: a clip never starts or ends inside a word."""
    if words:
        starts, ends = [w['start'] for w in words], [w['end'] for w in words]
        i = bisect.bisect_left(starts, start)
        near = min((starts[k] for k in (i - 1, i) if 0 <= k < len(starts)), key=lambda t: abs(t - start))
        if abs(near - start) <= .6:
            start = near
        j = bisect.bisect_left(ends, end)
        near = min((ends[k] for k in (j - 1, j) if 0 <= k < len(ends)), key=lambda t: abs(t - end))
        if abs(near - end) <= .6:
            end = near
    return round(max(0.0, start - .12), 3), round(min(total, end + .3), 3)


def check(selection, total: float) -> list[str]:
    cfg = config.get('workflows.clips')
    problems = []
    if not isinstance(selection, list) or not selection:
        return ['props.workflow.clips doit être une liste de moments {"in", "out"}.']
    for i, c in enumerate(selection, 1):
        try:
            a, b = float(c['in']), float(c['out'])
        except (KeyError, TypeError, ValueError):
            problems.append(f'extrait {i} : "in" et "out" en secondes sont obligatoires')
            continue
        if not 0 <= a < b <= total + .5:
            problems.append(f'extrait {i} : {a} -> {b} sort de la vidéo ({total:.1f} s)')
        elif b - a < cfg['min_s']:
            problems.append(f"extrait {i} : {b - a:.1f} s, moins que le minimum de {cfg['min_s']} s")
    return problems


def run(ctx, track: Track) -> list[Track]:
    meta = tools.info(track.video)
    selection = ctx.options.get(ID)
    # With times given by hand the cut still works without transcription, only less cleanly: no word boundary to land on
    heard = meta['audio'] and transcript.missing() is None
    words = transcript.words_of(track.video, ctx.out_dir / f'{ctx.name}.mots.json', ctx.opt('captions', 'spoken'))['words'] if heard else []
    if not selection:
        if not heard:
            raise RuntimeError(transcript.missing() or 'Extraits : cette vidéo n\'a pas de son. Indique les moments en secondes dans props.workflow.clips.')
        if not words:
            raise NeedsInput("Extraits : aucune parole reconnue dans cette vidéo, il n'y a pas de texte pour choisir. Regarde la vidéo ou demande les moments à l'utilisateur, "
                             'puis écris-les en secondes dans props.workflow.clips, par exemple [{"in": 12.4, "out": 41.0}], et relance.')
        text = transcript.write_text(words, ctx.out_dir / f'{ctx.name}.transcription.txt', f"Durée : {meta['duration']:.1f} s. Les temps sont en secondes.")
        raise NeedsInput(f"Extraits : la transcription est dans {text}. Lis-la, choisis les moments qui tiennent debout seuls (une idée complète, une accroche au début), "
                         'puis écris-les dans props.workflow.clips, par exemple [{"in": 12.4, "out": 41.0, "title": "..."}], et relance.', text)
    problems = check(selection, meta['duration'])
    if problems:
        raise ValueError('Extraits : ' + ' ; '.join(problems))
    out = []
    for i, c in enumerate(selection, 1):
        a, b = snap(float(c['in']), float(c['out']), words, meta['duration'])
        dst = ctx.temp(f'extrait-{i}')
        # The sound comes in and goes out over a breath: a clip cut out of a longer take must not click or stop dead
        sound = ['-af', f'afade=t=in:st=0:d=0.03,afade=t=out:st={max(0, b - a - .15):.3f}:d=0.15'] if meta['audio'] else []
        tools.ffmpeg(['-ss', a, '-t', round(b - a, 3), '-i', track.video] + sound + tools.INTERMEDIATE + [dst], cwd=ctx.work)
        out.append(Track(dst, f'{track.suffix}-{i}', list(track.files), expected_s=b - a, changed=True))
    advise = config.get('workflows.clips.advise_max_s')
    long = [i for i, t in enumerate(out, 1) if t.expected_s > advise]
    if long:
        ctx.notes.append(f"Extraits {', '.join(map(str, long))} : plus de {advise} s. Vérifier la durée acceptée par la plateforme visée.")
    ctx.notes.append(f'Extraits : {len(out)} coupés sur des fins de mots.')
    return out
