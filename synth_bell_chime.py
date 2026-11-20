"""Synthesize a single bell chime: one strike with a long ring.

Bell timbre via an inharmonic partial stack (fundamental + hum/prime/
tierce/quint/nominal partials), each decaying exponentially, higher
partials decaying faster. Output: mono 22050 Hz MP3.
"""
import numpy as np
from scipy.io import wavfile
import subprocess
import os

SR = 22050
DUR = 3.0
t = np.arange(int(DUR * SR)) / SR

# Fundamental ~ E5 (659.25 Hz), inharmonic bell partials.
f0 = 659.25
partials = [
    (0.50, 0.30, 2.5),   # hum, octave below
    (1.00, 1.00, 1.0),   # prime
    (1.19, 0.35, 1.6),   # minor tierce-ish
    (1.56, 0.45, 1.2),   # quint-ish
    (2.00, 0.55, 0.8),   # nominal, octave
    (2.74, 0.35, 0.45),  # higher inharmonic
    (3.36, 0.20, 0.35),
    (4.07, 0.15, 0.28),
    (5.43, 0.10, 0.20),
]

y = np.zeros_like(t)
for ratio, amp, decay_s in partials:
    y += amp * np.sin(2 * np.pi * f0 * ratio * t) * np.exp(-t / decay_s)

# Fast strike attack, then let the ring carry.
attack = int(0.005 * SR)
y[:attack] *= np.linspace(0, 1, attack)
y = 0.89 * y / np.max(np.abs(y))

wavfile.write('/tmp/bell_chime.wav', SR, (y * 32767).astype(np.int16))
out = '/home/hatch/workspace/feather-sounds/sounds/bell-chime.mp3'
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', '/tmp/bell_chime.wav',
                '-ar', '22050', '-ac', '1', '-b:a', '64k', out],
               check=True)
print(f'done: {DUR:.2f}s, {os.path.getsize(out)} bytes -> sounds/bell-chime.mp3')
