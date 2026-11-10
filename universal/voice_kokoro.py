"""Kokoro speech, free and offline once its model is downloaded. French, Spanish and English here.

Kokoro gives no timing. With the local transcription model, words get their real time: the written text stays
the reference and the transcription only supplies the times, because it mishears (homophones, names, numbers).
Without the model, words are placed by length and the result says `timing: estimated`.
Mouth shapes come from letters, as with ElevenLabs: enough for a stylized character, not for a realistic face.
"""
from __future__ import annotations
import json
import re
import shutil
import tempfile
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path
from . import modules
from .render import duration
from .voice import _estimate_words
from .voice_elevenlabs import LETTER_VISEME

ROOT = Path(__file__).resolve().parents[1]
TTS = ROOT / 'modules/opuscar/core/tts/tts.py'
WORDS = ROOT / 'modules/video-effects/scripts/words.py'
VOICES = {'fr': ('ff_siwis', 'fr-fr'), 'es': ('ef_dora', 'es'), 'en': ('af_bella', 'en-us')}
MIN_MATCH = .6  # under this, what was heard is too far from the text to trust its times


def transcribe(media: Path, out: Path, language: str | None = None) -> list[dict]:
    """Word timings of any audio or video, offline: [{text, start, end}]."""
    return transcribe_full(media, out, language)['words']


