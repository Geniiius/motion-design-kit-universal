"""Real asset inventory: reads files with ffprobe and their headers, never the extension alone.

Originals are only read. Anything that transforms a file works on a copy.
"""
from __future__ import annotations
import csv
import hashlib
import json
import re
import shutil
import struct
import subprocess
import zipfile
from pathlib import Path

IMAGE_EXT = {'.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tif', '.tiff', '.svg', '.gif'}
VIDEO_EXT = {'.mp4', '.mov', '.mkv', '.webm', '.avi', '.m4v'}
AUDIO_EXT = {'.mp3', '.wav', '.aac', '.m4a', '.flac', '.ogg'}
MODEL_EXT = {'.glb', '.gltf', '.fbx', '.obj', '.vrm', '.blend'}
DOC_EXT = {'.pdf', '.md', '.txt', '.pptx', '.docx'}
DATA_EXT = {'.csv', '.tsv', '.json', '.xlsx'}
SUB_EXT = {'.srt', '.vtt'}
ALPHA_FMT = re.compile(r'^(yuva|rgba|bgra|argb|abgr|gbrap|ya|pal8)')
VISEME_NAMES = re.compile(r'viseme|jawopen|mouth|^aa$|^ih$|^ou$|^ee$|^oh$', re.I)


def classify(path: Path) -> str:
    if str(path).lower().startswith(('http://', 'https://')):
        return 'url'
    if path.is_dir():
        return 'project'
    x = path.suffix.lower()
    for kind, group in (('image', IMAGE_EXT), ('video', VIDEO_EXT), ('audio', AUDIO_EXT), ('3d', MODEL_EXT),
                        ('document', DOC_EXT), ('data', DATA_EXT), ('subtitles', SUB_EXT)):
        if x in group:
            return kind
    return 'unknown'


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def ffprobe(path: Path) -> dict:
    if not shutil.which('ffprobe'):
        return {}
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    return json.loads(r.stdout or '{}') if r.returncode == 0 else {}


def _rate(value: str | None) -> float:
    try:
        a, b = (value or '0/1').split('/')
        return round(float(a) / float(b), 3) if float(b) else 0.0
    except ValueError:
        return 0.0


def _rotation(stream: dict) -> int:
    for side in stream.get('side_data_list', []):
        if 'rotation' in side:
            return int(side['rotation'])
    return int(stream.get('tags', {}).get('rotate', 0) or 0)


def _media(path: Path, kind: str) -> dict:
    data = ffprobe(path)
    streams = data.get('streams', [])
    v = next((s for s in streams if s.get('codec_type') == 'video' and not s.get('disposition', {}).get('attached_pic')), None)
    a = next((s for s in streams if s.get('codec_type') == 'audio'), None)
    meta: dict = {'container': data.get('format', {}).get('format_name')}
    try:
        meta['duration_s'] = round(float(data['format']['duration']), 3)
    except (KeyError, ValueError, TypeError):
        pass
    if v:
        rot = _rotation(v)
        w, h = int(v.get('width', 0)), int(v.get('height', 0))
        meta.update(width=w, height=h, rotation=rot, codec=v.get('codec_name'), pix_fmt=v.get('pix_fmt'),
                    alpha=bool(ALPHA_FMT.match(v.get('pix_fmt') or '')),
                    color_space=v.get('color_space'), color_transfer=v.get('color_transfer'), color_range=v.get('color_range'))
        if rot in (90, -90, 270, -270):
            meta.update(display_width=h, display_height=w)
        if kind == 'video':
            avg, base = _rate(v.get('avg_frame_rate')), _rate(v.get('r_frame_rate'))
            meta.update(fps=avg, variable_frame_rate=bool(avg and abs(avg - base) / avg > .01))
    if a:
        meta['audio'] = {'codec': a.get('codec_name'), 'channels': a.get('channels'),
                         'sample_rate': a.get('sample_rate'), 'language': a.get('tags', {}).get('language')}
    return meta


def _svg(path: Path) -> dict:
    head = path.read_text(encoding='utf-8', errors='replace')[:4000]
    w, h = re.search(r'\bwidth="([\d.]+)', head), re.search(r'\bheight="([\d.]+)', head)
    box = re.search(r'viewBox="[\d.\-]+ [\d.\-]+ ([\d.]+) ([\d.]+)"', head)
    return {'vector': True, 'alpha': True,
            'width': float(w.group(1)) if w else float(box.group(1)) if box else None,
            'height': float(h.group(1)) if h else float(box.group(2)) if box else None}


def _gltf_json(path: Path) -> dict | None:
    if path.suffix.lower() == '.gltf':
        return json.loads(path.read_text(encoding='utf-8'))
    with open(path, 'rb') as f:
        head = f.read(20)
        if len(head) < 20 or head[:4] != b'glTF':
            return None
        size = struct.unpack('<I', head[12:16])[0]
        if head[16:20] != b'JSON':
            return None
        return json.loads(f.read(size).decode('utf-8'))


