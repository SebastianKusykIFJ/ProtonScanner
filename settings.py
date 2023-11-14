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

def exit_handler():
    print("Disconnecting...")
    grbl.close()
    tn2.close()
atexit.register(exit_handler)


def init():
    print('Init...')




