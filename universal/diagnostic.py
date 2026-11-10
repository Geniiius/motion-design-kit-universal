"""What this machine is and what is installed on it: measured, not assumed.

Read-only: nothing is installed, written or changed here. No secret is ever read, only whether one exists.
Every probe may fail: a missing answer is reported as unknown, never guessed.
"""
from __future__ import annotations
import ctypes
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from . import config, modules
from .capabilities import _pkg, find_blender

ROOT = Path(__file__).resolve().parents[1]
HARDWARE_ENCODERS = ('h264_nvenc', 'h264_qsv', 'h264_amf', 'h264_videotoolbox')
SYNCED = ('onedrive', 'dropbox', 'google drive', 'googledrive', 'icloud', 'mobile documents')


def _out(cmd: list, timeout: int = 25) -> str | None:
    """What a command answers, or None when it is absent, fails or hangs."""
    try:
        r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=timeout)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return (r.stdout or r.stderr).strip() if r.returncode == 0 else None


def numbers(text: str | None) -> tuple:
    """(9, 0, 2) out of 'ffmpeg version 9.0.2-full_build'."""
    m = re.search(r'(\d+)(?:\.(\d+))?(?:\.(\d+))?', text or '')
    return tuple(int(x) for x in m.groups() if x is not None) if m else ()


def dotted(parts: tuple) -> str | None:
    return '.'.join(str(p) for p in parts) or None


# ------------------------------------------------------------------ the machine

def memory() -> dict:
    try:
        if platform.system() == 'Windows':
            class Status(ctypes.Structure):
                _fields_ = [('length', ctypes.c_ulong), ('load', ctypes.c_ulong), ('total', ctypes.c_ulonglong), ('free', ctypes.c_ulonglong), ('page_total', ctypes.c_ulonglong),
                            ('page_free', ctypes.c_ulonglong), ('virtual_total', ctypes.c_ulonglong), ('virtual_free', ctypes.c_ulonglong), ('extended', ctypes.c_ulonglong)]
            s = Status()
            s.length = ctypes.sizeof(Status)
            if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(s)):
                raise OSError('GlobalMemoryStatusEx')
            return {'ram_gb': round(s.total / 2 ** 30, 1), 'ram_free_gb': round(s.free / 2 ** 30, 1)}
        if platform.system() == 'Darwin':
            total = int(_out(['sysctl', '-n', 'hw.memsize']) or 0)
            return {'ram_gb': round(total / 2 ** 30, 1) or None, 'ram_free_gb': None}
        info = dict(re.findall(r'^(\w+):\s+(\d+) kB', Path('/proc/meminfo').read_text(), re.M))
        return {'ram_gb': round(int(info['MemTotal']) / 2 ** 20, 1), 'ram_free_gb': round(int(info.get('MemAvailable', 0)) / 2 ** 20, 1)}
    except (OSError, ValueError, KeyError, AttributeError):
        return {'ram_gb': None, 'ram_free_gb': None}


def _windows_cim() -> dict:
    """One PowerShell call for what the registry does not hold: physical cores, and the adapters Windows really uses."""
    script = ("$c=Get-CimInstance Win32_Processor|Select-Object -First 1 NumberOfCores;"
              "$g=Get-CimInstance Win32_VideoController|Select-Object Name,AdapterRAM,DriverVersion;"
              "@{cores=$c.NumberOfCores;gpus=@($g)}|ConvertTo-Json -Depth 3 -Compress")
    raw = _out(['powershell', '-NoProfile', '-NonInteractive', '-Command', script], 40)
    try:
        return json.loads(raw) if raw else {}
    except ValueError:
        return {}


def _windows_vram() -> dict:
    """Video memory per adapter, from the display class key: the one place where sizes above 4 GB are exact."""
    import winreg
    out: dict = {}
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}') as root:
            for i in range(32):
                try:
                    with winreg.OpenKey(root, f'{i:04d}') as k:
                        name = winreg.QueryValueEx(k, 'DriverDesc')[0]
                        try:
                            size = winreg.QueryValueEx(k, 'HardwareInformation.qwMemorySize')[0]
                        except OSError:
                            size = winreg.QueryValueEx(k, 'HardwareInformation.MemorySize')[0]
                        if isinstance(size, bytes):
                            size = int.from_bytes(size, 'little')
                        out[name] = max(out.get(name, 0), int(size))
                except OSError:
                    continue
    except OSError:
        pass
    return out