def _model(path: Path) -> dict:
    x = path.suffix.lower()
    if x in ('.fbx', '.obj', '.blend'):
        return {'readable': False, 'needs_conversion': 'glb'}
    doc = _gltf_json(path)
    if doc is None:
        return {'readable': False, 'error': "En-tête glTF invalide"}
    targets: list[str] = []
    for mesh in doc.get('meshes', []):
        targets += (mesh.get('extras') or {}).get('targetNames', [])
    exts = doc.get('extensions', {}) or {}
    return {'readable': True, 'meshes': len(doc.get('meshes', [])), 'skins': len(doc.get('skins', [])),
            'rigged': bool(doc.get('skins')), 'animations': [a.get('name', '') for a in doc.get('animations', [])],
            'morph_targets': sorted(set(targets)), 'visemes': any(VISEME_NAMES.search(t) for t in targets),
            'vrm': 'VRM' in exts or 'VRMC_vrm' in exts, 'generator': (doc.get('asset') or {}).get('generator')}


def _document(path: Path) -> dict:
    x = path.suffix.lower()
    if x in ('.txt', '.md'):
        text = path.read_text(encoding='utf-8', errors='replace')
        return {'words': len(text.split()), 'lines': text.count('\n') + 1}
    if x == '.pdf':
        return {'pages': len(re.findall(rb'/Type\s*/Page[^s]', path.read_bytes())), 'text_extracted': False}
    if x in ('.pptx', '.docx'):
        with zipfile.ZipFile(path) as z:
            return {'slides': sum(bool(re.match(r'ppt/slides/slide\d+\.xml', n)) for n in z.namelist())} if x == '.pptx' else {'parts': len(z.namelist())}
    return {}


def _data(path: Path) -> dict:
    x = path.suffix.lower()
    if x in ('.csv', '.tsv'):
        text = path.read_text(encoding='utf-8', errors='replace')
        lines = [l for l in text.splitlines() if l.strip() and not l.startswith('#')]
        rows = list(csv.reader(lines, delimiter='\t' if x == '.tsv' else ','))
        return {'rows': max(0, len(rows) - 1), 'columns': rows[0] if rows else [], 'comment_lines': text.count('\n#')}
    if x == '.json':
        doc = json.loads(path.read_text(encoding='utf-8'))
        return {'kind': type(doc).__name__, 'length': len(doc), 'keys': list(doc)[:12] if isinstance(doc, dict) else None}
    return {}


def _subtitles(path: Path) -> dict:
    text = path.read_text(encoding='utf-8', errors='replace')
    return {'cues': len(re.findall(r'-->', text)), 'format': path.suffix.lower().lstrip('.')}


def _project(path: Path) -> dict:
    markers = {'project.json': 'universal', 'remotion.config.ts': 'remotion', 'hyperframes.json': 'hyperframes', 'package.json': 'node'}
    found = sorted({v for k, v in markers.items() if (path / k).exists()})
    return {'engines': found, 'files': sum(1 for _ in path.glob('*'))}


ROLE_HINTS = (('logo', re.compile(r'logo', re.I)), ('voice', re.compile(r'voix|voz|voice|narration|locucion|\bvo\b', re.I)),
              ('music', re.compile(r'musi[cq]|bgm|soundtrack', re.I)))


def guess_role(path: str, kind: str) -> str:
    for role, rx in ROLE_HINTS:
        if rx.search(Path(path).name) and (kind in ('image', 'video') if role == 'logo' else kind == 'audio'):
            return role
    return {'audio': 'voice'}.get(kind, 'source')


def _warnings(kind: str, role: str, m: dict) -> list[str]:
    out = []
    if kind == 'image' and role == 'logo':
        if not m.get('vector') and not m.get('alpha'):
            out.append("Logo matriciel sans transparence : détourage nécessaire sur une copie, ne pas le présumer vectoriel.")
        if not m.get('vector') and m.get('width') and max(m['width'], m.get('height') or 0) < 512:
            out.append('Logo en basse définition : risque de flou à grande échelle, demander la source vectorielle.')
    if kind == 'image' and role != 'logo':
        out.append("Photo plate : pas d'information 3D réelle, la parallaxe est une simulation 2.5D.")
    if kind == 'video':
        if m.get('rotation'):
            out.append(f"Rotation {m['rotation']}° à appliquer au montage.")
        if m.get('variable_frame_rate'):
            out.append('Cadence variable : transcoder une copie avant le montage.')
        if not m.get('audio'):
            out.append('Clip sans piste audio.')
    if kind == '3d':
        if m.get('needs_conversion'):
            out.append('Format non lu directement : convertir en GLB.')
        elif m.get('readable') and not m.get('rigged'):
            out.append('Modèle sans squelette : pas de gestes sans rigging.')
        elif m.get('readable') and not m.get('visemes'):
            out.append('Pas de formes de bouche : synchronisation labiale impossible, repli sur la tête et le corps.')
    if kind == 'document' and m.get('text_extracted') is False:
        out.append("Texte non extrait automatiquement : le lire et citer les pages avant d'écrire un script.")
    return out


