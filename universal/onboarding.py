"""The kit's single way in: first launch, health check, repair, uninstall, update check.

Always the same order: look (read-only), explain, ask, install only what was approved by name, check each part for real,
then make one small video from start to end. A part that is already there and works is said so and left alone.
"""
from __future__ import annotations
import json
import locale
import os
import platform
import shutil
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path
from . import config, diagnostic, logs, modules, state

ROOT = Path(__file__).resolve().parents[1]
READY, WARNING, FAILED, OPTIONAL = 'READY', 'WARNING', 'FAILED', 'OPTIONAL'
PINS = {'hyperframes': '0.8.164'}
QUIET = {'HYPERFRAMES_SKIP_SKILLS': '1', 'HYPERFRAMES_NO_TELEMETRY': '1', 'HYPERFRAMES_NO_UPDATE_CHECK': '1', 'DO_NOT_TRACK': '1', 'NO_COLOR': '1'}
CACHE_NOTE = 'Son navigateur de rendu se range dans le cache de Playwright, hors du dossier du kit.'

# level: required (the kit's promise depends on it), recommended, optional. kind: system (lives on the computer), kit (lives in the kit folder), account.
PARTS = [
    {'id': 'python', 'level': 'required', 'kind': 'system', 'mb': 30, 'licence': 'PSF',
     'title': {'fr': 'Python', 'es': 'Python', 'en': 'Python'},
     'why': {'fr': 'Fait tourner le kit.', 'es': 'Hace funcionar el kit.', 'en': 'Runs the kit.'},
     'without': 'le kit ne démarre pas',
     'packages': {'winget': 'Python.Python.3.13', 'brew': 'python@3.13', 'apt-get': 'python3 python3-venv', 'dnf': 'python3', 'pacman': 'python', 'zypper': 'python3'}, 'site': 'https://www.python.org/downloads/'},
    {'id': 'ffmpeg', 'level': 'required', 'kind': 'system', 'mb': 200, 'licence': 'GPL',
     'title': {'fr': 'FFmpeg', 'es': 'FFmpeg', 'en': 'FFmpeg'},
     'why': {'fr': 'Monte, coupe, recadre, sous-titre et exporte les vidéos.', 'es': 'Monta, corta, reencuadra, subtitula y exporta los vídeos.', 'en': 'Edits, cuts, reframes, captions and exports videos.'},
     'without': 'aucun montage, traitement ni export n\'est possible',
     'packages': {'winget': 'Gyan.FFmpeg', 'brew': 'ffmpeg', 'apt-get': 'ffmpeg', 'dnf': 'ffmpeg', 'pacman': 'ffmpeg', 'zypper': 'ffmpeg'}, 'site': 'https://ffmpeg.org/download.html'},
    {'id': 'node', 'level': 'required', 'kind': 'system', 'mb': 90, 'licence': 'MIT',
     'title': {'fr': 'Node.js', 'es': 'Node.js', 'en': 'Node.js'},
     'why': {'fr': 'Fait tourner le moteur de création de vidéos.', 'es': 'Hace funcionar el motor de creación de vídeos.', 'en': 'Runs the video creation engine.'},
     'without': 'la création de vidéos à partir d\'une idée ne fonctionne pas',
     'packages': {'winget': 'OpenJS.NodeJS.LTS', 'brew': 'node'}, 'site': 'https://nodejs.org/'},
    {'id': 'engine-remotion', 'level': 'required', 'kind': 'kit', 'mb': 1200, 'needs': ['node'],
     'title': {'fr': 'Moteur de création', 'es': 'Motor de creación', 'en': 'Creation engine'},
     'why': {'fr': 'Crée une vidéo à partir d\'une idée : promo, logo animé, photos, graphiques, personnage 3D.',
             'es': 'Crea un vídeo a partir de una idea: promo, logo animado, fotos, gráficos, personaje 3D.',
             'en': 'Makes a video from an idea: promo, animated logo, photos, charts, 3D character.'},
     'without': 'la création de vidéos à partir d\'une idée ne fonctionne pas'},
    {'id': 'captions', 'level': 'recommended', 'kind': 'kit', 'mb': 345, 'needs': ['python-modules'],
     'title': {'fr': 'Sous-titres automatiques', 'es': 'Subtítulos automáticos', 'en': 'Automatic captions'},
     'why': {'fr': 'Transcrit la voix hors ligne : sous-titres, traductions, extraits, chapitres.', 'es': 'Transcribe la voz sin conexión: subtítulos, traducciones, extractos, capítulos.',
             'en': 'Transcribes speech offline: captions, translations, clips, chapters.'}},
    {'id': 'python-modules', 'level': 'optional', 'kind': 'system', 'mb': 30, 'licence': 'PSF', 'hidden': True,
     'title': {'fr': 'Python 3.13 pour les options', 'es': 'Python 3.13 para las opciones', 'en': 'Python 3.13 for the options'},
     'why': {'fr': 'Les options voix, sous-titres et effets demandent Python 3.12 ou 3.13.', 'es': 'Las opciones de voz, subtítulos y efectos piden Python 3.12 o 3.13.',
             'en': 'The voice, caption and effect options need Python 3.12 or 3.13.'},
     'packages': {'winget': 'Python.Python.3.13', 'brew': 'python@3.13'}, 'site': 'https://www.python.org/downloads/'},
    {'id': 'voice-local', 'level': 'optional', 'kind': 'kit', 'mb': 550, 'needs': ['python-modules'],
     'title': {'fr': 'Voix off gratuite', 'es': 'Voz en off gratuita', 'en': 'Free voice-over'},
     'why': {'fr': 'Voix de synthèse hors ligne, sans abonnement.', 'es': 'Voz sintética sin conexión, sin suscripción.', 'en': 'Offline synthetic voice, no subscription.'}},
    {'id': 'effects', 'level': 'optional', 'kind': 'kit', 'mb': 450, 'needs': ['python-modules'],
     'title': {'fr': 'Effets autour d\'une personne', 'es': 'Efectos alrededor de una persona', 'en': 'Effects around a person'},
     'why': {'fr': 'Texte derrière la tête, suivi du visage, recadrage vertical qui suit la personne.', 'es': 'Texto detrás de la cabeza, seguimiento de la cara, reencuadre vertical que sigue a la persona.',
             'en': 'Text behind the head, face tracking, vertical reframing that follows the person.'}},
    {'id': 'film-styles', 'level': 'optional', 'kind': 'kit', 'mb': 400, 'needs': ['node', 'python-modules'], 'outside': CACHE_NOTE,
     'title': {'fr': 'Styles de films', 'es': 'Estilos de película', 'en': 'Film styles'},
     'why': {'fr': 'Films écrits en code dans 66 styles : aquarelle, risographie, estampe…', 'es': 'Películas escritas en código en 66 estilos: acuarela, risografía, estampa…',
             'en': 'Films written in code in 66 styles: watercolour, risograph, woodblock…'}},
    {'id': 'prompt-motion', 'level': 'optional', 'kind': 'kit', 'mb': 370, 'needs': ['node'], 'outside': CACHE_NOTE,
     'title': {'fr': 'Interfaces animées', 'es': 'Interfaces animadas', 'en': 'Animated interfaces'},
     'why': {'fr': 'Démonstrations d\'interface animées et film d\'une présentation.', 'es': 'Demostraciones de interfaz animadas y película de una presentación.',
             'en': 'Animated interface demos and the film of a presentation.'}},
    {'id': 'hyperframes', 'level': 'optional', 'kind': 'kit', 'mb': None, 'needs': ['node'], 'outside': 'Se range dans le cache de npm, hors du dossier du kit.',
     'title': {'fr': 'HyperFrames', 'es': 'HyperFrames', 'en': 'HyperFrames'},
     'why': {'fr': 'Blocs prêts à l\'emploi en HTML : cartes, transitions, titres.', 'es': 'Bloques listos en HTML: tarjetas, transiciones, títulos.', 'en': 'Ready-made HTML blocks: cards, transitions, titles.'}},
    {'id': 'design-check', 'level': 'optional', 'kind': 'kit', 'mb': 20, 'needs': ['node'],
     'title': {'fr': 'Contrôle de design', 'es': 'Control de diseño', 'en': 'Design check'},
     'why': {'fr': 'Relit les pages livrées et signale les défauts de mise en page. Conseille, ne bloque pas.', 'es': 'Revisa las páginas entregadas y señala defectos de maquetación. Aconseja, no bloquea.',
             'en': 'Reviews delivered pages and points out layout defects. Advises, never blocks.'}},
    {'id': 'blender', 'level': 'optional', 'kind': 'system', 'mb': 400, 'licence': 'GPL',
     'title': {'fr': 'Blender', 'es': 'Blender', 'en': 'Blender'},
     'why': {'fr': 'Rendu 3D d\'une mascotte. Sans lui, la 3D du moteur de création reste disponible.', 'es': 'Render 3D de una mascota. Sin él, el 3D del motor de creación sigue disponible.',
             'en': '3D render of a mascot. Without it, the creation engine\'s 3D still works.'},
     'packages': {'winget': 'BlenderFoundation.Blender', 'brew': '--cask blender', 'apt-get': 'blender', 'dnf': 'blender', 'pacman': 'blender'}, 'site': 'https://www.blender.org/download/'},
    {'id': 'git', 'level': 'optional', 'kind': 'system', 'mb': 60, 'licence': 'GPL',
     'title': {'fr': 'Git', 'es': 'Git', 'en': 'Git'},
     'why': {'fr': 'Sert seulement à récupérer des démonstrations de styles et le module de montage Herk.', 'es': 'Solo sirve para obtener demostraciones de estilos y el módulo de montaje Herk.',
             'en': 'Only used to fetch style demos and the Herk editing module.'},
     'packages': {'winget': 'Git.Git', 'brew': 'git', 'apt-get': 'git', 'dnf': 'git', 'pacman': 'git', 'zypper': 'git'}, 'site': 'https://git-scm.com/downloads'},
    {'id': 'uv', 'level': 'optional', 'kind': 'system', 'mb': 20, 'licence': 'MIT ou Apache-2.0',
     'title': {'fr': 'uv', 'es': 'uv', 'en': 'uv'},
     'why': {'fr': 'Accélère l\'installation des options et peut fournir Python 3.13.', 'es': 'Acelera la instalación de las opciones y puede aportar Python 3.13.', 'en': 'Speeds up installing the options and can provide Python 3.13.'},
     'packages': {'winget': 'astral-sh.uv', 'brew': 'uv'}, 'site': 'https://docs.astral.sh/uv/'},
    {'id': 'elevenlabs', 'level': 'optional', 'kind': 'account', 'mb': 0,
     'title': {'fr': 'ElevenLabs (payant)', 'es': 'ElevenLabs (de pago)', 'en': 'ElevenLabs (paid)'},
     'why': {'fr': 'Voix, musique et bruitages de haute qualité. Chaque appel demande ton accord.', 'es': 'Voces, música y efectos de alta calidad. Cada llamada pide tu acuerdo.',
             'en': 'High-quality voices, music and sound effects. Every call needs your approval.'},
     'manual': {'fr': 'La clé se saisit dans la fenêtre d\'installation (INSTALAR.bat), jamais dans la conversation.', 'es': 'La clave se escribe en la ventana de instalación (INSTALAR.bat), nunca en la conversación.',
                'en': 'The key is typed in the installer window (INSTALAR.bat), never in the conversation.'}},
]
BY_ID = {p['id']: p for p in PARTS}
TIERS_OF = {'captions': ['transcribe'], 'voice-local': ['voice'], 'effects': ['effects'], 'film-styles': ['audio']}
SUDO = {'apt-get': 'sudo apt-get install -y', 'dnf': 'sudo dnf install -y', 'pacman': 'sudo pacman -S --needed', 'zypper': 'sudo zypper install -y'}
FEATURES = [
    (['ffmpeg'], 'Monter des clips, des photos, un logo et une musique ; exporter pour YouTube, TikTok, Instagram ou Shorts'),
    (['ffmpeg'], 'Traiter une vidéo fournie : enlever les silences, recadrer en vertical ou en carré'),
    (['ffmpeg', 'captions'], 'Sous-titres, traductions des sous-titres, extraits courts et chapitres'),
    (['engine-remotion'], 'Créer une vidéo à partir d\'une idée : promo, logo animé, photos animées, graphiques, personnage 3D'),
    (['python'], 'Présentation interactive en page web'),
    (['voice-local'], 'Voix off gratuite, hors ligne'),
    (['effects'], 'Effets autour d\'une personne filmée, recadrage qui suit le visage'),
    (['film-styles'], 'Films écrits en code dans 66 styles'),
    (['prompt-motion'], 'Démonstrations d\'interface animées'),
    (['hyperframes'], 'Blocs HyperFrames'),
    (['blender'], 'Mascotte 3D rendue avec Blender'),
    (['elevenlabs'], 'Voix, musique et bruitages ElevenLabs (payant, accord à chaque appel)'),
]


