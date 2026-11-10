"""Runs all 51 effects on a clip with nobody in it, and writes docs/preuves/effects/.

Proves that every effect runs on this machine with the pinned packages, and that accents are drawn.
It does not prove face tracking or layering behind a person: that needs a real, consented video.
python tests/effets_tous.py [vertical|paysage]"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding='utf-8')

from universal import effects, fixtures, modules  # noqa: E402

OUT = ROOT / 'out' / 'demos' / 'effets'
PROOFS = ROOT / 'docs' / 'preuves' / 'effects'
SPAN = .6

# Test values, nothing here claims to be true
OPTIONS = {
    'lineup': {'text': 'Un|Deux|Trois'},
    'backdrop-word': {'text': 'ÉTÉ'}, 'the-bill': {'text': 'Café|Thé|Total'}, 'todo': {'text': 'Écrire|Tourner|Monter'}, 'comment-box': {'text': 'Bravo', 'reply': 'Merci', 'chip': 'Lien'},
    'red-collage': {'text': 'NUIT', 'lines': 'Un|Deux|Trois'}, 'split-headline': {'text': 'Une ligne|Deux lignes'}, 'pastel-word': {'text': 'MATIN'}, 'check-pills': {'text': 'Un|Deux|Trois'},
    'timeline': {'text': 'MONTAGE'}, 'headline-box': {'text': 'Première ligne|Seconde ligne'}, 'profile-wall': {'label': 'essai', 'count': 1000}, 'tier-list': {'title': 'Classement', 'others': 'B|C|D|F', 'item': 'Essai'},
    'broll-split': {'text': 'Étiquette'}, 'phone-fan': {'text': 'Une ligne|Deux lignes'}, 'headline-wall': {'text': 'Titre un::note|Titre deux::note', 'total': '12', 'label': 'essais'},
    'checklist': {'text': 'Étape un::note|Étape deux::note'}, 'glass-widgets': {'text': '12', 'label': 'Essai', 'to': '12', 'bars': '3|2|1'}, 'liquid-glass-graph': {'text': 'Essai', 'to': '12%'},
    'match-cut': {'text': 'Mot'}, 'apple-toggles': {'text': 'Un|Deux|Trois'}, 'led-sign': {'text': 'OUVERT'}, 'cover-star': {'text': 'REVUE'}, 'over-the-shoulder-zoom': {'text': 'Un|Deux', 'to': '12|34'},
    'messages': {'text': 'Bonjour|Ça va ?'}, 'place-in-grid': {'views': '1|2|3|4|5|6|7|8|9'}, 'tape-label': {'text': 'Étiquette'}, 'select-resize': {'text': '2X'}, 'huge-strike': {'text': 'NON'}, 'crayon-write': {'text': 'OUI'},
}


def clip(seconds: float, framing: str, folder: Path) -> Path:
    src = fixtures.build()['clips'][0]
    out = folder / 'source.mp4'
    folder.mkdir(parents=True, exist_ok=True)
    picture = 'crop=ih*9/16:ih,scale=1080:1920,setsar=1' if framing == 'vertical' else 'scale=1920:1080,setsar=1'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-stream_loop', '-1', '-i', str(src), '-t', str(seconds), '-vf', picture, '-r', '30', '-c:v', 'libx264', '-crf', '20', '-pix_fmt', 'yuv420p', '-an', str(out)], check=True)
    return out


def main() -> int:
    framing = sys.argv[1] if len(sys.argv) > 1 else 'vertical'
    work = OUT / framing
    names = [x['id'] for x in effects.catalog()]
    plan = [{'fx': n, 'start': round(i * SPAN, 2), 'end': round((i + 1) * SPAN - .02, 2), **OPTIONS.get(n, {})} for i, n in enumerate(names)]
    effects.check(plan, work / 'tous.plan.json')
    source = clip(len(names) * SPAN + 1, framing, work)
    at = ','.join(str(round(i * SPAN + SPAN * .62, 2)) for i in range(len(names)))
    frames = work / 'images'
    frames.mkdir(parents=True, exist_ok=True)
    result = effects.render(source, plan, frames / 'e.png', profile='draft', stills=at, brand_ui_ok=True)
    made = sorted(frames.glob('e_*.png'), key=lambda f: float(f.stem.split('_')[1]))
    PROOFS.mkdir(parents=True, exist_ok=True)
    cols, cw, ch = (13, 150, 267) if framing == 'vertical' else (8, 240, 135)
    inputs = sum((['-i', str(f)] for f in made), [])
    layout = '|'.join(f'{(i % cols) * cw}_{(i // cols) * ch}' for i in range(len(made)))
    scale = ';'.join(f'[{i}:v]scale={cw}:{ch}[v{i}]' for i in range(len(made)))
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error'] + inputs + ['-filter_complex', scale + ';' + ''.join(f'[v{i}]' for i in range(len(made))) + f'xstack=inputs={len(made)}:layout={layout}:fill=black', '-frames:v', '1', str(PROOFS / f'planche-{framing}.jpg')], check=True)
    report = {'effets': len(names), 'images': len(made), 'pass': len(made) == len(names), 'tracking': result['tracking'], 'versions': sorted(x.split('==')[0] + ' ' + x.split('==')[1].split()[0] for x in (modules.LOCKS / 'versions.txt').read_text(encoding='utf-8').splitlines() if x.split('==')[0] in ('mediapipe', 'opencv-python', 'numpy', 'pillow')),
              'limite': 'Clip sans personne : le suivi du visage et le passage derrière la tête ne sont pas prouvés ici.'}
    (PROOFS / f'resultats-{framing}.json').write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False))
    return 0 if report['pass'] else 1


if __name__ == '__main__':
    sys.exit(main())
