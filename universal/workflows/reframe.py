"""Reframes a video for another shape, for instance a landscape video for a vertical feed.

Three ways: follow the face, cut at the centre, or keep the whole picture over a blurred background.
"auto" follows the face when one is found most of the time, and otherwise keeps everything: nothing important is cut blindly.
"""
from __future__ import annotations
import json
from pathlib import Path
from .. import config, modules
from . import Track, tools

ID = 'reframe'
ORDER = 30
TITLE = {'fr': 'Recadrer pour un autre format', 'es': 'Reencuadrar para otro formato', 'en': 'Reframe for another shape'}
WORDS = ['recadr', 'reencuadr', 'reframe', 'a la verticale', 'en vertical', 'format (vertical|portrait|carre|paysage|tiktok|reels?|shorts?|instagram)',
         'formato (vertical|cuadrado|horizontal|tiktok|reels?|shorts?|instagram)', '(pour|para|for) (tiktok|instagram|reels?|shorts?|youtube shorts?)']
NEEDS = ['ffmpeg']
MODES = ('auto', 'face', 'center', 'blur')
FACES = Path(__file__).resolve().parent / '_faces.py'
MODEL = Path(__file__).resolve().parents[2] / 'modules/video-effects/models/yunet.onnx'


def probe_faces(video: Path) -> dict | None:
    """None when the effects module, which brings the face detector, is not installed. Nothing is installed from here."""
    if not (modules.VENV / '.tier-effects').exists() or not MODEL.exists():
        return None
    r = modules.run_python([FACES, video, MODEL, config.get('workflows.reframe.samples_per_s', 2)], tier='effects')
    if r.returncode:
        raise RuntimeError('Détection du visage en échec : ' + r.stderr.strip()[-400:])
    return json.loads(r.stdout.strip().splitlines()[-1])


def _smooth(points: list[tuple[float, float]], total: float) -> list[tuple[float, int]]:
    """Keys at a steady pace, each averaged with its neighbours: the frame glides, it never chases every twitch.
    A long video gets fewer keys, so that the expression FFmpeg evaluates on every frame stays light."""
    every = .5 if total <= 300 else 1.0 if total <= 1800 else 2.0
    grid, t, i = [], 0.0, 0
    while t <= total + every:
        while i + 1 < len(points) and points[i + 1][0] <= t:
            i += 1
        (t0, v0), (t1, v1) = points[i], points[min(i + 1, len(points) - 1)]
        grid.append(v0 if t <= t0 or t1 <= t0 else v1 if t >= t1 else v0 + (v1 - v0) * (t - t0) / (t1 - t0))
        t += every
    for _ in range(2):
        grid = [sum(grid[max(0, k - 2):k + 3]) / len(grid[max(0, k - 2):k + 3]) for k in range(len(grid))]
    return [(round(k * every, 2), round(v)) for k, v in enumerate(grid)]


