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
import itertools


##  This synthesizer will have n voices each run by an oscilator launched on its own thread.
## Synthesize 1 segment of note, do not apply envelopes and do not partition

#https://people.csail.mit.edu/hubert/pyaudio/docs/

#Globals
fs = 44100           # sampling rate, Hz, must be integer
chunks_per_second = 1
delay = 0.1*fs  # seconds * fs
my_queue=[]
waves = {}
DO_SIGNAL = False
active_notes = set()
this_active_notes = set()


def init_soundwaves():
    volume = 0.3     # 
    duration = 0.05   # in seconds, may be float
    decay=-0.000001
    for i in range(22,122):
        note_mapper = (2.0**((i-69)/12.0))*440.0
        gain=np.exp(decay*np.arange(fs*duration))
        #kernel=np.sign(np.sin(2*np.pi*np.arange(fs*duration)*note_mapper/fs))
        #kernel=np.sign(np.sin(2*np.pi*np.arange(fs*duration)*note_mapper/fs))
        kernel=signal.sawtooth(2*np.pi*np.arange(fs*duration)*note_mapper/fs)
        samples = (volume* kernel ).astype(np.float32)
        waves[i]=samples
    waves[0]=0.0*waves[23]


def signal_processor(data):
    for i in range(len(data)-20):
        data[i+20-1] = data[i+20-1] + 0.5 * data[i]
    return data

def play_audio(Qout):
    p = pyaudio.PyAudio()
    # open output stream
    ostream = p.open(format=pyaudio.paFloat32, channels=1, rate=int(fs),output=True,output_device_index=None)
    # play audio

            
    while ( 1 ):
        try:

            #data = my_queue.pop(0)
            Qout.put(synth_engine())
            data = Qout.get()
            print("Im here")
            ostream.write( data.astype(np.float32).tostring() )
        except:
            continue

    ostream.close()

def execute_note(note_value,Qout,event_type):
    if event_type == 'note_on':
        active_notes.add(note_value)
    if event_type == 'note_off':
        active_notes.remove(note_value)
    print("Active notes:", active_notes)


def synth_engine(Qout):
    print(" and here...")
    this_active_notes = active_notes.copy()
    if len(this_active_notes)  > 0:
        data = None
        for note in this_active_notes:
            print(" synthesis of  ", note, " in ", this_active_notes)
            if data is None:
                data = waves[note]
            else:
                data += waves[note]
        return data
    else:
        print("Dealing with empty buffer")


def listen_midi(Qout):
    print("Im here")
    for msg in mido.open_input():
        print(msg)
        if msg.type == 'note_on':
            execute_note(msg.note,Qout,'note_on')
        if msg.type == 'note_off':
            execute_note(msg.note,Qout,'note_off')
    

def main():
    init_soundwaves()

    # create an input output FIFO queues
    Qin = queue.Queue()
    Qout = queue.Queue()
    Qdata = queue.Queue()

    # initialize stop_flag
    stop_flag = threading.Event()


    t_listen_midi = threading.Thread(target=listen_midi,args = (Qout,))
    t_play_audio = threading.Thread(target = play_audio, args = (Qout,))
    #t_synth_engine = threading.Thread(target = synth_engine, args = (Qout,))
    #t_signal_process = threading.Thread(target = signal_process, args = ( Qin, Qdata, pulse_a, Nseg, Nplot, fs, maxdist, temperature, functions, stop_flag))


    t_listen_midi.start()
    #t_synth_engine.start()
    t_play_audio.start()


    return stop_flag


if __name__ == "__main__":
    main()

