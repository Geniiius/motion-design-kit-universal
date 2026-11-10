"""Reads the short brief format of examples/universal and turns it into a routed project."""
from __future__ import annotations
import json
from pathlib import Path
from .inventory import classify, inspect
from .router import FORMATS, route

__all__ = ['FORMATS', 'classify', 'resolve_asset', 'read_spec', 'plan']


def resolve_asset(root: Path, asset: str | dict) -> Path:
    s = asset if isinstance(asset, str) else asset.get('path', '')
    if not s or not isinstance(s, str):
        raise ValueError('asset.path manquant')
    p = Path(s).expanduser()
    return (p if p.is_absolute() else root / p).resolve()


def read_spec(path: Path) -> dict:
    obj = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(obj, dict):
        raise ValueError('Le manifeste doit être un objet JSON')
    if 'format' in obj and obj['format'] not in FORMATS:
        raise ValueError('Format invalide. Utiliser 16:9, 9:16, 1:1 ou 4:5')
    if 'assets' in obj and not isinstance(obj['assets'], list):
        raise ValueError('assets doit être une liste')
    return obj


LEGACY_INTENT = {'interactive': 'INTERACTIVE_PRESENTATION', 'presentation': 'INTERACTIVE_PRESENTATION', 'infographic': 'DATA_EXPLAINER',
                 'explainer': 'DATA_EXPLAINER', 'character3d': 'CHARACTER_ANIMATION', '3d': 'CHARACTER_ANIMATION', 'model3d': 'CHARACTER_ANIMATION',
                 'edit': 'EDIT_FOOTAGE', 'montage': 'EDIT_FOOTAGE', 'logo': 'ANIMATE_LOGO', 'create': 'CREATE_FROM_SCRATCH'}


def plan(spec: dict, base: Path) -> dict:
    inputs = [inspect(a, base) for a in spec.get('assets', [])]
    wanted = LEGACY_INTENT.get(str(spec.get('intent', '')).lower())
    return route(' '.join(str(spec.get(k, '')) for k in ('brief', 'title')).strip(), inputs, name=spec.get('name', 'projet'), language=spec.get('language'),
                 style=spec.get('style'), fmt=spec.get('format'), duration=spec.get('duration'), intent=[wanted] if wanted else None)