def text(part: dict, key: str, language: str) -> str:
    return part[key].get(language) or part[key]['fr']


def fr(number: float) -> str:
    return f'{number:.1f}'.replace('.', ',')


def size(mb: int | None) -> str:
    return 'taille variable' if mb is None else f'{fr(mb / 1000)} Go' if mb >= 1000 else f'{mb} Mo'


# ------------------------------------------------------------------ looking

def npx_cached(name: str, version: str) -> bool:
    """Whether npx already holds this exact version: it would otherwise download it at first use."""
    cache = os.environ.get('npm_config_cache')
    root = Path(cache) if cache else Path(os.environ.get('LOCALAPPDATA') or Path.home() / 'AppData/Local') / 'npm-cache' if platform.system() == 'Windows' else Path.home() / '.npm'
    for f in (root / '_npx').glob(f'*/node_modules/{name}/package.json') if (root / '_npx').exists() else []:
        try:
            if json.loads(f.read_text(encoding='utf-8')).get('version') == version:
                return True
        except (OSError, ValueError):
            continue
    return False


def snapshot(machine: dict | None = None) -> dict:
    m, s = machine or diagnostic.machine(), diagnostic.software()
    return {'machine': m, 'software': s, 'kit': diagnostic.kit(), 'conflicts': diagnostic.conflicts(m, s)}


def present(seen: dict) -> dict:
    """For each part: is it there and usable, and its version when it has one."""
    s, k = seen['software'], seen['kit']
    tiers = k['tiers']
    hf = npx_cached('hyperframes', PINS['hyperframes'])
    return {
        'python': (s['python']['ok'], s['python']['version']),
        'ffmpeg': (s['ffmpeg']['found'] and s['ffmpeg']['ok'] is not False and s['ffprobe']['found'], s['ffmpeg'].get('version')),
        'node': (bool(s['node']['found'] and s['node']['ok'] and s['npm']['found']), s['node'].get('version')),
        'engine-remotion': (k['remotion']['installed'] and k['remotion']['browser'], k['remotion']['version']),
        'captions': (tiers['transcribe'] and k['whisper_model'], None),
        'python-modules': (bool(s['python']['for_modules']) or s['uv']['found'], s['python']['for_modules'] or ('uv' if s['uv']['found'] else None)),
        'voice-local': (tiers['voice'] and bool(k['packs'].get('voice-model')), None),
        'effects': (tiers['effects'], None),
        'film-styles': (k['film']['installed'] and k['film']['browser'] and tiers['audio'], k['film']['version']),
        'prompt-motion': (k['prompt-motion']['installed'] and k['prompt-motion']['browser'], k['prompt-motion']['version']),
        'hyperframes': (hf, PINS['hyperframes'] if hf else None),
        'design-check': (k['design-check']['installed'], None),
        'blender': (s['blender']['found'], s['blender']['version']),
        'git': (s['git']['found'], s['git'].get('version')),
        'uv': (s['uv']['found'], s['uv'].get('version')),
        'elevenlabs': (s['elevenlabs_key']['found'], None),
    }