TREATMENTS = {
    ('image', 'logo'): ['réutiliser', 'animer sans déformer', 'respecter proportions et couleurs'],
    ('image', 'source'): ['recadrer', 'séparer en plans si faisable', 'mettre en mouvement'],
    ('video', 'source'): ['repérer', 'sélectionner', 'monter', 'étalonner'],
    ('audio', 'voice'): ['réutiliser', 'normaliser', 'transcrire'],
    ('audio', 'music'): ['réutiliser', 'baisser sous la voix'],
    ('3d', 'source'): ['vérifier licence', 'importer', 'animer'],
    ('document', 'source'): ['extraire fidèlement', 'citer la source'],
    ('data', 'source'): ['vérifier unités et dates', 'citer la source'],
    ('subtitles', 'source'): ['réutiliser', 'vérifier la synchronisation'],
    ('project', 'source'): ['inspecter', 'modifier sur une copie'],
    ('url', 'source'): ['capturer seulement si demandé'],
}


def inspect(item, base: Path | None = None) -> dict:
    """One manifest input record. `item` is a path or {path, role, rights, source}."""
    spec = item if isinstance(item, dict) else {'path': item}
    raw = str(spec.get('path', ''))
    if not raw:
        raise ValueError('asset.path manquant')
    if raw.lower().startswith(('http://', 'https://')):
        return {'path': raw, 'type': 'url', 'role': spec.get('role', 'source'), 'exists': True, 'metadata': {},
                'rights': spec.get('rights', {'status': 'unknown'}), 'provenance': {'source': raw},
                'treatment': TREATMENTS[('url', 'source')], 'warnings': ['URL non téléchargée : aucune requête réseau pendant le routage.']}
    p = Path(raw).expanduser()
    p = (p if p.is_absolute() or base is None else base / p).resolve()
    kind = classify(p)
    role = spec.get('role') or guess_role(raw, kind)
    rec = {'path': str(p), 'type': kind, 'role': role, 'exists': p.exists(), 'metadata': {},
           'rights': spec.get('rights', {'status': 'unknown'}), 'provenance': {'source': spec.get('source', 'user')}}
    if p.is_file():
        rec['provenance'].update(sha256=sha256(p), bytes=p.stat().st_size)
        if kind == 'image' and p.suffix.lower() == '.svg':
            rec['metadata'] = _svg(p)
        elif kind == 'image':
            rec['metadata'] = {**_media(p, kind), 'vector': False}
        elif kind in ('video', 'audio'):
            rec['metadata'] = _media(p, kind)
        elif kind == '3d':
            rec['metadata'] = _model(p)
        elif kind == 'document':
            rec['metadata'] = _document(p)
        elif kind == 'data':
            rec['metadata'] = _data(p)
        elif kind == 'subtitles':
            rec['metadata'] = _subtitles(p)
    elif p.is_dir():
        rec['metadata'] = _project(p)
    rec['treatment'] = TREATMENTS.get((kind, role)) or TREATMENTS.get((kind, 'source'), ['inspecter'])
    rec['warnings'] = _warnings(kind, role, rec['metadata']) + ([] if p.exists() else ['Fichier absent.'])
    return rec


def contact_sheet(paths: list[Path], out: Path, columns: int = 5, cell: int = 320) -> Path:
    """Repérage: one tiled image per call, from clips (sampled evenly) or stills."""
    out.parent.mkdir(parents=True, exist_ok=True)
    args, chains = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y'], []
    per_clip = max(1, columns * 2 // max(1, len(paths)))
    labels = []
    for i, p in enumerate(paths):
        args += ['-i', str(p)]
        if classify(p) == 'video':
            d = float(_media(p, 'video').get('duration_s') or 1) or 1
            chains.append(f"[{i}:v]fps={per_clip / d:.5f},scale={cell}:{cell * 9 // 16}:force_original_aspect_ratio=decrease,"
                          f"pad={cell}:{cell * 9 // 16}:(ow-iw)/2:(oh-ih)/2:color=0x101018,setsar=1[c{i}]")
        else:
            chains.append(f"[{i}:v]scale={cell}:{cell * 9 // 16}:force_original_aspect_ratio=decrease,"
                          f"pad={cell}:{cell * 9 // 16}:(ow-iw)/2:(oh-ih)/2:color=0x101018,setsar=1[c{i}]")
        labels.append(f'[c{i}]')
    join = ''.join(labels) + f'concat=n={len(labels)}:v=1:a=0,tile={columns}x{max(1, (per_clip * len(paths) + columns - 1) // columns)}:color=0x101018[o]'
    chains.append(join)
    subprocess.run(args + ['-filter_complex', ';'.join(chains), '-map', '[o]', '-frames:v', '1', str(out)],
                   check=True, capture_output=True)
    return out
