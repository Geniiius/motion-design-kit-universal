"""The assistant on this machine, for real. python tests/assistant.py [--hors-ligne] -> docs/preuves/assistant/

Detection, the entry point, the full check with its two test videos, the repair and uninstall listings (nothing is repaired or
removed), the update comparison (reads public registries unless --hors-ligne) and a Blender render when Blender is there.
Installing a missing tool is not exercised here: on a machine where everything is present there is nothing to install.
That path is covered by tests/test_onboarding.py with stand-ins, and by tests/paquet.ps1 on a freshly unpacked kit."""
import datetime
import json
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding='utf-8')

from universal import capabilities, character, diagnostic, logs, onboarding, state  # noqa: E402
from universal.workflows import tools  # noqa: E402

PROOFS = ROOT / 'docs' / 'preuves' / 'assistant'
rows = []


def note(test: str, ok: bool, detail: str, status: str | None = None) -> None:
    rows.append({'test': test, 'status': status or ('PASS' if ok else 'FAIL'), 'detail': detail})
    print(f"{rows[-1]['status']:<11}{test} : {detail}"[:230])


def main() -> int:
    PROOFS.mkdir(parents=True, exist_ok=True)
    start = time.time()
    seen = diagnostic.full(test=True)
    m, s = seen['machine'], seen['software']
    summary = onboarding.summary(m)
    note('Machine mesurée', bool(m['ram_gb'] and m['cpu'] and m['threads'] and m['disk_free_gb']), ' · '.join(summary.values()) + f' · {round(time.time() - start, 1)} s')
    versions = ', '.join(f"{name} {s[name].get('version')}" for name in ('python', 'node', 'npm', 'ffmpeg', 'git', 'uv', 'blender') if s[name].get('found'))
    note('Logiciels et versions lus', all(s[x]['found'] for x in ('python', 'ffmpeg')), versions + f" · gestionnaire : {s['package_manager']['name'] if s['package_manager']['found'] else 'aucun'}")
    note('Conflits signalés', True, '; '.join(c['what'] for c in seen['conflicts']) or 'aucun sur cette machine')
    note('Encodeurs matériels essayés pour de vrai', True, ', '.join(f"{k} : {'fonctionne' if v else 'échoue'}" for k, v in seen['encoders'].items()) or 'aucun proposé par FFmpeg')

    # A first launch, on a blank state kept in a temporary file: the real state is not touched by this part
    with tempfile.TemporaryDirectory() as tmp, mock.patch.object(state, 'FILE', Path(tmp) / 'kit-state.json'), mock.patch.object(logs, 'DIR', Path(tmp) / 'logs'):
        first = onboarding.start()
        there = [r for r in first['rows'] if r['state'] == 'present']
        todo = sum(len(v) for v in first['to_approve'].values())
        note('Premier lancement : ce qui est déjà installé est reconnu', first['phase'] == 'first-launch' and len(there) + todo + len(first['by_hand']) == len(first['rows']),
             f"{len(there)} éléments déjà là sur {len(first['rows'])}, {todo} à proposer, {len(first['by_hand'])} à faire à la main")
        done = onboarding.apply([r['id'] for r in there])
        note('Demander à installer ce qui est déjà là ne refait rien', all(x['result'] == 'already' for x in done['results']) and not state.load()['installed_by_kit'],
             f"{len(done['results'])} éléments, tous laissés tels quels")

    began = time.time()
    report = onboarding.verify(deep=True)
    took = round(time.time() - began)
    counts = report['counts']
    note('Vérification complète', report['verdict'] != 'FAILED', f"{report['verdict']} en {took} s : {counts['READY']} READY, {counts['WARNING']} WARNING, {counts['FAILED']} FAILED, {counts['OPTIONAL']} OPTIONAL")
    for key in ('essai-montage', 'essai-creation'):
        row = next((r for r in report['rows'] if r['id'] == key), None)
        if row:
            made = Path(row.get('file') or '')
            note(f"{row['title']}", row['status'] == 'READY' and made.exists(), row['detail'] + (f' · {made.name} {tools.info(made)["width"]}x{tools.info(made)["height"]}' if made.exists() else ''))
    began = time.time()
    ready = onboarding.start()
    note('Kit déjà configuré : contrôle de santé sans rien relancer', ready['phase'] == 'ready' and time.time() - began < 3, f"phase {ready['phase']} en {round(time.time() - began, 2)} s, {len(ready['features']['pret'])} usages prêts")
    fixes = onboarding.repair()
    note('Diagnostic de réparation', isinstance(fixes['fixes'], list), f"{len(fixes['fixes'])} élément(s) à réparer ; rien n'est réparé sans accord")
    leaving = onboarding.uninstall()
    kept = ', '.join(k['where'] for k in leaving['kept']) or 'aucun dossier personnel présent'
    note('Désinstallation : liste seule', bool(leaving['removable']) and all((ROOT / p).exists() for g in leaving['removable'] for p in g['paths']),
         f"{len(leaving['removable'])} groupes, {sum(g['size_mb'] for g in leaving['removable'])} Mo ; jamais supprimés : {kept} ; hors du kit : {len(leaving['outside_the_kit'])} élément(s) listés")
    online = '--hors-ligne' not in sys.argv
    found = onboarding.updates(online=online)
    newer = [f"{d['name']} {d['pinned']} → {d['latest']} ({d['change']})" for d in found['dependencies'] if d['change'] not in ('à jour', 'inconnu')]
    note('Comparaison des versions, sans rien mettre à jour', bool(found['dependencies']) and (found['online'] or not online),
         (f"{len(found['dependencies'])} versions fixées comparées le {datetime.date.today().isoformat()} ; plus récentes : " + ('; '.join(newer) or 'aucune')) if found['online'] else 'registres non consultés',
         None if found['online'] else 'NOT TESTED')
    leaks = []
    for f in list(logs.DIR.glob('*')) + [state.FILE]:
        text = f.read_text(encoding='utf-8', errors='replace') if f.is_file() else ''
        leaks += [f.name for word in (str(Path.home()), Path.home().name) if word and word.lower() in text.lower()]
        leaks += [f.name for _ in re.findall(r'sk_[A-Za-z0-9]{20,}', text)]
    note('Journal et état sans donnée sensible', not leaks, f"{len(list(logs.DIR.glob('*')))} fichier(s) de journal lus : ni dossier personnel, ni nom d'utilisateur, ni clé" if not leaks else 'trouvé dans ' + ', '.join(sorted(set(leaks))))

    blender = capabilities.find_blender()
    if blender:
        out = ROOT / 'out' / 'demos' / 'blender' / 'mascotte.mp4'
        began = time.time()
        try:
            character.build({'duration': 2, 'assets': []}, ROOT, out)
            meta = tools.info(out)
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', '1', '-i', str(out), '-frames:v', '1', '-vf', 'scale=640:-2', '-q:v', '3', str(PROOFS / 'mascotte-blender.jpg')], check=True)
            note(f"Blender {s['blender']['version']} trouvé{'' if s['blender']['on_path'] else ' hors du PATH'}, mascotte rendue", abs(meta['duration'] - 2) < .2 and meta['width'] == 960,
                 f"{meta['duration']:.1f} s, {meta['width']}x{meta['height']}, en {round(time.time() - began)} s")
        except (RuntimeError, OSError, subprocess.SubprocessError) as e:
            note('Blender : rendu de la mascotte', False, str(e)[-200:])
    else:
        note('Blender', False, 'non installé sur cette machine', 'NOT TESTED')

    data = {'date': datetime.date.today().isoformat(), 'machine': summary, 'tests': rows,
            'bilan': [{k: r.get(k) for k in ('title', 'level', 'status', 'version', 'detail')} for r in report['rows']], 'conseils': report['advice'],
            'versions': [{k: d[k] for k in ('name', 'where', 'pinned', 'latest', 'change')} for d in found['dependencies']]}
    (PROOFS / 'resultats.json').write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding='utf-8', newline='\n')
    failed = [r['test'] for r in rows if r['status'] == 'FAIL']
    print('\nÉchecs :', ', '.join(failed) if failed else 'aucun')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
