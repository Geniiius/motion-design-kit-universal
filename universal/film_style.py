"""Films written in code in one of the Lemo-Opuscar styles (modules/opuscar).

A style is a recipe, not a template: the agent writes the film's page and its mix from STYLE.md,
and this module renders them. Each frame is a pure function of t, so any frame can be rendered alone.
"""
from __future__ import annotations
import json
import re
import shutil
import subprocess
from pathlib import Path
from . import modules
from .render import dimensions, duration, has_audio

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / 'modules/opuscar'
WORKERS = {'draft': 2, 'review': 3, 'final': 3, '4k': 3}
TRUE_PEAK = -1.5  # AAC adds a few tenths of a dB: the delivered file must stay under -1
# The frames come from JPEG screenshots: full range, BT.601. Naming the source matrix keeps the colours where the page drew them.
TV = 'scale=in_range=pc:in_color_matrix=bt601:out_range=tv:out_color_matrix=bt709,format=yuv420p,setparams=range=tv:colorspace=bt709:color_primaries=bt709:color_trc=bt709'

PAGE = """<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><title>{name}</title>
<style>html,body{{margin:0;height:100%;background:#000;overflow:hidden}}canvas{{display:block}}</style></head>
<body><canvas id="c"></canvas>
<script type="module">
// Style: modules/opuscar/styles/{slug}/STYLE.md. Write the film here; every frame depends only on t.
import {{ seg, eo, ss }} from '/core/lib.js';
const W = innerWidth, H = innerHeight, S = Math.min(W / 1920, H / 1080);
const cv = document.getElementById('c'); cv.width = W; cv.height = H;
const g = cv.getContext('2d');
window.DUR = {seconds};
window.EV = [];   // sound cues, read by mix.py: {{t, type}}
window.TEXTS = t => [];   // every text visible at t, for the reading-time check
window.render = t => {{
  g.fillStyle = '#111'; g.fillRect(0, 0, W, H);
  g.fillStyle = '#eee'; g.font = `${{64 * S}}px sans-serif`; g.textAlign = 'center';
  g.globalAlpha = eo(seg(t, 0, 1)) * (1 - ss(seg(t, window.DUR - .6, window.DUR)));
  g.fillText('{name}', W / 2, H / 2); g.globalAlpha = 1;
}};
document.fonts.ready.then(() => {{ window.READY = true; }});
</script></body></html>
"""

MIX = """\"\"\"Score and sound effects of this film. Run: python -m universal.cli film-style py <this file>\"\"\"
import json
from pathlib import Path
import numpy as np
import soundfile as sf
from core.audio.sfx import SR, add, limit, whoosh

HERE = Path(__file__).resolve().parent
events = json.loads((HERE / 'events.json').read_text(encoding='utf-8')) if (HERE / 'events.json').exists() else {{'dur': {seconds}, 'ev': []}}
mix = np.zeros((int(events['dur'] * SR), 2), np.float32)
for e in events['ev']:
    add(mix, whoosh(.3), e['t'], .4)
(HERE / 'out').mkdir(exist_ok=True)
sf.write(HERE / 'out/mix.wav', limit(mix), SR)
"""


def styles() -> list[dict]:
    out = []
    for f in sorted((LIB / 'styles').glob('*/style.json')):
        d = json.loads(f.read_text(encoding='utf-8'))
        out.append({'id': d['slug'], 'nom': d['en'], 'categorie': d['category_en'], 'usages': d.get('uses', []), 'recette': str((f.parent / 'STYLE.md').relative_to(ROOT))})
    return out


def find(name: str) -> dict:
    wanted = re.sub(r'[^a-z0-9]+', '', name.lower())
    for s in styles():
        if wanted in (re.sub(r'[^a-z0-9]+', '', s['id']), re.sub(r'[^a-z0-9]+', '', s['nom'].lower())):
            return s
    raise ValueError(f'Style inconnu : {name}. Liste : python -m universal.cli film-style list')


def new(slug: str, film_dir: Path, *, name: str = 'Film', language: str = 'fr', seconds: float = 12) -> Path:
    """Creates the film's folder without ever overwriting a page already written."""
    style = find(slug)
    film_dir = Path(film_dir)
    if (film_dir / 'index.html').exists():
        raise FileExistsError(f'{film_dir} contient déjà un film : rien n\'a été écrasé.')
    film_dir.mkdir(parents=True, exist_ok=True)
    (film_dir / 'index.html').write_text(PAGE.format(slug=style['id'], name=name, lang=language, seconds=seconds), encoding='utf-8')
    (film_dir / 'mix.py').write_text(MIX.format(seconds=seconds), encoding='utf-8')
    (film_dir / 'CREDITS').write_text('', encoding='utf-8')
    return film_dir


