from threading import Thread
import matplotlib.pyplot as plt
from socket import *
import numpy as np
import sounddevice as sd

def send():
    global sdata
    stream = sd.InputStream(samplerate=Rate,
                    channels=Channels,
                    dtype=Format)
    stream.start()
    while running:
        sdata = stream.read(Chunk)[0]
        data = sdata.tobytes()
        sock.sendto(data, Saddr)
    stream.close()

def recv():
    global rdata
    stream = sd.OutputStream(samplerate=Rate,
                             channels=Channels,
                             dtype=Format)
    stream.start()
    while running:
        data, addr = sock.recvfrom(Chunk * 2)
        if addr == Saddr:
            rdata = np.frombuffer(data, dtype=Format)
            stream.write(rdata)
    stream.close()

def plot():
    global sdata, rdata
    fig = plt.figure()
    axs = fig.add_subplot(211)
    axr = fig.add_subplot(212)

    axs.set_xlim(0,Chunk); axs.set_ylim(-2**15,2**15)
    axr.set_xlim(0,Chunk); axr.set_ylim(-2**15,2**15)
    
    x = np.arange(Chunk,dtype=Format)
    y = np.zeros((Chunk,),dtype=Format)

    sline, = axs.plot(x,y,'b-')
    rline, = axr.plot(x,y,'r-')

    fig.show()
    while running:
        sline.set_ydata(sdata)
        rline.set_ydata(rdata)
        fig.canvas.draw()
        fig.canvas.flush_events()    

IP = input('Client IP : ')
Port = int(input('Client Port : '))

sock = socket(AF_INET, SOCK_DGRAM)
sock.bind((IP, Port))

SIP = input('Server IP : ')
SPort = int(input('Server Port : '))
Saddr = (SIP, SPort)

Rate = 22050
Channels = 1
Format = np.int16
Chunk = 1024
running = True

sdata = np.zeros((Chunk,), dtype=Format)
rdata = np.zeros((Chunk,), dtype=Format)

tsend = Thread(target=send, name='thread-send')
trecv = Thread(target=recv, name='thread-recv')
tplot = Thread(target=plot, name='thread-plot')

tsend.start()
trecv.start()
tplot.start()

while running:
    if input() == 'e':
        running = False

sock.close()
