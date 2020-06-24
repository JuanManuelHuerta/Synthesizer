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


#https://people.csail.mit.edu/hubert/pyaudio/docs/

#Globals
fs = 44100           # sampling rate, Hz, must be integer
chunks_per_second = 10
delay = 0.1*fs  # seconds * fs
my_queue=[]
waves = {}
DO_SIGNAL = False

def init_soundwaves():
    volume = 1.0     # range [0.0, 1.0]
    duration = 1.0   # in seconds, may be float
    decay=-0.000001
    for i in range(22,122):
        note_mapper = (2.0**((i-69)/12.0))*440.0
        gain=np.exp(decay*np.arange(fs*duration))

        #kernel=np.sign(np.sin(2*np.pi*np.arange(fs*duration)*note_mapper/fs))
        #kernel=np.sign(np.sin(2*np.pi*np.arange(fs*duration)*note_mapper/fs))
        #kernel=signal.sawtooth(2*np.pi*np.arange(fs*duration)*note_mapper/fs)
        kernel=np.sin((2*np.pi*np.arange(fs*duration)*note_mapper)/fs+ np.sin(2*np.pi*np.arange(fs*duration)*note_mapper*0.314/fs))
        

        samples = (volume*(1.0-gain)*gain* kernel ).astype(np.float32)

        print(len(samples))
        waves[i]=np.split(samples,int(chunks_per_second*duration))


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
            data = Qout.get()
        except:
            continue
        if data=="EOT" :
            continue

        if DO_SIGNAL is True:
            data = signal_processor(data)

        try:
            ostream.write( data.astype(np.float32).tostring() )
        except:
            continue
    ostream.close()

def execute_note(note_value,Qout):
    list_a = waves[note_value]
    list_b = []
    list_c = []
    while Qout.empty() is False:
        try:
            data = Qout.get()
            list_b.append(data)
        except:
            continue
    for item in itertools.zip_longest(list_a,list_b):
        print("zipping")
        if item[0] is None:
            Qout.put(item[1])
        elif item[1] is None:
            Qout.put(item[0])
        elif item[0] is not None and item[1] is not None:
            Qout.put(item[0]+item[1])

    #for chunk in list_a:
    #    Qout.put(chunk)
    print("len of my queue",len(my_queue))

def listen_midi(Qout):
    print("Im here")
    for msg in mido.open_input():
        print(msg)
        if msg.type == 'note_on':
            execute_note(msg.note,Qout)
    

def main():
    init_soundwaves()

    # create an input output FIFO queues
    Qin = queue.Queue()
    Qout = queue.Queue()
    Qdata = queue.Queue()

    # initialize stop_flag
    stop_flag = threading.Event()

    # initialize threads
    t_listen_midi = threading.Thread(target=listen_midi,args = (Qout,))
    #t_put_data = threading.Thread(target = put_data,   args = (Qout, ptrain, stop_flag  ))
    t_play_audio = threading.Thread(target = play_audio, args = (Qout,))
    #t_signal_process = threading.Thread(target = signal_process, args = ( Qin, Qdata, pulse_a, Nseg, Nplot, fs, maxdist, temperature, functions, stop_flag))
    # start threads
    t_listen_midi.start()
    #t_put_data.start()
    t_play_audio.start()
    #t_signal_process.start()
    return stop_flag


if __name__ == "__main__":
    main()

