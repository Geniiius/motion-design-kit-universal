"""Treatments of a provided video, for real. python tests/traitements.py [--longue] -> docs/preuves/traitements/

A talking video is made with the local voice over generated pictures, then worked on as a person would ask, in plain words.
Where the kit waits for a reader, this script plays the agent: it corrects the transcript, picks the clips, writes the translations.
It checks lengths, shapes and counts. It does not judge the wording of the captions or the choice of the clips: that is a reader's job.
--longue adds a twenty-minute video with hundreds of cuts (about four minutes more)."""
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding='utf-8')

from universal import fixtures, manifest, perfil, voice_kokoro  # noqa: E402
from universal.inventory import inspect  # noqa: E402
from universal.router import route  # noqa: E402
from universal.run import NOT_UNDERSTOOD, run_project  # noqa: E402
from universal.workflows import NeedsInput, tools, transcript  # noqa: E402
from universal.workflows.captions import cues  # noqa: E402

WORK = ROOT / 'out' / 'demos' / 'traitements'
PROOFS = ROOT / 'docs' / 'preuves' / 'traitements'
LINES = ["Bonjour et bienvenue dans cette vidéo.", "Aujourd'hui, je vous montre comment préparer un bon café.", "Merci d'avoir regardé, et à bientôt."]
WORDS = {'en': ["Hello and welcome to this video.", "Today, I'll show you", "how to make a good coffee.", "Thanks for watching, see you soon."],
         'es': ["Hola y bienvenidos a este vídeo.", "Hoy os enseño", "cómo preparar un buen café.", "Gracias por verlo y hasta pronto."]}
ff = lambda *a: subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *map(str, a)], check=True)
rows = []


def shape(path) -> str:
    m = tools.info(Path(path))
    return f"{Path(path).name} {m['duration']:.1f} s {m['width']}x{m['height']}"


def project(name: str, brief: str, source: Path, extra=(), **kw) -> Path:
    shutil.rmtree(WORK / name, ignore_errors=True)
    p = route(brief, [inspect(str(source))] + list(extra), name=name, profile={}, **kw)
    path = WORK / f'{name}.json'
    manifest.save(p, path)
    return path


def attempt(path: Path) -> dict:
    start = time.time()
    try:
        r = run_project(path, 'draft', WORK)
        res = r['results'][0]
        outputs = res.get('outputs') or [{'output': res.get('output'), 'files': []}]
        return {'etat': r['status'], 'fichiers': [o['output'] for o in outputs if o.get('output')], 'textes': [f for o in outputs for f in o.get('files', [])], 'notes': res.get('notes') or [],
                'montage': res.get('montage'), 'logo': res.get('logo'), 'attendu_s': outputs[0].get('expected_s'), 'bloquants': res['qc'].get('blocking') or [], 's': round(time.time() - start, 1)}
    except NeedsInput as e:
        return {'etat': 'needs-input', 'message': str(e), 'fichier': e.file, 's': round(time.time() - start, 1)}
    except (RuntimeError, ValueError) as e:
        return {'etat': 'refuse', 'message': str(e), 's': round(time.time() - start, 1)}


def options(path: Path, change) -> None:
    p = manifest.load(path)
    change(p.setdefault('props', {}).setdefault('workflow', {}))
    manifest.save(p, path)


def note(case: str, brief: str, expected: str, got: str, ok: bool, result: dict | None = None, status: str | None = None) -> None:
    rows.append({'cas': case, 'demande': brief, 'attendu': expected, 'obtenu': got, 'statut': status or ('PASS' if ok else 'FAIL'),
                 'notes': (result or {}).get('notes') or ([result['message'][:200]] if result and result.get('message') and not ok else []), 'secondes': (result or {}).get('s')})
    print(f"{rows[-1]['statut']:<11}{case:<18}{got}")


def review(srt) -> None:
    """The agent's reading: here, the known mishearings of this test voice."""
    text = Path(srt).read_text(encoding='utf-8')
    Path(srt).write_text(text.replace('Goutter', 'Goûtez').replace('bien venu', 'bienvenue'), encoding='utf-8')