def system_command(part: dict, manager: dict) -> tuple[list | None, str | None]:
    """(what the kit can run itself once approved, what the person has to do by hand). Exactly one of the two is set."""
    packages = part.get('packages', {})
    name = manager.get('name') if manager.get('found') else None
    if name == 'winget' and packages.get('winget'):
        # The two "accept" flags answer winget's licence questions: they are only ever used after the person said yes to this very tool
        return ['winget', 'install', '--id', packages['winget'], '-e', '--silent', '--accept-source-agreements', '--accept-package-agreements'], None
    if name == 'brew' and packages.get('brew'):
        return ['brew', 'install'] + packages['brew'].split(), None
    if name in SUDO and packages.get(name):  # the administrator password is the person's to type: the kit never does
        return None, f'{SUDO[name]} {packages[name]}'
    return None, f"Télécharger depuis le site officiel : {part['site']}"


def summary(m: dict) -> dict:
    """The machine in the words of its owner."""
    cores = f"{m['cores']} cœurs, " if m.get('cores') else ''
    cards = ' ; '.join(g['name'] + (f" ({fr(g['vram_gb'])} Go)" if g.get('vram_gb') else '') for g in m['gpus']) or 'aucune carte graphique reconnue'
    return {'systeme': f"{m['os']}, {m['arch']}", 'processeur': f"{m['cpu'] or 'processeur non reconnu'} ({cores}{m['threads']} fils)",
            'memoire': f"{fr(m['ram_gb'])} Go" if m.get('ram_gb') else 'inconnue', 'graphique': cards,
            'disque': f"{fr(m['disk_free_gb'])} Go libres sur {fr(m['disk_total_gb'])}"}


def advice(m: dict, encoders: dict | None = None) -> list[str]:
    """What this machine suggests about how to work, so that the first video is not a bad surprise."""
    out = []
    best = max((g.get('vram_gb') or 0 for g in m['gpus']), default=0)
    if m.get('ram_gb') and m['ram_gb'] < 8:
        out.append('Peu de mémoire : faire les essais en qualité brouillon et préférer des vidéos courtes.')
    if best < 2:
        out.append('Pas de carte graphique puissante : les scènes 3D seront lentes. Préférer le 2D ou des durées courtes.')
    if (m.get('threads') or 0) <= 4:
        out.append('Processeur modeste : la transcription d\'une longue vidéo prendra du temps, à peu près sa durée.')
    if m['disk_free_gb'] < config.get('requirements.disk_free_gb_warn', 10):
        out.append('Peu de place sur le disque : éviter les options lourdes et supprimer les essais dont tu n\'as plus besoin.')
    fast = [name for name, ok in (encoders or {}).items() if ok]
    if fast:
        out.append(f"Export des longues vidéos accéléré par la carte graphique ({', '.join(fast)}), vérifié sur cette machine.")
    return out


def plan(seen: dict | None = None, language: str = 'fr') -> dict:
    """The proposal: every part, whether it is already there, and what would be done. Changes nothing."""
    seen = seen or snapshot()
    here = present(seen)
    manager = seen['software']['package_manager']
    rows = []
    for part in PARTS:
        pid = part['id']
        ok, version = here[pid]
        if ok and part.get('hidden'):
            continue
        outdated = not ok and pid in ('python', 'ffmpeg', 'node') and seen['software'][pid]['found']
        row = {'id': pid, 'title': text(part, 'title', language), 'why': text(part, 'why', language), 'level': part['level'],
               'state': 'present' if ok else 'outdated' if outdated else 'missing', 'version': version or (seen['software'][pid].get('version') if outdated else None)}
        if ok:
            row['action'] = 'déjà installé et reconnu : rien à faire'
        else:
            row['size_mb'] = part.get('mb')
            row['needs'] = [n for n in part.get('needs', []) if not here[n][0]]
            if part['kind'] == 'system':
                command, manual = system_command(part, manager)
                row.update(how=manager['name'] if command else 'manual', manual=manual, licence=part.get('licence') if command else None, outside='S\'installe sur l\'ordinateur, hors du dossier du kit, dans la dernière version publiée par son éditeur.')
            elif part['kind'] == 'account':
                row.update(how='manual', manual=text(part, 'manual', language))
            else:
                row.update(how='kit', outside=part.get('outside'))
            row['action'] = (f"à faire à la main : {row['manual']}" if row['how'] == 'manual' else
                             f"à installer avec ton accord ({'dans le dossier du kit' if row['how'] == 'kit' else 'avec ' + row['how']}, gratuit, {size(part.get('mb'))})")
        rows.append(row)
    todo = [r for r in rows if r['state'] != 'present' and r['how'] != 'manual']
    return {'machine': summary(seen['machine']), 'rows': rows, 'conflicts': seen['conflicts'], 'advice': advice(seen['machine'], state.load().get('encoders')),
            'to_approve': {level: [r['id'] for r in todo if r['level'] == level] for level in ('required', 'recommended', 'optional')},
            'by_hand': [{'id': r['id'], 'title': r['title'], 'manual': r['manual']} for r in rows if r['state'] != 'present' and r['how'] == 'manual'],
            'required_mb': sum(r.get('size_mb') or 0 for r in todo if r['level'] == 'required')}


# ------------------------------------------------------------------ installing, only what was approved

def run(cmd: list, cwd: Path | None = None, env: dict | None = None, check: bool = True) -> str:
    start = time.time()
    r = subprocess.run([str(c) for c in cmd], cwd=cwd, env={**os.environ, **QUIET, **(env or {})}, capture_output=True, text=True, encoding='utf-8', errors='replace')
    logs.write('command', command=' '.join(str(c) for c in cmd), where=str(cwd or ''), code=r.returncode, seconds=round(time.time() - start, 1), tail=(r.stderr or r.stdout)[-600:] if r.returncode else '')
    if r.returncode and check:
        raise RuntimeError((r.stderr or r.stdout).strip()[-900:] or f'code {r.returncode}')
    return r.stdout


