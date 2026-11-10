"""The routing cases, with their manifest and a real local run. python tests/routage_preuves.py [profil]

Status means what really ran. PARTIAL: the route is right and something ran, but not the whole request.
BLOCKED: needs a service, asset or consent that is absent here.
"""
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding='utf-8')

from universal import fixtures, manifest, remotion  # noqa: E402
from universal.catalog import load  # noqa: E402
from universal.inventory import inspect  # noqa: E402
from universal.router import route, summary  # noqa: E402
from universal.run import run_deliverable  # noqa: E402

PROOFS = ROOT / 'docs' / 'preuves' / 'routage'
GENERATED = {'status': 'generated-locally'}
DARK = [{'type': 'black', 'from': 0, 'to': 1e9, 'reason': 'Scène sombre voulue'}, {'type': 'no-audio', 'reason': 'Démonstrateur image'}]
NO_AUDIO = [{'type': 'no-audio', 'reason': 'Démonstrateur image'}]
GLB = ROOT / 'examples/modelos/RobotExpressive/RobotExpressive.glb'
CC0 = {'status': 'cc0', 'note': 'Tomás Laulhé (Quaternius), CC0 1.0, via three.js r180'}


def medios():
    made = fixtures.build()
    voice = ROOT / 'out' / 'demos' / 'montage' / 'voz.wav'
    if not voice.exists():
        from universal.voice import synthesize
        synthesize('A short test voice, made locally.', voice, 'en')
    return made, voice


def cases(made, voice):
    g = lambda p, **k: {'path': str(p), 'rights': GENERATED, **k}
    logo, clips, fotos = made['logo'], made['clips'], made['fotos']
    return [
        dict(id='01-brief', titre='Brief sans aucun média', brief='Vidéo promo pour une boulangerie. Du pain chaud chaque matin. Ouvert dès six heures.', inputs=[], intent={'CREATE_FROM_SCRATCH'}, engine='remotion-2d', exc=NO_AUDIO),
        dict(id='02-logo', titre='Logo PNG seul', brief='', inputs=[g(logo)], intent={'ANIMATE_LOGO'}, engine='remotion-2d', exc=NO_AUDIO, name='Studio'),
        dict(id='03-photos', titre='Lot de photos', brief='', inputs=[g(p) for p in fotos], intent={'ANIMATE_IMAGES'}, engine='remotion-2d', exc=NO_AUDIO),
        dict(id='04-clips', titre='Trois clips à monter', brief='Monte ces trois clips', inputs=[g(p) for p in clips], intent={'EDIT_FOOTAGE'}, engine='ffmpeg-edit', only=True),
        dict(id='05-hybride', titre='Logo + photos + vidéos + voix', brief='', inputs=[g(logo), g(fotos[0]), g(fotos[1]), g(clips[0]), g(clips[1]), g(voice, role='voice')], intent={'EDIT_FOOTAGE', 'HYBRID_COMPOSITE'}, engine='ffmpeg-edit'),
        dict(id='06-restylage', titre='Restylage caricatural', brief='Transforme cette vidéo en caricature', inputs=[g(clips[2])], intent={'RESTYLE_FOOTAGE'}, engine='ffmpeg-edit', partial="Aperçu par filtres seulement. Le vrai restylage exige un fournisseur, un budget et le consentement : BLOCKED sans eux."),
        dict(id='07-3d-stylisee', titre='Création 3D stylisée', brief='Une création 3D stylisée : un objet qui tourne dans la lumière', inputs=[], intent={'CREATE_FROM_SCRATCH'}, engine='remotion-3d', exc=DARK),
        dict(id='08-realiste', titre='Scène réaliste cinématographique', brief='Une scène réaliste cinématographique façon Hollywood', inputs=[], intent={'CREATE_FROM_SCRATCH'}, engine='remotion-3d', exc=DARK, partial="Look cinéma en 3D PBR. Le photoréalisme n'est pas atteint : il demande des modèles et des matières réalistes, que le kit ne fournit pas."),
        dict(id='09-5d', titre='Demande ambiguë « 5D »', brief='Je veux une vidéo 5D de ma ville', inputs=[], intent={'CREATE_FROM_SCRATCH'}, engine='remotion-2d', question=True, exc=NO_AUDIO),
        dict(id='10-interactif', titre='Présentation HTML interactive', brief='Une présentation interactive de nos services avec de vrais boutons', inputs=[], intent={'INTERACTIVE_PRESENTATION'}, engine='html-deck', props=json.loads((ROOT / 'examples/universal/services.json').read_text(encoding='utf-8')), interactive=True),
        dict(id='M1-donnees', titre='Fichier de données', brief='', inputs=[{'path': str(ROOT / 'examples/datos/co2_annmean_mlo.csv'), 'rights': {'status': 'licensed', 'note': 'NOAA GML'}}], intent={'DATA_EXPLAINER'}, engine='remotion-2d', exc=NO_AUDIO + [{'type': 'freeze', 'from': 0, 'to': 1e9, 'reason': 'Lecture de graphique'}]),
        dict(id='M2-glb', titre='Personnage fourni en GLB', brief='', inputs=[{'path': str(GLB), 'rights': CC0}], intent={'CHARACTER_ANIMATION'}, engine='remotion-3d', exc=NO_AUDIO),
        dict(id='M3-projet', titre='Projet déjà créé', brief='', inputs=[str(ROOT / 'prompt-motion')], intent={'REVISE_EXISTING_PROJECT'}, engine=None, route_only='La modification dépend de la demande : route et inspection testées, pas de rendu.'),
    ]