def cpu(cim: dict | None = None) -> dict:
    name, cores = None, None
    try:
        if platform.system() == 'Windows':
            import winreg
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'HARDWARE\DESCRIPTION\System\CentralProcessor\0') as k:
                name = winreg.QueryValueEx(k, 'ProcessorNameString')[0].strip()
            cores = (cim or {}).get('cores')
        elif platform.system() == 'Darwin':
            name = _out(['sysctl', '-n', 'machdep.cpu.brand_string'])
            cores = int(_out(['sysctl', '-n', 'hw.physicalcpu']) or 0) or None
        else:
            text = Path('/proc/cpuinfo').read_text(errors='replace')
            m = re.search(r'^model name\s*:\s*(.+)$', text, re.M)
            name = m.group(1).strip() if m else None
            pairs = set(zip(re.findall(r'^physical id\s*:\s*(\d+)', text, re.M), re.findall(r'^core id\s*:\s*(\d+)', text, re.M)))
            cores = len(pairs) or None
    except (OSError, ValueError):
        pass
    return {'cpu': name or platform.processor() or None, 'cores': cores, 'threads': os.cpu_count()}


def gpus(cim: dict | None = None) -> list[dict]:
    found: list[dict] = []
    system = platform.system()
    if system == 'Windows':
        exact = _windows_vram()
        listed = (cim or {}).get('gpus') or []
        for g in listed if isinstance(listed, list) else [listed]:
            name = (g.get('Name') or '').strip()
            size = exact.get(name) or g.get('AdapterRAM') or 0
            found.append({'name': name, 'vram_gb': round(size / 2 ** 30, 1) if size else None, 'driver': g.get('DriverVersion')})
        if not found:
            found = [{'name': n, 'vram_gb': round(s / 2 ** 30, 1) if s else None, 'driver': None} for n, s in exact.items()]
    elif system == 'Darwin':
        try:
            for g in json.loads(_out(['system_profiler', 'SPDisplaysDataType', '-json'], 40) or '{}').get('SPDisplaysDataType', []):
                text = g.get('spdisplays_vram') or g.get('_spdisplays_vram') or g.get('spdisplays_vram_shared') or ''
                size = numbers(text)
                gb = (size[0] / (1024 if 'MB' in text.upper() else 1)) if size else None
                found.append({'name': g.get('sppci_model') or g.get('_name') or 'GPU', 'vram_gb': round(gb, 1) if gb else None, 'driver': None,
                              'note': None if gb else 'mémoire unifiée, partagée avec le système'})
        except ValueError:
            pass
    else:
        for line in (_out(['lspci']) or '').splitlines():
            if re.search(r'VGA compatible|3D controller|Display controller', line):
                found.append({'name': line.split(': ', 1)[-1].strip(), 'vram_gb': None, 'driver': None})
    # Where NVIDIA's own tool exists, its numbers are the exact ones
    for line in (_out(['nvidia-smi', '--query-gpu=name,memory.total,driver_version', '--format=csv,noheader,nounits']) or '').splitlines():
        parts = [p.strip() for p in line.split(',')]
        if len(parts) >= 2 and parts[1].isdigit():
            fresh = {'name': parts[0], 'vram_gb': round(int(parts[1]) / 1024, 1), 'driver': parts[2] if len(parts) > 2 else None}
            same = next((g for g in found if parts[0].lower() in g['name'].lower() or g['name'].lower() in parts[0].lower()), None)
            if same:
                same.update(fresh)
            else:
                found.append(fresh)
    return found


def system_name() -> str:
    system = platform.system()
    if system == 'Windows':
        edition = ''
        try:
            edition = platform.win32_edition() or ''
        except (AttributeError, OSError):
            pass
        return f'Windows {platform.release()} {edition}'.strip() + f' ({platform.version()})'
    if system == 'Darwin':
        return f'macOS {platform.mac_ver()[0]}'
    try:
        pretty = re.search(r'^PRETTY_NAME="?([^"\n]+)', Path('/etc/os-release').read_text(), re.M)
        name = pretty.group(1) if pretty else 'Linux'
    except OSError:
        name = 'Linux'
    return name + (' (WSL)' if 'microsoft' in platform.release().lower() else '')