def refresh_path() -> None:
    """A tool installed a moment ago is not on this process's PATH yet: Windows keeps the new one in the registry."""
    if platform.system() != 'Windows':
        return
    import winreg
    fresh = []
    for hive, key in ((winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'), (winreg.HKEY_CURRENT_USER, 'Environment')):
        try:
            with winreg.OpenKey(hive, key) as k:
                fresh += os.path.expandvars(winreg.QueryValueEx(k, 'Path')[0]).split(os.pathsep)
        except OSError:
            continue
    known = os.environ.get('PATH', '').split(os.pathsep)
    os.environ['PATH'] = os.pathsep.join(known + [p for p in fresh if p and p not in known])


def _npm() -> str:
    path = shutil.which('npm')
    if not path:
        raise RuntimeError('npm introuvable : il arrive avec Node.js.')
    return path


def _install_remotion(run_) -> None:
    run_([_npm(), 'ci', '--no-fund', '--no-audit'], cwd=ROOT / 'template')
    run_(['node', 'node_modules/@remotion/cli/remotion-cli.js', 'browser', 'ensure'], cwd=ROOT / 'template')


def _install_prompt_motion(run_) -> None:
    run_([_npm(), 'ci', '--no-fund', '--no-audit'], cwd=ROOT / 'prompt-motion')
    run_(['node', 'node_modules/playwright/cli.js', 'install', 'chromium'], cwd=ROOT / 'prompt-motion')


def _install_hyperframes(run_) -> None:
    npx = shutil.which('npx')
    if not npx:
        raise RuntimeError('npx introuvable : il arrive avec Node.js.')
    run_([npx, '--yes', f"hyperframes@{PINS['hyperframes']}", 'doctor'], cwd=ROOT / 'hyperframes-starter', check=False)


def _install_captions(run_) -> None:
    modules.install_tier('transcribe')
    modules.install_whisper(approved=True)


def _install_voice(run_) -> None:
    modules.install_tier('voice')
    modules.install_pack('voice-model', approved=True)


def _install_film(run_) -> None:
    modules.install_film()
    modules.install_tier('audio')


def _install_design(run_) -> None:
    from . import design_check
    design_check.install()


INSTALLERS = {'engine-remotion': _install_remotion, 'prompt-motion': _install_prompt_motion, 'hyperframes': _install_hyperframes, 'captions': _install_captions,
              'voice-local': _install_voice, 'effects': lambda run_: modules.install_tier('effects'), 'film-styles': _install_film, 'design-check': _install_design}


def ensure_profile() -> str:
    """The user's own folder, created empty from the template once. Never overwritten."""
    target, template = ROOT / 'perfil', ROOT / 'perfil-plantilla'
    if target.exists():
        return 'profil conservé'
    if not template.exists():
        return 'modèle de profil absent'
    shutil.copytree(template, target)
    return 'profil vierge créé'


def _record(pid: str, status: str, detail: str = '') -> None:
    st = state.load()
    st.pop('note', None)
    st['steps'][pid] = {'status': status, 'at': state.now(), 'detail': detail[:300]}
    state.save(st)


def decline(ids: list[str]) -> dict:
    """Remembers a refusal, so that the report says "not installed at your request" instead of calling it a failure."""
    st = state.load()
    st.pop('note', None)
    for pid in ids:
        if pid in BY_ID:
            st['consent'][pid] = {'declined': True, 'at': state.now()}
    state.save(st)
    logs.write('declined', parts=ids)
    return {'declined': [i for i in ids if i in BY_ID]}


def apply(approved: list[str], *, force: bool = False, installers: dict | None = None, runner=None, look=None) -> dict:
    """Installs the parts named in `approved`, and nothing else. `force` reinstalls a kit part that is there but broken."""
    installers, runner, look = installers or INSTALLERS, runner or run, look or snapshot
    seen = look()
    results = [{'id': a, 'result': 'unknown', 'detail': 'élément inconnu'} for a in approved if a not in BY_ID]
    for part in [p for p in PARTS if p['id'] in approved]:
        pid = part['id']
        here = present(seen)
        if here[pid][0] and not (force and part['kind'] == 'kit'):
            results.append({'id': pid, 'result': 'already', 'detail': 'déjà installé et reconnu' + (f' (version {here[pid][1]})' if here[pid][1] else '') + ' : rien n\'a été refait'})
            continue
        lacking = [n for n in part.get('needs', []) if not here[n][0]]
        if lacking:
            results.append({'id': pid, 'result': 'blocked', 'detail': 'demande d\'abord : ' + ', '.join(text(BY_ID[n], 'title', 'fr') for n in lacking)})
            continue
        command, manual = system_command(part, seen['software']['package_manager']) if part['kind'] == 'system' else (None, text(part, 'manual', 'fr') if part['kind'] == 'account' else None)
        if manual:
            results.append({'id': pid, 'result': 'manual', 'detail': manual})
            continue
        st = state.load()
        st.pop('note', None)
        st['consent'][pid] = {'approved': True, 'at': state.now()}
        state.save(st)
        _record(pid, 'running')
        logs.write('install-start', part=pid, how='system' if command else 'kit')
        if force:  # a repair must really reinstall: the marker of a finished install would make it a no-op
            for tier in TIERS_OF.get(pid, []):
                modules._marker(tier).unlink(missing_ok=True)
        try:
            if command:
                runner(command)
                refresh_path()
            else:
                installers[pid](runner)
            seen = look(seen['machine'])
            if not present(seen)[pid][0]:
                raise RuntimeError('l\'installation s\'est terminée, mais l\'élément reste introuvable' + (' : fermer et rouvrir Claude Code, puis relancer la vérification' if command else ''))
            status, detail = check(pid, deep=False)
        except (RuntimeError, OSError, ValueError, KeyError, subprocess.SubprocessError) as e:
            status, detail = FAILED, str(e).strip()[-600:]
        _record(pid, 'done' if status != FAILED else 'failed', detail)
        if status != FAILED:
            st = state.load()
            if not any(x.get('id') == pid for x in st['installed_by_kit']):
                st['installed_by_kit'].append({'id': pid, 'kind': part['kind'], 'at': state.now(), 'how': command[0] if command else 'kit'})
                state.save(st)
        logs.write('install-end', part=pid, status=status, detail=detail)
        results.append({'id': pid, 'result': 'installed' if status != FAILED else 'failed', 'status': status, 'detail': detail})
    return {'results': results, 'profile': ensure_profile(), 'next': 'Lancer la vérification complète (setup verify --deep) avant de dire que c\'est prêt.'}


# ------------------------------------------------------------------ checking for real

def _check_ffmpeg(deep: bool) -> tuple[str, str]:
    with tempfile.TemporaryDirectory(prefix='kit-ff-') as tmp:
        out = Path(tmp) / 'essai.mp4'
        r = subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'lavfi', '-i', 'testsrc2=s=320x180:r=25:d=1', '-f', 'lavfi', '-i', 'sine=f=440:d=1',
                            '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', str(out)], capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=120)
        if r.returncode or not out.exists():
            return FAILED, 'FFmpeg est là mais n\'a pas encodé la vidéo d\'essai : ' + r.stderr.strip()[-200:]
        length = diagnostic._out(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(out)])
        if not length or abs(float(length.splitlines()[0]) - 1) > .3:
            return FAILED, 'ffprobe ne relit pas la vidéo d\'essai'
    return READY, 'une vidéo d\'essai encodée puis relue'


def _check_node(deep: bool) -> tuple[str, str]:
    answer = diagnostic._out(['node', '-e', 'process.stdout.write(process.version)'])
    return (READY, 'exécute du code') if answer else (FAILED, 'Node est là mais ne répond pas')


def _check_captions(deep: bool) -> tuple[str, str]:
    if not deep:
        return READY, 'outil et modèle présents'
    from . import voice_kokoro
    with tempfile.TemporaryDirectory(prefix='kit-tr-') as tmp:
        tone = Path(tmp) / 'ton.wav'
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'lavfi', '-i', 'sine=f=300:d=2', str(tone)], check=True, capture_output=True, timeout=60)
        voice_kokoro.transcribe_full(tone, Path(tmp) / 'mots.json', 'fr')
    return READY, 'le modèle se charge et transcrit hors ligne'


