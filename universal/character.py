"""Optional Blender renderer for a procedural stylized mascot.
No claim of human photorealism or phoneme-level lip synchronization.
"""
from __future__ import annotations
import shutil
import subprocess
import tempfile
from pathlib import Path
from .capabilities import find_blender
from .engine import resolve_asset,classify
from .render import run

def build(spec,root,output):
    blender=find_blender()
    if not blender: raise RuntimeError('Blender non installé. Installer Blender ou utiliser le preview Three.js (modules/three-studio).')
    script=Path(__file__).resolve().parents[1]/'modules/character-studio/mascot_blender.py'
    output=Path(output).resolve();output.parent.mkdir(parents=True,exist_ok=True)
    voice=next((resolve_asset(root,a) for a in spec.get('assets',[]) if isinstance(a,dict) and a.get('role')=='voice'),None)
    seconds=float(spec.get('duration',6))
    if not 1<=seconds<=120:raise ValueError('duration doit être entre 1 et 120 secondes')
    with tempfile.TemporaryDirectory(prefix='character-studio-') as d:
        raw=Path(d)/'raw.mp4'
        # Factory settings: the user's own add-ons and preferences stay out of the render. A Python error must fail the run.
        cmd=[blender,'-b','--factory-startup','-noaudio','--python-exit-code','1','--python',str(script),'--','--output',str(raw),'--duration',str(seconds)]
        r=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',errors='replace')
        if r.returncode or not raw.exists():
            raise RuntimeError("Blender n'a pas rendu le personnage : "+((r.stderr or r.stdout).strip()[-600:] or 'aucun fichier produit'))
        if voice:
            if not voice.is_file() or classify(voice)!='audio':raise ValueError('Piste voix manquante ou invalide')
            # Blender animates a non-phonemic mouth loop; external audio is muxed exactly.
            run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(raw),'-i',str(voice),
                 '-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-t',str(seconds),str(output)])
        else:shutil.copy2(raw,output)
    return {'output':str(output),'engine':'blender','demo':'stylized procedural mascot',
            'voice_muxed':bool(voice),'mouth_sync':'illustrative loop only; NOT phoneme/viseme accurate'}