def transcribe_full(media: Path, out: Path, language: str | None = None) -> dict:
    """{'words': [{text, start, end}], 'language'}: the spoken language is the one given, or the one the model heard."""
    if not (modules.WHISPER_DIR / 'model.bin').exists():
        raise RuntimeError('Option « sous-titres automatiques » absente (gratuite, 345 Mo) : demander l\'accord, puis python -m universal.cli setup apply --approve captions')
    out = Path(out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    args = [WORDS, Path(media).resolve(), out] + ([language] if language else [])
    r = modules.run_python(args, tier='transcribe', env={'WHISPER_MODEL': str(modules.WHISPER_DIR), 'HF_HUB_OFFLINE': '1'})
    if r.returncode:
        raise RuntimeError(r.stderr[-1500:])
    words = []
    for w in json.loads(out.read_text(encoding='utf-8')):
        # The model splits « Aujourd'hui » or « c'est » at the apostrophe, and « ici-même » at the hyphen: one written word again
        if words and re.match(r"['’]|-\w", w['w']):
            words[-1]['text'] += w['w']
            words[-1]['end'] = w['e']
        elif w['w']:
            words.append({'text': w['w'], 'start': w['s'], 'end': w['e']})
    out.write_text(json.dumps(words, ensure_ascii=False, indent=0), encoding='utf-8')
    spoken = re.search(r'^LANG ([a-z]{2,3})\b', r.stdout, re.M)
    return {'words': words, 'language': spoken.group(1) if spoken else language}


def _letters(text: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFD', text.lower()) if c.isalnum())


def _tokens(text: str) -> list[str]:
    """Words of the text. Punctuation standing alone, as in French « Bonjour ! », stays with its word."""
    out: list[str] = []
    for token in text.split():
        if out and not _letters(token):
            out[-1] += ' ' + token
        else:
            out.append(token)
    return out


def align(text: str, heard: list[dict]) -> tuple[list[dict], float]:
    """Words of the written text with the times of what was heard, compared letter by letter.
    A word with no match, such as a number said in full, is placed between its neighbours by length."""
    tokens = _tokens(text)
    written, owner = '', []
    for i, token in enumerate(tokens):
        for c in _letters(token):
            written += c
            owner.append(i)
    said, spans = '', []
    for w in heard:
        letters = _letters(w['text'])
        step = (w['end'] - w['start']) / max(len(letters), 1)
        for k, c in enumerate(letters):
            said += c
            spans.append((w['start'] + k * step, w['start'] + (k + 1) * step))
    matcher = SequenceMatcher(None, written, said, autojunk=False)
    starts: list[float | None] = [None] * len(tokens)
    ends: list[float | None] = [None] * len(tokens)
    for a, b, size in matcher.get_matching_blocks():
        for k in range(size):
            i = owner[a + k]
            starts[i] = spans[b + k][0] if starts[i] is None else min(starts[i], spans[b + k][0])
            ends[i] = spans[b + k][1] if ends[i] is None else max(ends[i], spans[b + k][1])
    weight = [max(len(_letters(t)), 1) for t in tokens]
    i = 0
    while i < len(tokens):
        if starts[i] is not None:
            i += 1
            continue
        j = i
        while j < len(tokens) and starts[j] is None:
            j += 1
        left = ends[i - 1] if i else (heard[0]['start'] if heard else 0.0)
        right = starts[j] if j < len(tokens) else (heard[-1]['end'] if heard else left)
        right = max(right, left)
        total, done = sum(weight[i:j]), 0
        for k in range(i, j):
            starts[k] = left + (right - left) * done / total
            done += weight[k]
            ends[k] = left + (right - left) * done / total
        i = j
    words, previous = [], 0.0
    for token, a, b in zip(tokens, starts, ends):
        a = max(a, previous)
        b = max(b, a + .01)
        words.append({'text': token, 'start': round(a, 3), 'end': round(b, 3)})
        previous = b
    return words, matcher.ratio()


def visemes_from_words(words: list[dict]) -> list[dict]:
    """Letters spread evenly over each word; a gap of 80 ms or more closes the mouth.
    A number has no letters to read but is still spoken: the mouth keeps moving through it."""
    out, prev_end = [], 0.0
    for w in words:
        letters = [c for c in w['text'].lower() if c.isalpha()]
        if not letters and any(c.isdigit() for c in w['text']):
            letters = list('aeoa' * max(1, sum(c.isdigit() for c in w['text'])))
        if not letters:
            continue
        if w['start'] - prev_end >= .08:
            out.append({'id': 0, 'start': round(prev_end, 3), 'duration': round(w['start'] - prev_end, 3)})
        step = max(w['end'] - w['start'], .01) / len(letters)
        for i, c in enumerate(letters):
            vid = LETTER_VISEME.get(c)
            if vid is not None:
                out.append({'id': vid, 'start': round(w['start'] + i * step, 3), 'duration': round(step, 3)})
        prev_end = w['end']
    return out


def synthesize(text: str, wav: Path, language: str = 'fr', voice: str | None = None, speed: float = .92) -> dict:
    if language not in VOICES:
        raise ValueError(f'Kokoro : langue {language} non prévue ici. Disponibles : {", ".join(VOICES)}')
    if not (TTS.parent / 'kokoro-v1.0.onnx').exists():
        raise RuntimeError('Option « voix off gratuite » absente (environ 550 Mo) : demander l\'accord, puis python -m universal.cli setup apply --approve voice-local')
    wav = Path(wav).resolve()
    wav.parent.mkdir(parents=True, exist_ok=True)
    name, lang = VOICES[language]
    voice = voice or name
    with tempfile.TemporaryDirectory(prefix='kokoro-') as tmp:
        lines = Path(tmp) / 'lines.json'
        lines.write_text(json.dumps([{'id': 'voz', 'text': text, 'voice': voice, 'speed': speed, 'lang': lang}], ensure_ascii=False), encoding='utf-8')
        r = modules.run_python([TTS, lines, tmp], tier='voice')
        if r.returncode:
            raise RuntimeError(r.stderr[-1500:] or r.stdout[-1500:])
        shutil.move(Path(tmp) / 'voz.wav', wav)
    total = duration(wav)
    words, timing, heard, match = [], 'estimated', None, None
    if (modules.WHISPER_DIR / 'model.bin').exists():
        with tempfile.TemporaryDirectory(prefix='mots-') as tmp:
            said = transcribe(wav, Path(tmp) / 'mots.json', language)
        heard = re.sub(r' (?=[,.!?;:])', '', ' '.join(w['text'] for w in said))
        aligned, match = align(text, said)
        if match >= MIN_MATCH:
            words, timing = aligned, 'real'
    if not words:
        words = _estimate_words(text, total)
        for i, w in enumerate(words):
            w['end'] = words[i + 1]['start'] if i + 1 < len(words) else round(total, 3)
    return {'voice': voice, 'culture': lang, 'language_match': True, 'engine': 'kokoro', 'timing': timing, 'visemes_source': 'letters', 'text': text,
            'heard': heard, 'text_match': round(match, 3) if match is not None else None,
            'duration': round(total, 3), 'words': words, 'visemes': visemes_from_words(words), 'chars_billed_now': 0}
