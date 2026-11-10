"""Local FFmpeg montage: cuts, crossfades, Ken Burns stills, logo, voice over ducked music, loudness.

This edits media that already exists. It does not replace Remotion, HyperFrames,
professional grading or generation services. Originals are only read.
"""
from __future__ import annotations
import json
import re
import shutil
import subprocess
import tempfile
import textwrap
from pathlib import Path
from .engine import FORMATS, classify, resolve_asset
from .qc import qc  # noqa: F401  (public API of this module)

PROFILES = {'draft': 640, 'review': 960, 'final': 1920, '4k': 3840}
ENCODE = {'draft': ('veryfast', 28), 'review': ('medium', 23), 'final': ('slow', 17), '4k': ('slow', 17)}
FPS = 30
TV = ['-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv']
# The AAC encoder overshoots by several dB when a loud sound starts on the very first sample: the first 50 ms fade in, too short to hear
FADE_IN = 'afade=t=in:st=0:d=0.05'
PEAK_LIMIT, PEAK_TARGET = -1.0, -1.5
FONT_CANDIDATES = ('C:/Windows/Fonts/segoeuib.ttf', 'C:/Windows/Fonts/arialbd.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
                   '/usr/share/fonts/TTF/DejaVuSans-Bold.ttf', '/System/Library/Fonts/Supplemental/Arial Bold.ttf')


def run(args: list, cwd: Path | None = None) -> str:
    result = subprocess.run([str(a) for a in args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                            encoding='utf-8', errors='replace', cwd=cwd)
    if result.returncode:
        raise RuntimeError(f"Commande échouée ({result.returncode}): {args[0]}\n{result.stderr[-2700:]}")
    return result.stdout


def probe(p: Path) -> dict:
    return json.loads(run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(p)]))


def has_audio(p: Path) -> bool:
    return any(s.get('codec_type') == 'audio' for s in probe(p).get('streams', []))


def true_peak(p: Path) -> float | None:
    """The true peak of the delivered sound, measured on the encoded file: what a listener's player decodes."""
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(p), '-vn', '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    found = re.findall(r'Peak:\s+(-?[\d.]+) dBFS', r.stderr)
    return float(found[-1]) if found else None


def limit_peak(path: Path) -> str | None:
    """Safety net after a delivery encode: a peak still above the limit lowers the whole sound just enough, the picture is copied as is.
    Returns what was done, or None when nothing had to be done."""
    path = Path(path)
    peak = true_peak(path) if has_audio(path) else None
    if peak is None or peak <= PEAK_LIMIT:
        return None
    cut = round(peak - PEAK_TARGET, 2)
    fixed = path.with_name(path.stem + '.crete' + path.suffix)
    run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', path, '-map', '0', '-c:v', 'copy', '-af', f'volume=-{cut}dB', '-c:a', 'aac', '-b:a', '192k',
         '-ar', '48000', '-movflags', '+faststart', fixed])
    fixed.replace(path)
    return f'crête de {peak:+.1f} dBTP après encodage : son baissé de {cut} dB'


def duration(p: Path) -> float:
    try:
        return float(probe(p)['format']['duration'])
    except (ValueError, KeyError, TypeError):
        return 0.0


def dimensions(fmt: str, profile: str) -> tuple[int, int]:
    if fmt not in FORMATS:
        raise ValueError('Format non reconnu')
    if profile not in PROFILES:
        raise ValueError('Profil non reconnu')
    w, h = FORMATS[fmt]
    scale = PROFILES[profile] / 1920
    return max(2, round(w * scale / 2) * 2), max(2, round(h * scale / 2) * 2)


def _font(tmp: Path) -> str | None:
    """A copy next to the command: Windows paths and drawtext escaping do not mix."""
    for candidate in FONT_CANDIDATES:
        if Path(candidate).exists():
            shutil.copy(candidate, tmp / 'font.ttf')
            return 'font.ttf'
    return None


