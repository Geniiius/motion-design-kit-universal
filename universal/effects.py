"""Effects on a video of a person, drawn around the face and behind the head (modules/video-effects).

Local: nothing leaves the machine. Every text and figure on screen comes from the plan, none is invented.
Effects that imitate a real app need an explicit acknowledgement, because of the marks and interfaces they copy.
"""
from __future__ import annotations
import json
import re
from pathlib import Path
from . import modules
from .render import probe

ROOT =Path(__file__).resolve().parents[1]
FX = ROOT / 'modules/video-effects/scripts/fx.py'
WORDS = ROOT / 'modules/video-effects/scripts/words.py'
SHORT_SIDE = {'draft': 540, 'review': 720, 'final': 1080, '4k': 2160}
BRAND_UI = {'comment-box': 'Instagram', 'reel-frame': 'Instagram', 'tap': 'Instagram', 'pastel-word': 'Instagram', 'profile-wall': 'Instagram', 'place-in-grid': 'Instagram',
            'messages': 'iMessage', 'apple-toggles': 'iPhone'}
LOW_TRACKING = .5


def catalog() -> list[dict]:
    """Read from the source, so it needs no Python package."""
    src = FX.read_text(encoding='utf-8')
    out = []
    for name, desc in re.findall(r"^@effect\('([a-z-]+)', '([^\n]*)'\)$", src, re.M):
        item = {'id': name, 'description': desc}
        if name in BRAND_UI:
            item['imite'] = BRAND_UI[name]
        out.append(item)
    return out


def aliases() -> dict:
    src = FX.read_text(encoding='utf-8')
    block = src[src.index('ALIASES = {'):src.index('LOOK_NAMES =')]
    return dict(re.findall(r"'([a-z0-9-]+)': '([a-z0-9-]+)'", block))


def _names(plan: list[dict]) -> list[str]:
    table = aliases()
    return [table.get(p['fx'].lower().lstrip('/'), p['fx'].lower().lstrip('/')) for p in plan]


def brand_gate(plan: list[dict], brand_ui_ok: bool) -> list[str]:
    used = sorted({n for n in _names(plan) if n in BRAND_UI})
    if used and not brand_ui_ok:
        detail = ', '.join(f'{n} ({BRAND_UI[n]})' for n in used)
        raise PermissionError(f"Ces effets imitent une interface de marque : {detail}. Vérifier que l'usage est permis, puis relancer avec --interfaces-marques.")
    return used


def _absolute_images(plan: list[dict], base: Path) -> list[dict]:
    out = []
    for p in plan:
        q = dict(p)
        if q.get('images'):
            q['images'] = str((base / q['images']).resolve())
        out.append(q)
    return out


def _write_plan(plan: list[dict], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({'effects': plan}, ensure_ascii=False, indent=1), encoding='utf-8')
    return path


def check(plan: list[dict], out: Path) -> str:
    """Stops on a missing text or figure, without any video."""
    r = modules.run_python([FX, '--plan', _write_plan(plan, Path(out)), '--check'], tier='effects')
    if r.returncode:
        raise ValueError((r.stderr or r.stdout).strip()[-600:])
    return 'OK'


def tracking(stdout: str) -> dict | None:
    m = re.search(r'^TRACK (\{.*\})$', stdout, re.M)
    return json.loads(m.group(1)) if m else None


def render(video: Path, plan: list[dict], out: Path, *, profile: str = 'draft', stills: str | None = None, brand_ui_ok: bool = False, base: Path | None = None) -> dict:
    video, out = Path(video).resolve(), Path(out).resolve()
    if not video.exists():
        raise FileNotFoundError(video)
    if profile not in SHORT_SIDE:
        raise ValueError(f'Profil non reconnu : {profile}')
    used = brand_gate(plan, brand_ui_ok)
    plan = _absolute_images(plan, Path(base or Path.cwd()))
    out.parent.mkdir(parents=True, exist_ok=True)
    plan_file = _write_plan(plan, out.with_suffix('.plan.json'))
    args = [FX, '--plan', plan_file, video, out, '--width', SHORT_SIDE[profile]]
    if stills:
        args += ['--still', stills]
    r = modules.run_python(args, tier='effects')
    if r.returncode:
        raise RuntimeError((r.stderr or r.stdout).strip()[-1500:])
    track = tracking(r.stdout)
    warnings = []
    size = next((s for s in probe(video)['streams'] if s.get('codec_type') == 'video'), {})
    if size.get('width', 0) > size.get('height', 0):
        warnings.append('Vidéo en paysage : ces effets sont pensés pour le vertical, certains titres et cartes sortent du cadre. Regarder chaque effet avant de livrer.')
    if track and track['frames'] and track['faces'] / track['frames'] < LOW_TRACKING:
        warnings.append(f"Visage trouvé sur {track['faces']} images sur {track['frames']} : les éléments peuvent se placer devant la personne. Regarder les images avant de livrer.")
    return {'output': str(out), 'effects': _names(plan), 'brand_ui': used, 'tracking': track, 'warnings': warnings, 'profile': profile, 'engine': 'video-effects'}