def machine() -> dict:
    cim = _windows_cim() if platform.system() == 'Windows' else {}
    total, _, free = shutil.disk_usage(ROOT)
    return {'os': system_name(), 'family': {'Windows': 'windows', 'Darwin': 'macos'}.get(platform.system(), 'linux'), 'arch': platform.machine() or None,
            'bits': 64 if sys.maxsize > 2 ** 32 else 32, **cpu(cim), **memory(), 'gpus': gpus(cim),
            'disk_free_gb': round(free / 2 ** 30, 1), 'disk_total_gb': round(total / 2 ** 30, 1)}


# ------------------------------------------------------------------ the tools

def on_path(name: str) -> list[str]:
    """Every copy of a tool the PATH can reach, the one that wins first. Two different copies are a classic source of surprises."""
    windows = platform.system() == 'Windows'
    exts = [e.lower() for e in os.environ.get('PATHEXT', '.EXE').split(';') if e] if windows else ['']
    seen, keys = [], set()
    for folder in os.environ.get('PATH', '').split(os.pathsep):
        if not folder:
            continue
        for ext in exts:
            f = Path(folder) / f'{name}{ext}'
            try:
                if not f.is_file() or not (windows or os.access(f, os.X_OK)):
                    continue
                real = str(f.resolve())
            except OSError:
                continue
            key = real.lower() if windows else real
            if key not in keys:
                keys.add(key)
                seen.append(real)
    return seen


def tool(name: str, args: list, pattern: str | None = None) -> dict:
    path = shutil.which(name)
    if not path:
        return {'found': False}
    first = ((_out([path] + args) or '').splitlines() or [''])[0]
    if pattern:
        m = re.search(pattern, first)
        parts = tuple(int(x) for x in m.groups() if x) if m else ()
    else:
        parts = numbers(first)
    return {'found': True, 'path': path, 'version': dotted(parts), 'parts': parts}


def pythons() -> dict:
    need = numbers(config.get('requirements.python_min', '3.10'))
    base = modules._base_python()
    if platform.system() == 'Windows' and shutil.which('py'):
        listed = sorted(set(re.findall(r'-V:(\d+\.\d+)', _out(['py', '-0p']) or '')), key=numbers, reverse=True)
    else:
        listed = [v for v in ('3.14', '3.13', '3.12', '3.11', '3.10') if shutil.which(f'python{v}')]
    return {'found': True, 'path': sys.executable, 'version': platform.python_version(), 'ok': sys.version_info[:2] >= need[:2], 'minimum': dotted(need),
            'installed': listed, 'for_modules': ' '.join(base) if base else None, 'modules_need': config.get('requirements.modules_python', ['3.12', '3.13'])}


def package_manager() -> dict:
    system = platform.system()
    names = ['winget'] if system == 'Windows' else ['brew'] if system == 'Darwin' else ['apt-get', 'dnf', 'pacman', 'zypper']
    for n in names:
        path = shutil.which(n)
        if path:
            return {'found': True, 'name': n, 'path': path, 'version': dotted(numbers(_out([path, '--version']))) if n in ('winget', 'brew') else None}
    return {'found': False, 'name': names[0]}


def secret_present(name: str) -> bool:
    """Whether a key exists for this user, in this session or saved in the user's settings. Its value never enters the kit."""
    if os.environ.get(name):
        return True
    if platform.system() == 'Windows':
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment') as k:
                winreg.QueryValueEx(k, name)
                return True
        except OSError:
            return False
    return False


