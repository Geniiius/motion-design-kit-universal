"""Runs a routed project.json: each deliverable goes to its engine, then through QC."""
from __future__ import annotations
import json
import subprocess
from pathlib import Path
from . import design_check, effects, film_style, manifest, perfil, present, remotion, workflows
from .qc import qc
from .render import edit, restyle_preview
from .workflows import tools as video

ROOT = Path(__file__).resolve().parents[1]
STILL_S = 2.5
NOT_UNDERSTOOD = ("Demande non comprise : aucun travail précis n'a été reconnu, et rien n'est livré au hasard. Comprendre le besoin, puis refaire le routage "
                  "en le précisant (intention, traitement, style ou effets), ou poser une question à l'utilisateur.")


def _edl_from_inputs(project: dict) -> tuple[list[dict], str]:
    """The edit list, and how it was decided. Whole media in order: cutting is a choice, never a default.
    Only a duration that was asked for shortens the clips, each by the same share."""
    edl = project['timeline'].get('edl') or []
    if edl:
        return edl, 'plan de montage fourni'
    media = [x for x in project['inputs'] if x['exists'] and x['type'] in ('video', 'image') and x['role'] not in ('logo', 'cover')]
    videos = [x for x in media if x['type'] == 'video']
    target = next((d.get('duration_s') for d in project['deliverables'] if d.get('duration_s')), None)
    stills = STILL_S * (len(media) - len(videos))
    total = sum(x['metadata'].get('duration_s') or 0 for x in videos) + stills
    share = max(1.0, (target - stills) / len(videos)) if target and videos and total > target * 1.05 else None
    out = []
    for i, x in enumerate(media):
        item = {'src': x['path'], 'transition': 'fade' if i else 'cut', 'fade_s': .4}
        if x['type'] == 'image':
            item['seconds'] = STILL_S
        elif share:
            item['seconds'] = round(min(share, x['metadata'].get('duration_s') or share), 2)
        out.append(item)
    if share:
        return out, f'durée demandée de {target:g} s répartie à parts égales, en gardant le début de chaque clip : passages à vérifier'
    return out, 'médias entiers, dans l\'ordre'


def _input(project: dict, role: str, kind: str) -> Path | None:
    x = next((i for i in project['inputs'] if i['exists'] and i['role'] == role and i['type'] == kind), None)
    return Path(x['path']) if x else None


def _size(d: dict, profile: str) -> tuple[int, int] | None:
    """The source's own shape when no format was asked: a vertical phone video stays vertical."""
    return video.fit(d['width'], d['height'], profile) if d.get('format') not in workflows.FORMATS and d.get('width') and d.get('height') else None


def _finisher(project: dict, profile: str):
    """A logo, a music or a voice handed over with the video goes into the last encode of a treatment chain."""
    logo, voice, music = _input(project, 'logo', 'image'), _input(project, 'voice', 'audio'), _input(project, 'music', 'audio')
    if not (logo or voice or music):
        return None

    def finish(src: Path, final: Path, frame: tuple) -> dict:
        edit([{'src': str(src)}], ROOT, final, profile=profile, size=frame, logo=logo, voice=voice, music=music)
        return {'encoder': 'libx264', 'loudness': 'normalisé', 'logo': bool(logo), 'voice': bool(voice), 'music': bool(music)}
    return finish


def _merge(reports: list[dict]) -> dict:
    """One verdict for several delivered files: all must pass, and every remark says which file it is about."""
    if not reports:
        return {'pass': True, 'blocking': [], 'warnings': [], 'note': 'Aucune vidéo à produire : fichiers texte seulement.'}
    tag = lambda r, items: [f"{r['file']} : {x}" for x in items] if len(reports) > 1 else list(items)
    first = reports[0]
    return {'pass': all(r['pass'] for r in reports), 'blocking': sum((tag(r, r['blocking']) for r in reports), []), 'warnings': sum((tag(r, r['warnings']) for r in reports), []),
            'declared': sum((tag(r, r.get('declared', [])) for r in reports), []), 'aesthetic': sum((tag(r, r.get('aesthetic', [])) for r in reports), []),
            'duration': first.get('duration'), 'audio': first.get('audio'), 'files': len(reports), 'proofs': first.get('proofs'), 'note': first.get('note')}