def run_case(c, profile):
    target = PROOFS / c['id']
    target.mkdir(parents=True, exist_ok=True)
    inputs = [inspect(x) for x in c['inputs']]
    p = route(c['brief'], inputs, name=c['id'], language='fr')
    p['props'] = c.get('props') or {}
    if c.get('props') is None:
        del p['props']
    p['quality']['exceptions'] = c.get('exc', [])
    problems = manifest.validate(p)
    checks = {'manifeste_valide': not problems, 'intention': c['intent'] <= set(p['intent'])}
    if c.get('engine'):
        checks['moteur'] = c['engine'] in [e['id'] for e in p['engines']]
    if c.get('only'):
        checks['moteur_sobre'] = [e['id'] for e in p['engines']] == [c['engine']]
    if c.get('question'):
        checks['question_posee'] = bool(p['questions'])
    if not c['inputs']:
        p['inputs'] = []
    manifest.save(p, target / 'project.json')
    (target / 'fiche.txt').write_text(summary(p), encoding='utf-8')
    row = {'id': c['id'], 'cas': c['titre'], 'intent': p['intent'], 'engines': [e['id'] for e in p['engines']], 'questions': len(p['questions']), 'approvals': len(p['approval_required']), 'checks': checks}
    if not all(checks.values()):
        row.update(status='FAIL', detail=f'Routage inattendu: {checks} {problems[:2]}')
        return row
    if c.get('route_only'):
        row.update(status='ROUTE OK, NOT TESTED', detail=c['route_only'])
        return row
    results = []
    for d in p['deliverables']:
        start = time.time()
        r = run_deliverable(p, d, ROOT / 'out' / 'routage' / c['id'], profile)
        results.append(r)
        row['seconds'] = round(time.time() - start)
    r = results[0]
    if c.get('interactive'):
        t = subprocess.run(['node', str(ROOT / 'tests/deck.spec.mjs'), r['output'], str(target)], capture_output=True, text=True, encoding='utf-8', errors='replace')
        row['interactions'] = t.stdout.count('PASS')
        ok = t.returncode == 0
        detail = f"{row['interactions']} interactions réelles réussies dans Chromium"
    else:
        q = r['qc']
        for name in q.get('proofs', {}).values():
            shutil.copy(name, target / Path(name).name)
        (target / 'qc.json').write_text(json.dumps(q, ensure_ascii=False, indent=1), encoding='utf-8')
        ok = q['pass']
        detail = f"{q['width']}x{q['height']}, {q['duration']} s, bloquants: {q['blocking'] or 0}, alertes: {len(q['warnings'])}"
    row['output'] = r['output']
    row.update(status='FAIL' if not ok else 'PARTIAL' if c.get('partial') else 'PASS', detail=(c.get('partial', '') + ' ' + detail).strip())
    return row


def presets(profile):
    """Each demonstrator preset resolves to something that really renders."""
    target = ROOT / 'docs' / 'preuves' / 'presets'
    target.mkdir(parents=True, exist_ok=True)
    out = []
    stub = route('', [], name='preset', language='fr')
    for d in load('demonstrators.json')['demonstrators']:
        row = {'id': d['id'], 'composition': d['composition']}
        if not d['composition']:
            row.update(status='PASS', detail='Voir le cas 10-interactif')
        else:
            png = target / f"{d['id']}.png"
            try:
                frame = 150 if not d['composition'].startswith('Escena3D') else 200
                remotion.render(stub, d['composition'], png, 'draft', still_frame=frame, props=d['props'] or {})
                row.update(status='PASS', detail=str(png.relative_to(ROOT)))
            except RuntimeError as e:
                row.update(status='FAIL', detail=str(e)[-300:])
        out.append(row)
        print(row['id'], row['status'], flush=True)
    return out


def main():
    profile = sys.argv[1] if len(sys.argv) > 1 else 'draft'
    only = set(sys.argv[2:])
    made, voice = medios()
    PROOFS.mkdir(parents=True, exist_ok=True)
    results = PROOFS / 'resultats.json'
    rows = {r['id']: r for r in json.loads(results.read_text(encoding='utf-8'))} if results.exists() else {}
    for c in cases(made, voice):
        if only and c['id'] not in only:
            continue
        try:
            row = run_case(c, profile)
        except Exception as e:
            row = {'id': c['id'], 'cas': c['titre'], 'status': 'FAIL', 'detail': str(e)[-500:]}
        rows[c['id']] = row
        print(row['id'], row['status'], '-', row.get('detail', '')[:170], flush=True)
        results.write_text(json.dumps(sorted(rows.values(), key=lambda r: r['id']), ensure_ascii=False, indent=1), encoding='utf-8')
    preset_rows = []
    if not only:
        preset_rows = presets(profile)
        (ROOT / 'docs' / 'preuves' / 'presets' / 'resultats.json').write_text(json.dumps(preset_rows, ensure_ascii=False, indent=1), encoding='utf-8')
    return 1 if any(r['status'] == 'FAIL' for r in [*rows.values(), *preset_rows]) else 0


if __name__ == '__main__':
    sys.exit(main())
