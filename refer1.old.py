import settings
from settings import grbl
from settings import tn2
from resetGrbl import resetGrbl

def refer():
    for axis in ['x','y']:
        print('home axis '+axis+'...\r\n')
        resetGrbl()
        
        if axis=='x':
            line_actual = 'G1 X10000 Y0 F100'
        elif axis=='y':
            line_actual = 'G1 X0 Y-10000 F100'
        print(line_actual)
        grbl.write(line_actual.encode('utf-8') + b'\n')
        ans = grbl.read_until(b'[MSG:Reset to continue]\r\n')
        print('RECEIVED: '+str(ans))
        ############### END STOP PRESSED #######################
        
        #reset and prepare GRBL again
        resetGrbl()
        
        #move to limit switch release
        if axis=='x':
            line_actual = 'G1 X-10 F50'
        elif axis=='y':
            line_actual = 'G1 Y10 F50'
        print(line_actual)
        grbl.write(line_actual.encode('utf-8') + b'\n')
        ans = grbl.read_until(b'[MSG:Reset to continue]\r\n', timeout=10)
        print('RECEIVED: '+str(ans))
        print('END STOP RELEASED')
        ############## END STOP RELEASED ######################
        resetGrbl()
        #enable forwarding
        #q='1'
        tn2.write('1'.encode('utf-8') + b'\n')
        #if enabling forwarding caused end-stop error, that's our 0 point
        l=grbl.read_until(b'[MSG:Reset to continue]\r\n', timeout=1)
        print('RECEIVED: '+str(l))
        #print('RECEIVED: '+str(grbl.read_all(timeout=1)))
        if(str(l).find('Hard limit')!=-1):
            print('Zero point for axis '+axis+' found at limit release')
        #if it didn't, move till that error
        else:
            print('Limit release for axis '+axis+' reached, going to 0 point...')
            grbl.write(line_actual.encode('utf-8') + b'\n')
            ans = grbl.read_until(b'[MSG:Reset to continue]\r\n', timeout=10)
        print('RECEIVED: '+str(ans))
        #disable forwarding
        #q='0'
        tn2.write('0'.encode('utf-8') + b'\n')
    #reset GRBL and set home position:
    resetGrbl()
    line_set0 = 'G92 X0 Y0 Z0'
    print('setting 0 coords in Grbl - sending line '+line_set0)
    grbl.write(line_set0.encode('utf-8') + b'\n')
    print('RECEIVED: '+str(grbl.read_until(b'ok\r\n')))

if __name__ == "__main__":
    refer()
