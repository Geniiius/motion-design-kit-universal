"""Technical QC of a delivered video. Separates blocking defects from aesthetic signals.

A black, silent or still passage is not a defect when the project declares it
(quality.exceptions in project.json): it is then listed as declared.
QC never replaces watching the frames and listening to the mix.
"""
from __future__ import annotations
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from .inventory import contact_sheet

STILL_WINDOW_S = .5
STILL_THRESHOLD = .25  # mean luma difference between frames, 0-255 scale


def _ffmpeg(args: list, cwd: Path | None = None) -> str:
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats'] + [str(a) for a in args], capture_output=True, text=True,
                       encoding='utf-8', errors='replace', cwd=cwd)
    return r.stderr


def _probe(path: Path) -> dict:
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    return json.loads(r.stdout or '{}')


def _covered(kind: str, start: float, end: float, exceptions: list[dict]) -> dict | None:
    for e in exceptions:
        if e.get('type') == kind and e.get('from', 0) - .1 <= start and end <= e.get('to', 1e9) + .1:
            return e
    return None


def measure_video(path: Path) -> dict:
    """black, freeze, cuts and per-frame motion, in one low-resolution pass."""
    path = Path(path).resolve()  # ffmpeg runs in a temporary folder: a relative path would find nothing
    with tempfile.TemporaryDirectory(prefix='qc-') as tmp:
        log = _ffmpeg(['-i', path, '-an', '-vf', 'scale=320:-2,blackdetect=d=0.2:pix_th=0.08,freezedetect=n=-60dB:d=1,scdet=threshold=8,'
                       'signalstats,metadata=print:key=lavfi.signalstats.YDIF:file=ydif.txt', '-f', 'null', '-'], cwd=Path(tmp))
        ydif_txt = (Path(tmp) / 'ydif.txt').read_text(encoding='utf-8', errors='replace') if (Path(tmp) / 'ydif.txt').exists() else ''
    black = [(float(a), float(b)) for a, b in re.findall(r'black_start:([\d.]+) black_end:([\d.]+)', log)]
    fs = [float(x) for x in re.findall(r'freeze_start: ([\d.]+)', log)]
    fe = [float(x) for x in re.findall(r'freeze_end: ([\d.]+)', log)]
    cuts = sorted({round(float(x), 3) for x in re.findall(r'lavfi\.scd\.time: ([\d.]+)', log)})
    times = [float(x) for x in re.findall(r'pts_time:([\d.]+)', ydif_txt)]
    ydif = [float(x) for x in re.findall(r'YDIF=([\d.]+)', ydif_txt)]
    return {'black': black, 'freeze_start': fs, 'freeze_end': fe, 'cuts': cuts, 'times': times, 'ydif': ydif}


def still_windows(times: list[float], ydif: list[float]) -> list[list[float]]:
    """Runs of at least STILL_WINDOW_S where nothing visibly moves."""
    out, start = [], None
    for t, v in zip(times, ydif):
        if v < STILL_THRESHOLD:
            start = t if start is None else start
        else:
            if start is not None and t - start >= STILL_WINDOW_S:
                out.append([round(start, 2), round(t, 2)])
            start = None
    if start is not None and times and times[-1] - start >= STILL_WINDOW_S:
        out.append([round(start, 2), round(times[-1], 2)])
    return out


def measure_audio(path: Path, duration: float) -> dict:
    log = _ffmpeg(['-i', path, '-vn', '-af', 'ebur128=peak=true,silencedetect=n=-45dB:d=0.4', '-f', 'null', '-'])
    tail = log[log.rfind('Summary:'):] if 'Summary:' in log else ''
    num = lambda rx: (lambda m: None if not m or m.group(1) == '-inf' else float(m.group(1)))(re.search(rx, tail))
    starts = [float(x) for x in re.findall(r'silence_start: (-?[\d.]+)', log)]
    ends = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', log)]
    end_log = _ffmpeg(['-sseof', '-0.15', '-i', path, '-vn', '-af', 'volumedetect', '-f', 'null', '-'])
    last = re.search(r'mean_volume: (-?[\d.]+) dB', end_log)
    return {'lufs': num(r'I:\s+(-?[\d.]+) LUFS'), 'lra': num(r'LRA:\s+(-?[\d.]+) LU'), 'true_peak': num(r'Peak:\s+(-?[\d.]+|-inf) dBFS'),
            'silence_start_s': round(ends[0], 2) if starts and starts[0] <= .05 and ends else 0.0,
            'silence_end_s': round(duration - starts[-1], 2) if len(starts) > len(ends) else 0.0,
            'last_150ms_db': float(last.group(1)) if last else None}