def run_deliverable(project: dict, d: dict, out_dir: Path, profile: str) -> dict:
    adapter = d['adapter']
    name = project['name']
    engine = adapter['engine']
    exceptions = project['quality'].get('exceptions', [])
    fmt = d.get('format') if d.get('format') in workflows.FORMATS else '16:9'
    if engine == 'html-deck':
        spec = project.get('props') or {'title': name, 'services': [{'title': 'Service', 'summary': project['request']['brief'][:90]}]}
        page = out_dir / f'{name}.html'
        result = present.presentation({**spec, 'language': d.get('language', 'fr')}, page)
        return {**result, 'deliverable': 'html', 'qc': {**design_check.as_report(design_check.check(page)), 'note': 'Interaction vérifiée par tests/deck.spec.mjs. Le contrôle de design conseille et ne bloque pas.'}}
    if engine == 'revision':
        raise RuntimeError(adapter['note'])
    if engine == 'video-workflow':
        result = workflows.run_steps(project, d, out_dir, profile, finisher=_finisher(project, profile))
        reports = []
        for o in result['outputs']:
            if o['output']:
                r = qc(Path(o['output']), out_dir / f"{Path(o['output']).stem}-preuves", exceptions=exceptions, expect={'duration_s': o['expected_s']} if o['expected_s'] else {})
                o['qc_pass'] = r['pass']
                reports.append({**r, 'file': Path(o['output']).name})
        report = _merge(reports)
        unchanged = not any(o['output'] or o['files'] for o in result['outputs'])
        if unchanged:
            report['note'] = "Rien à changer : aucun traitement n'a modifié la vidéo. L'originale reste le bon fichier, aucun autre n'a été écrit."
        return {**result, 'deliverable': d['kind'], 'unchanged': unchanged, 'qc': report}
    if engine == 'ffmpeg-edit' and adapter.get('mode') == 'restyle-preview':
        src = next((Path(x['path']) for x in project['inputs'] if x['exists'] and x['type'] in ('video', 'image')), None)
        if not src:
            raise ValueError('Restylage : aucun média fourni.')
        out = out_dir / f'{name}-apercu-filtres.mp4'
        result = restyle_preview(src, out, fmt=fmt, profile=profile)
    elif engine == 'ffmpeg-edit':
        out = out_dir / f'{name}.mp4'
        edl, how = _edl_from_inputs(project)
        result = edit(edl, ROOT, out, fmt=fmt, profile=profile, size=_size(d, profile), logo=_input(project, 'logo', 'image'),
                      voice=_input(project, 'voice', 'audio'), music=_input(project, 'music', 'audio'))
        result['montage'] = how
    elif engine == 'remotion':
        out = out_dir / f'{name}.mp4'
        result = remotion.render(project, adapter['composition'], out, profile)
    elif engine == 'video-effects':
        plan = (project.get('props') or {}).get('effects')
        if not plan:
            raise RuntimeError("Effets : écrire le plan dans props.effects de project.json, par exemple [{\"fx\": \"orbit\", \"start\": 3, \"end\": 6}]. Liste : python -m universal.cli effects list")
        src = next((Path(x['path']) for x in project['inputs'] if x['exists'] and x['type'] == 'video'), None)
        if not src:
            raise ValueError('Effets : aucune vidéo fournie.')
        out = out_dir / f'{name}.mp4'
        result = effects.render(src, plan, out, profile=profile, brand_ui_ok=bool((project.get('props') or {}).get('brand_ui_ok')), base=ROOT)
    elif engine == 'film-style':
        film = out_dir / 'film'
        if not (film / 'index.html').exists():
            film_style.new(adapter['style'], film, name=name, language=d.get('language', 'fr'), seconds=d.get('duration_s') or 12)
            raise RuntimeError(f"Dossier du film créé : {film}. Écrire le film d'après modules/opuscar/styles/{adapter['style']}/STYLE.md, puis relancer. Rien n'est rendu avant : un style est une recette, pas un gabarit.")
        out = out_dir / f'{name}.mp4'
        result = film_style.render(film, out, fmt=fmt, profile=profile)
    else:
        raise ValueError(f'Moteur inconnu : {engine}')
    report = qc(out, out_dir / f'{name}-preuves', exceptions=exceptions, audio_target=None if engine in ('remotion', 'video-effects') else -14.0)
    return {**result, 'deliverable': d['kind'], 'qc': report}


def run_project(path: Path, profile: str | None = None, out_root: Path | None = None) -> dict:
    project = manifest.load(path)
    if project['status'] == 'blocked' and not any(d['adapter'].get('mode') == 'restyle-preview' for d in project['deliverables']):
        raise RuntimeError('Projet bloqué : ' + '; '.join(m['need'] for m in project.get('missing', []) if m['blocking']))
    if (project.get('understanding') or {}).get('certain') is False:
        raise RuntimeError(NOT_UNDERSTOOD)
    profile = profile or project['quality'].get('profile', 'draft')
    out_dir = (out_root or ROOT / 'out') / project['name']
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        results = [run_deliverable(project, d, out_dir, profile) for d in project['deliverables']]
    except workflows.NeedsInput as waiting:
        if waiting.reset:  # a new text was written: an earlier "reviewed" must not let it through unread
            step, key = waiting.reset
            options = project.setdefault('props', {}).setdefault('workflow', {}).setdefault(step, {})
            if options.get(key):
                options[key] = False
                manifest.save(project, Path(path))
        raise
    for d, r in zip(project['deliverables'], results):
        if not r.get('unchanged'):
            perfil.remember_delivery(project, d, r)
    ok = all(r['qc']['pass'] for r in results)
    idle = all(r.get('unchanged') for r in results)  # every treatment found nothing to do: saying "delivered" would be false
    project['results'] = [{k: v for k, v in r.items() if k != 'qc'} | {'qc_pass': r['qc']['pass']} for r in results]
    project['status'] = 'unchanged' if idle else 'delivered' if ok else 'failed'
    manifest.save(project, Path(path))
    (out_dir / 'qc.json').write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
    return {'status': project['status'], 'results': results}


def film(deck_html: Path, out: Path, stills: str | None = None) -> str:
    """Linear recap of a deck, rendered by the Prompt Motion engine. A film has no real buttons."""
    args = ['node', 'render.mjs', str(Path(deck_html).resolve()), '--out', str(Path(out).resolve())]
    if stills:
        args += ['--stills', stills]
    r = subprocess.run(args, cwd=ROOT / 'prompt-motion', capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode:
        raise RuntimeError(r.stderr[-1500:])
    return r.stdout.strip()
