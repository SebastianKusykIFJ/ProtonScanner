import settings
from settings import grbl
from settings import tn2
from resetGrbl import resetGrbl
import time

def refer():
    tn2.write('0'.encode('utf-8') + b'\n')
    #standard home command - to limit switches release (requires GRBL with XY homing)
    resetGrbl()
    print('Sending home command...')
    grbl.write('$H'.encode('utf-8')+b'\n')
    for i in range(1):
        ans = grbl.read_until(b'ok\r\n')
        print('RECEIVED: '+str(ans))
    #input('Press enter to start encoder homing')
    for i in range(60,1,-1):
        print('Encoder homing starts in '+str(i))
        time.sleep(1)
        
    #going to encoder 0:
    for axis in ['x','y']:
        print('\r\nGoing to encoder 0 for axis '+axis)
        tn2.write(axis.encode('utf-8') + b'\n')
        #if enabling forwarding caused end-stop error, that's our 0 point for some axis
        l=grbl.read_until(b'[MSG:Reset to continue]\r\n', timeout=1)
        print('RECEIVED:'+str(l))
        if(str(l).find('[MSG:Reset to continue]\r\n')!=-1):
            print('Encoder forwarding caused end-stop error for some axis')
            print('Resetting GRBL...')
            resetGrbl()
        if axis=='x':
            line_actual = 'G1 X-10 F50'
        elif axis=='y':
            line_actual = 'G1 Y-10 F50'
        print('Sending line '+line_actual)
        grbl.write(line_actual.encode('utf-8') + b'\n')
        ans = grbl.read_until(b'[MSG:Reset to continue]\r\n', timeout=10)
        print(ans)
        tn2.write('0'.encode('utf-8') + b'\n')
        resetGrbl()
    #reset GRBL and set home position:
    print('\r\nSetting home position in GRBL...')
    line_set0 = 'G92 X0 Y0 Z0'
    print('setting 0 coords in Grbl - sending line '+line_set0)
    grbl.write(line_set0.encode('utf-8') + b'\n')
    print('RECEIVED: '+str(grbl.read_until(b'ok\r\n')))
        
    

if __name__ == "__main__":
    refer()
    input('press enter to close connections')
    grbl.close()
    tn2.close()
    