def software() -> dict:
    node = tool('node', ['--version'])
    ffmpeg = tool('ffmpeg', ['-version'], r'ffmpeg version n?(\d+)(?:\.(\d+))?(?:\.(\d+))?')
    blender = find_blender()
    node_min, ffmpeg_min = config.get('requirements.node_min', 22), config.get('requirements.ffmpeg_min', 6)
    out = {
        'python': pythons(),
        'node': {**node, 'ok': bool(node.get('parts')) and node['parts'][0] >= node_min, 'minimum': node_min},
        'npm': tool('npm', ['--version']),
        # A development build carries no version number: it is reported as unknown rather than judged
        'ffmpeg': {**ffmpeg, 'ok': (None if not ffmpeg['parts'] else ffmpeg['parts'][0] >= ffmpeg_min) if ffmpeg['found'] else False, 'minimum': ffmpeg_min},
        'ffprobe': {'found': bool(shutil.which('ffprobe')), 'path': shutil.which('ffprobe')},
        'git': tool('git', ['--version']),
        'uv': tool('uv', ['--version']),
        'blender': {'found': bool(blender), 'path': blender, 'version': dotted(numbers(_out([blender, '--version'], 40))) if blender else None, 'on_path': bool(shutil.which('blender'))},
        'package_manager': package_manager(),
        'elevenlabs_key': {'found': secret_present('ELEVENLABS_API_KEY'), 'note': 'présence seulement : la valeur n\'est jamais lue'},
    }
    for entry in out.values():
        entry.pop('parts', None)
    return out


# ------------------------------------------------------------------ what the kit holds

def lock_version(project: str, package: str) -> str | None:
    try:
        return json.loads((ROOT / project / 'package-lock.json').read_text(encoding='utf-8'))['packages'][f'node_modules/{package}']['version']
    except (OSError, ValueError, KeyError):
        return None


def node_project(project: str, package: str) -> dict:
    """Installed means the key package is there at the exact version the lockfile fixes."""
    have, want = _pkg(project, package), lock_version(project, package)
    return {'installed': bool(have) and (want is None or have == want), 'version': have, 'expected': want}


def browsers_cache() -> Path:
    """Where Playwright keeps the browsers it downloads: the user's cache, outside the kit."""
    if os.environ.get('PLAYWRIGHT_BROWSERS_PATH'):
        return Path(os.environ['PLAYWRIGHT_BROWSERS_PATH'])
    if platform.system() == 'Windows':
        return Path(os.environ.get('LOCALAPPDATA') or Path.home() / 'AppData/Local') / 'ms-playwright'
    return Path.home() / ('Library/Caches/ms-playwright' if platform.system() == 'Darwin' else '.cache/ms-playwright')


def kit() -> dict:
    mod = modules.status()
    cache = browsers_cache()
    has = lambda pattern: cache.exists() and any(cache.glob(pattern))
    return {
        'remotion': {**node_project('template', 'remotion'), 'browser': (ROOT / 'template/node_modules/.remotion/chrome-headless-shell').exists()},
        'prompt-motion': {**node_project('prompt-motion', 'playwright'), 'browser': has('chromium-*')},
        'film': {**node_project('modules/opuscar', 'playwright-core'), 'browser': has('chromium_headless_shell-*')},
        'design-check': {'installed': mod['design']},
        'tiers': mod['tiers'], 'packs': mod['packs'], 'whisper_model': mod['whisper_model'],
        'profile': (ROOT / 'perfil').exists(),
    }


# ------------------------------------------------------------------ encoders, tested for real

def test_encoders() -> dict:
    """Hardware encoders that really produce a file here. Being listed by FFmpeg is not enough: a driver that is too old fails on the first frame."""
    listed = _out(['ffmpeg', '-hide_banner', '-encoders']) or ''
    out = {}
    with tempfile.TemporaryDirectory(prefix='kit-enc-') as tmp:
        for name in HARDWARE_ENCODERS:
            if not re.search(rf'\b{name}\b', listed):
                continue
            dst = Path(tmp) / f'{name}.mp4'
            try:
                r = subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'lavfi', '-i', 'testsrc2=s=1280x720:r=30:d=1', '-c:v', name, str(dst)],
                                   capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=60)
                out[name] = r.returncode == 0 and dst.exists() and dst.stat().st_size > 1000
            except (OSError, subprocess.TimeoutExpired):
                out[name] = False
    return out


# ------------------------------------------------------------------ what does not fit together