def check_srt(path: Path, duration: float) -> list[str]:
    """Subtitle defects a viewer would notice: overlaps, outside the film, too long or too fast."""
    text = Path(path).read_text(encoding='utf-8', errors='replace').replace('\r', '')
    problems, prev = [], 0.0
    to_s = lambda h, m, s, ms: int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
    for block in re.split(r'\n\n+', text.strip()):
        m = re.search(r'(\d+):(\d+):(\d+)[,.](\d+) --> (\d+):(\d+):(\d+)[,.](\d+)', block)
        if not m:
            continue
        a, b = to_s(*m.groups()[:4]), to_s(*m.groups()[4:])
        lines = block.split('\n')[block.split('\n').index(m.group(0)) + 1:]
        chars = sum(len(l) for l in lines)
        if a < prev - .01:
            problems.append(f'chevauchement à {a:.2f} s')
        if b > duration + .05:
            problems.append(f'sous-titre après la fin à {b:.2f} s')
        if any(len(l) > 44 for l in lines):
            problems.append(f'ligne trop longue à {a:.2f} s')
        if b > a and chars / (b - a) > 25:
            problems.append(f'lecture trop rapide à {a:.2f} s ({chars / (b - a):.0f} car/s)')
        prev = b
    return problems


def safe_area_frame(path: Path, at: float, out: Path, width: int, height: int) -> Path:
    """Frame with the zones platforms cover drawn on it, for a human or visual check."""
    vertical = height > width
    top, bottom, right = (.14, .20, .12) if vertical else (.05, .05, .05)
    boxes = (f"drawbox=x=0:y=0:w=iw:h=ih*{top}:color=red@0.28:t=fill,drawbox=x=0:y=ih*{1 - bottom}:w=iw:h=ih*{bottom}:color=red@0.28:t=fill,"
             f"drawbox=x=iw*{1 - right}:y=0:w=iw*{right}:h=ih:color=red@0.28:t=fill")
    _ffmpeg(['-y', '-ss', at, '-i', path, '-frames:v', 1, '-vf', f'{boxes},scale=640:-2', out])
    return out


