"""Where the tokens of a conversation in the kit go, measured on the kit's own files and on real command outputs.
python tests/tokens.py -> docs/preuves/tokens.json

Estimates, not tokenizer counts: text is counted as characters / 3.6 (French and Spanish run a little denser than English),
images as width x height / 750, the approximation Anthropic publishes for vision. Claude Code's own instructions and the
user's global skills are not counted: they are the same with or without the kit. Nothing in the kit is changed: the run
measured here works in a temporary folder, with the profile redirected."""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding='utf-8')

from universal import logs, manifest, onboarding, perfil, state  # noqa: E402
from universal.inventory import inspect  # noqa: E402
from universal.router import route, summary  # noqa: E402
from universal.run import run_project  # noqa: E402

PROOF = ROOT / 'docs' / 'preuves' / 'tokens.json'
text_tokens = lambda chars: round(chars / 3.6)
image_tokens = lambda w, h: round(w * h / 750)
FLOWS = {'kit prêt, vidéo fournie à traiter': ['universal-motion-director', 'video-workflows'],
         'création à partir d\'une idée': ['universal-motion-director', 'remotion-motion-graphics', 'quality-reviewer'],
         'premier lancement': ['kit-onboarding']}


def main() -> int:
    out: dict = {'methode': 'caractères / 3,6 pour le texte, largeur x hauteur / 750 pour une image'}
    claude = (ROOT / 'CLAUDE.md').read_text(encoding='utf-8')
    skills = {}
    for f in sorted((ROOT / '.claude/skills').glob('*/SKILL.md')):
        body = f.read_text(encoding='utf-8')
        m = re.search(r'^description:\s*"?(.*?)"?\s*$', body, re.M)
        skills[f.parent.name] = {'description': len(m.group(1)) if m else 0, 'corps': len(body)}
    always = len(claude) + sum(v['description'] + len(k) for k, v in skills.items())
    out['toujours_charge'] = {'claude_md': len(claude), 'descriptions_des_skills': sum(v['description'] for v in skills.values()), 'skills': len(skills),
                              'caracteres': always, 'tokens': text_tokens(always)}
    bodies = sum(v['corps'] for v in skills.values())
    out['corps_des_skills'] = {'caracteres': bodies, 'tokens': text_tokens(bodies), 'note': 'jamais tous à la fois : chaque skill se lit seulement quand la tâche en a besoin'}
    out['parcours'] = {name: {'skills': names, 'caracteres': sum(skills[n]['corps'] for n in names), 'tokens': text_tokens(sum(skills[n]['corps'] for n in names))}
                       for name, names in FLOWS.items() if all(n in skills for n in names)}

    with tempfile.TemporaryDirectory() as tmp, mock.patch.object(state, 'FILE', Path(tmp) / 'etat.json'), mock.patch.object(logs, 'DIR', Path(tmp) / 'logs'):
        first = json.dumps(onboarding.start(), ensure_ascii=False, indent=2)
        st = state.blank()
        st.update(configured=True, verified_at=state.now(), verdict='READY', components={pid: {'status': 'READY'} for pid in onboarding.QUICK})
        state.save(st)
        ready = json.dumps(onboarding.start(), ensure_ascii=False, indent=2)
    out['start'] = {'premier_lancement': {'caracteres': len(first), 'tokens': text_tokens(len(first))}, 'kit_pret': {'caracteres': len(ready), 'tokens': text_tokens(len(ready))}}

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        clip = tmp / 'parle.mp4'
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'lavfi', '-i', 'testsrc2=s=1280x720:r=25:d=14', '-f', 'lavfi', '-i',
                        "aevalsrc='0.3*sin(2*PI*440*t)*lt(mod(t,3.5),1.5)':d=14:s=48000", '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', str(clip)], check=True)
        saved, perfil.DIR = perfil.DIR, tmp / 'perfil'
        try:
            p = route('Enlève les silences de ma vidéo', [inspect(str(clip))], name='mesure', profile={})
            path = tmp / 'mesure.json'
            manifest.save(p, path)
            card = summary(p)
            result = run_project(path, 'draft', tmp / 'out')
        finally:
            perfil.DIR = saved
        printed = json.dumps(result, ensure_ascii=False, indent=2)
        manifest_chars = len(path.read_text(encoding='utf-8'))
        out['route'] = {'fiche_lue_par_claude': {'caracteres': len(card), 'tokens': text_tokens(len(card))}, 'manifeste_complet': {'caracteres': manifest_chars, 'tokens': text_tokens(manifest_chars)}}
        out['run'] = {'sortie': {'caracteres': len(printed), 'tokens': text_tokens(len(printed))}, 'note': 'le détail du contrôle qualité reste dans qc.json, lu seulement en cas de problème'}
        sheet = next((tmp / 'out').rglob('planche.jpg'), None)
        if sheet:
            w, h = (int(x) for x in subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', str(sheet)],
                                                   capture_output=True, text=True).stdout.strip().split(','))
            out['planche'] = {'images_dans_la_planche': 10, 'taille': f'{w}x{h}', 'tokens': image_tokens(w, h),
                              'tokens_si_10_images_en_1280x720': 10 * image_tokens(1280, 720)}
            out['planche']['facteur'] = round(out['planche']['tokens_si_10_images_en_1280x720'] / out['planche']['tokens'], 1)

    pairs = [(w, w.with_name(w.name.replace('.mots.json', '.transcription.txt'))) for w in (ROOT / 'out').rglob('*.mots.json')] if (ROOT / 'out').exists() else []
    words, script = next(((w, t) for w, t in pairs if t.exists()), (None, None))
    if words and script:
        a, b = len(words.read_text(encoding='utf-8')), len(script.read_text(encoding='utf-8'))
        out['transcription'] = {'mots_minutes_json': a, 'texte_lu_par_claude': b, 'facteur': round(a / b, 1)}
    else:
        out['transcription'] = {'note': 'aucune transcription dans out/ : mesure non refaite cette fois'}
    PROOF.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8', newline='\n')
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
