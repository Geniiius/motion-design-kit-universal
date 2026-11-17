#!/usr/bin/env python3
"""Hear a sung voice over music: the model of words.py, asked several times.

usage: python song_words.py output.json language windows name=file.wav=tempo [name=file.wav=tempo ...]

Each file is the same song as 16 kHz mono WAV, prepared by the kit (as is, voice band, slowed down); `tempo` is the
speed it was slowed to, so that times go back to the real song. `language` is a code, or `auto`.
`windows` is `grid` for the whole song in overlapping windows, or a list such as `4.5-17,6-18.5` to read again exactly
those stretches: the model hears a verse much better when the window starts where the singing starts.

Speech detection is off here: it takes a sung voice for music and drops it. Each window is read with and without a
neutral hint, because a single long reading drifts into repeated or invented text on the instrumental parts. Every
reading is saved with the model's confidence for each word. This script decides nothing: the kit compares the readings,
asks for the stretches left empty and flags the doubtful words (universal/song.py).
"""
import json, os, sys, wave

WINDOW, HOP, TAIL = 12.5, 11.0, 3.0  # seconds; a last piece shorter than TAIL joins the window before it
HINTS = {'es': 'Letra de una canción.', 'fr': "Paroles d'une chanson.", 'en': 'Song lyrics.'}

if len(sys.argv) < 5:
    sys.exit(__doc__)
out, language, wanted, items = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
try:
    import numpy as np
    from faster_whisper import WhisperModel
except ImportError:
    sys.exit('faster-whisper absent : python -m universal.cli modules install transcribe')


def load(path):
    with wave.open(path) as w:
        if w.getnchannels() != 1 or w.getsampwidth() != 2:
            sys.exit(f'{path} : WAV mono 16 bits attendu')
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768, w.getframerate()


def grid(seconds):
    marks, start = [], 0.0
    while start < seconds:
        end = min(seconds, start + WINDOW)
        if seconds - end < TAIL:
            end = seconds
        marks.append((round(start, 2), round(end, 2)))
        if end >= seconds:
            break
        start += HOP
    return marks


model = WhisperModel(os.environ.get('WHISPER_MODEL', 'base'), device='cpu', compute_type='int8')
variants = []
for item in items:
    name, rest = item.split('=', 1)
    path, tempo = rest.rsplit('=', 1)
    audio, rate = load(path)
    variants.append((name, audio, rate, float(tempo)))
seconds = len(variants[0][1]) / variants[0][2] * variants[0][3]
if language == 'auto':
    _, heard = model.transcribe(variants[0][1][:int(30 * variants[0][2])], vad_filter=False)
    language = heard.language
windows = grid(seconds) if wanted == 'grid' else [tuple(float(x) for x in pair.split('-')) for pair in wanted.split(',')]
hints = [None] + ([HINTS[language]] if language in HINTS else [])
passes = []
for start, end in windows:
    for name, audio, rate, tempo in variants:
        piece = audio[int(start / tempo * rate):int(min(end, seconds) / tempo * rate)]
        for hint in hints:
            segments, _ = model.transcribe(piece, language=language, word_timestamps=True, vad_filter=False, beam_size=5, temperature=0.0,
                                           condition_on_previous_text=False, initial_prompt=hint, no_speech_threshold=0.95)
            words = [{'w': w.word.strip(), 's': round(start + w.start * tempo, 2), 'e': round(start + w.end * tempo, 2), 'p': round(w.probability, 3)}
                     for s in segments for w in (s.words or [])]
            passes.append({'variant': name, 'hint': bool(hint), 'start': start, 'end': end, 'words': words})

json.dump({'duration': round(seconds, 2), 'language': language, 'passes': passes}, open(out, 'w', encoding='utf-8'), ensure_ascii=False)
print(f'{len(passes)} lectures, {len(windows)} fenêtres')
print(f'LANG {language}')
