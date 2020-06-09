import pyaudio
import numpy as np
import random
from array import array
import mido




##  FUnctional wavefiles
## How can I make it time synchronous?  multithreaded?


volume = 0.5     # range [0.0, 1.0]
fs = 44100       # sampling rate, Hz, must be integer
duration = 0.55   # in seconds, may be float

def distort(X):
    y=np.array([1.0 if x >= 0.0 else -1.0 for x in X])
    return y


def filter(x,d):
    y=x
    N=len(y)
    ii=0
    for i in range(int(d),N):
        y[i]=x[i]-0.8*x[ii]
        ii+=1
    return y

p = pyaudio.PyAudio()

stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=fs,
                input=True,
                output=True)

correct=0
wrong=0
#mapper={' ':110,'a':440,'s':660,'d':880,'f':1220,'g':1660}
mapper={' ':0,'c1':32,'c2':65,'c3':130, 'c4':261,'c5':523,'d5':587,'e5':659,'f5':698,'g5':784,'a5':880,'b5':988,'g7':3136,'g6':1568}

seq1=[['c1'],['c2'],['c1'],['c3'],['c1'],['c4'],['c3'],['c2'],['c3'],['c1'],['c2'],['c1']]
#seq2=[['  '],['c3'],['c4'],['e5'],['c2'],['c4'],['e5'],['g5'],['c2']]
distort_seq=0

index=0
for msg in mido.open_input():
    print(msg)
    z=[]
    z=seq1[index%len(seq1)]
    #z=z+seq2[index%len(seq2)]
    print(z)
    if z==[]:
        z=['a','z']
    samples=None
    for x in z:
        if x in mapper:
            f3=mapper[x]
        else:
            f3=random.random()*880
        if samples is None:
            samples = distort(np.sin(2*np.pi*np.arange(fs*duration)*f3/fs)).astype(np.float32)
            #samples = np.sin(2*np.pi*np.arange(fs*duration)*f3/fs).astype(np.float32)
        else:
            samples += distort(np.sin(2*np.pi*np.arange(fs*duration)*f3/fs)).astype(np.float32)

        stream.write(volume*filter(samples,100.0*np.sin(2*np.pi*index/100.0)))
        #stream.write(volume*samples)
    index+=1

