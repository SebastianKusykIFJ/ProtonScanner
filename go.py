import settings
from settings import *

def go(set_x, set_y):
    global AllowEmigration
    global Xcurent
    global Ycurent
    global max_x
    global max_y

    print('Going to run go, emptying buffer:')
    print('RECEIVED: '+str(grbl.read_very_eager()))

    if float(set_x)>max_x or float(set_y)>max_y:
        if AllowEmigration==False:
            print('Too big coordinates!')
            return 1
        else:
            print('WARNING! GOING TO START MOVING BEYOND PROGRAMMED LIMITS!')

    for line in ['$X','G0 X-'+set_x+' Y-'+set_y]:
        print('sending line '+line)
        grbl.write(line.encode('utf-8') + b'\n')
        ans=grbl.read_until(b'ok\r\n')
        print('RECEIVED: '+str(ans))
    ans=grbl.read_until(b'ok\r\n',timeout=2)
    print('RECEIVED: '+str(ans))
    Xcurent=float(set_x)
    Ycurent=float(set_y)
    print('Current X:'+str(Xcurent)+' Y:'+str(Ycurent))

    return 0

if __name__=='__main__':
    set_x = input('Type dest. X: ')
    set_y = input('Type dest. Y')
    if go(set_x, set_y) == 0:
        print('Moved successfully')
    else:
        print('ERROR!!!')