def _check_voice(deep: bool) -> tuple[str, str]:
    if not deep:
        return READY, 'moteur et modèle de voix présents'
    from . import voice_kokoro
    with tempfile.TemporaryDirectory(prefix='kit-voix-') as tmp:
        out = Path(tmp) / 'essai.wav'
        voice_kokoro.synthesize('Bonjour.', out, 'fr')
        if not out.exists() or out.stat().st_size < 2000:
            return FAILED, 'aucun son produit'
    return READY, 'une phrase d\'essai prononcée hors ligne'


def _check_effects(deep: bool) -> tuple[str, str]:
    if not deep:
        return READY, 'module présent'
    r = modules.run_python(['-c', 'import cv2, mediapipe; print(cv2.__version__)'], tier='effects')
    return (READY, f'détection chargée (OpenCV {r.stdout.strip()})') if r.returncode == 0 else (FAILED, r.stderr.strip()[-200:])


def _check_film(deep: bool) -> tuple[str, str]:
    example = ROOT / 'examples/film-style/riso-pain'
    if not deep or not example.exists():
        return READY, 'moteur et navigateur de rendu présents'
    from . import film_style
    with tempfile.TemporaryDirectory(prefix='kit-film-') as tmp:
        made = film_style.stills(example, [5.0], profile='draft', out=Path(tmp))
        if not made or not Path(made[0]).exists():
            return FAILED, 'aucune image rendue'
    return READY, 'une image du film d\'exemple rendue'


def _check_prompt_motion(deep: bool) -> tuple[str, str]:
    if not deep:
        return READY, 'moteur et navigateur présents'
    code = "const {chromium}=require('playwright');chromium.launch().then(b=>b.close()).then(()=>process.stdout.write('ok'))"
    r = subprocess.run(['node', '-e', code], cwd=ROOT / 'prompt-motion', capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=120)
    return (READY, 'le navigateur de rendu démarre') if r.stdout.strip() == 'ok' else (FAILED, (r.stderr or r.stdout).strip()[-200:])


def _check_design(deep: bool) -> tuple[str, str]:
    from . import design_check
    return (READY, 'empreinte du détecteur vérifiée') if design_check.verified() else (FAILED, 'empreinte du détecteur différente de celle attendue : il ne sera pas lancé')


CHECKS = {
    'python': lambda deep: (READY, 'version suffisante'),
    'ffmpeg': _check_ffmpeg, 'node': _check_node,
    'engine-remotion': lambda deep: (READY, 'fichiers présents à la version fixée'),
    'captions': _check_captions, 'voice-local': _check_voice, 'effects': _check_effects, 'film-styles': _check_film, 'prompt-motion': _check_prompt_motion,
    'hyperframes': lambda deep: (READY, 'version fixée déjà en cache'),
    'design-check': _check_design,
    'blender': lambda deep: (READY, 'trouvé' + ('' if shutil.which('blender') else ' dans son dossier d\'installation')),
    'git': lambda deep: (READY, 'présent'), 'uv': lambda deep: (READY, 'présent'), 'python-modules': lambda deep: (READY, 'présent'),
    'elevenlabs': lambda deep: (READY, 'clé présente, valeur jamais lue. Service payant : chaque appel demande ton accord'),
}


def check(pid: str, deep: bool) -> tuple[str, str]:
    """One part, tested. A check that crashes is a failed check, never a crash of the assistant."""
    try:
        return CHECKS[pid](deep)
    except Exception as e:  # noqa: BLE001 - whatever breaks here is exactly what must be reported
        return FAILED, f'{type(e).__name__} : {str(e).strip()[-300:]}'


def end_to_end(creation: bool = True) -> dict:
    """One small video from start to end with the kit's own pipeline: files read, request routed, video made, quality checked.
    The result is kept in out/essai-installation so that the person can open it."""
    from . import manifest, perfil
    from .inventory import inspect
    from .router import route
    from .run import run_project
    keep = ROOT / 'out' / 'essai-installation'
    result: dict = {}
    saved = perfil.DIR
    with tempfile.TemporaryDirectory(prefix='kit-essai-') as tmp:
        tmp = Path(tmp)
        perfil.DIR = tmp / 'perfil'  # a test video must not be remembered as one of the person's

        def attempt(name: str, build) -> dict:
            start = time.time()
            try:
                project = build()
                path = tmp / f'{name}.json'
                manifest.save(project, path)
                done = run_project(path, 'draft', tmp / 'out')
                video = tmp / 'out' / name / f'{name}.mp4'
                if done['status'] != 'delivered' or not video.exists():
                    problems = done['results'][0]['qc'].get('blocking') or ['aucun fichier produit']
                    return {'status': FAILED, 'detail': 'le contrôle qualité refuse la vidéo : ' + ' ; '.join(problems)[:300]}
                keep.mkdir(parents=True, exist_ok=True)
                shutil.copy2(video, keep / video.name)
                return {'status': READY, 'detail': f"vidéo de {done['results'][0]['qc'].get('duration')} s faite et contrôlée en {round(time.time() - start)} s", 'file': str(keep / video.name)}
            except Exception as e:  # noqa: BLE001 - the test exists to catch whatever goes wrong
                return {'status': FAILED, 'detail': f'{type(e).__name__} : {str(e).strip()[-300:]}'}

        def montage() -> dict:
            clip = tmp / 'source.mp4'
            subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'lavfi', '-i', 'testsrc2=s=640x360:r=25:d=3', '-f', 'lavfi', '-i', 'sine=f=330:d=3',
                            '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', str(clip)], check=True, capture_output=True, timeout=120)
            logo = ROOT / 'examples/medios/logo-demo.png'
            if not logo.exists():
                from . import fixtures
                logo = fixtures.build(full=False)['logo']
            return route('Ajoute mon logo à cette vidéo', [inspect(str(clip)), inspect({'path': str(logo), 'role': 'logo'})], name='essai-montage', language='fr', profile={})

        try:
            result['montage'] = attempt('essai-montage', montage)
            if creation:
                result['creation'] = attempt('essai-creation', lambda: route('Bienvenue. Ton studio vidéo est prêt.', [], name='essai-creation', language='fr', fmt='9:16',
                                                                              intent=['CREATE_FROM_SCRATCH'], profile={}))
        finally:
            perfil.DIR = saved
    return result


