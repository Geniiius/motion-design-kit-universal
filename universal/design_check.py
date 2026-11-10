"""Automatic design check of delivered HTML pages, with Impeccable's rules (modules/design-check).

It advises and never blocks: part of its rules are a matter of taste, and it has false alarms (see UPSTREAM.md).
It reads HTML and CSS only, so text drawn on a canvas, as in the film pages, stays invisible to it: no finding there proves nothing.
The binary runs only after its checksum matches the manifest shipped with the pinned package.
"""
from __future__ import annotations
import hashlib
import json
import platform
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / 'modules' / 'design-check'
TASTE = 'slop'  # the detector's own category for what looks generated: an opinion to weigh, not a defect


def _target() -> tuple[str, str]:
    system = {'Windows': 'windows', 'Darwin': 'darwin', 'Linux': 'linux'}.get(platform.system(), platform.system().lower())
    arch = {'AMD64': 'x64', 'x86_64': 'x64', 'arm64': 'arm64', 'aarch64': 'arm64'}.get(platform.machine(), platform.machine())
    return system, arch


def binary() -> Path:
    system, arch = _target()
    return DIR / 'node_modules' / '@impeccable' / f'cli-{system}-{arch}' / 'bin' / ('impeccable.exe' if system == 'windows' else 'impeccable')


def expected_digest() -> str | None:
    system, arch = _target()
    asset = f"impeccable-{system}-{arch}{'.exe' if system == 'windows' else ''}"
    manifest = DIR / 'node_modules' / 'impeccable' / 'skill' / 'scripts' / 'engine-checksums.txt'
    if not manifest.exists():
        return None
    for line in manifest.read_text(encoding='utf-8').splitlines():
        parts = line.split()
        if len(parts) == 3 and parts[1] == asset:
            return parts[2].lower()
    return None


def install() -> dict:
    """Exact versions from the lockfile, no install script, nothing outside the kit."""
    npm = shutil.which('npm')
    if not npm:
        raise RuntimeError('npm absent.')
    r = subprocess.run([npm, 'ci', '--ignore-scripts', '--no-audit', '--no-fund', '--loglevel=error'], cwd=DIR, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode:
        raise RuntimeError(r.stderr[-800:])
    return {'tier': 'design', 'status': 'installé'}


def verified() -> bool:
    exe = binary()
    expected = expected_digest()
    return bool(exe.exists() and expected and hashlib.sha256(exe.read_bytes()).hexdigest() == expected)


def group(findings: list[dict]) -> dict:
    """The same defect found on four cards is one thing to fix, and taste is kept apart from measured defects."""
    seen: dict[tuple, dict] = {}
    for f in findings:
        key = (f.get('antipattern'), f.get('snippet'))
        if key in seen:
            seen[key]['nombre'] += 1
        else:
            seen[key] = {'regle': f.get('antipattern'), 'nom': f.get('name'), 'detail': f.get('snippet'), 'categorie': f.get('category'), 'nombre': 1}
    rows = list(seen.values())
    return {'defauts': [r for r in rows if r['categorie'] != TASTE], 'gout': [r for r in rows if r['categorie'] == TASTE]}


def check(html: Path) -> dict:
    """Never raises: a delivery must not fail because an adviser is unavailable, and the result says so."""
    try:
        if not binary().exists():
            from . import modules
            if not modules.may_install_alone():
                return {'ran': False, 'raison': "Contrôle de design non installé (gratuit, 20 Mo). Il conseille et ne bloque rien : proposer de l'installer (setup apply --approve design-check)."}
            install()
        if not verified():
            return {'ran': False, 'raison': "Empreinte du détecteur différente de celle attendue : il n'a pas été lancé."}
        with tempfile.TemporaryDirectory(prefix='design-') as tmp:  # no project configuration or file of the user is read
            r = subprocess.run([str(binary()), 'detect', '--json', '--no-design-system', str(Path(html).resolve())], cwd=tmp, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=120)
        if r.returncode not in (0, 2):
            return {'ran': False, 'raison': (r.stderr or r.stdout).strip()[-300:]}
        return {'ran': True, **group(json.loads(r.stdout or '[]'))}
    except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as e:
        return {'ran': False, 'raison': str(e)[-300:]}


def as_report(result: dict) -> dict:
    """In the words of the quality report: measured defects are warnings, taste is an aesthetic signal, nothing blocks."""
    if not result.get('ran'):
        return {'pass': True, 'blocking': [], 'warnings': [], 'aesthetic': [], 'design': result}
    line = lambda r: f"{r['nom']} : {r['detail']}" + (f" ({r['nombre']} fois)" if r['nombre'] > 1 else '')
    return {'pass': True, 'blocking': [], 'warnings': [line(r) for r in result['defauts']], 'aesthetic': [line(r) for r in result['gout']], 'design': result}
