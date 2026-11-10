"""Technical log of what the kit installed, checked and repaired: logs/, inside the kit, never shared.

Every line is scrubbed before it is written: no key, no token, no user or machine name, no home folder.
A log that cannot be written never stops the work.
"""
from __future__ import annotations
import datetime
import json
import os
import platform
import re
from pathlib import Path
from . import config

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / 'logs'
MASK = '[masqué]'
SECRETS = re.compile(r"""(?ix)
    \b(?:sk|xi|pk|rk|ghp|gho|hf)[-_][a-z0-9_\-]{12,}                                  # the shape of a provider key
  | \b(?:bearer|basic)\s+[a-z0-9._~+/=\-]{8,}                                         # an authorization header
  | (?P<name>(?:api[-_]?key|token|secret|password|passwd|authorization)["']?\s*[:=]\s*["']?(?:(?:bearer|basic)\s+)?)[^\s"',;]{4,}
""")


def scrub(text) -> str:
    text = str(text)
    for name, value in os.environ.items():  # the value of anything that looks like a secret, wherever it shows up
        if value and len(value) >= 8 and re.search(r'KEY|TOKEN|SECRET|PASSW', name, re.I):
            text = text.replace(value, MASK)
    text = SECRETS.sub(lambda m: (m.group('name') or '') + MASK, text)
    home = str(Path.home())
    for form in sorted({home, home.replace(os.sep, '/')}, key=len, reverse=True):
        text = re.sub(re.escape(form), '~', text, flags=re.I)
    for private in {os.environ.get('USERNAME'), os.environ.get('USER'), platform.node()}:
        if private and len(private) >= 3:
            text = re.sub(rf'(?<![A-Za-z0-9]){re.escape(private)}(?![A-Za-z0-9])', '[privé]', text, flags=re.I)
    return text


def clean(value):
    if isinstance(value, str):
        return scrub(value)[:4000]
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [clean(v) for v in value]
    if isinstance(value, Path):
        return scrub(value)
    return value


def write(event: str, **fields) -> None:
    try:
        DIR.mkdir(exist_ok=True)
        now = datetime.datetime.now()
        row = {'at': now.isoformat(timespec='seconds'), 'event': event, **clean(fields)}
        with open(DIR / f'kit-{now:%Y-%m-%d}.jsonl', 'a', encoding='utf-8', newline='\n') as f:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
        prune()
    except (OSError, TypeError, ValueError):
        pass


def prune() -> None:
    keep = config.get('logs.keep_days', 30)
    limit = datetime.date.today() - datetime.timedelta(days=keep)
    for f in DIR.glob('kit-*.jsonl'):
        try:
            if datetime.date.fromisoformat(f.stem[4:]) < limit:
                f.unlink()
        except (ValueError, OSError):
            continue


def tail(count: int = 30) -> list[dict]:
    rows = []
    for f in sorted(DIR.glob('kit-*.jsonl'))[-3:] if DIR.exists() else []:
        for line in f.read_text(encoding='utf-8', errors='replace').splitlines():
            try:
                rows.append(json.loads(line))
            except ValueError:
                continue
    return rows[-count:]
