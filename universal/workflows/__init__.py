"""Treatments for a video the user provides: silences, clips, reframing, captions, chapters.

One module per treatment. Each declares ID, ORDER, TITLE, WORDS and NEEDS, and exposes run(ctx, track) -> [Track].
Adding a treatment is adding a file here: the registry finds it, the router learns its words, the chain runs it in its order.
Steps go file to file, and one delivery encode ends the chain. A step that needs a reader's decision raises NeedsInput:
nothing is delivered on a guess.
"""
from __future__ import annotations
import importlib
import pkgutil
import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from . import tools

FORMATS = {'16:9': (1920, 1080), '9:16': (1080, 1920), '1:1': (1080, 1080), '4:5': (1080, 1350)}
HDR = ('arib-std-b67', 'smpte2084')


class NeedsInput(RuntimeError):
    """The treatment prepared what it could and now waits for a choice or a text only a reader can give."""

    def __init__(self, message: str, file: Path | None = None, reset: tuple | None = None):
        super().__init__(message)
        self.file = str(file) if file else None
        self.reset = reset  # (step, option) to clear in the manifest: an earlier "reviewed" no longer applies to a new text


@dataclass
class Track:
    video: Path
    suffix: str = ''
    files: list = field(default_factory=list)
    expected_s: float | None = None
    changed: bool = False


@dataclass
class Context:
    project: dict
    deliverable: dict
    profile: str
    work: Path
    out_dir: Path
    name: str
    options: dict
    frame: tuple
    notes: list = field(default_factory=list)
    counter: int = 0

    def temp(self, label: str) -> Path:
        self.counter += 1
        return self.work / f'{self.counter:02d}-{label}.mp4'

    def opt(self, step: str, key: str, default=None):
        return (self.options.get(step) or {}).get(key, default)


def registry() -> dict:
    found = {}
    for m in pkgutil.iter_modules(__path__):
        if m.name.startswith('_'):
            continue  # helper scripts run by another Python
        mod = importlib.import_module(f'{__name__}.{m.name}')
        if hasattr(mod, 'ID'):
            found[mod.ID] = mod
    return dict(sorted(found.items(), key=lambda kv: kv[1].ORDER))


def catalog(language: str = 'fr') -> list[dict]:
    return [{'id': m.ID, 'titre': m.TITLE.get(language, m.TITLE['fr']), 'besoins': list(m.NEEDS)} for m in registry().values()]


def frame_for(deliverable: dict, meta: dict, profile: str) -> tuple[int, int]:
    """The delivered frame: the asked format at this profile's size, or the source's own shape when none was asked."""
    fmt = deliverable.get('format')
    if fmt in FORMATS:
        w, h = FORMATS[fmt]
        k = tools.PROFILES[profile] / 1920
        return tools.even(w * k), tools.even(h * k)
    return tools.fit(meta['width'], meta['height'], profile)


def _prepare(ctx: Context, src: Path) -> Path:
    """HDR phone footage read as standard video looks washed out: bring it to standard colours once, before anything else."""
    data = tools.probe(src)
    v = next((s for s in data.get('streams', []) if s.get('codec_type') == 'video'), {})
    if v.get('color_transfer') not in HDR:
        return src
    out = ctx.temp('couleurs')
    chain = 'zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p'
    try:
        tools.ffmpeg(['-i', src, '-vf', chain] + tools.INTERMEDIATE + [out], cwd=ctx.work)
    except RuntimeError:
        ctx.notes.append('Vidéo HDR : la conversion des couleurs a échoué, l\'image peut paraître terne.')
        return src
    ctx.notes.append('Vidéo HDR convertie en couleurs standard.')
    return out


def run_steps(project: dict, deliverable: dict, out_dir: Path, profile: str, finisher=None) -> dict:
    """`finisher(video, final, frame)` replaces the plain delivery encode, for instance to lay a logo or a music over it."""
    mods = registry()
    steps = list(dict.fromkeys(deliverable['adapter'].get('steps') or []))
    unknown = [s for s in steps if s not in mods]
    if unknown:
        raise ValueError(f"Traitement inconnu : {', '.join(unknown)}. Disponibles : {', '.join(mods)}")
    item = next((x for x in project['inputs'] if x['exists'] and x['type'] == 'video'), None)
    if not item:
        raise ValueError('Aucune vidéo fournie.')
    src = Path(item['path'])
    meta = tools.info(src)
    frame = frame_for(deliverable, meta, profile)
    if abs(meta['width'] / meta['height'] - frame[0] / frame[1]) > .03 and 'reframe' not in steps:
        steps.append('reframe')  # another shape was asked: the picture has to be reframed, not stretched
    ordered = sorted((mods[s] for s in steps), key=lambda m: m.ORDER)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    name = project['name']
    with tempfile.TemporaryDirectory(prefix='traitement-') as tmp:
        ctx = Context(project, deliverable, profile, Path(tmp), out_dir, name, (project.get('props') or {}).get('workflow') or {}, frame)
        first = _prepare(ctx, src)
        tracks = [Track(first, expected_s=meta['duration'], changed=first != src)]
        for mod in ordered:
            tracks = [t for track in tracks for t in mod.run(ctx, track)]
        outputs = []
        for t in tracks:
            entry = {'output': None, 'files': [str(f) for f in t.files], 'expected_s': round(t.expected_s, 2) if t.expected_s else None}
            if t.changed or finisher:  # a video no treatment touched is not encoded again: the original stays the right file
                final = out_dir / f'{name}{t.suffix}.mp4'
                done = finisher(t.video, final, frame) if finisher else tools.finish(t.video, final, width=frame[0], height=frame[1], profile=profile, work=ctx.work)
                entry.update(output=str(final), **done)
            outputs.append(entry)
    return {'output': next((o['output'] for o in outputs if o['output']), None), 'outputs': outputs, 'steps': [m.ID for m in ordered], 'notes': list(dict.fromkeys(ctx.notes)),
            'engine': 'video-workflow', 'profile': profile, 'width': frame[0], 'height': frame[1]}
