"""Synthesize a classic sad trombone: wah-wah-wah-wahhhh.

Four descending chromatic notes (Bb3, A3, Ab3, G3) with vibrato, scoops,
a wah-wah amplitude wobble, and a pitch droop on the long final note.
Trombone-ish timbre via a harmonic stack. Output: mono 22050 Hz MP3.
"""
import numpy as np
from scipy.io import wavfile
import subprocess

SR = 22050
rng = np.random.default_rng(7)


def note(f0, dur, vib_rate=5.5, vib_depth=0.015, droop_semi=0.0,
         droop_time=0.45, scoop=True):
    n = int(dur * SR)
    t = np.arange(n) / SR
    # fractional pitch deviation: vibrato + scoop-in + final droop
    dev = vib_depth * np.sin(2 * np.pi * vib_rate * t) * np.minimum(1, t / 0.15)
    if scoop:
        dev -= (0.5 / 12) * np.exp(-t / 0.03)  # start ~half semitone flat
    if droop_semi:
        ramp = np.clip((t - (dur - droop_time)) / droop_time, 0, 1)
        dev -= (droop_semi / 12) * ramp ** 1.5
    freq = f0 * 2 ** dev
    phase = 2 * np.pi * np.cumsum(freq) / SR
    # harmonic stack: trombone-ish brass
    y = np.zeros(n)
    for k in range(1, 10):
        y += (1 / k ** 1.25) * np.sin(k * phase + 0.1 * k)
    y /= np.max(np.abs(y))
    # wah-wah amplitude wobble
    wah = 1 - 0.38 * (0.5 + 0.5 * np.sin(2 * np.pi * 4.3 * t + 1.0)) ** 1.5
    y *= wah
    # breath
    y += 0.008 * rng.standard_normal(n)
    # envelope
    a = int(0.025 * SR)
    r = int(0.09 * SR)
    env = np.ones(n)
    env[:a] = 0.5 - 0.5 * np.cos(np.pi * np.arange(a) / a)
    env[-r:] *= 0.5 + 0.5 * np.cos(np.pi * np.arange(r) / r)
    return y * env


parts = [
    note(233.08, 0.30),                    # Bb3 - wah
    note(220.00, 0.30),                    # A3  - wah
    note(207.65, 0.30),                    # Ab3 - wah
    note(196.00, 1.05, vib_depth=0.03,     # G3  - wahhhh + droop
         droop_semi=3.0, scoop=False),
]
gap = np.zeros(int(0.035 * SR))
y = np.concatenate([p for pair in zip(parts, [gap] * 4) for p in pair])
# long fade on the final droop
tail = int(0.35 * SR)
y[-tail:] *= 0.5 + 0.5 * np.cos(np.pi * np.arange(tail) / tail)
y = 0.89 * y / np.max(np.abs(y))

wavfile.write('/tmp/sad_trombone.wav', SR, (y * 32767).astype(np.int16))
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', '/tmp/sad_trombone.wav',
                '-ar', '22050', '-ac', '1', '-b:a', '64k',
                '/home/hatch/workspace/feather-sounds/sounds/sad-trombone.mp3'],
               check=True)
import os
dur = len(y) / SR
size = os.path.getsize('/home/hatch/workspace/feather-sounds/sounds/sad-trombone.mp3')
print(f'done: {dur:.2f}s, {size} bytes -> sounds/sad-trombone.mp3')
