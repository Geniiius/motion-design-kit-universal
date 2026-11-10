"""Remotion adapter: publishes project media into template/public and renders a composition.

GPU first (ANGLE), then software WebGL (swangle) when the machine has no usable GPU.
"""
from __future__ import annotations
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / 'template'
CLI = TEMPLATE / 'node_modules' / '@remotion' / 'cli' / 'remotion-cli.js'
PROFILES = {'draft': (.5, 28), 'review': (.75, 23), 'final': (1, 17), '4k': (2, 17)}
SIZES = {'Landscape': (1920, 1080), 'Reel': (1080, 1920), 'Square': (1080, 1080), 'Feed': (1080, 1350)}


def size_of(composition: str) -> tuple[int, int] | None:
    return SIZES.get(composition.rsplit('-', 1)[-1])


def publish(src: str | Path, project: str) -> str:
    """Copy into template/public/universal: Remotion only serves that folder. Returns the public path."""
    src = Path(src)
    safe = re.sub(r'[^a-zA-Z0-9_-]+', '-', project).strip('-') or 'projet'
    dest = TEMPLATE / 'public' / 'universal' / safe / src.name
    dest.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        shutil.copytree(src, dest, dirs_exist_ok=True)
    else:
        shutil.copy2(src, dest)
    return f'universal/{safe}/{src.name}'


def _sentences(brief: str) -> list[str]:
    parts = [x.strip(' ,;') for x in re.split(r'[.!?\n]+', brief) if x.strip(' ,;')]
    return parts or ['Votre idée, en mouvement']


def _key_word(text: str) -> str:
    words = re.findall(r"[\wÀ-ÿ'-]+", text)
    return max(words, key=len) if words else ''


def props_for(project: dict, composition: str) -> dict:
    """Starting props from the manifest. A human or Claude writes the real copy in project['props']."""
    name, brief = project['name'], project['request']['brief']
    custom = project.get('props') or {}
    inputs = [x for x in project['inputs'] if x['exists']]
    family = composition.split('-')[0]
    pick = lambda role, kind: next((x for x in inputs if x['role'] == role and x['type'] == kind), None)
    if family == 'Logo':
        logo = pick('logo', 'image')
        base = {'palette': 'midnight', 'brand': name.upper(), 'logo': publish(logo['path'], name) if logo else '', 'tagline': _sentences(brief)[0][:60], 'music': ''}
    elif family == 'Kinetic':
        beats = [{'text': s[:60], 'highlight': _key_word(s), 'seconds': min(4.0, max(1.6, len(s) / 18)), 'media': ''} for s in _sentences(brief)[:5]]
        base = {'palette': 'midnight', 'handle': '', 'beats': beats, 'music': ''}
    elif family == 'Promo':
        parts = _sentences(brief)
        scenes = [{'title': s[:48], 'highlight': _key_word(s), 'subtitle': '', 'media': ''} for s in (parts[1:4] or parts[:1])]
        base = {'palette': 'midnight', 'brand': name.upper(), 'logo': '', 'hook': {'title': parts[0][:48], 'highlight': _key_word(parts[0])}, 'scenes': scenes,
                'cta': {'label': 'En savoir plus', 'url': ''}, 'music': '', 'sceneSeconds': 3}
    elif family == 'Parallaxe':
        photos = [publish(x['path'], name) for x in inputs if x['type'] == 'image' and x['role'] != 'logo']
        base = {'fotos': photos, 'titulo': _sentences(brief)[0][:48] if brief else ''}
    elif family == 'Escena3D':
        base = {'titulo': _sentences(brief)[0][:48]}
    elif family == 'Personaje' and 'GLB' in composition:
        model = next(x for x in inputs if x['type'] == '3d')
        base = {'modelo': publish(model['path'], name), 'clip': (model['metadata'].get('animations') or [''])[0], 'titulo': ''}
    else:
        base = {}
    return {**base, **custom}


def ensure_defaults():
    """Default props of Parallaxe, Hibrido and GLB point into public/universal, which is not shipped."""
    pub = TEMPLATE / 'public' / 'universal'
    if (pub / 'medios/capas/frente.png').exists() and (pub / 'medios/clip-a.mp4').exists() and (pub / 'modelos/RobotExpressive.glb').exists():
        return
    from . import fixtures
    made = fixtures.build()
    shutil.copytree(made['capas'], pub / 'medios/capas', dirs_exist_ok=True)
    shutil.copy2(made['clips'][0], pub / 'medios/clip-a.mp4')
    (pub / 'modelos').mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / 'examples/modelos/RobotExpressive/RobotExpressive.glb', pub / 'modelos/RobotExpressive.glb')


def _command(kind: str, composition: str, out: Path, props: Path, profile: str, gl: str, frame: int | None) -> list[str]:
    scale, crf = PROFILES[profile]
    cmd = ['node', str(CLI), kind, 'src/index.ts', composition, str(out), f'--props={props}', f'--scale={scale}', f'--gl={gl}', '--log=error']
    if kind == 'render':
        cmd += [f'--crf={crf}', '--color-space=bt709']
    if frame is not None:
        cmd.append(f'--frame={frame}')
    return cmd


def render(project: dict, composition: str, out: Path, profile: str = 'draft', *, still_frame: int | None = None, props: dict | None = None) -> dict:
    if not CLI.exists():
        raise RuntimeError('Moteur de création absent (1,2 Go, gratuit) : demander l\'accord de l\'utilisateur, puis python -m universal.cli setup apply --approve engine-remotion')
    ensure_defaults()
    out = Path(out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    data = props if props is not None else props_for(project, composition)
    kind = 'still' if still_frame is not None else 'render'
    with tempfile.TemporaryDirectory(prefix='rprops-') as tmp:
        props_file = Path(tmp) / 'props.json'
        props_file.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
        last = ''
        for gl in ('angle', 'swangle'):
            r = subprocess.run(_command(kind, composition, out, props_file, profile, gl, still_frame), cwd=TEMPLATE, capture_output=True, text=True, encoding='utf-8', errors='replace')
            if r.returncode == 0 and out.exists():
                return {'output': str(out), 'engine': 'remotion', 'composition': composition, 'gl': gl, 'profile': profile, 'bytes': out.stat().st_size}
            last = (r.stderr or r.stdout)[-1500:]
    raise RuntimeError(f'Rendu Remotion échoué ({composition}):\n{last}')
