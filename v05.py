

import pyaudio
import numpy as np
import random
from array import array
import mido
import matplotlib.pyplot as plt
tapper_off = 20000




volume = 0.5     # range [0.0, 1.0]
fs = 44100       # sampling rate, Hz, must be integer
duration = 2.0   # in seconds, may be float
decay=-0.0003
waves = {}


#precompute waveforms
gain=1.0



for i in range(22,122):
    note_mapper = (2.0**((i-69)/12.0))*440.0
    gain=np.exp(decay*np.arange(fs*duration))
    #gain=1.0
    
    samples = (volume*(1.0-gain)*gain*np.sin(2*np.pi*np.arange(fs*duration)*note_mapper/fs)).astype(np.float32)
    waves[i]=samples

plt.plot(waves[71])
plt.show()

def play_note(note_value):
    stream.write(waves[note_value])
    print(waves[note_value][-3:])

p = pyaudio.PyAudio()

stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=fs,
                input=True,
                output=True,
                frames_per_buffer=220)



index=0
for msg in mido.open_input():
    print(msg)
    if msg.type == 'note_on':
        play_note(msg.note)


