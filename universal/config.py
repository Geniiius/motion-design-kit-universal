"""One place for the kit's settings.

kit.config.json holds the defaults that ship with the kit. kit.config.local.json holds what one user changed:
it is never shared and survives an update of the kit. A broken local file never stops a video: defaults apply.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULTS = ROOT / 'kit.config.json'
LOCAL = ROOT / 'kit.config.local.json'


def _merge(base: dict, over: dict) -> dict:
    out = dict(base)
    for k, v in over.items():
        out[k] = _merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def load() -> dict:
    data = json.loads(DEFAULTS.read_text(encoding='utf-8'))
    if LOCAL.exists():
        try:
            data = _merge(data, json.loads(LOCAL.read_text(encoding='utf-8-sig')))
        except ValueError:
            pass
    return data


def get(path: str, default=None):
    """get('workflows.silence.padding_s')"""
    node = load()
    for key in path.split('.'):
        if not isinstance(node, dict) or key not in node:
            return default
        node = node[key]
    return node


def set_local(path: str, value) -> None:
    """Writes one setting into the user's own file, leaving the shipped defaults untouched."""
    data = {}
    if LOCAL.exists():
        try:
            data = json.loads(LOCAL.read_text(encoding='utf-8-sig'))
        except ValueError:
            data = {}
    node = data
    keys = path.split('.')
    for key in keys[:-1]:
        node = node.setdefault(key, {})
    node[keys[-1]] = value
    LOCAL.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
