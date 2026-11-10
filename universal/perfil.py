"""What the kit remembers about its user: read before routing, written after each delivery. Stays in perfil/, never shared.

Facts the code can establish on its own live here (quality history, habits). Tastes in words stay in
perfil/mi-estilo.md and perfil/aprendizajes.md, which the agent keeps (skill motion-memoria).
"""
from __future__ import annotations
import datetime
import json
import re
import shutil
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / 'perfil'
HABIT_AFTER = 2  # the same choice twice in a row becomes the default
SHAPES = {'16:9': 16 / 9, '9:16': 9 / 16, '1:1': 1.0, '4:5': 4 / 5}
RECENT = 10


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding='utf-8-sig', errors='replace').splitlines():
        try:
            rows.append(json.loads(line))
        except ValueError:
            continue  # a line edited by hand must not stop a video
    return rows


def _append(path: Path, row: dict) -> None:
    if not DIR.exists() and (ROOT / 'perfil-plantilla').exists():
        shutil.copytree(ROOT / 'perfil-plantilla', DIR)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'a', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps(row, ensure_ascii=False) + '\n')


def preferences() -> dict:
    f = DIR / 'preferencias.json'
    try:
        return json.loads(f.read_text(encoding='utf-8-sig')) if f.exists() else {}
    except ValueError:
        return {}


def brands() -> list[str]:
    folder = DIR / 'marcas'
    return sorted(p.stem for p in folder.glob('*.md') if not p.stem.startswith('_')) if folder.exists() else []


def brand_for(brief: str) -> str | None:
    """The brand the request names, or the only one on file."""
    names = brands()
    text = brief.lower()
    return next((n for n in names if n.lower() in text), names[0] if len(names) == 1 else None)


def _problem_key(text: str) -> str:
    """Same problem, different numbers: « Crête haute -0.9 dBFS » and « Crête haute -0.7 dBFS » count together."""
    return re.sub(r'\s+', ' ', re.sub(r'-?\d+(?:[.,]\d+)?', '#', text)).strip()


def recurring_problems(minimum: int = 2) -> list[str]:
    seen: Counter = Counter()
    for row in _read_jsonl(DIR / 'calidad.jsonl')[-RECENT:]:
        for key in {_problem_key(p) for p in row.get('problemas', [])}:
            seen[key] += 1
    return [p for p, n in seen.most_common() if n >= minimum]


def habit(field: str) -> str | None:
    """A value is a habit once the last deliveries agree on it."""
    rows = [r.get(field) for r in _read_jsonl(DIR / 'historial.jsonl')[-HABIT_AFTER:]]
    if field == 'format' and rows and rows[0] not in SHAPES:
        return None  # only a real shape can become a default
    return rows[0] if len(rows) == HABIT_AFTER and rows[0] and all(r == rows[0] for r in rows) else None


def learned_rules(limit: int = 8) -> list[str]:
    f = DIR / 'aprendizajes.md'
    if not f.exists():
        return []
    m = re.search(r'## Reglas aprendidas[^\n]*\n(.*?)(?=\n## |\Z)', f.read_text(encoding='utf-8', errors='replace'), re.S)
    rows = re.findall(r'^- (.+)$', m.group(1), re.M) if m else []
    return [r.strip() for r in rows if 'aún sin' not in r][:limit]


def context(brief: str = '') -> dict:
    """Everything the router and the agent should know before deciding anything."""
    prefs = preferences()
    return {'idioma_por_defecto': prefs.get('idioma_por_defecto'), 'idioma_video': prefs.get('idioma_video'), 'formato_habitual': habit('format'), 'marca': brand_for(brief),
            'problemas_recurrentes': recurring_problems(), 'reglas': learned_rules(), 'videos_entregados': len(_read_jsonl(DIR / 'historial.jsonl'))}


def shape_name(deliverable: dict) -> str | None:
    """The format as a habit can use it. A provided video kept in its own shape counts as 9:16 if that is what it is, and as nothing otherwise."""
    fmt, w, h = deliverable.get('format'), deliverable.get('width'), deliverable.get('height')
    if fmt in SHAPES:
        return fmt
    return next((name for name, ratio in SHAPES.items() if w and h and abs(w / h - ratio) < .03), None)


def remember_delivery(project: dict, deliverable: dict, result: dict) -> None:
    """Called after each delivery, so that learning does not depend on anyone remembering to do it."""
    report = result.get('qc') or {}
    today = datetime.date.today().isoformat()
    _append(DIR / 'historial.jsonl', {'fecha': today, 'proyecto': project['name'], 'format': shape_name(deliverable), 'engine': deliverable['adapter']['engine'],
                                      'estilo': project['style'].get('film_style') or project['style'].get('preset'), 'idioma': deliverable.get('language'), 'duracion': report.get('duration')})
    _append(DIR / 'calidad.jsonl', {'fecha': today, 'proyecto': project['name'], 'plataforma': shape_name(deliverable), 'duracion': report.get('duration'),
                                    'lufs': (report.get('audio') or {}).get('lufs'), 'pico': (report.get('audio') or {}).get('true_peak'), 'ok': bool(report.get('pass')),
                                    'problemas': list(report.get('blocking', [])) + list(report.get('warnings', []))})
