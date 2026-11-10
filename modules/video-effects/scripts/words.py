#!/usr/bin/env python3
"""Find when each word is said, so effects can land on the right word.

usage: python words.py input.mp4 [output.json] [language]  -> prints "12.34  word" lines and saves the words
Uses faster-whisper from the kit's module environment. On a Mac with mlx-whisper installed, that is used instead.
"""
import json, os, sys

src = sys.argv[1]
out = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(src)[0] + '.words.json'
language = sys.argv[3] if len(sys.argv) > 3 else None
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
words = []
try:
    import mlx_whisper
    r = mlx_whisper.transcribe(src, path_or_hf_repo='mlx-community/whisper-large-v3-turbo', word_timestamps=True)
    spoken = r.get('language')
    words = [{'w': w['word'].strip(), 's': round(w['start'], 2), 'e': round(w['end'], 2)} for seg in r['segments'] for w in seg.get('words', [])]
except ImportError:
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit('faster-whisper absent : python -m universal.cli modules install transcribe')
    model = WhisperModel(os.environ.get('WHISPER_MODEL', 'base'), device='cpu', compute_type='int8')
    segs, heard = model.transcribe(src, word_timestamps=True, vad_filter=True, language=language)
    spoken = getattr(heard, 'language', None)
    words = [{'w': w.word.strip(), 's': round(w.start, 2), 'e': round(w.end, 2)} for s in segs for w in (s.words or [])]

json.dump(words, open(out, 'w', encoding='utf-8'), indent=0, ensure_ascii=False)
for w in words: print(f"{w['s']:7.2f}  {w['w']}")
print(f'\nSaved {len(words)} words to {out}')
print(f'LANG {language or spoken}')
