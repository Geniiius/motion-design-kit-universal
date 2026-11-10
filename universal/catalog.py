"""Searchable registry of styles, art directions and demonstrators (presets/*.json)."""
from __future__ import annotations
import json
from pathlib import Path
from .router import norm

PRESETS = Path(__file__).resolve().parents[1] / 'presets'


def load(name: str) -> dict:
    return json.loads((PRESETS / name).read_text(encoding='utf-8'))


def search(query: str = '', category: str | None = None, presets: bool = False) -> list[dict]:
    if presets:
        art, demos = load('art-directions.json')['directions'], load('demonstrators.json')['demonstrators']
        pool = [{**x, 'kind': 'direction'} for x in art] + [{**x, 'kind': 'demonstrateur'} for x in demos]
    else:
        pool = load('style-catalog.json')['styles']
    if category:
        pool = [x for x in pool if norm(category) in norm(x.get('categorie', ''))]
    words = norm(query).split()
    if words:
        scored = [(sum(w in norm(json.dumps(x, ensure_ascii=False)) for w in words), x) for x in pool]
        pool = [x for score, x in sorted(scored, key=lambda s: -s[0]) if score]
    return pool
