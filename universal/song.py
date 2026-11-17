"""A sung voice over music, heard offline with the kit's transcription model.

The ordinary transcription first removes what is not speech. On a song that filter takes the singing for music: whole
verses disappear and nothing says so. Here the song is read several times without that filter (as is, voice band only,
slowed down; with and without a neutral hint) in short overlapping windows. For each window the reading the others
agree with most is kept. A stretch left empty is then read again from several starting points, because the model hears
a verse much better when its window starts where the singing starts.

Every word says how sure it is: the model's own confidence and the share of readings that heard the same word at that
moment. A doubtful word comes with what the other readings heard instead. The small local model still mishears, above
all names and words of another language: the result is a draft to confirm with the person, never a text for the screen.
"""
from __future__ import annotations
import json
import re
import tempfile
import unicodedata
from pathlib import Path
from . import modules
from .render import run

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'modules/video-effects/scripts/song_words.py'
# name, FFmpeg audio filter, tempo. The slowed copy gives the model more time on fast syllables.
VARIANTS = (('plain', None, 1.0),
            ('voice', 'highpass=f=180,lowpass=f=5000,dynaudnorm', 1.0),
            ('slow', 'highpass=f=200,lowpass=f=4500,atempo=0.88,dynaudnorm', 0.88))
NEAR = .9          # seconds: two readings mean the same word when they place it this close (line starts drift by half a second)
DOUBT_P = .45      # under this confidence of the model, the word is flagged
DOUBT_VOTES = .5   # a word is flagged unless more than this share of the readings heard it: half is not a majority
WORD_LOOP, PHRASE_LOOP = 6, 3  # a word may be sung a few times in a row; six times, or a phrase three times running, is the model looping
HOLE = 3.0         # seconds without a word: worth reading again, it may be an instrumental break or a verse the model skipped
WINDOW = 12.5      # seconds read at once, as in the module script
TRIES, MAX_WINDOWS = 6, 24  # starting points per empty stretch, and second readings in all
SPARSE = .4        # an ordinary transcription covering less than this share of the audio may be a song