def verify(deep: bool = False) -> dict:
    """Every part with its state: READY, WARNING, FAILED or OPTIONAL. `deep` also runs each engine and makes the test videos."""
    seen = snapshot()
    here = present(seen)
    st = state.load()
    declined = {k for k, v in st['consent'].items() if v.get('declined')}
    rows = []
    for part in PARTS:
        pid = part['id']
        ok, version = here[pid]
        if part.get('hidden'):
            continue
        if ok:
            status, detail = check(pid, deep)
        elif part['level'] == 'required':
            status, detail = (WARNING, f"non installé à ta demande : {part['without']}") if pid in declined else (FAILED, f"absent : {part['without']}")
        else:
            status, detail = OPTIONAL, 'non installé' + (', recommandé' if part['level'] == 'recommended' else '') + f" ({size(part.get('mb'))})"
        rows.append({'id': pid, 'title': text(part, 'title', 'fr'), 'level': part['level'], 'status': status, 'version': version, 'detail': detail})
    for i, c in enumerate(seen['conflicts'], 1):
        rows.append({'id': f'machine-{i}', 'title': 'Machine', 'level': 'required', 'status': c['level'], 'version': None, 'detail': f"{c['what']} {c['effect']}"})
    by_id = {r['id']: r for r in rows}
    test = None
    if deep:
        test = end_to_end(creation=here['engine-remotion'][0]) if here['ffmpeg'][0] else {'montage': {'status': FAILED, 'detail': 'FFmpeg absent : essai impossible'}}
        for key, pid, label in (('montage', 'ffmpeg', 'Essai vidéo : montage'), ('creation', 'engine-remotion', 'Essai vidéo : création')):
            if test.get(key):
                rows.append({'id': f'essai-{key}', 'title': label, 'level': 'required', 'status': test[key]['status'], 'version': None, 'detail': test[key]['detail'], 'file': test[key].get('file')})
                if test[key]['status'] == FAILED and by_id[pid]['status'] == READY:
                    by_id[pid].update(status=FAILED, detail='présent, mais l\'essai vidéo a échoué')
                elif test[key]['status'] == READY and by_id[pid]['status'] == READY:
                    by_id[pid]['detail'] += ' ; une vidéo d\'essai rendue pour de vrai'
    blocking = [r for r in rows if r['status'] == FAILED and r['level'] == 'required']
    soft = [r for r in rows if r['status'] in (WARNING, FAILED) and r not in blocking]
    verdict = FAILED if blocking else WARNING if soft else READY
    encoders = diagnostic.test_encoders() if deep and here['ffmpeg'][0] else st.get('encoders') or {}
    report = {'verdict': verdict, 'deep': deep, 'at': state.now(), 'rows': rows, 'machine': summary(seen['machine']), 'advice': advice(seen['machine'], encoders),
              'counts': {s: sum(r['status'] == s for r in rows) for s in (READY, WARNING, FAILED, OPTIONAL)},
              'note': None if deep else 'Vérification rapide : les moteurs n\'ont pas été relancés et aucune vidéo d\'essai n\'a été faite. Seule la vérification complète permet de dire « prêt ».'}
    st = state.load()
    st.pop('note', None)
    st['components'] = {r['id']: {'status': r['status'], 'version': r['version'], 'detail': r['detail']} for r in rows}
    st['encoders'] = encoders
    if deep:
        st.update(configured=verdict != FAILED, verified_at=report['at'], verdict=verdict)
        (logs.DIR).mkdir(exist_ok=True)
        (logs.DIR / 'dernier-rapport.md').write_text(report_text(report), encoding='utf-8')
    state.save(st)
    logs.write('verify', deep=deep, verdict=verdict, rows=[{k: r[k] for k in ('id', 'status', 'detail')} for r in rows])
    return report


def report_text(report: dict) -> str:
    lines = [f"# État du kit : {report['verdict']}", '', f"Vérifié le {report['at'].replace('T', ' à ')}.", '', '| Élément | État | Version | Détail |', '|---|---|---|---|']
    lines += [f"| {r['title']} | {r['status']} | {r['version'] or ''} | {r['detail']} |" for r in report['rows']]
    lines += ['', 'READY : présent et vérifié. WARNING : fonctionne avec une limite. FAILED : à réparer. OPTIONAL : non installé, disponible sur demande.']
    if report.get('advice'):
        lines += ['', 'Conseils pour cette machine :'] + [f'- {a}' for a in report['advice']]
    return '\n'.join(lines) + '\n'


# ------------------------------------------------------------------ the way in

QUICK = {
    'ffmpeg': lambda: bool(shutil.which('ffmpeg') and shutil.which('ffprobe')),
    'node': lambda: bool(shutil.which('node')),
    'engine-remotion': lambda: (ROOT / 'template/node_modules/remotion/package.json').exists() and (ROOT / 'template/node_modules/.remotion').exists(),
    'captions': lambda: (modules.WHISPER_DIR / 'model.bin').exists() and (modules.VENV / '.tier-transcribe').exists(),
    'voice-local': lambda: (modules.VENV / '.tier-voice').exists() and (modules.OPUSCAR / 'core/tts/kokoro-v1.0.onnx').exists(),
    'effects': lambda: (modules.VENV / '.tier-effects').exists(),
    'film-styles': lambda: (modules.OPUSCAR / 'node_modules/playwright-core').exists(),
    'prompt-motion': lambda: (ROOT / 'prompt-motion/node_modules/playwright').exists(),
    'design-check': lambda: (modules.DIR / 'design-check/node_modules/impeccable').exists(),
}


def features(ready: set) -> dict:
    return {'pret': [label for needs, label in FEATURES if set(needs) <= ready],
            'sur_demande': [{'quoi': label, 'demande': [text(BY_ID[n], 'title', 'fr') for n in needs if n not in ready],
                             'taille': size(sum(BY_ID[n].get('mb') or 0 for n in needs if n not in ready))} for needs, label in FEATURES if not set(needs) <= ready]}


def start(language: str = 'fr') -> dict:
    """What to do right now. Instant when the kit is configured: files and PATH only, nothing is launched."""
    st = state.load()
    interrupted = [k for k, v in st['steps'].items() if v.get('status') == 'running']
    failed = [k for k, v in st['steps'].items() if v.get('status') == 'failed']
    if not st['configured']:
        proposal = plan(language=language)
        resume = bool(st['steps'] or st['consent'])
        return {'phase': 'resume' if resume else 'first-launch', 'note': st.get('note'), 'interrupted': interrupted, 'failed': failed, **proposal,
                'next': ('Une installation a commencé et n\'est pas terminée : dire où elle en est, proposer de la reprendre, puis vérifier.' if resume else
                         'Premier lancement : présenter la machine et le tableau en mots simples, demander l\'accord pour chaque élément à installer, '
                         'installer seulement ce qui est accepté, puis lancer la vérification complète.')}
    ready = {pid for pid, c in st['components'].items() if c.get('status') == READY and pid in BY_ID}
    lost = [text(BY_ID[pid], 'title', 'fr') for pid in sorted(ready) if pid in QUICK and not QUICK[pid]()]
    if lost or interrupted:
        return {'phase': 'repair', 'lost': lost, 'interrupted': interrupted, 'failed': failed,
                'next': 'Quelque chose qui fonctionnait ne répond plus : lancer le diagnostic de réparation, expliquer, demander l\'accord, réparer, vérifier.'}
    return {'phase': 'ready', 'verified_at': st.get('verified_at'), 'verdict': st.get('verdict'), 'features': features(ready),
            'advice': advice_from_state(st), 'warnings': [f"{c.get('detail')}" for pid, c in st['components'].items() if c.get('status') in (WARNING, FAILED)],
            'next': 'Le kit est prêt : demander quel projet vidéo la personne veut réaliser. Ne rien réinstaller.'}


def advice_from_state(st: dict) -> list[str]:
    fast = [name for name, ok in (st.get('encoders') or {}).items() if ok]
    return [f"Export des longues vidéos accéléré par la carte graphique ({', '.join(fast)}), vérifié sur cette machine."] if fast else []


def repair(approved: list[str] | None = None) -> dict:
    """Looks again, says what is broken and what would fix it. Fixes only what is named in `approved`."""
    if approved:
        done = apply(approved, force=True)
        return {**done, 'report': verify(deep=False)}
    report = verify(deep=False)
    st = state.load()
    broken = [r for r in report['rows'] if r['status'] == FAILED and r['id'] in BY_ID]
    stuck = [k for k, v in st['steps'].items() if v.get('status') in ('running', 'failed') and k not in [b['id'] for b in broken]]
    proposal = {r['id']: r for r in plan()['rows']}
    fixes = []
    for pid in [b['id'] for b in broken] + stuck:
        part, row = BY_ID[pid], proposal.get(pid, {})
        fixes.append({'id': pid, 'title': text(part, 'title', 'fr'), 'problem': next((b['detail'] for b in broken if b['id'] == pid), 'installation interrompue'),
                      'fix': row.get('manual') and f"à faire à la main : {row['manual']}" or f"réinstaller ({size(part.get('mb'))}), avec ton accord",
                      'by_hand': bool(row.get('manual'))})
    return {'report': report, 'fixes': fixes,
            'next': 'Rien à réparer.' if not fixes else 'Expliquer chaque problème, demander l\'accord, puis réparer seulement ce qui est accepté.'}


