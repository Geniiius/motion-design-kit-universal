"""Optional third-party modules: one local Python environment, exact versions, nothing outside the kit.

Every package is checked against its hash and only wheels are accepted, so no install script runs.
Big files (voice model, instrument samples) are downloaded only with an explicit approval and checked by SHA-256.
"""
from __future__ import annotations
import hashlib
import json
import os
import platform
import shutil
import subprocess
import tarfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / 'modules'
VENV = DIR / '.venv'
LOCKS = DIR / 'requirements'
OPUSCAR = DIR / 'opuscar'
OPUSCAR_REPO = 'https://github.com/lemomo-ai/lemo-opuscar.git'
OPUSCAR_COMMIT = 'bebbbe1aa92a3cb4bb6f83500e61b23a17d1aa00'
WHISPER = {'repo': 'Systran/faster-whisper-base', 'revision': 'ebe41f70d5b6dfa9166e2c581c45c9c0cfc57b66', 'mb': 145}
WHISPER_DIR = DIR / 'models' / 'whisper-base'
TIERS = {'effects': 'Effets vidéo (visage, détourage) : ~400 Mo', 'audio': 'Bruitages et mixage hors ligne : ~150 Mo',
         'music': 'Cordes pincées synthétisées (numba) : ~140 Mo', 'voice': 'Moteur de voix Kokoro : ~200 Mo', 'transcribe': 'Transcription locale faster-whisper : ~200 Mo'}


OPTION_OF = {'effects': 'effects', 'audio': 'film-styles', 'voice': 'voice-local', 'transcribe': 'captions'}


class DownloadApprovalRequired(RuntimeError):
    pass


class ConsentRequired(RuntimeError):
    """A free part of the kit is missing. Installing it is the user's decision, asked in plain words, never a side effect."""


def may_install_alone() -> bool:
    """False unless the user chose, in their own settings, to let free parts install without being asked each time."""
    from . import config
    return config.get('consent.free_modules', 'ask') == 'auto'


def python() -> Path:
    return VENV / ('Scripts/python.exe' if platform.system() == 'Windows' else 'bin/python')


def _lock(tier: str) -> Path:
    return LOCKS / f'{tier}.lock'


def _marker(tier: str) -> Path:
    return VENV / f'.tier-{tier}'


