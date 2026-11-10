"""Kokoro voice and local transcription, for real. python tests/voix_locale.py -> docs/preuves/voix-locale/

For each language: speak a text, transcribe what was said, compare it with the text, and check the word times
against the silences measured in the WAV. It does not judge how natural the voice sounds: that needs a human ear."""
import json
import re
import subprocess
import sys
import time
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding='utf-8')

from universal import voice_kokoro  # noqa: E402
from universal.qc import check_srt  # noqa: E402
from universal.voice import to_srt  # noqa: E402

OUT = ROOT / 'out' / 'demos' / 'voix-locale'
PROOFS = ROOT / 'docs' / 'preuves' / 'voix-locale'
TEXTS = {
    'fr': "Bonjour ! Du pain chaud, chaque matin, à deux pas de chez vous. Goûtez la différence, c'est préparé ici même, avant le lever du soleil.",
    'es': "¡Hola! Pan caliente, cada mañana, a dos pasos de tu casa. Prueba la diferencia, se prepara aquí mismo, antes de que salga el sol.",
    'en': "Hello! Warm bread, every morning, just around the corner. Taste the difference, it is made right here, before the sun comes up.",
}


def plain(text: str) -> list[str]:
    t = unicodedata.normalize('NFD', text.lower())
    t = ''.join(c for c in t if unicodedata.category(c) != 'Mn')
    return re.findall(r"[a-z0-9]+", t)


def silences(wav: Path) -> list[float]:
    log = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(wav), '-af', 'silencedetect=n=-40dB:d=0.12', '-f', 'null', '-'], capture_output=True, text=True, encoding='utf-8', errors='replace').stderr
    return [float(x) for x in re.findall(r'silence_end: ([\d.]+)', log)]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    PROOFS.mkdir(parents=True, exist_ok=True)
    rows = []
    for language, text in TEXTS.items():
        wav = OUT / f'voix-{language}.wav'
        start = time.time()
        marks = voice_kokoro.synthesize(text, wav, language)
        seconds = round(time.time() - start, 1)
        heard = marks['heard'] or ''
        match = SequenceMatcher(None, plain(text), plain(heard)).ratio()
        kept = ' '.join(w['text'] for w in marks['words']) == ' '.join(text.split())
        gaps = silences(wav)
        # After a pause, the next word must start where the sound comes back
        after_pause = [min((abs(w['start'] - g) for w in marks['words']), default=9) for g in gaps]
        srt = to_srt(marks['words'], OUT / f'voix-{language}.srt')
        problems = check_srt(srt, marks['duration'])
        row = {'langue': language, 'voix': marks['voice'], 'duree_s': marks['duration'], 'calcul_s': seconds, 'minutage': marks['timing'], 'mots': len(marks['words']), 'visemes': len(marks['visemes']),
               'texte_retrouve': round(match, 3), 'ecart_pauses_s': round(max(after_pause), 3) if after_pause else None, 'pauses': len(gaps), 'srt_problemes': problems, 'entendu': heard}
        row['texte_ecrit_conserve'] = kept
        row['pass'] = match >= .85 and kept and marks['timing'] == 'real' and not problems and (not after_pause or max(after_pause) < .3)
        rows.append(row)
        print(json.dumps(row, ensure_ascii=False))
    report = {'pass': all(r['pass'] for r in rows), 'voix': rows, 'limite': "Le texte entendu et le minutage sont mesurés. Le naturel de la voix ne se juge qu'à l'oreille."}
    (PROOFS / 'resultats.json').write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding='utf-8')
    return 0 if report['pass'] else 1


if __name__ == '__main__':
    sys.exit(main())