# ------------------------------------------------------------------ leaving

REMOVABLE = [
    ('engine-remotion', 'Moteur de création et son navigateur de rendu', ['template/node_modules']),
    ('prompt-motion', 'Moteur d\'interfaces animées', ['prompt-motion/node_modules']),
    ('film-styles', 'Moteur des styles de films', ['modules/opuscar/node_modules', 'modules/opuscar/.source', 'modules/opuscar/.release']),
    ('design-check', 'Contrôle de design', ['modules/design-check/node_modules']),
    ('options', 'Environnement des options : voix, sous-titres, effets, son', ['modules/.venv']),
    ('models', 'Modèles de voix et de transcription, instruments', ['modules/models', 'modules/opuscar/core/tts/kokoro-v1.0.onnx', 'modules/opuscar/core/tts/voices-v1.0.bin',
                                                                   'modules/opuscar/core/audio/instruments']),
    ('work-copies', 'Copies de travail des médias et fichiers générés', ['template/public/universal', 'modules/three-studio/node_modules', 'modules/three-studio/dist']),
    ('state', 'État de l\'installation et journaux techniques', ['kit-state.json', 'logs']),
]
KEPT = [('perfil', 'ton profil : goûts, marques, historique'), ('out', 'tes vidéos et tes projets'), ('kit.config.local.json', 'tes réglages')]


def weight(path: Path) -> int:
    if path.is_symlink() or not path.exists():
        return 0
    if path.is_file():
        return path.stat().st_size
    total = 0
    stack = [path]
    while stack:
        try:
            with os.scandir(stack.pop()) as it:
                for entry in it:
                    if entry.is_symlink():
                        continue
                    if entry.is_dir(follow_symlinks=False):
                        stack.append(Path(entry.path))
                    else:
                        total += entry.stat(follow_symlinks=False).st_size
        except OSError:
            continue
    return total


def _inside(rel: str) -> Path:
    """The path, only if it is one of the kit's own generated places. Anything else is refused."""
    allowed = {p for _, _, paths in REMOVABLE for p in paths}
    target = (ROOT / rel)
    if rel not in allowed or ROOT.resolve() not in target.resolve().parents:
        raise ValueError(f'Suppression refusée : {rel} n\'est pas un dossier généré par le kit.')
    return target


def uninstall(approved: list[str] | None = None) -> dict:
    """Without `approved`: the list of what can go, with sizes, and what stays. With it: removes only the named groups, inside the kit only."""
    st = state.load()
    groups = []
    for gid, label, paths in REMOVABLE:
        there = [p for p in paths if (ROOT / p).exists()]
        if there:
            groups.append({'id': gid, 'what': label, 'paths': there, 'size_mb': round(sum(weight(ROOT / p) for p in there) / 1e6)})
    outside = []
    cache = diagnostic.browsers_cache()
    if cache.exists():
        outside.append({'what': 'Navigateurs de rendu téléchargés par Playwright', 'where': logs.scrub(cache), 'size_mb': round(weight(cache) / 1e6),
                        'how': 'Dossier à supprimer à la main. D\'autres logiciels peuvent s\'en servir.'})
    if npx_cached('hyperframes', PINS['hyperframes']):
        outside.append({'what': 'HyperFrames dans le cache de npm', 'how': 'Il part avec le nettoyage du cache de npm.'})
    for item in st['installed_by_kit']:
        if item.get('kind') == 'system' and item.get('id') in BY_ID:
            outside.append({'what': f"{text(BY_ID[item['id']], 'title', 'fr')}, installé par le kit le {item.get('at', '')[:10]}",
                            'how': 'À désinstaller depuis les paramètres du système, rubrique des applications installées. D\'autres logiciels peuvent en avoir besoin.'})
    if diagnostic.secret_present('ELEVENLABS_API_KEY'):
        outside.append({'what': 'Clé ElevenLabs enregistrée dans tes variables d\'environnement', 'how': 'À retirer depuis les paramètres du système, variables d\'environnement du compte. Le kit ne la lit ni ne l\'efface.'})
    kept = [{'what': label, 'where': name} for name, label in KEPT if (ROOT / name).exists()]
    if not approved:
        return {'removable': groups, 'kept': kept, 'outside_the_kit': outside,
                'next': 'Montrer la liste et les tailles, demander ce qui doit partir, puis relancer avec les éléments acceptés. '
                        'Le profil, les vidéos et les réglages ne sont jamais supprimés par le kit : pour tout effacer, la personne supprime elle-même le dossier.'}
    removed, refused = [], [a for a in approved if a not in {g for g, _, _ in REMOVABLE}]
    for gid, label, paths in REMOVABLE:
        if gid not in approved:
            continue
        freed = 0
        for rel in paths:
            target = _inside(rel)
            if not target.exists():
                continue
            freed += weight(target)
            if target.is_dir() and not target.is_symlink():
                shutil.rmtree(target, ignore_errors=True)
            else:
                target.unlink(missing_ok=True)
        if gid != 'state':
            logs.write('uninstall', group=gid, freed_mb=round(freed / 1e6))
        removed.append({'id': gid, 'what': label, 'freed_mb': round(freed / 1e6)})
    if 'state' not in approved and state.FILE.exists():
        st = state.load()
        st.update(configured=False, components={}, steps={})
        state.save(st)
    return {'removed': removed, 'refused': refused, 'kept': kept, 'outside_the_kit': outside}


# ------------------------------------------------------------------ staying current

def _get(url: str) -> dict | None:
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'motion-design-kit'}), timeout=8) as r:
            return json.loads(r.read().decode('utf-8'))
    except (OSError, ValueError):
        return None


def pinned() -> list[dict]:
    rows = []
    for project, package in (('template', 'remotion'), ('template', 'three'), ('template', 'react'), ('prompt-motion', 'playwright'), ('modules/opuscar', 'playwright-core'),
                             ('modules/design-check', 'impeccable')):
        version = diagnostic.lock_version(project, package)
        if version:
            rows.append({'name': package, 'where': project, 'pinned': version, 'registry': 'npm'})
    rows.append({'name': 'hyperframes', 'where': 'cache de npm', 'pinned': PINS['hyperframes'], 'registry': 'npm'})
    wanted = {'mediapipe', 'opencv-python', 'opencv-python-headless', 'kokoro-onnx', 'faster-whisper', 'onnxruntime'}
    seen = set()
    for lock in sorted(modules.LOCKS.glob('*.lock')):
        for line in lock.read_text(encoding='utf-8', errors='replace').splitlines():
            name, _, rest = line.partition('==')
            if name in wanted and name not in seen and rest:
                seen.add(name)
                rows.append({'name': name, 'where': f'option {lock.stem}', 'pinned': rest.split()[0].rstrip('\\').strip(), 'registry': 'pypi'})
    return rows


def change(pinned_version: str, latest: str | None) -> str:
    if not latest:
        return 'inconnu'
    a, b = diagnostic.numbers(pinned_version), diagnostic.numbers(latest)
    if not a or not b or b <= a:
        return 'à jour'
    if b[0] != a[0] or (a[0] == 0 and b[1:2] != a[1:2]):  # before 1.0, the second number is the one that breaks things
        return 'majeure'
    return 'mineure' if b[1:2] != a[1:2] else 'corrective'


