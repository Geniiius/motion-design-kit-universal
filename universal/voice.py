"""Local speech with real timing, free and offline. ElevenLabs stays a separate, approved step.

Windows: System.Speech gives word and viseme marks. Linux/WSL: espeak-ng if present, with estimated timing.
"""
from __future__ import annotations
import json
import math
import platform
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from .render import duration

SAPI = Path(__file__).resolve().parent / 'voz_sapi.ps1'
READING_CPS = 17  # characters per second a viewer reads comfortably


def _estimate_words(text: str, total: float) -> list[dict]:
    words = text.split()
    weights = [max(1, len(re.sub(r'\W', '', w))) + (3 if re.search(r'[.,;:!?]$', w) else 0) for w in words]
    t, out = 0.0, []
    for w, k in zip(words, weights):
        out.append({'text': w, 'start': round(t, 3)})
        t += total * k / sum(weights)
    return out


def _true_timing(marks: dict, text: str) -> None:
    """SAPI reports AudioPosition on a wrong scale when writing to a file, but viseme durations sum to the
    real length. Real time is therefore their running total, and words are placed against those visemes.
    Checked against the silences measured in the WAV (tests/test_universal.py)."""
    raw, true, t = [], [], 0.0
    for v in marks['visemes']:
        raw.append(v['start'])
        true.append(round(t, 3))
        v['start'] = round(t, 3)
        t += v['duration']

    def place(position: float) -> float:
        for i in range(1, len(raw)):
            if raw[i] >= position:
                if raw[i] == raw[i - 1]:
                    return true[i]
                return round(true[i - 1] + (true[i] - true[i - 1]) * (position - raw[i - 1]) / (raw[i] - raw[i - 1]), 3)
        return true[-1] if true else position

    # A spoken number raises one event per spoken part, all at the same text position: keep the first.
    # Each word then takes its token from the text, because SAPI drops the punctuation.
    words, seen = [], set()
    for w in marks['words']:
        if w['pos'] in seen:
            continue
        seen.add(w['pos'])
        token = re.match(r'\S+', text[w['pos']:])
        words.append({'text': token.group(0) if token else w['text'], 'start': place(w['start'])})
    marks['words'] = words


def synthesize(text: str, wav: Path, language: str = 'en') -> dict:
    wav = Path(wav).resolve()
    wav.parent.mkdir(parents=True, exist_ok=True)
    if platform.system() == 'Windows':
        with tempfile.TemporaryDirectory(prefix='voz-') as tmp:
            txt, js = Path(tmp) / 't.txt', Path(tmp) / 'm.json'
            txt.write_text(text, encoding='utf-8')
            subprocess.run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(SAPI), '-TextFile', str(txt), '-Wav', str(wav),
                            '-Json', str(js), '-Culture', language], check=True, capture_output=True, text=True)
            marks = json.loads(js.read_text(encoding='utf-8'))
        _true_timing(marks, text)
        marks.update(timing='real', engine='sapi')
    elif shutil.which('espeak-ng'):
        subprocess.run(['espeak-ng', '-v', language, '-w', str(wav), text], check=True, capture_output=True)
        marks = {'voice': f'espeak-ng:{language}', 'culture': language, 'words': _estimate_words(text, duration(wav)), 'visemes': [], 'timing': 'estimated', 'engine': 'espeak-ng'}
    else:
        raise RuntimeError('Aucune voix locale : installer une voix ou fournir un fichier audio.')
    total = duration(wav)
    words = marks['words']
    for i, w in enumerate(words):
        w['end'] = words[i + 1]['start'] if i + 1 < len(words) else round(total, 3)
    marks.update(duration=round(total, 3), language_match=marks['culture'].lower().startswith(language.lower()), text=text)
    return marks


def amplitude_envelope(wav: Path, rate: int = 30) -> list[float]:
    """Loudness per frame, the lip-sync fallback when a model or voice has no visemes."""
    with tempfile.TemporaryDirectory(prefix='env-') as tmp:
        raw = Path(tmp) / 'a.raw'
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', str(wav), '-ac', '1', '-ar', '8000', '-f', 's16le', str(raw)], check=True)
        data = raw.read_bytes()
    step, out = 8000 // rate, []
    for i in range(0, len(data) // 2 - step, step):
        chunk = [int.from_bytes(data[j * 2:j * 2 + 2], 'little', signed=True) for j in range(i, i + step, 8)]
        out.append(sum(abs(x) for x in chunk) / max(1, len(chunk)) / 32768)
    peak = max(out or [1]) or 1
    return [round(min(1, x / peak), 3) for x in out]


def to_srt(words: list[dict], path: Path, max_chars: int = 40) -> Path:
    """Cues cut on sentences, then in even lengths, preferring a comma: a short leftover would be unreadably fast."""
    sentences, cur = [], []
    for w in words:
        cur.append(w)
        if re.search(r'[.!?…]$', w['text']):
            sentences.append(cur)
            cur = []
    if cur:
        sentences.append(cur)
    cues = []
    join = lambda part: len(' '.join(x['text'] for x in part))
    for rest in sentences:
        while join(rest) > max_chars:
            target = join(rest) / math.ceil(join(rest) / max_chars)
            cut, best = 1, float('inf')
            for i in range(1, len(rest)):
                if join(rest[:i]) > max_chars:
                    break
                score = abs(join(rest[:i]) - target) - (target * .5 if rest[i - 1]['text'].endswith(',') else 0)
                if score < best:
                    cut, best = i, score
            cues.append(rest[:cut])
            rest = rest[cut:]
        cues.append(rest)
    stamp = lambda s: f'{int(s // 3600):02d}:{int(s % 3600 // 60):02d}:{int(s % 60):02d},{int(round((s % 1) * 1000)) % 1000:03d}'
    body = []
    for i, c in enumerate(cues, 1):
        text = ' '.join(x['text'] for x in c)
        # A word can end almost as it starts: the cue stays long enough to read, without reaching the next one
        limit = cues[i][0]['start'] if i < len(cues) else c[-1]['end'] + 1.0
        end = max(c[-1]['end'], min(c[0]['start'] + len(text) / READING_CPS, limit))
        body.append(f"{i}\n{stamp(c[0]['start'])} --> {stamp(end)}\n{text}\n")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text('\n'.join(body), encoding='utf-8')
    return Path(path)
