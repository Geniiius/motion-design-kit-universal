"""Test media made here, from nothing: no third party rights, nobody's face or voice.

Deterministic: same files on every run. Clearly synthetic, they test pipelines, not taste.
"""
from __future__ import annotations
import math
import random
import struct
import subprocess
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MEDIOS = ROOT / 'examples' / 'medios'


def write_png(path: Path, w: int, h: int, rows: list[bytes]):
    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
    raw = b''.join(b'\x00' + r for r in rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(raw, 6)) + chunk(b'IEND', b''))


def logo(path: Path, size: int = 768):
    """Ring and chevron with soft edges, transparent background."""
    c = size / 2
    rows = []
    for y in range(size):
        row = bytearray(size * 4)
        for x in range(size):
            dx, dy = x + .5 - c, y + .5 - c
            r = math.hypot(dx, dy)
            ring = max(0, min(1, (size * .46 - r))) * max(0, min(1, r - size * .37))
            ax, ay = abs(dy) + dx * .9, dx
            chevron = max(0, min(1, size * .17 - abs(ax - size * .03))) * max(0, min(1, size * .2 - abs(dy)))
            a = max(ring, chevron)
            if a > 0:
                t = (y / size)
                row[x * 4:x * 4 + 4] = bytes((int(70 + 60 * t), int(220 - 90 * t), int(235 - 20 * t), int(a * 255)))
        rows.append(bytes(row))
    write_png(path, size, size, rows)


def ridge(w: int, rng: random.Random, base: float, amp: float) -> list[float]:
    waves = [(rng.uniform(.6, 1) * 2 ** i, rng.uniform(0, 6.28), .55 ** i) for i in range(6)]
    return [base + amp * sum(k * math.sin(x / w * 6.28 * f + p) for f, p, k in waves) for x in range(w)]


def layer(path: Path, w: int, h: int, seed: int, base: float, amp: float, top: tuple, bottom: tuple):
    rng = random.Random(seed)
    tops = ridge(w, rng, base * h, amp * h)
    rows = []
    for y in range(h):
        row = bytearray(w * 4)
        for x in range(w):
            if y >= tops[x]:
                t = min(1, (y - tops[x]) / (h * .45))
                row[x * 4:x * 4 + 4] = bytes((*(int(a + (b - a) * t) for a, b in zip(top, bottom)), 255))
            elif y >= tops[x] - 1:
                row[x * 4:x * 4 + 4] = bytes((*top, 120))
        rows.append(bytes(row))
    write_png(path, w, h, rows)


def sky(path: Path, w: int, h: int, top: tuple, bottom: tuple, sun: tuple):
    rows = []
    for y in range(h):
        t = y / h
        r0, g0, b0 = (int(a + (b - a) * t) for a, b in zip(top, bottom))
        row = bytearray(w * 4)
        for x in range(w):
            d = math.hypot(x - sun[0], y - sun[1])
            glow = max(0, 1 - d / (h * .6)) ** 2.4
            row[x * 4:x * 4 + 4] = bytes((min(255, int(r0 + 200 * glow)), min(255, int(g0 + 170 * glow)), min(255, int(b0 + 90 * glow)), 255))
        rows.append(bytes(row))
    write_png(path, w, h, rows)


def _ff(*args):
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', *[str(a) for a in args]], check=True)


PALETTES = [((18, 26, 64), (246, 151, 96), (36, 40, 92), (16, 18, 48)), ((12, 44, 74), (130, 208, 214), (24, 78, 92), (8, 30, 44)),
            ((44, 20, 66), (240, 120, 150), (70, 30, 90), (24, 10, 40)), ((10, 30, 36), (210, 200, 130), (30, 60, 56), (10, 24, 24)),
            ((60, 34, 24), (250, 196, 120), (92, 52, 40), (36, 18, 14))]


def build(*, full: bool = True, dest: Path = MEDIOS) -> dict:
    dest.mkdir(parents=True, exist_ok=True)
    made = {'logo': dest / 'logo-demo.png'}
    if not made['logo'].exists():
        logo(made['logo'])
    if not full:
        return made
    w, h = 1600, 900
    capas = dest / 'capas'
    if not (capas / 'frente.png').exists():
        sky(capas / 'cielo.png', w, h, *PALETTES[0][:2], (w * .68, h * .42))
        layer(capas / 'lejos.png', w, h, 11, .5, .05, (64, 62, 120), (38, 36, 84))
        layer(capas / 'medio.png', w, h, 23, .64, .07, (36, 40, 92), (22, 24, 62))
        layer(capas / 'frente.png', w, h, 37, .8, .06, (16, 18, 48), (6, 6, 20))
    made['capas'] = capas
    for i, (top, bottom, mid, front) in enumerate(PALETTES, 1):
        out = dest / f'foto-{i}.jpg'
        if not out.exists():
            s, m, f = dest / f'.s{i}.png', dest / f'.m{i}.png', dest / f'.f{i}.png'
            sky(s, 960, 540, top, bottom, (150 + 150 * i, 170 + 20 * i))
            layer(m, 960, 540, 100 + i, .55, .08, mid, front)
            layer(f, 960, 540, 200 + i, .76, .06, front, (4, 4, 12))
            _ff('-i', s, '-i', m, '-i', f, '-filter_complex', '[0][1]overlay[a];[a][2]overlay', '-q:v', 3, out)
            for x in (s, m, f):
                x.unlink()
    clips = {'clip-a.mp4': ('gradients=s=1920x1080:c0=0x0b2545:c1=0x13a89e:speed=0.02:seed=3:r=30:d=6', 220, 30),
             'clip-b.mp4': ('mandelbrot=s=1280x720:r=25:end_scale=0.7:start_scale=2.5', 330, 25),
             'clip-c.mp4': ('testsrc2=s=720x1280:r=30:d=5', 440, 30)}
    for name, (src, tone, _) in clips.items():
        out = dest / name
        if not out.exists():
            _ff('-f', 'lavfi', '-i', src, '-f', 'lavfi', '-i', f'sine=frequency={tone}:duration=6,volume=0.12', '-t', 5, '-c:v', 'libx264', '-preset', 'veryfast', '-crf', 24, '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', out)
    music = dest / 'musica-demo.m4a'
    if not music.exists():
        chord = '+'.join(f'0.11*sin(2*PI*{f}*t)*(0.6+0.4*sin(2*PI*0.25*t))' for f in (130.81, 196, 261.63, 329.63))
        _ff('-f', 'lavfi', '-i', f"aevalsrc='{chord}':d=20:s=48000:c=stereo", '-af', 'lowpass=f=1400', '-c:a', 'aac', '-b:a', '128k', music)
    made.update(fotos=sorted(dest.glob('foto-*.jpg')), clips=sorted(dest.glob('clip-*.mp4')), musica=music)
    return made
