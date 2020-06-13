import pyaudio
import numpy as np
import random
from array import array
import mido


#Globals
fs = 44100           # sampling rate, Hz, must be integer

def init_soundwaves(waves):
    volume = 1.0     # range [0.0, 1.0]
    duration = 3.0   # in seconds, may be float
    decay=-0.0002
    for i in range(22,122):
        note_mapper = (2.0**((i-69)/12.0))*440.0
        gain=np.exp(decay*np.arange(fs*duration))
        samples = (volume*(1.0-gain)*gain*np.sin(2*np.pi*np.arange(fs*duration)*note_mapper/fs)).astype(np.float32)
        waves[i]=samples

def play_note(note_value,stream,waves):
    stream.write(waves[note_value])

def main():
    waves={}
    init_soundwaves(waves)
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=fs,
                    input=False,
                    output=True,
                    frames_per_buffer=220)
    for msg in mido.open_input():
        print(msg)
        if msg.type == 'note_on':
            play_note(msg.note,stream,waves)


if __name__ == "__main__":
    main()