def conflicts(m: dict, s: dict) -> list[dict]:
    """Each: level (FAILED or WARNING), what is wrong, and what it means for the person, in plain words."""
    req = config.get('requirements')
    out = []

    def add(level, what, effect):
        out.append({'level': level, 'what': what, 'effect': effect})

    if m['bits'] != 64:
        add('FAILED', 'Système ou Python en 32 bits.', 'Les moteurs du kit demandent un système et un Python en 64 bits.')
    if not s['python']['ok']:
        add('FAILED', f"Python {s['python']['version']} est trop ancien : il faut {s['python']['minimum']} ou plus.", 'Le kit ne peut pas fonctionner de façon fiable avec cette version.')
    if s['node']['found'] and not s['node']['ok']:
        add('FAILED', f"Node {s['node']['version']} est trop ancien : il faut la version {s['node']['minimum']} ou plus.",
            'La création de vidéos à partir d\'une idée ne fonctionnera pas tant que Node n\'est pas mis à jour.')
    if s['ffmpeg']['found'] and s['ffmpeg']['ok'] is False:
        add('FAILED', f"FFmpeg {s['ffmpeg']['version']} est trop ancien : il faut la version {s['ffmpeg']['minimum']} ou plus.", 'Montage, sous-titres et export peuvent échouer.')
    if s['ffmpeg']['found'] and s['ffmpeg']['ok'] is None:
        add('WARNING', 'Version de FFmpeg non reconnue (compilation de développement).', 'Le kit l\'utilise tel quel : si un export échoue, installer une version publiée.')
    if s['ffmpeg']['found'] and not s['ffprobe']['found']:
        add('FAILED', 'FFmpeg est là mais pas ffprobe, qui l\'accompagne normalement.', 'Le kit ne peut pas lire la durée ni la taille des vidéos.')
    for name in ('ffmpeg', 'node'):
        copies = [c for c in on_path(name) if 'windowsapps' not in c.lower()]
        if len(copies) > 1:
            add('WARNING', f'Plusieurs {name} sont installés : celui qui est utilisé est {copies[0]}.',
                'Sans gravité si la version utilisée convient. À savoir si un comportement surprend après une mise à jour.')
    if not s['python']['for_modules'] and not s['uv']['found']:
        add('WARNING', f"Aucun Python {' ou '.join(s['python']['modules_need'])} trouvé (version par défaut : {s['python']['version']}).",
            'Les options voix locale, sous-titres automatiques et effets demandent une de ces versions. Le reste du kit fonctionne.')
    if m['disk_free_gb'] < req['disk_free_gb_fail']:
        add('FAILED', f"Il reste {m['disk_free_gb']} Go sur le disque.", 'Pas assez de place pour installer les moteurs ni pour rendre une vidéo.')
    elif m['disk_free_gb'] < req['disk_free_gb_warn']:
        add('WARNING', f"Il reste {m['disk_free_gb']} Go sur le disque.", 'Assez pour l\'essentiel, juste pour les options lourdes et les longues vidéos.')
    if m['ram_gb'] and m['ram_gb'] < req['ram_gb_warn']:
        add('WARNING', f"{m['ram_gb']} Go de mémoire vive.", 'Les rendus seront lents. Préférer des vidéos courtes et le profil brouillon pour les essais.')
    where = str(ROOT)
    if any(word in where.lower() for word in SYNCED):
        add('WARNING', 'Le kit est dans un dossier synchronisé avec le cloud.',
            'La synchronisation ralentit l\'installation et peut bloquer des fichiers. Mieux vaut un dossier local, hors synchronisation.')
    if platform.system() == 'Windows' and len(where) > 110:
        add('WARNING', f'Le chemin du kit est long ({len(where)} caractères).',
            'Windows limite la longueur des chemins : certains moteurs peuvent échouer. Un dossier plus près de la racine du disque évite le problème.')
    if not where.isascii():
        add('WARNING', 'Le chemin du kit contient des accents ou des caractères spéciaux.',
            'Certains outils les lisent mal. En cas d\'erreur étrange, déplacer le kit dans un dossier au nom simple.')
    if (m['arch'] or '').lower() in ('arm64', 'aarch64') and m['family'] != 'macos':
        add('WARNING', 'Processeur ARM.', 'Le kit n\'a pas été essayé sur cette architecture : les options d\'effets et de voix peuvent ne pas s\'installer.')
    return out


def full(test: bool = False) -> dict:
    m, s = machine(), software()
    out = {'machine': m, 'software': s, 'kit': kit(), 'conflicts': conflicts(m, s)}
    if test:
        out['encoders'] = test_encoders()
    return out
