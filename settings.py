import telnetlib
import atexit

############ PORT
global ip
ip="169.254.1.200"
global port1 #main Arduino, running GRBL
global port2
port1=2000
port2=3000
global grbl
global tn2
grbl=telnetlib.Telnet(ip, port1)
tn2=telnetlib.Telnet(ip, port2)

global max_x
global max_y
max_x = 385
max_y = 405
global AllowEmigration #allow for exceeding programmed limits
AllowEmigration = False

global Xcurent
global Ycurent
Xcurent=0.0
Ycurent=0.0

global stopflag #set when user presses stop button,
#refer/scan threads check it in loop,
#if set they reset it and return
stopflag = False
global antistart #prevents from executing move thread when other is running
antistart = False

global pilot_buttons
pilot_buttons = 'F'

def exit_handler():
    print("Disconnecting...")
    grbl.close()
    tn2.close()
atexit.register(exit_handler)


def init():
    print('Init...')




