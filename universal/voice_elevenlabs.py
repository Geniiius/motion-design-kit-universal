"""ElevenLabs speech with character timing. A paid service: nothing is sent without approved=True.

The same text, voice and model are never billed twice: results stay in out/cache-voix.
The key is read from the environment and is never written anywhere.
Mouth shapes come from the letters of the spoken text, not from phonemes: good enough for a
stylized character, not for a realistic face. The result says so in `visemes_source`.
"""
from __future__ import annotations
import base64
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / 'out' / 'cache-voix'
API = 'https://api.elevenlabs.io'
DEFAULT_MODEL = 'eleven_multilingual_v2'
MAX_CHARS = 2000

# Same ids as the Windows voice, so the character's mouth table works for both
LETTER_VISEME = {'a': 2, 'á': 2, 'à': 2, 'â': 2, 'e': 4, 'é': 4, 'è': 4, 'ê': 4, 'ë': 4, 'i': 6, 'í': 6, 'î': 6, 'ï': 6, 'y': 6, 'o': 8, 'ó': 8, 'ô': 8, 'u': 7, 'ú': 7, 'ù': 7, 'û': 7, 'ü': 7,
                 'w': 7, 'm': 21, 'b': 21, 'p': 21, 'f': 18, 'v': 18, 's': 15, 'z': 15, 'c': 15, 'ç': 15, 'x': 15, 'd': 19, 't': 19, 'n': 19, 'ñ': 19, 'k': 20, 'g': 20, 'q': 20, 'l': 14, 'r': 13, 'h': 12, 'j': 16}


class ApprovalRequired(RuntimeError):
    pass


def _key() -> str:
    key = os.environ.get('ELEVENLABS_API_KEY')
    if not key and platform.system() == 'Windows':
        key = subprocess.run(['powershell', '-NoProfile', '-Command', "[Environment]::GetEnvironmentVariable('ELEVENLABS_API_KEY','User')"], capture_output=True, text=True).stdout.strip()
    if not key:
        raise RuntimeError('Pas de clé ElevenLabs : relancer INSTALAR.bat. Elle ne doit jamais être écrite dans la conversation.')
    return key


def words_from_alignment(alignment: dict) -> list[dict]:
    """Words of the original text, with the time of their first and last character."""
    chars, starts, ends = alignment['characters'], alignment['character_start_times_seconds'], alignment['character_end_times_seconds']
    words, current = [], None
    for c, a, b in zip(chars, starts, ends):
        if c.isspace():
            if current:
                words.append(current)
                current = None
            continue
        if current is None:
            current = {'text': c, 'start': round(a, 3), 'end': round(b, 3)}
        else:
            current['text'] += c
            current['end'] = round(b, 3)
    if current:
        words.append(current)
    return words


def visemes_from_alignment(alignment: dict) -> list[dict]:
    """One mouth shape per sounded letter; a gap of 80 ms or more closes the mouth."""
    out, prev_end = [], 0.0
    for c, a, b in zip(alignment['characters'], alignment['character_start_times_seconds'], alignment['character_end_times_seconds']):
        vid = LETTER_VISEME.get(c.lower())
        if vid is None:
            continue
        if a - prev_end >= .08:
            out.append({'id': 0, 'start': round(prev_end, 3), 'duration': round(a - prev_end, 3)})
        out.append({'id': vid, 'start': round(a, 3), 'duration': round(max(b - a, .01), 3)})
        prev_end = b
    return out


def marks_from_response(data: dict, text: str, voice_id: str, model: str, language: str) -> dict:
    alignment = data.get('alignment')
    if not alignment:
        raise RuntimeError('Réponse sans minutage.')
    # normalized_alignment spells out numbers as they are said: closer to what the mouth does
    return {'voice': voice_id, 'culture': language, 'language_match': True, 'model': model, 'text': text, 'engine': 'elevenlabs', 'timing': 'real', 'visemes_source': 'letters',
            'words': words_from_alignment(alignment), 'visemes': visemes_from_alignment(data.get('normalized_alignment') or alignment)}


def cache_key(text: str, voice_id: str, model: str, language: str) -> str:
    return hashlib.sha256(json.dumps([text, voice_id, model, language], ensure_ascii=False).encode('utf-8')).hexdigest()[:24]


def _request(text: str, voice_id: str, model: str) -> tuple[dict, str | None]:
    body = {'text': text, 'model_id': model, 'voice_settings': {'stability': .5, 'similarity_boost': .75}}
    req = urllib.request.Request(f'{API}/v1/text-to-speech/{voice_id}/with-timestamps?output_format=mp3_44100_128', data=json.dumps(body).encode('utf-8'),
                                 headers={'xi-api-key': _key(), 'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return json.load(r), r.headers.get('x-character-count')
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"ElevenLabs a répondu {e.code} : {e.read().decode('utf-8', 'replace')[:240]}") from None


def synthesize(text: str, out: Path, language: str, voice_id: str, *, model: str = DEFAULT_MODEL, approved: bool = False, max_chars: int = MAX_CHARS) -> dict:
    out = Path(out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    key = cache_key(text, voice_id, model, language)
    audio, meta = CACHE / f'{key}.mp3', CACHE / f'{key}.json'
    if audio.exists() and meta.exists():
        shutil.copy2(audio, out)
        marks = json.loads(meta.read_text(encoding='utf-8'))
        marks['chars_billed_now'] = 0
    else:
        if not approved:
            raise ApprovalRequired(f'Appel payant ElevenLabs ({len(text)} caractères) : accord explicite requis pour cet appel.')
        if len(text) > max_chars:
            raise ApprovalRequired(f'{len(text)} caractères dépassent le plafond de {max_chars} accordé.')
        data, billed = _request(text, voice_id, model)
        marks = marks_from_response(data, text, voice_id, model, language)
        marks['chars_billed'] = int(billed) if billed and billed.isdigit() else len(text)
        CACHE.mkdir(parents=True, exist_ok=True)
        audio.write_bytes(base64.b64decode(data['audio_base64']))
        shutil.copy2(audio, out)
        probe = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(audio)], capture_output=True, text=True)
        marks['duration'] = round(float(probe.stdout.strip()), 3)
        meta.write_text(json.dumps(marks, ensure_ascii=False, indent=1), encoding='utf-8')
        marks['chars_billed_now'] = marks['chars_billed']
    return marks


def balance() -> dict:
    """Free call. Returns nothing sensitive, an empty result if the key may not read the account."""
    req = urllib.request.Request(f'{API}/v1/user/subscription', headers={'xi-api-key': _key()})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.load(r)
        return {k: d.get(k) for k in ('tier', 'character_count', 'character_limit')}
    except urllib.error.URLError:
        return {}
