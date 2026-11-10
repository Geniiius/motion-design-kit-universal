"""What this machine can really do. Never reads the value of an API key, only whether it exists."""
from __future__ import annotations
import json
import os
import platform
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _pkg(project: str, name: str) -> str | None:
    f = ROOT / project / 'node_modules' / name / 'package.json'
    return json.loads(f.read_text(encoding='utf-8'))['version'] if f.exists() else None


def find_blender() -> str | None:
    """PATH first, then where each system puts it: Blender's own installer does not add itself to PATH."""
    hit = shutil.which('blender')
    if hit:
        return hit
    system = platform.system()
    if system == 'Windows':
        bases = {os.environ.get(k) for k in ('ProgramFiles', 'ProgramW6432', 'ProgramFiles(x86)')} - {None}
        found = [p for b in bases for p in Path(b, 'Blender Foundation').glob('Blender*/blender.exe')]
    elif system == 'Darwin':
        found = [p for p in (Path('/Applications/Blender.app/Contents/MacOS/Blender'), Path.home() / 'Applications/Blender.app/Contents/MacOS/Blender') if p.exists()]
    else:
        found = [p for p in (Path('/snap/bin/blender'), Path('/var/lib/flatpak/exports/bin/org.blender.Blender'), Path.home() / '.local/share/flatpak/exports/bin/org.blender.Blender') if p.exists()]
    newest = sorted(found, key=lambda p: [int(n) for n in re.findall(r'[0-9]+', p.parent.name)], reverse=True)
    return str(newest[0]) if newest else None


def _voices() -> list[str]:
    if platform.system() == 'Windows':
        try:
            r = subprocess.run(['powershell', '-NoProfile', '-Command',
                                'Add-Type -AssemblyName System.Speech;(New-Object System.Speech.Synthesis.SpeechSynthesizer).GetInstalledVoices()|%{$_.VoiceInfo.Name+"|"+$_.VoiceInfo.Culture}'],
                               capture_output=True, text=True, timeout=25)
            return [x.strip() for x in r.stdout.splitlines() if '|' in x]
        except (OSError, subprocess.TimeoutExpired):
            return []
    return ['espeak-ng|multi'] if shutil.which('espeak-ng') else []


def detect(full: bool = False) -> dict:
    tools = {'ffmpeg': bool(shutil.which('ffmpeg')), 'ffprobe': bool(shutil.which('ffprobe')), 'node': bool(shutil.which('node')),
             'blender': bool(find_blender()),
             'three_vrm': _pkg('template', '@pixiv/three-vrm') is not None}
    remotion = _pkg('template', 'remotion')
    three = _pkg('template', '@remotion/three')
    engines = {'ffmpeg-edit': tools['ffmpeg'] and tools['ffprobe'], 'video-workflow': tools['ffmpeg'] and tools['ffprobe'], 'html-deck': True,
               'remotion-2d': bool(remotion and tools['node']), 'remotion-3d': bool(three and tools['node']),
               'prompt-motion': _pkg('prompt-motion', 'playwright') is not None,
               'hyperframes': (ROOT / 'hyperframes-starter/package.json').exists() and tools['node'],
               'herk-edit-kit': (ROOT / 'workspaces/herk-edit-kit/package.json').exists(),
               'blender': tools['blender'], 'elevenlabs': bool(os.environ.get('ELEVENLABS_API_KEY')),
               'film-style': (ROOT / 'modules/opuscar/node_modules/playwright-core').exists() and tools['node'] and tools['ffmpeg'],
               'video-effects': (ROOT / 'modules/.venv/.tier-effects').exists() and tools['ffmpeg'],
               'kokoro': (ROOT / 'modules/.venv/.tier-voice').exists() and (ROOT / 'modules/opuscar/core/tts/kokoro-v1.0.onnx').exists(),
               'transcription-locale': (ROOT / 'modules/models/whisper-base/model.bin').exists() and (ROOT / 'modules/.venv/.tier-transcribe').exists()}
    out = {'tools': tools, 'engines': engines, 'versions': {'remotion': remotion, 'three': _pkg('template', 'three'), 'zod': _pkg('template', 'zod')}}
    if full:
        from . import diagnostic, state
        seen = diagnostic.full()
        out.update(machine=seen['machine'], software=seen['software'], conflicts=seen['conflicts'], voices_local=_voices(),
                   encoders_verified=state.load().get('encoders') or 'non testés : le premier lancement les essaie',
                   render_gl="choisi à chaque rendu : accélération graphique d'abord, rendu logiciel en repli",
                   paid_services={'elevenlabs_key_present': seen['software']['elevenlabs_key']['found'], 'note': 'Aucun appel payant sans accord explicite.'})
    return out