def qc(path: Path, thumbnails: Path | None = None, *, exceptions: list[dict] | None = None, expect: dict | None = None,
       subtitles: Path | None = None, styleframes: list[dict] | None = None, audio_target: float | None = -14.0) -> dict:
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)
    if not shutil.which('ffmpeg'):
        raise RuntimeError('FFmpeg requis')
    exceptions, expect = exceptions or [], expect or {}
    data = _probe(path)
    streams = data.get('streams', [])
    v = next((s for s in streams if s.get('codec_type') == 'video'), None)
    a = next((s for s in streams if s.get('codec_type') == 'audio'), None)
    dur = float(data.get('format', {}).get('duration') or 0)
    blocking, warnings, declared, aesthetic = [], [], [], []
    w, h = int(v.get('width', 0)) if v else 0, int(v.get('height', 0)) if v else 0
    rate = v.get('avg_frame_rate', '0/1') if v else '0/1'
    x, y = rate.split('/')
    fps = round(float(x) / float(y), 3) if float(y) else 0
    checks = {'video_present': bool(v), 'duration_positive': dur > 0, 'even_dimensions': bool(v and w % 2 == 0 and h % 2 == 0),
              'h264_video': bool(v and v.get('codec_name') == 'h264'), 'yuv420p': bool(v and v.get('pix_fmt') == 'yuv420p')}
    if not v:
        blocking.append('Pas de piste vidéo.')
    if dur <= 0:
        blocking.append('Durée nulle.')
    if v and not checks['even_dimensions']:
        blocking.append(f'Dimensions impaires {w}x{h}.')
    if v and not checks['h264_video'] and expect.get('codec', 'h264') == 'h264':
        warnings.append(f"Codec {v.get('codec_name')} : H.264 attendu pour les réseaux.")
    if v and not checks['yuv420p']:
        warnings.append(f"Pixels {v.get('pix_fmt')} : yuv420p recommandé pour la compatibilité.")
    if expect.get('width') and (w, h) != (expect['width'], expect['height']):
        blocking.append(f"Résolution {w}x{h}, attendue {expect['width']}x{expect['height']}.")
    if expect.get('fps') and abs(fps - expect['fps']) > .05:
        blocking.append(f"Cadence {fps}, attendue {expect['fps']}.")
    if expect.get('duration_s') and abs(dur - expect['duration_s']) > max(.25, expect['duration_s'] * .03):
        blocking.append(f"Durée {dur:.2f} s, attendue {expect['duration_s']} s.")
    decode_errors = subprocess.run(['ffmpeg', '-hide_banner', '-v', 'error', '-i', str(path), '-f', 'null', '-'], capture_output=True, text=True, encoding='utf-8', errors='replace').stderr.strip()
    if decode_errors:
        blocking.append('Erreurs de décodage : ' + decode_errors[:160])
    vm = measure_video(path) if v and dur > 0 else {'black': [], 'freeze_start': [], 'freeze_end': [], 'cuts': [], 'times': [], 'ydif': []}
    if v and dur > 0 and not vm['times']:
        blocking.append("Analyse de l'image impossible : le noir, le figé et le mouvement n'ont pas été mesurés.")
    for start, end in vm['black']:
        e = _covered('black', start, end, exceptions)
        if e:
            declared.append(f"Noir {start:.2f}-{end:.2f} s : {e.get('reason', 'déclaré')}")
        else:
            blocking.append(f'Noir non déclaré {start:.2f}-{end:.2f} s.')
    freeze_ends = vm['freeze_end'] + [dur] * (len(vm['freeze_start']) - len(vm['freeze_end']))
    for start, end in zip(vm['freeze_start'], freeze_ends):
        e = _covered('freeze', start, end, exceptions)
        if e:
            declared.append(f"Image figée {start:.2f}-{end:.2f} s : {e.get('reason', 'déclaré')}")
        elif end - start >= 2:
            warnings.append(f'Image figée {start:.2f}-{end:.2f} s.')
        else:
            aesthetic.append(f'Tenue immobile {start:.2f}-{end:.2f} s.')
    still = still_windows(vm['times'], vm['ydif'])
    if still:
        aesthetic.append(f'{len(still)} passage(s) de plus de {STILL_WINDOW_S} s presque immobiles : acceptable si le genre ou le storyboard le veut.')
    audio = None
    if a and dur > 0:
        audio = measure_audio(path, dur)
        if audio['true_peak'] is not None and audio['true_peak'] > -.5:
            blocking.append(f"Saturation : crête {audio['true_peak']} dBFS.")
        elif audio['true_peak'] is not None and audio['true_peak'] > -1:
            warnings.append(f"Crête haute {audio['true_peak']} dBFS (objectif ≤ -1).")
        if audio_target is not None and audio['lufs'] is not None and abs(audio['lufs'] - audio_target) > 2:
            warnings.append(f"Volume {audio['lufs']} LUFS (objectif {audio_target} ± 2).")
        if audio['silence_start_s'] > 1 and not _covered('silence', 0, audio['silence_start_s'], exceptions):
            warnings.append(f"Silence de {audio['silence_start_s']} s au début.")
        if audio['last_150ms_db'] is not None and audio['last_150ms_db'] > -30 and not _covered('abrupt-end', 0, 1e9, exceptions):
            warnings.append(f"Fin audio coupée sec ({audio['last_150ms_db']} dB sur les 150 dernières ms) : ajouter un fondu.")
    elif not a:
        (declared if any(e.get('type') == 'no-audio' for e in exceptions) else warnings).append('Vidéo sans piste audio.')
    if subtitles:
        for problem in check_srt(subtitles, dur):
            blocking.append('Sous-titres : ' + problem)
    ssim = []
    for sf in styleframes or []:
        log = _ffmpeg(['-ss', sf['at'], '-i', path, '-i', sf['path'], '-frames:v', 1, '-lavfi', '[0:v][1:v]scale2ref[a][b];[a][b]ssim', '-f', 'null', '-'])
        m = re.search(r'All:([\d.]+)', log)
        value = float(m.group(1)) if m else None
        ssim.append({'at': sf['at'], 'styleframe': str(sf['path']), 'ssim': value})
        if value is not None and value < sf.get('min', .35):
            warnings.append(f"Écart au styleframe à {sf['at']} s (SSIM {value:.2f}).")
    proofs = {}
    if thumbnails and v and dur > 0:
        thumbnails = Path(thumbnails)
        thumbnails.mkdir(parents=True, exist_ok=True)
        for i, at in enumerate((dur * .1, dur * .5, dur * .9)):
            _ffmpeg(['-y', '-ss', f'{at:.3f}', '-i', path, '-frames:v', 1, '-vf', 'scale=640:-2', thumbnails / f'frame-{i + 1}.jpg'])
        proofs['contact_sheet'] = str(contact_sheet([path], thumbnails / 'planche.jpg'))
        proofs['safe_area'] = str(safe_area_frame(path, dur * .5, thumbnails / 'zones-sures.jpg', w, h))
    moving = sum(1 for t in vm['ydif'] if t >= STILL_THRESHOLD) / len(vm['ydif']) if vm['ydif'] else 0
    return {'pass': not blocking, 'blocking': blocking, 'warnings': warnings, 'declared': declared, 'aesthetic': aesthetic, 'checks': checks,
            'duration': round(dur, 3), 'width': w or None, 'height': h or None, 'fps': fps, 'video_codec': v.get('codec_name') if v else None,
            'pix_fmt': v.get('pix_fmt') if v else None, 'audio_codec': a.get('codec_name') if a else None, 'audio': audio,
            'cuts': vm['cuts'], 'moving_ratio': round(moving, 3), 'styleframes': ssim, 'proofs': proofs,
            'note': 'Le QC technique ne remplace pas un visionnage humain des plans et une écoute audio.'}