def translate(source: Path, language: str) -> str:
    rows_ = cues(source)
    lines = WORDS[language] if len(rows_) == len(WORDS[language]) else [f'{language} {i}' for i in range(1, len(rows_) + 1)]
    stamp = lambda s: f'{int(s // 3600):02d}:{int(s % 3600 // 60):02d}:{int(s % 60):02d},{int(round((s % 1) * 1000)) % 1000:03d}'
    source.with_name(source.name.replace('.fr.srt', f'.{language}.srt')).write_text('\n'.join(f'{i}\n{stamp(a)} --> {stamp(b)}\n{t}\n' for i, ((a, b, _), t) in enumerate(zip(rows_, lines), 1)), encoding='utf-8')
    return 'traduction écrite par le script' if lines is WORDS[language] else 'texte de remplacement : le découpage différait'


def main() -> int:
    WORK.mkdir(parents=True, exist_ok=True)
    PROOFS.mkdir(parents=True, exist_ok=True)
    saved, perfil.DIR = perfil.DIR, WORK / 'perfil'  # these runs are not the user's videos
    made = fixtures.build()
    speech = transcript.missing() is None  # the voice itself is tried just below
    talk = WORK / 'parle.mp4'
    try:
        if not talk.exists():
            wavs = []
            for i, text in enumerate(LINES):
                wavs.append(WORK / f'phrase{i}.wav')
                voice_kokoro.synthesize(text, wavs[-1], 'fr')
            ff('-i', wavs[0], '-i', wavs[1], '-i', wavs[2], '-filter_complex', '[0]apad=pad_dur=2.5[a];[1]apad=pad_dur=3[b];[a][b][2]concat=n=3:v=0:a=1,adelay=1000:all=1,apad=pad_dur=1.5[o]', '-map', '[o]', WORK / 'parole.wav')
            ff('-stream_loop', '-1', '-i', made['clips'][0], '-i', WORK / 'parole.wav', '-map', '0:v', '-map', '1:a', '-shortest', '-c:v', 'libx264', '-crf', '23', '-pix_fmt', 'yuv420p', '-c:a', 'aac', talk)
    except (RuntimeError, OSError, subprocess.SubprocessError) as e:
        speech = False
        print('Voix locale indisponible :', str(e)[:160])
    if not talk.exists():
        note('vidéo parlée', '', 'une vidéo avec une voix', 'voix locale ou transcription absente : cas parlés non essayés', False, status='NOT TESTED')
        ff('-f', 'lavfi', '-i', 'testsrc2=s=1280x720:r=25:d=14', '-f', 'lavfi', '-i', "aevalsrc='0.3*sin(2*PI*440*t)*lt(mod(t,3.5),1.5)':d=14:s=48000", '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', talk)
    source = tools.info(talk)
    length = source['duration']
    print(f"Vidéo d'essai : {length:.1f} s, {source['width']}x{source['height']}, voix {'française locale' if speech else 'absente (tonalité)'}\n")

    brief = 'Ajoute mon logo à cette vidéo'
    r = attempt(project('t-logo', brief, talk, [inspect({'path': str(made['logo']), 'role': 'logo'})]))
    ok = r['etat'] == 'delivered' and abs(tools.info(r['fichiers'][0])['duration'] - length) < .3 and bool(r.get('logo'))
    note('logo', brief, f'{length:.1f} s, entière, avec le logo', shape(r['fichiers'][0]) + f" ; {r['montage']}" if r.get('fichiers') else r['etat'], ok, r)

    brief = 'Enlève les silences de ma vidéo'
    r = attempt(project('t-silences', brief, talk))
    ok = r['etat'] == 'delivered' and tools.info(r['fichiers'][0])['duration'] < length - 3 and abs(tools.info(r['fichiers'][0])['duration'] - r['attendu_s']) < .3
    note('silences', brief, 'plus courte, la durée annoncée tenue', shape(r['fichiers'][0]) if r.get('fichiers') else r['etat'], ok, r)

    brief = 'Mets ma vidéo au format TikTok'
    path = project('t-vertical', brief, talk)
    r = attempt(path)
    m = tools.info(r['fichiers'][0]) if r.get('fichiers') else {}
    ok = r['etat'] == 'delivered' and (m['width'], m['height']) == (360, 640) and abs(m['duration'] - length) < .3
    note('vertical', brief, '360x640, entière ; sans visage, image gardée sur fond flou', shape(r['fichiers'][0]) if m else r['etat'], ok, r)
    options(path, lambda w: w.setdefault('reframe', {}).update(mode='center'))
    r = attempt(path)
    m = tools.info(r['fichiers'][0]) if r.get('fichiers') else {}
    note('vertical, centre', brief + ' (coupe au centre choisie)', '360x640', shape(r['fichiers'][0]) if m else r['etat'], r['etat'] == 'delivered' and (m['width'], m['height']) == (360, 640), r)

    steady = WORK / 'continu.mp4'
    ff('-f', 'lavfi', '-i', 'testsrc2=s=640x360:r=25:d=4', '-f', 'lavfi', '-i', 'sine=f=440:d=4', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', steady)
    r = attempt(project('t-rien', brief := 'Enlève les silences de ma vidéo', steady))
    note('rien à changer', brief + ' (vidéo sans silence)', '« unchanged », aucun fichier écrit', f"{r['etat']}, {len(r.get('fichiers', []))} fichier", r['etat'] == 'unchanged' and not r.get('fichiers'), r)

    brief = 'Ça fait pas assez pro, améliore'
    r = attempt(project('t-incomprise', brief, talk))
    note('demande floue', brief, 'refus : rien n\'est livré au hasard', 'refusée' if r.get('message') == NOT_UNDERSTOOD else r['etat'], r.get('message') == NOT_UNDERSTOOD)

    if speech:
        brief = 'Ajoute des sous-titres à ma vidéo'
        path = project('t-sous-titres', brief, talk)
        first = attempt(path)
        said = ' | '.join(c[2] for c in cues(first['fichier'])) if first.get('fichier') else ''
        review(first['fichier'])
        second = attempt(path)
        options(path, lambda w: w.setdefault('captions', {}).update(reviewed=True))
        r = attempt(path)
        ok = first['etat'] == second['etat'] == 'needs-input' and r['etat'] == 'delivered' and abs(tools.info(r['fichiers'][0])['duration'] - length) < .3
        note('sous-titres', brief, 'arrêt pour relecture, puis incrustés', (shape(r['fichiers'][0]) if r.get('fichiers') else r['etat']) + f' ; deux arrêts avant ; transcrit : {said}', ok, r)

        brief = 'Sous-titre ma vidéo en anglais et en espagnol'
        path = project('t-traduction', brief, talk)
        first = attempt(path)
        review(first['fichier'])
        options(path, lambda w: w.setdefault('captions', {}).update(reviewed=True))
        waiting = attempt(path)
        how = [translate(Path(first['fichier']), lang) for lang in ('en', 'es')]
        r = attempt(path)
        names = [Path(f).name for f in r.get('fichiers', [])]
        ok = waiting['etat'] == 'needs-input' and r['etat'] == 'delivered' and names == ['t-traduction-en.mp4', 't-traduction-es.mp4']
        note('traductions', brief, 'arrêt tant que les traductions manquent, puis une vidéo par langue', ', '.join(names) + f' ; {how[0]}', ok, r)

        brief = 'Fais 3 extraits courts de cette vidéo pour Instagram'
        path = project('t-extraits', brief, talk)
        first = attempt(path)
        options(path, lambda w: w.update(clips=[{'in': 0.5, 'out': 4.0, 'title': 'Bienvenue'}, {'in': 5.4, 'out': 9.0, 'title': 'Le café'}, {'in': 11.2, 'out': 14.6, 'title': 'Au revoir'}]))
        r = attempt(path)
        sizes = [tools.info(f) for f in r.get('fichiers', [])]
        ok = first['etat'] == 'needs-input' and r['etat'] == 'delivered' and len(sizes) == 3 and all((m['width'], m['height']) == (360, 640) and m['duration'] >= 3 for m in sizes)
        note('extraits', brief, 'arrêt pour le choix, puis 3 fichiers verticaux', ' ; '.join(shape(f) for f in r.get('fichiers', [])) or r['etat'], ok, r)

        triple = WORK / 'parle-trois-fois.mp4'
        ff('-stream_loop', '2', '-i', talk, '-c', 'copy', triple)
        brief = 'Écris les chapitres de cette vidéo pour YouTube'
        path = project('t-chapitres', brief, triple)
        first = attempt(path)
        options(path, lambda w: w.update(chapters=[{'t': 0, 'title': 'Bienvenue'}, {'t': 18, 'title': 'Le café'}, {'t': 36, 'title': 'Au revoir'}]))
        r = attempt(path)
        texts = [Path(f).name for f in r.get('textes', [])]
        ok = first['etat'] == 'needs-input' and r['etat'] == 'delivered' and texts == ['t-chapitres.chapitres.txt'] and not r['fichiers']
        note('chapitres', brief, 'arrêt pour la lecture, puis un texte, aucune vidéo réencodée', ', '.join(texts) + f" ; {len(r.get('fichiers', []))} vidéo", ok, r)

        brief = 'Enlève les silences, ajoute des sous-titres et mets-la en vertical pour TikTok'
        path = project('t-tout', brief, talk)
        first = attempt(path)
        review(first['fichier'])
        options(path, lambda w: w.setdefault('captions', {}).update(reviewed=True))
        r = attempt(path)
        m = tools.info(r['fichiers'][0]) if r.get('fichiers') else {}
        ok = r['etat'] == 'delivered' and (m['width'], m['height']) == (360, 640) and m['duration'] < length - 3 and abs(m['duration'] - r['attendu_s']) < .3
        note('chaîne complète', brief, 'trois traitements, un seul fichier vertical, plus court', shape(r['fichiers'][0]) if m else r['etat'], ok, r)
        sheet = [(WORK / 't-sous-titres/t-sous-titres.mp4', 6.5), (WORK / 't-traduction/t-traduction-en.mp4', 6.5), (WORK / 't-tout/t-tout.mp4', 4.2), (WORK / 't-extraits/t-extraits-2.mp4', 1.6)]
        if all(f.exists() for f, _ in sheet):
            args = sum((['-ss', t, '-i', f] for f, t in sheet), [])
            graph = ';'.join(f'[{i}:v]scale=-2:360[v{i}]' for i in range(len(sheet))) + ';' + ''.join(f'[v{i}]' for i in range(len(sheet))) + f'hstack=inputs={len(sheet)}[o]'
            ff(*args, '-filter_complex', graph, '-map', '[o]', '-frames:v', '1', '-q:v', '3', PROOFS / 'planche.jpg')
    else:
        for case in ('sous-titres', 'traductions', 'extraits', 'chapitres', 'chaîne complète'):
            note(case, '', '', 'voix locale ou transcription absente', False, status='NOT TESTED')

    if '--longue' in sys.argv:
        long = WORK / 'vingt-minutes.mp4'
        if not long.exists():
            ff('-f', 'lavfi', '-i', 'testsrc2=s=320x180:r=15:d=1200', '-f', 'lavfi', '-i', "aevalsrc='0.3*sin(2*PI*440*t)*lt(mod(t,3.5),1.5)':d=1200:s=48000", '-c:v', 'libx264', '-preset', 'ultrafast',
               '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', long)
        brief = 'Enlève les silences de ma vidéo'
        r = attempt(project('t-longue', brief, long))
        gap = None
        if r.get('fichiers'):
            streams = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=duration', '-of', 'csv=p=0', r['fichiers'][0]], capture_output=True, text=True).stdout.split()
            gap = round(abs(float(streams[0]) - float(streams[1])), 3)
        ok = r['etat'] == 'delivered' and gap is not None and gap < .1 and abs(tools.info(r['fichiers'][0])['duration'] - r['attendu_s']) < .5
        note('vidéo de 20 minutes', brief + ' (343 silences)', 'livrée, image et son de même durée', (shape(r['fichiers'][0]) + f' ; écart image-son {gap} s') if r.get('fichiers') else r['etat'], ok, r)
    else:
        note('vidéo de 20 minutes', 'Enlève les silences de ma vidéo (343 silences)', '', 'non lancé cette fois : ajouter --longue', False, status='NOT TESTED')

    perfil.DIR = saved
    limit = ('Les chiffres mesurent des durées, des formes et des nombres de fichiers. Le texte des sous-titres, le choix des extraits et des chapitres sont joués par ce script à la place de Claude. '
             'Le recadrage qui suit un visage n\'est pas essayé ici : la vidéo d\'essai ne montre personne.')
    (PROOFS / 'resultats.json').write_text(json.dumps({'source': f"{length:.1f} s, {source['width']}x{source['height']}", 'voix': speech, 'cas': rows, 'limite': limit}, ensure_ascii=False, indent=1), encoding='utf-8', newline='\n')
    failed = [r['cas'] for r in rows if r['statut'] == 'FAIL']
    print('\nÉchecs :', ', '.join(failed) if failed else 'aucun')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
