"""The kit's existing engines still work. python tests/regression.py -> docs/preuves/regression.json"""
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding='utf-8')

from universal.qc import qc  # noqa: E402

PROOFS = ROOT / 'docs' / 'preuves' / 'regression'
CLI = ROOT / 'template/node_modules/@remotion/cli/remotion-cli.js'
ENV = {**os.environ, 'HYPERFRAMES_SKIP_SKILLS': '1', 'HYPERFRAMES_NO_TELEMETRY': '1', 'DO_NOT_TRACK': '1', 'HYPERFRAMES_NO_UPDATE_CHECK': '1'}
NPX = 'npx.cmd' if platform.system() == 'Windows' else 'npx'
rows = []


def sh(args, cwd, timeout=600):
    start = time.time()
    r = subprocess.run([str(a) for a in args], cwd=cwd, capture_output=True, text=True, encoding='utf-8', errors='replace', env=ENV, timeout=timeout, shell=isinstance(args[0], str) and args[0].endswith('.cmd'))
    return r, round(time.time() - start)


def record(name, ok, detail, proof=None, status=None):
    rows.append({'test': name, 'status': status or ('PASS' if ok else 'FAIL'), 'detail': str(detail)[-260:], 'proof': proof})
    print(rows[-1]['status'], name, '-', rows[-1]['detail'][:150], flush=True)


def main():
    PROOFS.mkdir(parents=True, exist_ok=True)
    node = 'node'
    t = ROOT / 'template'
    r, s = sh([NPX, 'tsc', '--noEmit'], t)
    record('TypeScript du modèle Remotion', r.returncode == 0, f'{s} s ' + r.stdout[-160:])
    # Node vide stdout de façon asynchrone dans un tube Windows et la liste peut se perdre : elle passe par un fichier
    listing = PROOFS / 'compositions.txt'
    with open(listing, 'w', encoding='utf-8') as f:
        code = subprocess.run([node, str(CLI), 'compositions', 'src/index.ts'], cwd=t, stdout=f, stderr=subprocess.DEVNULL, env=ENV).returncode
    n = len(re.findall(r'\d{3,4}x\d{3,4}', listing.read_text(encoding='utf-8')))
    record('Compositions listées', code == 0 and n >= 37, f'{n} compositions')
    r, s = sh([node, CLI, 'versions'], t)
    record('Versions Remotion cohérentes', 'correct version' in r.stdout, r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-120:])
    r, s = sh(['npm.cmd' if platform.system() == 'Windows' else 'npm', 'audit', '--omit=dev', '--json'], t)
    try:
        v = json.loads(r.stdout)['metadata']['vulnerabilities']
        record('npm audit (production)', v['total'] == 0, v)
    except (ValueError, KeyError):
        record('npm audit (production)', False, 'non lisible', status='NOT TESTED')
    for comp, frame in (('Promo-Landscape', 60), ('Kinetic-Reel', 60), ('Showcase-Landscape', 90)):
        png = PROOFS / f'{comp}.png'
        r, s = sh([node, CLI, 'still', 'src/index.ts', comp, png, f'--frame={frame}', '--scale=0.5', '--log=error'], t)
        record(f'Modèle 2D existant : {comp}', r.returncode == 0 and png.exists(), f'{s} s', str(png.relative_to(ROOT)))
    mp4 = PROOFS / 'logo-square.mp4'
    r, s = sh([node, CLI, 'render', 'src/index.ts', 'Logo-Square', mp4, '--scale=0.5', '--color-space=bt709', '--log=error'], t)
    report = qc(mp4, exceptions=[{'type': 'no-audio'}], audio_target=None) if mp4.exists() else {'pass': False, 'pix_fmt': None, 'blocking': ['pas de sortie']}
    record('Vidéo 2D existante rendue : Logo-Square', r.returncode == 0 and report['pass'] and report['pix_fmt'] == 'yuv420p', f"{s} s, {report.get('pix_fmt')}, {report['blocking'] or 'QC OK'}")
    png = PROOFS / 'cpu-swangle.png'
    r, s = sh([node, CLI, 'still', 'src/index.ts', 'Personaje-Nodo-Landscape', png, '--frame=60', '--scale=0.4', '--gl=swangle', '--log=error'], t)
    record('Repli CPU pour la 3D (swangle)', r.returncode == 0 and png.exists(), f'{s} s', str(png.relative_to(ROOT)))
    r, s = sh([node, 'render.mjs', 'compositions/studio-hud.html', '--from', '0', '--to', '1.5', '--out', PROOFS / 'prompt-motion.mp4'], ROOT / 'prompt-motion')
    record('Prompt Motion : rendu', r.returncode == 0 and (PROOFS / 'prompt-motion.mp4').exists(), f'{s} s')
    with tempfile.TemporaryDirectory(prefix='hf-') as tmp:
        hf = Path(tmp) / 'hf'
        shutil.copytree(ROOT / 'hyperframes-starter', hf, ignore=shutil.ignore_patterns('.hyperframes'))
        r, s = sh([NPX, '--yes', 'hyperframes@0.8.164', 'check'], hf)
        record('HyperFrames 0.8.164 : check du starter', r.returncode == 0, f'{s} s, sortie {r.returncode}')
        r, s = sh([NPX, '--yes', 'hyperframes@0.8.164', 'add', 'data-chart', '--no-clipboard'], hf)
        record('HyperFrames : bloc du registre fixé (data-chart)', r.returncode == 0 and (hf / 'compositions/data-chart.html').exists(), f'{s} s, compositions/data-chart.html créé')
        out = PROOFS / 'hyperframes.mp4'
        r, s = sh([NPX, '--yes', 'hyperframes@0.8.164', 'render', '--quality', 'draft', '--output', out], hf, timeout=580)
        record('HyperFrames : rendu du starter', r.returncode == 0 and out.exists(), f'{s} s, MP4 créé')
    (ROOT / 'docs' / 'preuves' / 'regression.json').write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding='utf-8')
    return 1 if any(x['status'] == 'FAIL' for x in rows) else 0


if __name__ == '__main__':
    sys.exit(main())
