import settings
from settings import *
#from settings import grbl
#from settings import tn2
import time

def resetGrbl():
    print('Resetting GRBL...')
    grbl.write(b'\x18') #ctrl-x - soft-reset
    print('RECEIVED: '+str(grbl.read_until(b'\r\n', timeout=10)))
    grbl.write(b"$\n")
    print('RECEIVED: '+str(grbl.read_until(b'\r\n', timeout=10)))
    grbl.write(b"G21\n") #milimeters
    print('RECEIVED: '+str(grbl.read_until(b'\r\n', timeout=10)))
    line = '$X'
    print('Sending line: '+line)
    grbl.write(line.encode('utf-8') + b'\n')
    print('RECEIVED: '+str(grbl.read_until(b'ok\r\n', timeout=10)))
    time.sleep(2)

if __name__ == "__main__":
    resetGrbl()
    grbl.close()