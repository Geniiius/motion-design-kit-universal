"""Score and sound effects, all synthesized here: no sample library and no download.
Each ink brings one instrument, as the Risograph recipe suggests. python -m universal.cli film-style py <this file>"""
import json
from pathlib import Path
import numpy as np
import soundfile as sf
from core.audio import pluck as P
from core.audio.sfx import SR, add, click, clack, compress, ding, limit, noise, hp, env_exp, thump, whoosh

HERE = Path(__file__).resolve().parent
events = json.loads((HERE / 'events.json').read_text(encoding='utf-8'))
DUR = events['dur']
BEAT = .5
mix = np.zeros((int(DUR * SR), 2), np.float32)


def shaker(v=1.0):
    d = .07
    return hp(noise(d), 5000) * env_exp(d, .018) * v


# Blue plate: a dry bass, alone at first
ROOTS = ['C2', 'C2', 'G1', 'A1', 'F1', 'F1', 'G1', 'G1']
for bar in range(int(DUR / (BEAT * 4)) + 1):
    root = ROOTS[bar % len(ROOTS)]
    for beat, vel in ((0, .85), (2.5, .55)):
        at = (bar * 4 + beat) * BEAT
        if at < DUR - .3:
            add(mix, P.pluck('upright_bass_pizz', root, 1.1, vel=vel), at, .62, -.08)

# Yellow plate, at 4 s: the plucked tune
TUNE = [(0, 'E5'), (1, 'G5'), (1.5, 'C6'), (2.5, 'G5'), (4, 'A5'), (5, 'G5'), (5.5, 'E5'), (6.5, 'D5'), (8, 'C5'), (9, 'E5'), (9.5, 'A5'), (10.5, 'G5'), (12, 'F5'), (13, 'E5'), (13.5, 'D5')]
start = 4.0
for beat, pitch in TUNE:
    at = start + beat * BEAT
    if at < DUR - .3:
        add(mix, P.pluck('kalimba', pitch, 1.3, vel=.6), at, .36, .22)

# Pink plate, at 8.5 s: the rhythm, then the last chord under the title
for i in range(int((DUR - 8.5) / (BEAT / 2))):
    at = 8.5 + i * BEAT / 2
    add(mix, shaker(.9 if i % 2 == 0 else .5), at, .14, .3)
for i in range(0, int((DUR - 8.5) / BEAT), 2):
    add(mix, click(.75, .8), 9.0 + i * BEAT, .16, -.2)
for pitch in ('C4', 'E4', 'G4', 'C5'):
    add(mix, P.pluck('kalimba', pitch, 2.4, vel=.62), events['ev'][-1]['t'], .3, -.1)

# The press is the signature foley
for e in events['ev']:
    if e['type'] == 'feed':
        add(mix, whoosh(.5, .6), e['t'], .22, -.3)
    if e['type'] == 'plate':
        add(mix, thump(.9, 62), e['t'], .62)
        add(mix, clack(.8, .9), e['t'] + .012, .34, .1)
        add(mix, whoosh(.28, .7), e['t'] - .22, .3, -.2)
    if e['type'] == 'cut':
        add(mix, clack(1.1, .8), e['t'], .4)
    if e['type'] == 'bell':
        add(mix, ding(.8), e['t'], .24, .25)
for i in range(int(8 / .25)):  # the chain, ticking on twos while the bicycle rolls
    add(mix, click(1.5, .3), i * .25, .05, -.1)

mix[:, 0] = limit(compress(mix[:, 0], .5, 2.5), .92)
mix[:, 1] = limit(compress(mix[:, 1], .5, 2.5), .92)
fade = int(.2 * SR)  # the last chord closes just before the final cut: no click
mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
(HERE / 'out').mkdir(exist_ok=True)
sf.write(HERE / 'out/mix.wav', mix, SR)
print('mix', round(len(mix) / SR, 2), 's')
