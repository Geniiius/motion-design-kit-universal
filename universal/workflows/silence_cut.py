"""Removes the silences of a talking video. Each cut keeps a short breath on both sides, so speech never sounds clipped."""
from __future__ import annotations
import re
import subprocess
from pathlib import Path
from .. import config
from . import Track, tools

ID = 'silence-cut'
ORDER = 10
TITLE = {'fr': 'Supprimer les silences', 'es': 'Quitar los silencios', 'en': 'Remove the silences'}
WORDS = ['silences?', 'blancs', 'temps morts', 'silencios?', 'tiempos muertos', 'dead air', 'pauses?', 'pausas?']
NEEDS = ['ffmpeg']


def loudness(src: Path) -> float | None:
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(src), '-vn', '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True, encoding='utf-8', errors='replace')
    tail = r.stderr[r.stderr.rfind('Summary:'):] if 'Summary:' in r.stderr else ''
    m = re.search(r'I:\s+(-?[\d.]+) LUFS', tail)
    return float(m.group(1)) if m else None


def detect(src: Path, threshold_db: float, min_silence: float, total: float) -> list[tuple[float, float]]:
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(src), '-vn', '-af', f'silencedetect=n={threshold_db}dB:d={min_silence}', '-f', 'null', '-'],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    starts = [float(x) for x in re.findall(r'silence_start: (-?[\d.]+)', r.stderr)]
    ends = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', r.stderr)]
    ends += [total] * (len(starts) - len(ends))  # a silence still open at the end of the file
    return [(max(0.0, a), min(total, b)) for a, b in zip(starts, ends) if b > a]


def keep_segments(silences: list[tuple[float, float]], total: float, padding: float, min_keep: float) -> list[tuple[float, float]]:
    """What stays. Only the inside of each silence goes: `padding` seconds of it remain before and after the words."""
    cuts = []
    for a, b in silences:
        a2 = 0.0 if a <= .01 else a + padding
        b2 = total if b >= total - .01 else b - padding
        if b2 - a2 > .05:
            cuts.append((a2, b2))
    kept, at = [], 0.0
    for a, b in cuts:
        if a - at >= min_keep:
            kept.append((round(at, 3), round(a, 3)))
        at = b
    if total - at >= min_keep:
        kept.append((round(at, 3), round(total, 3)))
    return kept


def expression(segments: list[tuple[float, float]]) -> str:
    return tools.balanced_sum([f'between(t,{a},{b})' for a, b in segments])


def removed_before(kept: list[tuple[float, float]]) -> str:
    """How much has been cut before the instant T, as an FFmpeg expression: one step per cut.
    Picture and sound are both moved by this same amount, so they stay together whatever the number of cuts.
    Counting frames instead (N/FRAME_RATE) rounds every cut to a whole frame: a hundred cuts drifted by seconds."""
    steps, at = [], 0.0
    for a, b in kept:
        if a > at:
            steps.append(f'{round(a - at, 3)}*gte(T,{a})')
        at = b
    return tools.balanced_sum(steps) or '0'


def run(ctx, track: Track) -> list[Track]:
    meta = tools.info(track.video)
    if not meta['audio']:
        raise ValueError('Supprimer les silences : cette vidéo n\'a pas de son, il n\'y a rien à détecter.')
    cfg = config.get('workflows.silence')
    level = loudness(track.video)
    threshold = ctx.opt(ID, 'threshold_db')
    if threshold is None:
        threshold = max(-55.0, min(-28.0, level - cfg['db_below_loudness'])) if level is not None else -35.0
    total = meta['duration']
    silences = detect(track.video, threshold, ctx.opt(ID, 'min_silence_s', cfg['min_silence_s']), total)
    kept = keep_segments(silences, total, ctx.opt(ID, 'padding_s', cfg['padding_s']), cfg['min_keep_s'])
    left = sum(b - a for a, b in kept)
    removed = total - left
    if removed < .3 or not kept:
        ctx.notes.append('Silences : aucun silence notable trouvé, la vidéo reste telle quelle.')
        return [track]
    if left < total * .2:
        ctx.notes.append(f'Silences : il ne resterait que {left:.1f} s sur {total:.1f} s. Le seuil est peut-être trop sévère pour ce son : vérifier le résultat.')
    expr, shift = expression(kept), removed_before(kept)
    # Each stream keeps its own timestamps, moved back by what was cut before them. The picture is then put back on a steady
    # frame rate, and the sound is trimmed or filled by a few milliseconds where two pieces meet, always inside a silence.
    # The end of the stream keeps its own timestamp, after the last silence: without the ceiling, the last picture would be
    # repeated to fill a trailing silence that was just removed.
    ceiling = round(left + 1.5 / meta['fps'], 3)
    graph = (f"[0:v]select='{expr}',setpts='min(T-({shift}),{ceiling})/TB',fps={meta['fps']}[v];"
             f"[0:a]aselect='{expr}',asetpts='(T-({shift}))/TB',aresample=async=1:min_hard_comp=0.01:first_pts=0[a]")
    out = ctx.temp('silences')
    tools.ffmpeg(['-i', track.video] + tools.graph_args(graph, ctx.work, f'{out.stem}.txt') + ['-map', '[v]', '-map', '[a]'] + tools.INTERMEDIATE + [out], cwd=ctx.work)
    cuts = len(kept) - 1 + (kept[0][0] > .01) + (kept[-1][1] < total - .01)
    ctx.notes.append(f'Silences : {cuts} coupes, {removed:.1f} s retirées sur {total:.1f} s.')
    return [Track(out, track.suffix, track.files, expected_s=left, changed=True)]
