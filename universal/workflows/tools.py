"""What every treatment shares: reading a video, running FFmpeg with a long filter graph, intermediate and final encodes."""
from __future__ import annotations
import json
import re
import subprocess
from pathlib import Path
from .. import config
from ..render import ENCODE, FADE_IN, PROFILES, TV, limit_peak, probe

# Between two treatments the picture is kept close to lossless: only the last encode decides the delivered quality
INTERMEDIATE = ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '14', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '256k', '-ar', '48000']
HARDWARE = {'h264_qsv': lambda crf: ['-global_quality', str(crf + 3)], 'h264_nvenc': lambda crf: ['-cq', str(crf + 4)],
            'h264_amf': lambda crf: ['-qp_i', str(crf + 3), '-qp_p', str(crf + 5)], 'h264_videotoolbox': lambda crf: ['-q:v', str(max(30, 80 - crf))]}


def ffmpeg(args: list, cwd: Path | None = None) -> str:
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-y'] + [str(a) for a in args], capture_output=True, text=True, encoding='utf-8', errors='replace', cwd=cwd)
    if r.returncode:
        raise RuntimeError('FFmpeg a échoué : ' + r.stderr.strip()[-900:])
    return r.stderr


def ffmpeg_major() -> int:
    r = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, encoding='utf-8', errors='replace')
    m = re.search(r'ffmpeg version n?(\d+)', r.stdout)
    return int(m.group(1)) if m else 0


def graph_args(graph: str, work: Path, name: str = 'graphe.txt') -> list:
    """A long video means a long filter graph: it goes through a file, never through the command line and its length limit."""
    f = Path(work) / name
    f.write_text(graph, encoding='utf-8')
    # An unknown version is a development build, newer than any release: only FFmpeg 6 and older still need the former option
    return ['-filter_complex_script', f] if 0 < ffmpeg_major() < 7 else ['-/filter_complex', f]


def balanced_sum(terms: list[str]) -> str:
    """a+b+c+… written as a balanced tree. FFmpeg refuses an expression nested deeper than about a hundred levels, and a plain
    chain of additions nests once per term: a long video failed on its hundredth cut. A balanced tree is only log2(n) deep."""
    if len(terms) <= 2:
        return '+'.join(terms)
    mid = len(terms) // 2
    return f'({balanced_sum(terms[:mid])})+({balanced_sum(terms[mid:])})'


def info(path: Path) -> dict:
    """Size as displayed (a phone clip stored sideways counts upright), frame rate, length, sound."""
    data = probe(Path(path))
    v = next((s for s in data.get('streams', []) if s.get('codec_type') == 'video'), {})
    w, h = int(v.get('width', 0)), int(v.get('height', 0))
    rot = next((abs(int(x['rotation'])) for x in v.get('side_data_list', []) if 'rotation' in x), 0)
    if rot in (90, 270):
        w, h = h, w
    a, _, b = (v.get('avg_frame_rate') or v.get('r_frame_rate') or '30/1').partition('/')
    fps = float(a) / float(b or 1) if float(b or 1) else 30.0
    return {'width': w, 'height': h, 'fps': round(fps, 3) if 1 <= fps <= 240 else 30.0, 'duration': float(data.get('format', {}).get('duration') or 0),
            'audio': any(s.get('codec_type') == 'audio' for s in data.get('streams', []))}


def even(x: float) -> int:
    return max(2, int(round(x / 2)) * 2)


def fit(width: int, height: int, profile: str) -> tuple[int, int]:
    """The source's own shape at the size of this profile, never enlarged."""
    cap = PROFILES[profile]
    k = min(1.0, cap / max(width, height))
    return even(width * k), even(height * k)


def loudness_filter(src: Path, target: float) -> str | None:
    """Two-pass loudness to the target. None when there is no sound to measure: silence stays silence."""
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(src), '-vn', '-af', f'loudnorm=I={target}:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    m = re.search(r'\{[^{}]*"input_i"[^{}]*\}', r.stderr, re.S)
    if r.returncode or not m:
        return None
    d = json.loads(m.group(0))
    if any(re.search(r'inf|nan', str(d[k]), re.I) for k in ('input_i', 'input_tp', 'input_lra', 'input_thresh', 'target_offset')):
        return None
    return (f"loudnorm=I={target}:TP=-1.5:LRA=11:measured_I={d['input_i']}:measured_TP={d['input_tp']}:measured_LRA={d['input_lra']}"
            f":measured_thresh={d['input_thresh']}:offset={d['target_offset']}:linear=true,aresample=48000")


def verified_encoders() -> list[str]:
    """Hardware encoders that really produced a file on this machine, as recorded by the first-run check."""
    from .. import state
    return [name for name, ok in (state.load().get('encoders') or {}).items() if ok]


def final_encoder(profile: str, seconds: float) -> tuple[list, str]:
    """Software by default: it is the reference quality. Hardware only where it pays off, a long video, and only if it was verified here."""
    preset, crf = ENCODE[profile]
    software = (['-c:v', 'libx264', '-preset', preset, '-crf', str(crf)], 'libx264')
    policy = config.get('render.hardware_encoder', 'long')
    if policy == 'never' or (policy == 'long' and seconds < config.get('render.long_video_s', 300)):
        return software
    for name in verified_encoders():
        if name in HARDWARE:
            return ['-c:v', name] + HARDWARE[name](int(crf)), name
    return software


def finish(src: Path, out: Path, *, width: int, height: int, profile: str, work: Path) -> dict:
    """The one delivery encode: size of the profile, loudness, broadcast colours, a file that starts playing at once."""
    meta = info(src)
    target = config.get('render.loudness_lufs', -14)
    level = loudness_filter(src, target) if meta['audio'] else None
    video = f'scale={width}:{height}:flags=lanczos,setsar=1,format=yuv420p'
    codec, used = final_encoder(profile, meta['duration'])
    out.parent.mkdir(parents=True, exist_ok=True)

    sound = ','.join(x for x in (level, FADE_IN) if x) if meta['audio'] else None

    def encode(codec_args):
        args = ['-i', src, '-vf', video] + (['-af', sound] if sound else []) + codec_args + ['-pix_fmt', 'yuv420p', *TV]
        args += (['-c:a', 'aac', '-b:a', '192k', '-ar', '48000'] if meta['audio'] else ['-an']) + ['-movflags', '+faststart', out]
        ffmpeg(args, cwd=work)
    try:
        encode(codec)
    except RuntimeError:
        if used == 'libx264':
            raise
        preset, crf = ENCODE[profile]  # the hardware path failed on this file: the reference encoder takes over
        encode(['-c:v', 'libx264', '-preset', preset, '-crf', str(crf)])
        used = 'libx264 (repli : encodeur matériel en échec)'
    fixed = limit_peak(out)
    result = {'encoder': used, 'loudness': 'normalisé' if level else ('silence conservé' if meta['audio'] else 'sans piste audio')}
    return {**result, 'peak_fix': fixed} if fixed else result
