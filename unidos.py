import serial
#from settings import u_port1, u_port2

u_port1 = '\\.\COM3'
u_port2 = '\\.\COM4'

def u_command(command, port):
    ser = serial.Serial()
    ser.baudrate = 9600
    ser.timeout = 3
    ser.port = port
    ser.open()
    #ser.write(b'V\r\n')
    #ser.write(b'G\r\n')
    #ser.write(b'T1\r\n')
    ser.write(command)
    l = ser.readline()
    ser.close()
    return str(l)

def u_start(port):
    return u_command(b'G\r\n', port)

def u_reset(port):
    return u_command(b'K\r\n', port)

def u_meas(port):
    return u_command(b'V\r\n', port)

def u_close(port):
    return u_command(b'T1\r\n', port)

def u_hold(port):
    return u_command(b'H\r\n', port)

def u_ran(port, range):
    if range==0:
        return u_command(b'R0\r\n', port)
    elif range==1:
        return u_command(b'R1\r\n', port)
    elif range==2:
        return u_command(b'R2\r\n', port)


if __name__ == "__main__":
    #print(u_command(b'G\r\n', u_port2))
    print(u_reset(u_port2))
    print(u_ran(u_port2, 1))
    print(u_start(u_port2))
    import time
    for i in range(10):
        print(u_meas(u_port2))
        time.sleep(0.5)
    print(u_hold(u_port2))
    u_close(u_port2)