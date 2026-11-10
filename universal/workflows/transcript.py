"""Shared by the treatments that need to know what is said, and when. Local and offline once the model is installed."""
from __future__ import annotations
import json
import re
from pathlib import Path
from .. import modules, voice_kokoro
from . import tools


def missing() -> str | None:
    """None when transcription can run here, otherwise what to ask the user in plain words."""
    if (modules.WHISPER_DIR / 'model.bin').exists() and (modules.VENV / '.tier-transcribe').exists():
        return None
    return ("La transcription locale n'est pas installée. Elle est gratuite et hors ligne, mais demande un téléchargement d'environ 345 Mo "
            "(outil et modèle). Demander l'accord de l'utilisateur, puis : python -m universal.cli setup apply --approve captions")


def words_of(video: Path, cache: Path, language: str | None = None) -> dict:
    """{'language', 'words': [{text, start, end}], 'fresh'}. Reuses the last result when the video has the same length;
    `fresh` tells a new transcription from a reused one, because a text already reviewed must not be replaced silently."""
    length = round(tools.info(video)['duration'], 1)
    if cache.exists():
        try:
            saved = json.loads(cache.read_text(encoding='utf-8'))
            if isinstance(saved, dict) and abs(saved.get('duration', -9) - length) < .15:
                return {**saved, 'fresh': False}
        except ValueError:
            pass
    problem = missing()
    if problem:
        raise RuntimeError(problem)
    heard = voice_kokoro.transcribe_full(video, cache.with_suffix('.brut.json'), language)
    cache.with_suffix('.brut.json').unlink(missing_ok=True)
    data = {'duration': length, 'language': heard['language'], 'words': heard['words']}
    cache.write_text(json.dumps(data, ensure_ascii=False, indent=0), encoding='utf-8')
    return {**data, 'fresh': True}


def sentences(words: list[dict], pause: float = .7) -> list[dict]:
    """Words grouped on end punctuation or on a real pause."""
    out, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        gap = words[i + 1]['start'] - w['end'] if i + 1 < len(words) else 0
        if re.search(r'[.!?…]$', w['text']) or gap >= pause:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return [{'start': s[0]['start'], 'end': s[-1]['end'], 'text': re.sub(r' (?=[,.!?;:])', '', ' '.join(x['text'] for x in s))} for s in out]


def stamp(seconds: float, tenths: bool = True) -> str:
    seconds = max(0.0, seconds)
    h, m, s = int(seconds // 3600), int(seconds % 3600 // 60), seconds % 60
    body = f'{m:02d}:{s:04.1f}' if tenths else f'{m:02d}:{int(s):02d}'
    return f'{h}:{body}' if h else body


def write_text(words: list[dict], path: Path, note: str = '') -> Path:
    """A transcript a person can read and point at: one sentence per line, with its times in seconds."""
    lines = [note, ''] if note else []
    lines += [f"[{s['start']:.2f} -> {s['end']:.2f}]  {s['text']}" for s in sentences(words)]
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return path
