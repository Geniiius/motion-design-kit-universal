"""What the kit knows about its own installation on this machine: kit-state.json, never shared.

A kit folder copied to another computer starts over: the state carries a fingerprint of the machine it was written on.
The fingerprint is a hash, so the file holds no machine or user name.
"""
from __future__ import annotations
import datetime
import hashlib
import json
import platform
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / 'kit-state.json'
SCHEMA = 1


def fingerprint() -> str:
    raw = '|'.join((platform.node(), platform.system(), platform.machine(), str(ROOT)))
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()[:16]


def now() -> str:
    return datetime.datetime.now().isoformat(timespec='seconds')


def blank() -> dict:
    return {'schema': SCHEMA, 'machine': fingerprint(), 'configured': False, 'consent': {}, 'components': {}, 'steps': {}, 'encoders': {}, 'installed_by_kit': []}


def load() -> dict:
    """The saved state, or a blank one when there is none, when it is unreadable or when it comes from another machine."""
    if not FILE.exists():
        return blank()
    try:
        data = json.loads(FILE.read_text(encoding='utf-8'))
    except ValueError:
        return {**blank(), 'note': 'état illisible : repris de zéro'}
    if data.get('schema') != SCHEMA or data.get('machine') != fingerprint():
        return {**blank(), 'note': 'état venu d\'une autre machine ou d\'un autre dossier : repris de zéro'}
    return {**blank(), **data}


def save(data: dict) -> None:
    data = {**data, 'schema': SCHEMA, 'machine': fingerprint(), 'saved_at': now()}
    FILE.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n', encoding='utf-8', newline='\n')


def update(**fields) -> dict:
    data = load()
    data.pop('note', None)
    for key, value in fields.items():
        if isinstance(value, dict) and isinstance(data.get(key), dict):
            data[key] = {**data[key], **value}
        else:
            data[key] = value
    save(data)
    return data