def updates(online: bool = True) -> dict:
    """Compares what the kit fixes with what exists today. Reads only: nothing is ever updated from here."""
    rows = pinned()
    reached = False
    for row in rows:
        latest = None
        if online:
            data = _get(f"https://registry.npmjs.org/{row['name']}/latest") if row['registry'] == 'npm' else _get(f"https://pypi.org/pypi/{row['name']}/json")
            latest = (data or {}).get('version') if row['registry'] == 'npm' else ((data or {}).get('info') or {}).get('version')
            reached = reached or bool(latest)
        row.update(latest=latest, change=change(row['pinned'], latest))
    logs.write('updates', online=online, reached=reached, newer=[r['name'] for r in rows if r['change'] not in ('à jour', 'inconnu')])
    return {'kit': {'version': config.get('kit.version'), 'source': config.get('updates.source'),
                    'how': 'Le kit se met à jour en remplaçant son dossier par une version plus récente. Le profil (perfil), les vidéos (out) et les réglages (kit.config.local.json) se recopient dans le nouveau dossier.'},
            'online': online and reached, 'dependencies': rows,
            'note': 'Rien n\'est mis à jour par cette vérification. Les versions du kit sont fixées et auditées : une plus récente se teste d\'abord, puis s\'adopte avec une nouvelle version du kit et ton accord.'
                    + ('' if reached or not online else ' Les registres n\'ont pas répondu : hors ligne ?')}


# ------------------------------------------------------------------ the same assistant in a console window, for a double click

WORDS = {
    'fr': {'title': 'MOTION DESIGN KIT UNIVERSAL STUDIO : assistant d\'installation', 'machine': 'Ta machine', 'table': 'Ce que le kit utilise',
           'present': 'déjà là', 'missing': 'absent', 'outdated': 'trop ancien', 'required': 'indispensable', 'recommended': 'recommandé', 'optional': 'optionnel',
           'ask': 'Installer {title} ? {why} Gratuit, {size}. {extra}[o/N] ', 'licence': 'L\'installation accepte pour toi sa licence ({licence}). ',
           'nothing': 'Rien à installer : tout ce qu\'il faut est déjà là.', 'hand': 'À faire toi-même', 'installing': 'Installation de {title}…',
           'verifying': 'Vérification complète, avec deux vidéos d\'essai. Cela prend environ une minute…', 'report': 'Résultat', 'noinput': 'Pas de réponse possible ici : rien ne sera installé.',
           'READY': 'Le kit est prêt. Ouvre ce dossier dans Claude Code et dis ce que tu veux créer.', 'WARNING': 'Le kit fonctionne, avec les limites indiquées ci-dessus.',
           'FAILED': 'Le kit n\'est pas prêt : voir les lignes FAILED ci-dessus.'},
    'es': {'title': 'MOTION DESIGN KIT UNIVERSAL STUDIO: asistente de instalación', 'machine': 'Tu equipo', 'table': 'Lo que usa el kit',
           'present': 'ya está', 'missing': 'falta', 'outdated': 'demasiado antiguo', 'required': 'imprescindible', 'recommended': 'recomendado', 'optional': 'opcional',
           'ask': '¿Instalar {title}? {why} Gratis, {size}. {extra}[s/N] ', 'licence': 'La instalación acepta por ti su licencia ({licence}). ',
           'nothing': 'Nada que instalar: todo lo necesario ya está.', 'hand': 'Para hacer tú mismo', 'installing': 'Instalando {title}…',
           'verifying': 'Comprobación completa, con dos vídeos de prueba. Tarda alrededor de un minuto…', 'report': 'Resultado', 'noinput': 'Aquí no se puede responder: no se instalará nada.',
           'READY': 'El kit está listo. Abre esta carpeta en Claude Code y di qué quieres crear.', 'WARNING': 'El kit funciona, con los límites indicados arriba.',
           'FAILED': 'El kit no está listo: mira las líneas FAILED de arriba.'},
    'en': {'title': 'MOTION DESIGN KIT UNIVERSAL STUDIO: setup assistant', 'machine': 'Your machine', 'table': 'What the kit uses',
           'present': 'already there', 'missing': 'missing', 'outdated': 'too old', 'required': 'required', 'recommended': 'recommended', 'optional': 'optional',
           'ask': 'Install {title}? {why} Free, {size}. {extra}[y/N] ', 'licence': 'Installing accepts its licence for you ({licence}). ',
           'nothing': 'Nothing to install: everything needed is already there.', 'hand': 'To do yourself', 'installing': 'Installing {title}…',
           'verifying': 'Full check, with two test videos. This takes about a minute…', 'report': 'Result', 'noinput': 'No answer can be given here: nothing will be installed.',
           'READY': 'The kit is ready. Open this folder in Claude Code and say what you want to make.', 'WARNING': 'The kit works, with the limits listed above.',
           'FAILED': 'The kit is not ready: see the FAILED lines above.'},
}
YES = {'o', 'oui', 's', 'si', 'sí', 'y', 'yes'}


def system_language() -> str:
    try:
        name = (locale.getlocale()[0] or os.environ.get('LANG') or '').lower()
    except (ValueError, TypeError):
        name = ''
    return 'fr' if name.startswith(('fr', 'french')) else 'en' if name.startswith(('en', 'english')) else 'es'


def wizard(language: str | None = None, *, ask=input, say=print, approved: list[str] | None = None, deep: bool = True) -> int:
    """Asks about each missing part in turn. `approved` holds the parts already accepted on the command line, for a run with nobody to answer."""
    lang = language if language in WORDS else system_language()
    w = WORDS[lang]
    say(f"\n  {w['title']}\n")
    proposal = plan(language=lang)
    say(f"  {w['machine']}")
    for value in proposal['machine'].values():
        say(f'    {value}')
    for c in proposal['conflicts']:
        say(f"    [{c['level']}] {c['what']} {c['effect']}")
    say(f"\n  {w['table']}")
    for r in proposal['rows']:
        say(f"    {r['title']:<30} {w[r['state']]:<18} {(r['version'] or ''):<10} {w[r['level']]}")
    todo = [r for r in proposal['rows'] if r['state'] != 'present' and r['how'] != 'manual']
    chosen = [r['id'] for r in todo if r['id'] in (approved or [])]
    asked = [r for r in todo if r['id'] not in chosen]
    if not todo:
        say(f"\n  {w['nothing']}")
    refused = []
    if approved is None:
        say('')
        for r in asked:
            extra = (w['licence'].format(licence=r['licence']) if r.get('licence') else '') + (f"{r['outside']} " if r.get('outside') else '')
            try:
                answer = ask('  ' + w['ask'].format(title=r['title'], why=r['why'], size=size(r.get('size_mb')), extra=extra))
            except EOFError:
                say(f"  {w['noinput']}")
                break
            (chosen if answer.strip().lower() in YES else refused).append(r['id'])
    if refused:
        decline([i for i in refused if BY_ID[i]['level'] == 'required'])
    for r in proposal['by_hand']:
        say(f"\n  {w['hand']} : {r['title']}. {r['manual']}")
    if chosen:
        for pid in chosen:
            say('  ' + w['installing'].format(title=text(BY_ID[pid], 'title', lang)))
        for item in apply(chosen)['results']:
            say(f"    {text(BY_ID[item['id']], 'title', lang) if item['id'] in BY_ID else item['id']} : {item['result']}. {item['detail']}")
    else:
        ensure_profile()
    say(f"\n  {w['verifying']}" if deep else '')
    report = verify(deep=deep)
    say(f"\n  {w['report']}")
    for r in report['rows']:
        say(f"    {r['status']:<9} {r['title']:<30} {r['detail']}")
    say(f"\n  {w[report['verdict']]}\n")
    return 1 if report['verdict'] == FAILED else 0