def _key(text: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFD', text.lower()) if c.isalnum())


def _unloop(words: list[dict]) -> list[dict]:
    """A word or a phrase the model repeats in a loop is kept once, with the number of times it came back."""
    keys, keep, i = [_key(w['w']) for w in words], [True] * len(words), 0
    while i < len(words):
        for n in range(1, 9):
            unit = keys[i:i + n]
            if len(unit) < n:
                continue
            reps = 1
            while keys[i + reps * n:i + (reps + 1) * n] == unit:
                reps += 1
            if reps >= (WORD_LOOP if n == 1 else PHRASE_LOOP):
                keep[i + n:i + reps * n] = [False] * ((reps - 1) * n)
                words[i + n - 1] = {**words[i + n - 1], 'x': reps}  # said, not hidden: the text shows how often it came back
                i += reps * n - 1
                break
        i += 1
    return [w for w, k in zip(words, keep) if k]


def clean(words: list[dict]) -> list[dict]:
    """One reading without what the model invents over music: signs that are not words, words piled on one instant, loops."""
    out: list[dict] = []
    for w in words:
        text = w['w'].strip()
        if out and re.match(r"['’]|-\w", text):  # « c'est », « ici-même » are split by the model: one written word again
            out[-1] = {**out[-1], 'w': out[-1]['w'] + text, 'e': max(out[-1]['e'], w['e']), 'p': min(out[-1]['p'], w['p'])}
            continue
        if not _key(text):
            continue
        if out and w['s'] - out[-1]['s'] < .03 and w['e'] - w['s'] < .03:
            continue
        out.append({'w': text, 's': w['s'], 'e': max(w['e'], w['s']), 'p': w['p']})
    return _unloop(out)


def _same(word: dict, reading: list[dict]) -> bool:
    key = _key(word['w'])
    return any(abs(o['s'] - word['s']) <= NEAR and _key(o['w']) == key for o in reading)


def _closest(word: dict, reading: list[dict]) -> dict | None:
    near = [o for o in reading if abs(o['s'] - word['s']) <= NEAR]
    return min(near, key=lambda o: abs(o['s'] - word['s'])) if near else None


def choose(readings: list[list[dict]]) -> list[dict]:
    """The reading of one window that the others agree with most, each word with its votes and what else was heard."""
    readings = [r for r in readings if r]
    if not readings:
        return []

    def score(i: int) -> float:
        others = readings[:i] + readings[i + 1:]
        if not others:
            return sum(w['p'] for w in readings[i])
        # a word nobody else heard counts against its reading: an invented passage is long, sure of itself and alone
        return sum(w['p'] * (sum(_same(w, o) for o in others) / len(others) - .3) for w in readings[i])

    best = max(range(len(readings)), key=score)
    others = readings[:best] + readings[best + 1:]
    out = []
    for w in readings[best]:
        agree = sum(_same(w, o) for o in others)
        heard: dict[str, int] = {}
        for o in others:
            if not _same(w, o):
                other = _closest(w, o)
                if other:
                    heard[other['w']] = heard.get(other['w'], 0) + 1
        alt = [t for t, _ in sorted(heard.items(), key=lambda x: -x[1]) if _key(t) != _key(w['w'])][:2]
        out.append({**w, 'votes': round((1 + agree) / len(readings), 2), 'alt': alt})
    return out


def stitch(parts: list[tuple[float, float, list[dict]]]) -> list[dict]:
    """Windows overlap: each word is taken from the window where it is furthest from an edge, and only once."""
    out: list[tuple[int, dict]] = []
    for i, (start, end, words) in enumerate(parts):
        lo = (start + parts[i - 1][1]) / 2 if i else float('-inf')
        hi = (parts[i + 1][0] + end) / 2 if i + 1 < len(parts) else float('inf')
        for w in words:
            if not lo <= (w['s'] + w['e']) / 2 < hi:
                continue
            if out and out[-1][0] != i and _key(out[-1][1]['w']) == _key(w['w']) and w['s'] - out[-1][1]['s'] < .4:
                continue  # the same word seen from both sides of a seam; inside one window a repeated word is sung twice
            out.append((i, w))
    return sorted((w for _, w in out), key=lambda w: w['s'])


def _by_window(data: dict) -> dict[tuple[float, float], list[list[dict]]]:
    windows: dict[tuple[float, float], list[list[dict]]] = {}
    for p in data.get('passes', []):
        windows.setdefault((p['start'], p['end']), []).append(clean(p['words']))
    return windows


def _shape(w: dict) -> dict:
    word = {'text': w['w'], 'start': w['s'], 'end': w['e'], 'p': round(w['p'], 2), 'votes': w['votes']}
    if w['p'] < DOUBT_P or w['votes'] <= DOUBT_VOTES or 'x' in w:
        word['doubt'] = True
        if w['alt']:
            word['alt'] = w['alt']
    if 'x' in w:
        word['repeat'] = w['x']
    return word


def merge(data: dict) -> list[dict]:
    """Every reading of the whole song -> [{text, start, end, p, votes, doubt?, alt?, repeat?}]."""
    return [_shape(w) for w in stitch([(a, b, choose(r)) for (a, b), r in sorted(_by_window(data).items())])]


def holes(words: list[dict], seconds: float) -> list[tuple[float, float]]:
    """Stretches of at least HOLE seconds where no word was found, edges of the song included."""
    out, last = [], 0.0
    for w in words:
        if w['start'] - last >= HOLE:
            out.append((round(last, 2), w['start']))
        last = max(last, w['end'])
    if seconds - last >= HOLE:
        out.append((round(last, 2), round(seconds, 2)))
    return out


def tries(hole: tuple[float, float], seconds: float) -> list[tuple[float, float]]:
    """Windows that start at several points of an empty stretch: one of them may start where the singing starts."""
    first = max(0.0, hole[0] - .3)
    last = max(first, hole[1] - 2.5)
    n = min(TRIES, int((last - first) / 1.5) + 1)
    starts = [first + (last - first) * i / (n - 1) for i in range(n)] if n > 1 else [first]
    return [(round(s, 2), round(min(seconds, s + WINDOW), 2)) for s in starts]


def fill(hole: tuple[float, float], readings_of_tries: list[list[list[dict]]]) -> list[dict]:
    """Words for an empty stretch, from the starting point whose readings agree best. Nothing when it is an instrumental
    break: there the readings invent, each on its own, and what they share is too little to be a sung line."""
    best: list[dict] = []
    for readings in readings_of_tries:
        got = [w for w in choose(readings) if w['s'] >= hole[0] - .2 and w['e'] <= hole[1] + .2 and w['votes'] >= DOUBT_VOTES and 'x' not in w]
        if len(got) >= 3 and sum(w['p'] for w in got) > sum(w['p'] for w in best):
            best = got
    return [_shape(w) for w in best]


def _add(words: list[dict], more: list[dict]) -> list[dict]:
    out: list[dict] = []
    for w in sorted(words + more, key=lambda w: w['start']):
        if out and _key(out[-1]['text']) == _key(w['text']) and w['start'] - out[-1]['start'] < .2:
            continue
        out.append(w)
    return out


def lines(words: list[dict], pause: float = .6) -> list[list[dict]]:
    """Sung lines. The model seldom leaves a gap between two lines, so a capital or a comma after a few words also starts one."""
    out: list[list[dict]] = []
    for i, w in enumerate(words):
        before = words[i - 1] if i else None
        if (before is None or w['start'] - before['end'] >= pause or re.search(r'[.!?…]$', before['text'])
                or (len(out[-1]) >= 4 and (before['text'].endswith(',') or w['text'][:1].isupper() or w['text'][:1] in '¡¿'))):
            out.append([])
        out[-1].append(w)
    return out


def as_text(words: list[dict]) -> str:
    """The lyrics as heard, one sung line per row. [word|other] is a doubtful word and what other readings heard."""
    rows = ['Paroles entendues (mode chanson). Entre crochets : mots peu sûrs, suivis de ce que d\'autres lectures ont entendu.',
            '« (répété ×N ?) » : le modèle a redit ce passage N fois de suite ; il est gardé une fois, à vérifier à l\'écoute.',
            'Brouillon à faire confirmer par la personne avant de l\'écrire à l\'écran : le modèle local se trompe, surtout sur les noms.', '']
    for line in lines(words):
        said = ' '.join(('[' + '|'.join([w['text']] + w.get('alt', [])) + ']' if w.get('doubt') else w['text'])
                        + (f" (répété ×{w['repeat']} ?)" if w.get('repeat') else '') for w in line)
        rows.append(f"{int(line[0]['start'] // 60)}:{line[0]['start'] % 60:04.1f}  {said}")
    return '\n'.join(rows) + '\n'


def sparse(words: list[dict], seconds: float) -> str | None:
    """A hint for an ordinary transcription that found few words for the length: on a song, sung parts were dropped."""
    if seconds < 20:
        return None
    share = sum(max(0.0, w['end'] - w['start']) for w in words) / seconds
    if share >= SPARSE:
        return None
    return (f"Peu de paroles pour la durée ({share:.0%} du son). S'il s'agit d'une chanson, relancer avec --song : "
            "sans cela, la voix chantée est prise pour de la musique et ignorée.")


def read(media: Path, out: Path, language: str | None = None) -> dict:
    """{'words', 'language', 'doubtful', 'text'}; writes the words as JSON and the lyrics as a text file next to it."""
    media, out = Path(media).resolve(), Path(out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='chanson-') as tmp:
        items = []
        for name, chain, tempo in VARIANTS:
            wav = Path(tmp) / f'{name}.wav'
            run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', media, '-vn'] + (['-af', chain] if chain else [])
                + ['-ac', 1, '-ar', 16000, '-c:a', 'pcm_s16le', wav])
            items.append(f'{name}={wav}={tempo}')

        def listen(windows: str, lang: str) -> dict:
            raw = Path(tmp) / 'lectures.json'
            r = modules.run_python([SCRIPT, raw, lang, windows] + items, tier='transcribe', env={'WHISPER_MODEL': str(modules.WHISPER_DIR), 'HF_HUB_OFFLINE': '1'})
            if r.returncode:
                raise RuntimeError(r.stderr[-1500:])
            return json.loads(raw.read_text(encoding='utf-8'))

        data = listen('grid', language or 'auto')
        words, seconds = merge(data), data['duration']
        empty = sorted(holes(words, seconds), key=lambda h: h[0] - h[1])  # the longest first if they cannot all be read again
        again = {h: tries(h, seconds) for h in empty}
        while sum(len(v) for v in again.values()) > MAX_WINDOWS:
            again.popitem()
        if again:
            second = _by_window(listen(','.join(f'{a}-{b}' for v in again.values() for a, b in v), data['language']))
            for hole, windows in again.items():
                words = _add(words, fill(hole, [second.get(w, []) for w in windows]))
    out.write_text(json.dumps(words, ensure_ascii=False, indent=0), encoding='utf-8')
    text = out.with_suffix('.paroles.txt')
    text.write_text(as_text(words), encoding='utf-8')
    return {'words': words, 'language': data.get('language') or language, 'doubtful': sum(1 for w in words if w.get('doubt')), 'text': str(text)}
