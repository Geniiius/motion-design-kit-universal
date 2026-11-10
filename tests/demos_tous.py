"""Runs every demonstrator and writes docs/preuves/demos.json. python tests/demos_tous.py [profil] [noms...] [--accord]

--accord autorise les appels payants des démos FR et ES (ElevenLabs). Sans lui, seul le cache est lu."""
import json
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding='utf-8')

from universal.demos import ALL, PAID, PROOFS  # noqa: E402


def main():
    args = [a for a in sys.argv[1:] if a != '--accord']
    approved = '--accord' in sys.argv
    profile = args[0] if args else 'review'
    names = args[1:] or list(ALL)
    path = PROOFS / 'demos.json'
    results = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    for name in names:
        start = time.time()
        try:
            r = PAID[name](profile, approved) if name in PAID else ALL[name](profile)
        except Exception as e:  # a failing demo must not hide the others
            r = {'demo': name, 'pass': False, 'error': str(e)[-600:], 'trace': traceback.format_exc()[-300:]}
        r['seconds'] = round(time.time() - start)
        r['profile'] = profile
        results[name] = r
        print(json.dumps({k: r.get(k) for k in ('demo', 'pass', 'seconds', 'blocking', 'warnings', 'error')}, ensure_ascii=False))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding='utf-8')
    return 0 if all(r.get('pass') for r in results.values()) else 1


if __name__ == '__main__':
    sys.exit(main())