def text_segment(title: str, out: Path, seconds: float, w: int, h: int, temp: Path):
    """Title on a moving gradient: text enters and leaves, background never sits still."""
    title = title.strip() or 'Motion Design Kit'
    (temp / 'title.txt').write_text('\n'.join(textwrap.wrap(title, width=24, break_long_words=True)[:4]), encoding='utf-8')
    font = _font(temp)
    frames = round(seconds * FPS)
    src = f'gradients=s={w}x{h}:c0=0x10162b:c1=0x2b1d5c:c2=0x0d3b4f:nb_colors=3:speed=0.012:seed=7:r={FPS}:d={seconds}'
    enter = f'min(1,t/0.5)'
    leave = f'min(1,({seconds}-t)/0.35)'
    draw = ('drawtext=' + (f'fontfile={font}:' if font else '') + f'textfile=title.txt:fontcolor=white:fontsize={max(19, w // 18)}:line_spacing=12'
            f":x=(w-text_w)/2:y='(h-text_h)/2+{h // 24}*pow(1-{enter},3)':alpha='min({enter},{leave})'")
    run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'lavfi', '-i', src, '-f', 'lavfi', '-i', 'anullsrc=channel_layout=stereo:sample_rate=48000',
         '-frames:v', frames, '-t', seconds, '-vf', f'{draw},format=yuv420p', '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', 20,
         '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-ar', 48000, '-ac', 2, '-b:a', '128k', out.name], cwd=out.parent)


def _is_silent(src: Path) -> bool:
    if classify(src) != 'video' or not has_audio(src):
        return True
    log = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(src), '-vn', '-af', 'volumedetect', '-f', 'null', '-'], capture_output=True, text=True, encoding='utf-8', errors='replace').stderr
    m = re.search(r'max_volume: (-?[\d.]+|-inf) dB', log)
    return not m or m.group(1) == '-inf' or float(m.group(1)) < -70


def _visual_chain(i: int, kind: str, w: int, h: int, seconds: float, src_w: int, src_h: int, kb_seed: int) -> str:
    """Every source ends up as a w x h, 30 fps stream. A portrait clip in a wide frame keeps its whole picture."""
    if kind == 'image':
        frames = round(seconds * FPS)
        dx, dy = (-1, 1)[kb_seed % 2], (1, -1)[kb_seed % 3 == 0]
        return (f"[{i}:v]scale={w * 2}:{h * 2}:force_original_aspect_ratio=increase,crop={w * 2}:{h * 2},setsar=1,"
                f"zoompan=z='1+0.08*on/{frames}':x='(iw-iw/zoom)/2+{dx}*{w // 40}*on/{frames}':y='(ih-ih/zoom)/2+{dy}*{h // 60}*on/{frames}':d={frames}:s={w}x{h}:fps={FPS},"
                f"format=yuv420p,settb=AVTB,trim=duration={seconds},setpts=PTS-STARTPTS[v{i}]")
    same_shape = src_w and src_h and abs(src_w / src_h - w / h) < .06
    if same_shape or not (src_w and src_h):
        return f"[{i}:v]fps={FPS},scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1,format=yuv420p,settb=AVTB,trim=duration={seconds},setpts=PTS-STARTPTS[v{i}]"
    return (f"[{i}:v]fps={FPS},split[a{i}][b{i}];[a{i}]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},boxblur=24:2,eq=brightness=-0.08[bg{i}];"
            f"[b{i}]scale={w}:{h}:force_original_aspect_ratio=decrease[fg{i}];[bg{i}][fg{i}]overlay=(W-w)/2:(H-h)/2,setsar=1,format=yuv420p,settb=AVTB,trim=duration={seconds},setpts=PTS-STARTPTS[v{i}]")


def _audio_chain(i: int, seconds: float, with_audio: bool) -> str:
    base = f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,apad,atrim=duration={seconds},asetpts=PTS-STARTPTS" if with_audio else f"aevalsrc=0:d={seconds}:s=48000:c=stereo"
    return f"{base}[a{i}]"


