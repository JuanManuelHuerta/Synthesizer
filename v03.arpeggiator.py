

import pyaudio
import numpy as np
import random
from array import array
import mido
import threading
import time


tapper_off = 20000

# https://docs.python.org/3/library/threading.html

volume = 0.5     # range [0.0, 1.0]
fs = 44100       # sampling rate, Hz, must be integer
duration = 0.75   # in seconds, may be float
chunk = int(fs/2)
bpm = 120
signature = 4                # beats per minute / beats per measure

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
                output=True,
                frames_per_buffer = chunk)



index=0

'''
print( "recording...")
frames = [] 
for i in range(0, int(fs / chunk * 3.0)):
    data = stream.read(chunk)
    frames.append(data)
print( "finished recording")
 '''
 
def arpeggiator_sequencer(active_notes):
    current_time = time.time()
    while 1:
        num_notes = len(active_notes)
        if num_notes > 0:
            spacing = (signature * (60.0/bpm))/num_notes
        else:
            spacing = 0.1
        current_buffer =  list(sorted(active_notes))
        while len(current_buffer)>0:
            this_note = current_buffer.pop(0)
            z=threading.Thread( target = play_note, args=(this_note,))
            z.start()
            time.sleep(spacing)
            
        
        

def arpeggiator_listener(active_notes):
    for msg in mido.open_input():
        print(msg)
        if msg.type == 'note_on':
            active_notes.add(msg.note)
            print(active_notes)
            play_note(msg.note)
        if msg.type == 'note_off':
            try:
                active_notes.remove(msg.note)
                print(active_notes)
            except:
                continue

# Create two threads as follows
active_notes=set()
try:
    
   x = threading.Thread(target =  arpeggiator_listener , args =( active_notes, ))
   y = threading.Thread(target =  arpeggiator_sequencer , args = (active_notes, ))

   x.start()
   y.start()
except:
   print ("Error: unable to start thread")

while 1:
   pass
        

