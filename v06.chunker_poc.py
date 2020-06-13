from __future__ import division
import pyaudio
import numpy as np
import random
from array import array
import mido
import numpy as np
import matplotlib.cm as cm
from scipy import signal
from scipy import interpolate
from numpy import *
import threading,time, queue



#https://people.csail.mit.edu/hubert/pyaudio/docs/

#Globals
fs = 44100           # sampling rate, Hz, must be integer
chunks_per_second = 10
my_queue=[]
waves = {}

def init_soundwaves():
    volume = 1.0     # range [0.0, 1.0]
    duration = 1.0   # in seconds, may be float
    decay=-0.000002
    for i in range(22,122):
        note_mapper = (2.0**((i-69)/12.0))*440.0
        gain=np.exp(decay*np.arange(fs*duration))
        samples = (volume*(1.0-gain)*gain*np.sin(2*np.pi*np.arange(fs*duration)*note_mapper/fs)).astype(np.float32)
        print(len(samples))
        waves[i]=np.split(samples,int(chunks_per_second*duration))

def play_audio():
    p = pyaudio.PyAudio()
    # open output stream
    ostream = p.open(format=pyaudio.paFloat32, channels=1, rate=int(fs),output=True,output_device_index=None)
    # play audio
    while ( 1 ):
        try:
            data = my_queue.pop(0)
        except:
            continue
        if data=="EOT" :
            continue
        try:
            ostream.write( data.astype(np.float32).tostring() )
        except:
            continue
    ostream.close()

def play_note(note_value):
    for chunk in waves[note_value]:
        #stream.write(chunk)
        my_queue.append(chunk)
    print("len of my queue",len(my_queue))

def listen_midi():
    print("Im here")
    for msg in mido.open_input():
        print(msg)
        if msg.type == 'note_on':
            play_note(msg.note)
    

def main():
    init_soundwaves()

    # create an input output FIFO queues
    Qin = queue.Queue()
    Qout = queue.Queue()
    Qdata = queue.Queue()

    # initialize stop_flag
    stop_flag = threading.Event()

    # initialize threads
    t_listen_midi = threading.Thread(target=listen_midi)
    #t_put_data = threading.Thread(target = put_data,   args = (Qout, ptrain, stop_flag  ))
    t_play_audio = threading.Thread(target = play_audio)
    #t_signal_process = threading.Thread(target = signal_process, args = ( Qin, Qdata, pulse_a, Nseg, Nplot, fs, maxdist, temperature, functions, stop_flag))
    # start threads
    t_listen_midi.start()
    #t_put_data.start()
    t_play_audio.start()
    #t_signal_process.start()
    return stop_flag


if __name__ == "__main__":
    main()

