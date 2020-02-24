from threading import Thread
from socket import *
import numpy as np
import sounddevice as sd
import logging
import time

def get():
    global data
    logging.info('thread-get Started.')
        
    while running:
        rdata, Caddr = sock.recvfrom(2*Chunk)
        rdata = np.frombuffer(rdata, dtype=Format)

        if Caddr in users:
            rdata = rdata.reshape((Chunk,1))
            indx = users.index(Caddr)
            data[indx] = rdata

        else:
            rdata = rdata.reshape((1,Chunk,1))
            users.append(Caddr)
            indx = users.index(Caddr)
            ndata = np.zeros((len(data)+1,Chunk,1), dtype=Format)
            ndata[:-1] = data
            data = ndata
            
            logging.info('New user joined: %s', Caddr)
            logging.debug('All users: %s', users)

            tuser = Thread(target=user, args=(indx,), name='thread-user%d'%indx)
            tuser.start()
            
    logging.info('thread-get Closed.')

def user(indx):
    Caddr = users[indx]
    logging.info('thread-user%d Started',indx)
    
    while running:
        try:
            w = np.ones(len(users))
            w[indx] = 0
            sdata = np.average(data, axis=0, weights=w)
        except:
            sdata = np.zeros((Chunk,1), dtype=Format)
            
        sdata = sdata.astype(Format)
        sdata = sdata.tobytes()
        sock.sendto(sdata, Caddr)
        time.sleep(Chunk/Rate * 1)
        
    logging.info('thread-user%d Closed.', indx)

logging.basicConfig(format='[%(asctime)s] %(levelname)s : %(message)s',
                    filename='TelfSer.log',
                    filemode='w',
                    level=logging.DEBUG)
logging.info('Server Started.')

SIP = input('Server IP : ')
SPort = int(input('Server Port : '))

sock = socket(AF_INET, SOCK_DGRAM)
sock.bind((SIP, SPort))

logging.info('Socket Created.')

Rate = 22050
Channels = 1
Format = np.int16
Chunk = 1024
running = True

logging.debug('Rate, Chunk = %s', (Rate, Chunk))

data = np.zeros((0,Chunk,1), dtype=Format)
users = []

tget = Thread(target=get, name='thread-get')
tget.start()

while running:
    if input() == 'e':
        running = False
        
sock.close()
logging.info('Socket Closed.')
logging.info('Server Closed.')