def edit(edl: list[dict], root: Path, output: Path, *, fmt: str = '16:9', profile: str = 'draft', logo: Path | None = None, voice: Path | None = None,
         music: Path | None = None, subtitles: Path | None = None, target_lufs: float = -14.0, size: tuple | None = None) -> dict:
    """edl items: {src, in?, out?, seconds?, transition?: cut|fade, fade_s?}. `src` paths resolve against root.
    `size` gives the frame directly, for a source whose shape is none of the standard formats."""
    if not edl:
        raise ValueError('EDL vide')
    w, h = size or dimensions(fmt, profile)
    output = Path(output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    args, chains, segs = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y'], [], []
    for i, item in enumerate(edl):
        src = resolve_asset(root, item['src'])
        if not src.is_file():
            raise FileNotFoundError(f'Média manquant: {src}')
        kind = classify(src)
        if kind not in ('image', 'video'):
            raise ValueError(f'Média non compatible: {src}')
        info = probe(src)
        vs = next((s for s in info.get('streams', []) if s.get('codec_type') == 'video'), {})
        src_w, src_h = int(vs.get('width', 0)), int(vs.get('height', 0))
        rot = next((abs(int(x['rotation'])) for x in vs.get('side_data_list', []) if 'rotation' in x), 0)
        if rot in (90, 270):
            src_w, src_h = src_h, src_w
        start = float(item.get('in', 0))
        if kind == 'video':
            total = float(info['format'].get('duration') or 0)
            seconds = float(item.get('seconds') or (float(item['out']) - start if 'out' in item else total - start))
            seconds = min(seconds, total - start) if total else seconds
            args += ['-ss', start, '-t', seconds, '-i', src]
        else:
            seconds = float(item.get('seconds', 3))
            args += ['-i', src]
        if seconds <= 0:
            raise ValueError(f'Durée invalide pour {src.name}')
        chains.append(_visual_chain(i, kind, w, h, seconds, src_w, src_h, i))
        chains.append(_audio_chain(i, seconds, kind == 'video' and any(s.get('codec_type') == 'audio' for s in info.get('streams', []))))
        segs.append({'seconds': seconds, 'transition': item.get('transition', 'cut'), 'fade': float(item.get('fade_s', .4)), 'src': src.name})
    # Chain: a crossfade shortens the film, a cut does not
    vlabel, alabel, offset = '[v0]', '[a0]', segs[0]['seconds']
    for i, seg in enumerate(segs[1:], 1):
        if seg['transition'] == 'fade':
            d = min(seg['fade'], offset / 2, seg['seconds'] / 2)
            chains.append(f"{vlabel}[v{i}]xfade=transition=fade:duration={d:.3f}:offset={offset - d:.3f}[xv{i}]")
            chains.append(f"{alabel}[a{i}]acrossfade=d={d:.3f}[xa{i}]")
            offset += seg['seconds'] - d
        else:
            chains.append(f"{vlabel}[v{i}]concat=n=2:v=1:a=0[xv{i}]")
            chains.append(f"{alabel}[a{i}]concat=n=2:v=0:a=1[xa{i}]")
            offset += seg['seconds']
        vlabel, alabel = f'[xv{i}]', f'[xa{i}]'
    next_input = len(edl)
    if logo:
        args += ['-i', logo]
        margin = max(12, w // 32)
        chains.append(f"[{next_input}:v]scale={round(w * .14)}:-1,format=rgba[lg]")
        chains.append(f"{vlabel}[lg]overlay=W-w-{margin}:{margin}:format=auto[withlogo]")
        vlabel = '[withlogo]'
        next_input += 1
    with tempfile.TemporaryDirectory(prefix='motionkit-') as tmp:
        if subtitles:
            shutil.copy(subtitles, Path(tmp) / 'subs.srt')
            chains.append(f"{vlabel}subtitles=subs.srt:force_style='FontName=Arial,FontSize={11 if h > w else 15},Outline=1,Shadow=0,MarginV={40 if h > w else 14},Bold=1'[withsubs]")
            vlabel = '[withsubs]'
        bed = alabel
        if music:
            args += ['-stream_loop', -1, '-i', music]
            chains.append(f"[{next_input}:a]aresample=48000,aformat=channel_layouts=stereo,loudnorm=I=-26:TP=-3,aresample=48000,atrim=duration={offset:.3f}[mu]")
            chains.append(f"{bed}[mu]amix=inputs=2:duration=first:normalize=0[bedmix]")
            bed = '[bedmix]'
            next_input += 1
        if voice:
            args += ['-i', voice]
            chains.append(f"[{next_input}:a]aresample=48000,aformat=channel_layouts=stereo,loudnorm=I=-16:TP=-2,aresample=48000,asplit[vo][vosc]")
            chains.append(f"{bed}[vosc]sidechaincompress=threshold=0.04:ratio=8:attack=20:release=350[duck]")
            chains.append("[duck][vo]amix=inputs=2:duration=first:normalize=0[mixed]")
            bed = '[mixed]'
            next_input += 1
        fade_at = max(0, offset - .35)
        # loudnorm turns pure silence into NaN: a film with no sound at all keeps its silent track
        level = '' if not voice and not music and all(_is_silent(resolve_asset(root, x['src'])) for x in edl) else f'loudnorm=I={target_lufs}:TP=-1.5:LRA=11,aresample=48000,'
        chains.append(f"{bed}{level}{FADE_IN},afade=t=out:st={fade_at:.3f}:d=0.35[aout]")
        preset, crf = ENCODE[profile]
        args += ['-filter_complex', ';'.join(chains), '-map', vlabel, '-map', '[aout]', '-t', f'{offset:.3f}', '-c:v', 'libx264', '-preset', preset, '-crf', crf,
                 '-pix_fmt', 'yuv420p', *TV, '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', str(output)]
        run(args, cwd=Path(tmp))
    peak_fix = limit_peak(output)
    data = probe(output)
    vs = next((s for s in data.get('streams', []) if s.get('codec_type') == 'video'), {})
    return {'output': str(output), 'bytes': output.stat().st_size, 'width': vs.get('width'), 'height': vs.get('height'), 'duration': duration(output),
            'profile': profile, 'scenes': len(segs), 'logo': bool(logo), 'voice': bool(voice), 'music': bool(music), 'subtitles': bool(subtitles), 'peak_fix': peak_fix,
            'edl': segs}


def restyle_preview(src: Path, output: Path, *, fmt: str = '16:9', profile: str = 'draft', seconds: float = 4) -> dict:
    """Posterized + inked look by filters. A local preview of a direction, NOT a real restyle: no identity tracking."""
    w, h = dimensions(fmt, profile)
    output = Path(output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    chain = (f"[0:v]fps={FPS},scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1,split[p][e];"
             "[p]lutyuv=y='floor(val/36)*36+18',eq=saturation=1.45:contrast=1.08[flat];"
             "[e]edgedetect=low=0.08:high=0.22:mode=wires,format=gray,negate,format=gbrp[ink];"
             "[flat]format=gbrp[f2];[f2][ink]blend=all_mode=multiply,format=yuv420p[o]")  # blend en RGB: en YUV todo vira a verde
    preset, crf = ENCODE[profile]
    run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', src, '-t', seconds, '-filter_complex', chain, '-map', '[o]', '-map', '0:a?', '-c:v', 'libx264', '-preset', preset,
         '-crf', crf, '-pix_fmt', 'yuv420p', *TV, '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', output])
    return {'output': str(output), 'duration': duration(output), 'restyle': 'preview-filters-only'}


def render(spec: dict, root: Path, output: Path, profile: str = 'draft') -> dict:
    """Short brief format: assets with roles. Without images or clips, a title film."""
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
        raise RuntimeError('FFmpeg/ffprobe requis pour render')
    assets = [(resolve_asset(root, a), a.get('role', 'source') if isinstance(a, dict) else 'source') for a in spec.get('assets', [])]
    missing = [str(p) for p, _ in assets if not p.is_file()]
    if missing:
        raise FileNotFoundError('Médias manquants: ' + ', '.join(missing))
    pick = lambda role, kind: next((p for p, r in assets if r == role and classify(p) == kind), None)
    logo, voice, music = pick('logo', 'image'), pick('voice', 'audio'), pick('music', 'audio')
    media = [p for p, r in assets if classify(p) in ('video', 'image') and r not in ('logo', 'cover')]
    fmt = spec.get('format', '16:9')
    with tempfile.TemporaryDirectory(prefix='motionkit-') as tmp:
        work = Path(tmp)
        if not media:
            w, h = dimensions(fmt, profile)
            title = work / 'title.mp4'
            text_segment(spec.get('title') or spec.get('brief', 'Motion Design Kit'), title, float(spec.get('duration', 5)), w, h, work)
            media = [title]
        seconds = spec.get('clip_duration')
        edl = [{'src': str(p), **({'seconds': float(seconds)} if seconds else {}), **({'transition': spec['transition']} if spec.get('transition') else {})} for p in media]
        result = edit(edl, root, output, fmt=fmt, profile=profile, logo=logo, voice=voice, music=music)
    return result
