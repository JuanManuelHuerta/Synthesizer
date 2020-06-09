

import pyaudio
import numpy as np
import random
from array import array
import mido
tapper_off = 20000




volume = 0.5     # range [0.0, 1.0]
fs = 44100       # sampling rate, Hz, must be integer
duration = 0.75   # in seconds, may be float



def play_note(note_value):
    note_mapper = (2.0**((note_value-69)/12.0))*440.0
    samples = np.sin(2*np.pi*np.arange(fs*duration)*note_mapper/fs).astype(np.float32)
    for i in range(tapper_off):
        samples[-i-1]=samples[-i-1]*i/float(tapper_off) 


    stream.write(volume*samples)


p = pyaudio.PyAudio()

stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=fs,
                input=True,
                output=True)



index=0
for msg in mido.open_input():
    print(msg)
    if msg.type == 'note_on':
        play_note(msg.note)