def crop_plan(samples: list[dict], sw: int, sh: int, tw: int, th: int, total: float) -> dict:
    """The window to keep, in source pixels. Fixed when the face hardly moves, which is the steadiest picture; moving otherwise."""
    ratio = tw / th
    if ratio < sw / sh:
        cw, ch, axis = min(sw, tools.even(sh * ratio)), sh, 'x'
        room = sw - cw
        offset = lambda s: min(max(s['x'] * sw - cw / 2, 0), room)
    else:
        cw, ch, axis = sw, min(sh, tools.even(sw / ratio)), 'y'
        room = sh - ch
        offset = lambda s: min(max(s['y'] * sh - ch * .42, 0), room)  # a face sits a little above the middle
    plan = {'cw': cw, 'ch': ch, 'axis': axis, 'mode': 'fixed', 'at': round(room / 2)}
    seen = [(s['t'], offset(s)) for s in samples if 'x' in s]
    if not seen:
        return plan
    values = sorted(v for _, v in seen)
    low, high = values[int(len(values) * .05)], values[min(len(values) - 1, int(len(values) * .95))]
    if high - low <= (cw if axis == 'x' else ch) * .18:
        return {**plan, 'at': round(values[len(values) // 2])}
    return {**plan, 'mode': 'moving', 'keys': _smooth(seen, total)}


def moving_expression(keys: list[tuple[float, int]]) -> str:
    parts = [f'lt(t,{keys[0][0]})*{keys[0][1]}']
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        parts.append(f'gte(t,{t0})*lt(t,{t1})*({v0}+({v1 - v0})*(t-{t0})/{round(t1 - t0, 2)})')
    parts.append(f'gte(t,{keys[-1][0]})*{keys[-1][1]}')
    return tools.balanced_sum(parts)


def crop_filter(plan: dict) -> str:
    where = f"'{moving_expression(plan['keys'])}'" if plan['mode'] == 'moving' else str(plan['at'])
    x, y = (where, '0') if plan['axis'] == 'x' else ('0', where)
    return f"crop={plan['cw']}:{plan['ch']}:{x}:{y},setsar=1"


def run(ctx, track: Track) -> list[Track]:
    meta = tools.info(track.video)
    tw, th = ctx.frame
    sw, sh = meta['width'], meta['height']
    if abs(sw / sh - tw / th) <= .03:
        return [track]
    mode = ctx.opt(ID, 'mode', config.get('workflows.reframe.mode', 'auto'))
    if mode not in MODES:
        raise ValueError(f"Recadrage : mode « {mode} » inconnu. Possibles : {', '.join(MODES)}")
    found = None
    if mode in ('auto', 'face'):
        found = probe_faces(track.video)
        if found is None and mode == 'face':
            raise RuntimeError("Recadrage sur le visage : le module d'effets, qui apporte la détection du visage, n'est pas installé (gratuit, environ 500 Mo). "
                               'Demander l\'accord de l\'utilisateur, puis python -m universal.cli setup apply --approve effects ; ou choisir le mode « center » ou « blur ».')
        coverage = found['coverage'] if found else 0
        if mode == 'auto':
            mode = 'face' if found and coverage >= config.get('workflows.reframe.face_coverage_min', .6) else 'blur'
            if mode == 'blur':
                ctx.notes.append('Recadrage : ' + ('aucun visage suivi de façon fiable' if found else 'détection du visage non installée') + ', l\'image entière est gardée sur un fond flou.')
        elif coverage < .2:
            mode = 'center'
            ctx.notes.append(f'Recadrage : visage trouvé sur {round(coverage * 100)} % des images seulement, recadrage au centre.')
    out = ctx.temp('recadrage')
    if mode == 'blur':
        graph = (f'[0:v]split[a][b];[a]scale={tw}:{th}:force_original_aspect_ratio=increase,crop={tw}:{th},boxblur=24:2,eq=brightness=-0.08[bg];'
                 f'[b]scale={tw}:{th}:force_original_aspect_ratio=decrease[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1[v]')
    else:
        plan = crop_plan(found['samples'] if mode == 'face' and found else [], sw, sh, tw, th, meta['duration'])
        graph = f'[0:v]{crop_filter(plan)}[v]'
        zoom = max(tw / plan['cw'], th / plan['ch'])
        suivi = {'fixed': 'cadre fixe sur le visage', 'moving': 'cadre qui suit le visage'}[plan['mode']] if mode == 'face' else 'coupe au centre'
        ctx.notes.append(f'Recadrage : {suivi}' + (f", image agrandie {zoom:.1f} fois, donc moins nette qu'à l'origine." if zoom > 1.25 else '.'))
    maps = ['-map', '[v]'] + (['-map', '0:a'] if meta['audio'] else [])
    tools.ffmpeg(['-i', track.video] + tools.graph_args(graph, ctx.work, f'{out.stem}.txt') + maps + tools.INTERMEDIATE + [out], cwd=ctx.work)
    return [Track(out, track.suffix, track.files, track.expected_s, changed=True)]