def _digest(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def _base_python() -> list[str] | None:
    """kokoro-onnx refuses Python 3.14 and the locks start at 3.12."""
    candidates = [['py', '-3.13'], ['py', '-3.12']] if platform.system() == 'Windows' else []
    candidates += [['python3.13'], ['python3.12'], ['python3'], ['python']]
    for c in candidates:
        if not shutil.which(c[0]):
            continue
        r = subprocess.run(c + ['-c', 'import sys;print(sys.version_info[:2])'], capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip() in ('(3, 12)', '(3, 13)'):
            return c
    return None


def _ensure_venv() -> None:
    if python().exists():
        return
    base = _base_python()
    if base:
        subprocess.run(base + ['-m', 'venv', str(VENV)], check=True)
    elif shutil.which('uv'):
        subprocess.run(['uv', 'venv', '--python', '3.13', str(VENV)], check=True)
    else:
        raise RuntimeError('Python 3.12 ou 3.13 requis pour les modules (3.14 ne convient pas à Kokoro). Installer Python 3.13 ou uv, puis relancer.')


def install_tier(tier: str) -> dict:
    if tier not in TIERS:
        raise ValueError(f'Niveau inconnu : {tier}')
    _ensure_venv()
    lock = _lock(tier)
    if _marker(tier).exists() and _marker(tier).read_text(encoding='utf-8') == _digest(lock):
        return {'tier': tier, 'status': 'déjà installé'}
    if shutil.which('uv'):
        cmd = ['uv', 'pip', 'install', '--python', str(python()), '--require-hashes', '--only-binary', ':all:', '-r', str(lock)]
    else:
        cmd = [str(python()), '-m', 'pip', 'install', '--disable-pip-version-check', '--require-hashes', '--only-binary', ':all:', '-r', str(lock)]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode:
        raise RuntimeError(f'Installation de {tier} échouée :\n{r.stderr[-1800:]}')
    _marker(tier).write_text(_digest(lock), encoding='utf-8')
    return {'tier': tier, 'status': 'installé'}


def install_film() -> dict:
    """Node packages of the film engine, exact versions from the lockfile, with no install script."""
    npm = shutil.which('npm')
    if not npm:
        raise RuntimeError('npm absent : installer Node 20 ou plus.')
    r = subprocess.run([npm, 'ci', '--ignore-scripts', '--no-audit', '--no-fund', '--loglevel=error'], cwd=OPUSCAR, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode:
        raise RuntimeError(r.stderr[-1500:])
    r = subprocess.run(['node', 'node_modules/playwright-core/cli.js', 'install', 'chromium-headless-shell'], cwd=OPUSCAR, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode:
        raise RuntimeError(r.stderr[-1500:])
    return {'tier': 'film', 'status': 'installé'}


def _packs() -> dict:
    return json.loads((OPUSCAR / 'tools/assets.json').read_text(encoding='utf-8'))


def pack_names() -> dict:
    out = {}
    for name, p in _packs()['packs'].items():
        out['voice-model' if name == 'voice' else name] = {'pack': name, 'mb': round(p['size'] / 1e6), 'file': p['file'], 'sha256': p['sha256']}
    return out


def _pack_installed(pack: str) -> bool:
    if pack == 'voice':
        return (OPUSCAR / 'core/tts/kokoro-v1.0.onnx').exists() and (OPUSCAR / 'core/tts/voices-v1.0.bin').exists()
    if pack == 'hdri':
        return (OPUSCAR / 'core/assets/polyhaven/lythwood_lounge_2k.hdr').exists()
    if pack.startswith('instruments-'):
        return (OPUSCAR / 'core/audio/instruments' / pack.split('-', 1)[1]).exists()
    return False


def install_pack(name: str, approved: bool = False) -> dict:
    """Downloads one pack from the upstream release; nothing is unpacked unless its SHA-256 matches the audited manifest."""
    known = pack_names()
    if name not in known:
        raise ValueError(f'Paquet inconnu : {name}. Disponibles : {", ".join(known)}')
    p = known[name]
    if _pack_installed(p['pack']):
        return {'tier': name, 'status': 'déjà installé'}
    man = _packs()
    url = f"https://github.com/{man['repo']}/releases/download/{man['tag']}/{p['file']}"
    if not approved:
        raise DownloadApprovalRequired(f"{name} : téléchargement de {p['file']} ({p['mb']} Mo) depuis {url}. Accord explicite requis : relancer avec --approve-download.")
    if shutil.disk_usage(OPUSCAR).free < p['mb'] * 2.2 * 1e6:
        raise RuntimeError(f"Espace disque insuffisant : il faut environ {round(p['mb'] * 2.2)} Mo.")
    tmp = OPUSCAR / '.release' / (p['file'] + '.download')
    tmp.parent.mkdir(exist_ok=True)
    print(f"Téléchargement de {p['file']} ({p['mb']} Mo)...", flush=True)
    urllib.request.urlretrieve(url, tmp)
    if _digest(tmp) != p['sha256']:
        tmp.unlink()
        raise RuntimeError(f"{p['file']} : empreinte SHA-256 différente de celle du manifeste audité. Rien n'a été installé.")
    with tarfile.open(tmp) as t:
        t.extractall(OPUSCAR, filter='data')
    tmp.unlink()
    shutil.rmtree(tmp.parent, ignore_errors=True)
    return {'tier': name, 'status': 'installé', 'sha256': p['sha256']}


def install_whisper(approved: bool = False) -> dict:
    """The transcription model, at a fixed revision, kept in the kit rather than in the user's Hugging Face cache."""
    if (WHISPER_DIR / 'model.bin').exists():
        return {'tier': 'whisper-model', 'status': 'déjà installé'}
    if not approved:
        raise DownloadApprovalRequired(f"whisper-model : téléchargement de {WHISPER['repo']} ({WHISPER['mb']} Mo) depuis Hugging Face. Accord explicite requis : relancer avec --approve-download.")
    install_tier('transcribe')
    code = ('import sys\nfrom huggingface_hub import snapshot_download\n'
            f"snapshot_download({WHISPER['repo']!r}, revision={WHISPER['revision']!r}, local_dir=sys.argv[1], allow_patterns=['config.json', 'model.bin', 'tokenizer.json', 'vocabulary.txt'])\n")
    r = subprocess.run([str(python()), '-c', code, str(WHISPER_DIR)], capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode:
        raise RuntimeError(r.stderr[-1500:])
    return {'tier': 'whisper-model', 'status': 'installé', 'revision': WHISPER['revision']}


def install(names: list[str], approved: bool = False) -> list[dict]:
    out = []
    for n in names:
        if n == 'film':
            out.append(install_film())
        elif n == 'design':
            from .design_check import install as install_design
            out.append(install_design())
        elif n == 'whisper-model':
            out.append(install_whisper(approved))
        elif n in TIERS:
            out.append(install_tier(n))
        else:
            out.append(install_pack(n, approved))
    return out


def status() -> dict:
    tiers = {t: _marker(t).exists() and _marker(t).read_text(encoding='utf-8') == _digest(_lock(t)) for t in TIERS}
    packs = {name: _pack_installed(p['pack']) for name, p in pack_names().items()}
    return {'tiers': tiers, 'film': (OPUSCAR / 'node_modules/playwright-core').exists(), 'design': (DIR / 'design-check/node_modules/impeccable').exists(), 'packs': packs, 'whisper_model': (WHISPER_DIR / 'model.bin').exists(), 'python': str(python().relative_to(ROOT)) if python().exists() else None}


def run_python(args: list[str], *, cwd: Path | None = None, tier: str | None = None, env: dict | None = None) -> subprocess.CompletedProcess:
    if tier and not _marker(tier).exists():
        if not may_install_alone():
            option = OPTION_OF.get(tier, tier)
            raise ConsentRequired(f"L'option « {option} » n'est pas installée ({TIERS[tier]}). Elle est gratuite et reste dans le dossier du kit. "
                                  f"Demander l'accord de l'utilisateur en mots simples, puis : python -m universal.cli setup apply --approve {option}")
        install_tier(tier)
    if not python().exists():
        raise RuntimeError('Environnement des modules absent.')
    full = {**os.environ, 'PYTHONUTF8': '1', **(env or {})}
    return subprocess.run([str(python())] + [str(a) for a in args], cwd=cwd, env=full, capture_output=True, text=True, encoding='utf-8', errors='replace')


def pinned_checkout(paths: list[str]) -> Path:
    """Fetches only these paths of Lemo-Opuscar at the audited commit into modules/opuscar/.source, never its main branch."""
    src = OPUSCAR / '.source'
    if not shutil.which('git'):
        raise RuntimeError('git absent : nécessaire pour récupérer ce contenu au commit audité.')
    git = ['git', '-C', str(src)]
    if not (src / '.git').exists():
        src.mkdir(parents=True, exist_ok=True)
        subprocess.run(git + ['init', '-q'], check=True)
        subprocess.run(git + ['remote', 'add', 'origin', OPUSCAR_REPO], check=True)
    subprocess.run(git + ['sparse-checkout', 'set', '--no-cone'] + [f'/{p}' for p in paths], check=True, capture_output=True)
    subprocess.run(git + ['fetch', '-q', '--depth', '1', '--filter=blob:none', 'origin', OPUSCAR_COMMIT], check=True, capture_output=True)
    subprocess.run(git + ['checkout', '-q', OPUSCAR_COMMIT], check=True, capture_output=True)
    return src