def _node(script: str, args: list) -> str:
    if not (LIB / 'node_modules/playwright-core').exists():
        if not modules.may_install_alone():
            raise modules.ConsentRequired("L'option « film-styles » n'est pas installée (gratuite, environ 400 Mo, dans le dossier du kit). "
                                          "Demander l'accord de l'utilisateur en mots simples, puis : python -m universal.cli setup apply --approve film-styles")
        modules.install_film()
    r = subprocess.run(['node', f'core/render/{script}'] + [str(a) for a in args], cwd=LIB, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode:
        raise RuntimeError(f'{script} a échoué :\n{(r.stderr or r.stdout)[-1500:]}')
    return r.stdout


def _size(fmt: str, profile: str) -> str:
    w, h = dimensions(fmt, profile)
    return f'{w}x{h}'


def stills(film_dir: Path, times: list[float], *, fmt: str = '16:9', profile: str = 'review', out: Path | None = None) -> list[str]:
    film_dir = Path(film_dir).resolve()
    args = [film_dir] + times + ['--size', _size(fmt, profile)]
    if out:
        args += ['--out', Path(out).resolve()]
    return re.findall(r'^(.*?\.jpg) ', _node('still.mjs', args), re.M)


def run_py(script: Path) -> str:
    """Runs one of the film's scripts in the module environment, with core/ importable."""
    script = Path(script).resolve()
    r = modules.run_python([script], cwd=LIB, tier='audio', env={'PYTHONPATH': str(LIB)})
    if r.returncode:
        raise RuntimeError(f'{script.name} a échoué :\n{r.stderr[-1500:]}')
    return r.stdout


def _measure(mix: Path) -> dict | None:
    """First loudnorm pass. None when the mix is too quiet to measure."""
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(mix), '-af', f'loudnorm=I=-14:TP={TRUE_PEAK}:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode:
        raise RuntimeError(f'Mixage illisible : {mix}\n{r.stderr[-800:]}')
    m = re.search(r'\{[^{}]*"input_i"[^{}]*\}', r.stderr, re.S)
    if not m:
        return None
    d = json.loads(m.group(0))
    return None if any(re.search(r'inf|nan', d[k], re.I) for k in ('input_i', 'input_tp', 'input_lra', 'input_thresh', 'target_offset')) else d


def master(video: Path, mix: Path | None, out: Path, *, fps: float = 24, grain: float = 2) -> dict:
    """Muxes picture and mix with two-pass loudness at -14 LUFS, in BT.709. The picture is never cut to fit the sound."""
    video, out = Path(video).resolve(), Path(out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    picture = f"fps={fps}" + (f',noise=c0s={grain}:allf=t' if grain else '') + ',' + TV
    length = duration(video)
    tv = ['-color_range', 'tv', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709']
    enc = ['-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-r', str(fps)] + tv + ['-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-movflags', '+faststart']
    measured = _measure(Path(mix)) if mix else None
    if mix:
        level = 'anull' if measured is None else (f"loudnorm=I=-14:TP={TRUE_PEAK}:LRA=11:measured_I={measured['input_i']}:measured_TP={measured['input_tp']}:measured_LRA={measured['input_lra']}"
                                                  f":measured_thresh={measured['input_thresh']}:offset={measured['target_offset']}:linear=true")
        cmd = ['-i', str(video), '-i', str(mix), '-filter_complex', f'[0:v]{picture}[v];[1:a]{level},aresample=48000,apad=whole_dur={length}[a]', '-map', '[v]', '-map', '[a]', '-t', str(length)]
    else:
        cmd = ['-i', str(video), '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-filter_complex', f'[0:v]{picture}[v]', '-map', '[v]', '-map', '1:a', '-t', str(length)]
    r = subprocess.run(['ffmpeg', '-y', '-loglevel', 'error'] + cmd + enc + [str(out)], capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode:
        out.unlink(missing_ok=True)
        raise RuntimeError(f'Mastering échoué :\n{r.stderr[-1200:]}')
    return {'output': str(out), 'duration_s': round(duration(out), 3), 'audio': bool(mix) and measured is not None, 'audio_track': has_audio(out)}


def render(film_dir: Path, out: Path, *, fmt: str = '16:9', profile: str = 'draft', fps: float = 24, grain: float = 2) -> dict:
    film_dir, out = Path(film_dir).resolve(), Path(out).resolve()
    if not (film_dir / 'index.html').exists():
        raise FileNotFoundError(f'Pas de film dans {film_dir} : python -m universal.cli film-style new <style> {film_dir}')
    size = _size(fmt, profile)
    _node('events.mjs', [film_dir, '--size', size])
    silent = film_dir / 'out' / 'video.mp4'
    _node('video.mjs', [film_dir, '--fps', fps, '--workers', WORKERS.get(profile, 3), '--size', size, '--out', silent])
    mix = None
    if (film_dir / 'mix.py').exists():
        run_py(film_dir / 'mix.py')
        mix = film_dir / 'out' / 'mix.wav'
    result = master(silent, mix if mix and mix.exists() else None, out, fps=fps, grain=grain)
    return {**result, 'engine': 'film-style', 'size': size, 'profile': profile}


def reading_check(film_dir: Path, *, fmt: str = '16:9', profile: str = 'review') -> str:
    return _node('readcheck.mjs', [Path(film_dir).resolve(), '--size', _size(fmt, profile)])


def demo(slug: str) -> Path:
    """The style's demo source at the audited commit, to read its techniques. It stays out of the kit's package."""
    style = find(slug)['id']
    src = modules.pinned_checkout([f'styles/{style}/demo/', f'styles/{style}/DEMO.md'])
    return src / 'styles' / style


def assets3d() -> Path:
    """Poly Haven textures and models (CC0) at the audited commit, for the styles that use them."""
    src = modules.pinned_checkout(['core/assets/polyhaven/'])
    shutil.copytree(src / 'core/assets/polyhaven', LIB / 'core/assets/polyhaven', dirs_exist_ok=True)
    return LIB / 'core/assets/polyhaven'
