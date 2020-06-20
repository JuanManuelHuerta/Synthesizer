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
#from numpy import *
import threading,time, queue
import itertools
import time

##  This synthesizer will have n voices each run by an oscilator launched on its own thread.
## Synthesize 1 segment of note, do not apply envelopes and do not partition

#https://people.csail.mit.edu/hubert/pyaudio/docs/

#Globals
fs = 44100           # sampling rate, Hz, must be integer
delay = 0.1*fs  # seconds * fs
my_queue=[]
waves = {}
phase={}
frequency={}
DO_SIGNAL = False
active_notes = set()
this_active_notes = set()
sample_duration = 1.00
chunk_duration = 0.10
samples_per_chunk = int(fs * chunk_duration)

def init_soundwaves():
    volume = 0.3     # 
    duration = sample_duration   # in seconds, may be float
    decay=-0.000001
    
    for i in range(22,122):
        note_mapper = (2.0**((i-69)/12.0))*440.0
        gain=np.exp(decay*np.arange(fs*duration))
        time=np.arange(fs*duration)+np.random.normal(0.0,0.0001*note_mapper,fs)
        #kernel=np.sin(2*np.pi*time*note_mapper/fs)
        #kernel=np.sign(np.sin(2*np.pi*np.arange(fs*duration)*note_mapper/fs))
        kernel=signal.sawtooth(2*np.pi*time*note_mapper/fs)
        samples = (volume* kernel ).astype(np.float32)
        #frequency[i]=int(fs/2.0*np.pi*note_mapper)
        frequency[i]=int(100.0*fs/note_mapper)
        print(frequency[i],note_mapper)
        waves[i]=samples
        phase[i]=0
    waves[0]=0.0*waves[23]


def signal_processor(data):
    for i in range(len(data)-20):
        data[i+20-1] = data[i+20-1] + 0.5 * data[i]
    return data

def play_audio(Qout):
    p = pyaudio.PyAudio()
    # open output stream
    ostream = p.open(format=pyaudio.paFloat32, channels=1, rate=int(fs),output=True,output_device_index=None)
    while True:
        data = None
        if len(active_notes)>0:
            data = synth_engine(Qout)
        if data is not None:
            ostream.write( data.astype(np.float32).tostring() )
        else:
            time.sleep(chunk_duration)
            

#    try:
#            #data = my_queue.pop(0)
#        if len(active_notes) > 0:
#            Qout.put(synth_engine())
#        if not Queue.empty() :
#            data = Qout.get()
#            ostream.write( data.astype(np.float32).tostring() )
#    except:
#        pass

    ostream.close()

def execute_note(note_value,Qout,event_type):
    if event_type == 'note_on':
        active_notes.add(note_value)
    if event_type == 'note_off':
        active_notes.remove(note_value)
        phase[note_value]=0
    print("Active notes:", active_notes)


def synth_engine(Qout):
    this_active_notes = active_notes.copy()
    data = None
    if len(this_active_notes)  > 0:
        for note in this_active_notes:
            print(" synthesis of  ", note, " in ", this_active_notes)
            print(phase[note])
            if data is None:
                data = waves[note][phase[note]:phase[note]+samples_per_chunk+1]
            else:
                data += waves[note][phase[note]:phase[note]+samples_per_chunk+1]
            phase[note]=(phase[note]+samples_per_chunk)%frequency[note]
                
    else:
        print("Dealing with empty buffer")
    return data


def listen_midi(Qout):
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

