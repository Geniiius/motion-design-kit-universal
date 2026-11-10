"""project.json contract: validated against schema/project.schema.json with no third-party dependency.

Supports the JSON Schema keywords the contract uses: type, required, enum, properties,
additionalProperties (false), items, minItems, minimum, pattern.
"""
from __future__ import annotations
import json
import re
from pathlib import Path

SCHEMA_PATH = Path(__file__).resolve().parent / 'schema' / 'project.schema.json'
TYPES = {'object': dict, 'array': list, 'string': str, 'boolean': bool, 'null': type(None)}


def _type_ok(value, name: str) -> bool:
    if name == 'number':
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if name == 'integer':
        return isinstance(value, int) and not isinstance(value, bool)
    return isinstance(value, TYPES[name])


def errors(value, schema: dict, where: str = '$') -> list[str]:
    out: list[str] = []
    t = schema.get('type')
    if t and not any(_type_ok(value, x) for x in ([t] if isinstance(t, str) else t)):
        return [f'{where}: type {type(value).__name__}, attendu {t}']
    if 'enum' in schema and value not in schema['enum']:
        out.append(f'{where}: {value!r} hors de {schema["enum"]}')
    if 'pattern' in schema and isinstance(value, str) and not re.search(schema['pattern'], value):
        out.append(f'{where}: format invalide')
    if 'minimum' in schema and isinstance(value, (int, float)) and value < schema['minimum']:
        out.append(f'{where}: inférieur à {schema["minimum"]}')
    if isinstance(value, dict):
        for k in schema.get('required', []):
            if k not in value:
                out.append(f'{where}: champ requis manquant « {k} »')
        props = schema.get('properties', {})
        for k, v in value.items():
            if k in props:
                out += errors(v, props[k], f'{where}.{k}')
            elif schema.get('additionalProperties') is False:
                out.append(f'{where}: champ inconnu « {k} »')
    if isinstance(value, list):
        if len(value) < schema.get('minItems', 0):
            out.append(f'{where}: au moins {schema["minItems"]} élément(s)')
        if 'items' in schema:
            for i, v in enumerate(value):
                out += errors(v, schema['items'], f'{where}[{i}]')
    return out


def validate(project: dict) -> list[str]:
    return errors(project, json.loads(SCHEMA_PATH.read_text(encoding='utf-8')))


def save(project: dict, path: Path) -> Path:
    problems = validate(project)
    if problems:
        raise ValueError('Manifeste invalide:\n- ' + '\n- '.join(problems[:12]))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(project, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return path


def load(path: Path) -> dict:
    project = json.loads(Path(path).read_text(encoding='utf-8'))
    problems = validate(project)
    if problems:
        raise ValueError('Manifeste invalide:\n- ' + '\n- '.join(problems[:12]))
    return project
