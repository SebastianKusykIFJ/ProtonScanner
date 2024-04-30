import settings
from settings import * #telnet objects must be imported, otherwise they are closed after settings.py is done
from configrbl import *
from go import *
import telnetlib
import atexit
from resetGrbl import resetGrbl
from refer import refer
from tkinter import *
from tkinter import ttk
import time
from threading import Thread
from unidos import *

settings.init()
if offline==False:
    resetGrbl()

def receiveArdu2():
    global tn2_last_ans
    print("THREAD RECEIVING FEEDBACK DATA STARTED")
    while True:
        l=tn2.read_until(b'\n')
        tn2_last_ans = l
        #print('odebrano od Arduino 2:'+str(l))
        if str(l)[2:4]=='01':
            #print('V')
            label_X_ok.config(bg="#00FF00")
            label_X_diff.config(bg="#550")
            label_X_error.config(bg="#500")
        elif str(l)[2:4]=='11':
            #print("...")
            label_X_ok.config(bg="#050")
            label_X_diff.config(bg="#FFFF00")
            label_X_error.config(bg="#500")
        elif str(l)[2:4]=='00' or str(l)[2:4]=='10':
            #print("X")
            label_X_ok.config(bg="#050")
            label_X_diff.config(bg="#550")
            label_X_error.config(bg="#FF0000")
        
        if str(l)[4:6]=='01':
            #print('V')
            label_Y_ok.config(bg="#00FF00")
            label_Y_diff.config(bg="#550")
            label_Y_error.config(bg="#500")
        elif str(l)[4:6]=='11':
            #print("...")
            label_Y_ok.config(bg="#050")
            label_Y_diff.config(bg="#FFFF00")
            label_Y_error.config(bg="#500")
        elif str(l)[4:6]=='00' or str(l)[4:6]=='10':
            #print("X")
            label_Y_ok.config(bg="#050")
            label_Y_diff.config(bg="#550")
            label_Y_error.config(bg="#FF0000")

        if str(l)[6]=='1':
            label_X_0.config(bg='#48C')
        else:
            label_X_0.config(bg='#123')
        if str(l)[7]=='1':
            label_Y_0.config(bg='#48C')
        else:
            label_Y_0.config(bg='#123')

        global pilot_buttons
        pilot_buttons = str(l)[9]
        #print('Pilot buttons state: '+pilot_buttons)

def jog_pilot():
    print('Thread using pilot buttons started')
    global pilot_buttons
    pilot_buttons_prev = pilot_buttons

    speed_min = 100
    jog_speed = speed_min
    speed_max = 1000
    acc = 50
    step_min = 1
    jog_step = step_min
    step_max = 10
    step_incr = 1

    global Xcurent
    global Ycurent
    global max_x
    global max_y
    global AllowEmigration

    while True:
        #set speed to minimum if direction changed:
        if (pilot_buttons != pilot_buttons_prev):
            jog_speed = speed_min
            jog_step = step_min
            pilot_buttons_prev = pilot_buttons
        #now pilot_buttons_prev contains the current value - I will use it to prevent changes during loop turn
        if pilot_buttons_prev != 'F':#0b1111
            
            print('Waiting for idle:')
            while True:
                line='?'
                print('SEND: '+line)
                grbl.write(line.encode('utf-8'))
                ans=grbl.read_until(b'\r\n', timeout=1)
                print('RECEIVED: '+str(ans))
                if str(ans).find('<Idle|')!=-1:
                    break
                else:
                    time.sleep(0.5)
            #print('Current parameters: speed '+str(jog_speed)+', step '+str(jog_step))
            line = ''
            x_new = Xcurent
            y_new = Ycurent
            #if pilot_buttons_prev == '7':#0b0111up
            if pilot_buttons_prev == 'B':#0b1011up
                y_new = y_new-jog_step
                line='$J=G91'+'Y'+str(jog_step)+'F'+str(jog_speed)
            #elif pilot_buttons_prev == '3':#0b0011up-right
            elif pilot_buttons_prev == 'A':#0b1010up-right
                y_new = y_new-jog_step
                x_new = x_new + jog_step
                line='$J=G91'+'X-'+str(jog_step)+'Y'+str(jog_step)+'F'+str(jog_speed)
            #elif pilot_buttons_prev == 'B':#0b1011right
            elif pilot_buttons_prev == 'E':#0b1110right
                x_new = x_new + jog_step
                line='$J=G91'+'X-'+str(jog_step)+'F'+str(jog_speed)
            #elif pilot_buttons_prev == '9':#0b1001right-down
            elif pilot_buttons_prev == '6':#0b0110right-down
                x_new = x_new + jog_step
                y_new = y_new+jog_step
                line='$J=G91'+'X-'+str(jog_step)+'Y-'+str(jog_step)+'F'+str(jog_speed)
            #elif pilot_buttons_prev == 'D':#0b1101down
            elif pilot_buttons_prev == '7':#0b0111down
                y_new = y_new+jog_step
                line='$J=G91'+'Y-'+str(jog_step)+'F'+str(jog_speed)
            #elif pilot_buttons_prev == 'C':#0b1100down-left
            elif pilot_buttons_prev == '5':#0b0101down-left
                y_new = y_new+jog_step
                x_new = x_new - jog_step
                line='$J=G91'+'X'+str(jog_step)+'Y-'+str(jog_step)+'F'+str(jog_speed)
            #elif pilot_buttons_prev == 'E':#0b1110left
            elif pilot_buttons_prev == 'D':#0b1101left
                x_new = x_new - jog_step
                line='$J=G91'+'X'+str(jog_step)+'F'+str(jog_speed)
            elif pilot_buttons_prev == '9':#0b1001left-up
                x_new = x_new - jog_step
                y_new = y_new-jog_step
                line='$J=G91'+'X'+str(jog_step)+'Y'+str(jog_step)+'F'+str(jog_speed)
            else:
                print('ERROR: Opposite directions chosen on pilot buttons!')
                time.sleep(0.5)
            #check if won't exceed programmed limits:
            #if ((x_new>0 and x_new<max_x and y_new>0 and y_new<max_y) or AllowEmigration==True) and line!='':
            if (x_new>=0 and x_new<=max_x and y_new>=0 and y_new<=max_y) or AllowEmigration==True:
                if x_new<=0 or x_new>=max_x or y_new<=0 and y_new>=max_y:
                    print('WARNING! Going to move beyond programmed limits!')
                #SEND COMMAND:
                print('Going to run jog, emptying buffer:')
                print('RECEIVED: '+str(grbl.read_very_eager()))
                print('SEND: '+line)
                grbl.write(line.encode('utf-8') + b'\n')
                ans=grbl.read_until(b'ok\r\n', timeout=1)
                print('RECEIVED: '+str(ans))
                ans=grbl.read_until(b'ok\r\n', timeout=1)
                print('RECEIVED: '+str(ans))
                Xcurent = x_new
                Ycurent = y_new
                upd8curentpos()
                #accelerate:
                if jog_speed<speed_max:
                    jog_speed = jog_speed + acc
                if jog_step<step_max:
                    jog_step = jog_step + step_incr
            else:
                print('Cant jog - would exceed programmed limits')
        else:
            jog_speed = speed_min
            jog_step = step_min
            time.sleep(0.1)#otherwise thread takes too much power - indicators change with delay
        '''
        if pilot_buttons_prev != pilot_buttons:
            print('Pilot buttons state: '+pilot_buttons)
            pilot_buttons_prev = pilot_buttons
        '''

def upd8curentpos():
    global Xcurent
    global Ycurent
    newtext = "CURRENT POSITION: X"+str(Xcurent)+" Y"+str(Ycurent)
    print('Updating current position display with text '+newtext)
    label_curentpos.config(text=newtext)

global refer_worx
refer_worx = False
global thread_refer
global go_worx
go_worx = False
global thread_go
global scan_worx
scan_worx = False
global thread_scan
global ScanWithUnidos
ScanWithUnidos1=False
ScanWithUnidos2=False

def refer_function():
    button_refer.config(text='REFER\nWORKS...', fg='#9F0')
    global refer_worx
    global Xcurent
    global Ycurent
    refer()
    Xcurent=0.0
    Ycurent=0.0
    upd8curentpos()
    refer_worx=False
    button_refer.config(text='REFER', fg='black')
    
def refer_button_click():
    global thread_refer
    global refer_worx
    if refer_worx==False:
        refer_worx=True
        thread_refer = Thread(target=refer_function)
        window.after_idle(thread_refer.start)
    else:
        #window.after_idle(thread_refer.stop)
        refer_worx=False

def zero_wout_refer():
    print('Going to run zero_wout_refer, emptying buffer:')
    print('RECEIVED: '+str(grbl.read_very_eager()))
    print('\r\nSetting home position in GRBL...')
    line_set0 = 'G92 X0 Y0 Z0'
    print('setting 0 coords in Grbl:')
    print('SEND: '+line_set0)
    grbl.write(line_set0.encode('utf-8') + b'\n')
    print('RECEIVED: '+str(grbl.read_until(b'ok\r\n')))
    Xcurent=0.0
    Ycurent=0.0
    upd8curentpos()

def go_function():
    global go_worx
    button_goto_init.config(text='GO\nWORKS...')
    global AllowEmigration
    global Xcurent
    global Ycurent
    global max_x
    global max_y
    set_x = entry_initpos_X.get()
    set_y = entry_initpos_Y.get()
    '''
    print('Going to run go_button_click, emptying buffer:')
    print('RECEIVED: '+str(grbl.read_very_eager()))
    if float(set_x)>max_x or float(set_y)>max_y:
        if AllowEmigration==False:
            print('Too big coordinates!')
            return
        else:
            print('WARNING! GOING TO START MOVING BEYOND PROGRAMMED LIMITS!')
    #for line in ['$X','G0 X-'+entry_initpos_X.get()+' Y-'+entry_initpos_Y.get()+' F'+entry_speed.get()]:
    for line in ['$X','G0 X-'+set_x+' Y-'+set_y]:
        print('sending line '+line)
        grbl.write(line.encode('utf-8') + b'\n')
        ans=grbl.read_until(b'ok\r\n')
        print('RECEIVED: '+str(ans))
    ans=grbl.read_until(b'ok\r\n',timeout=2)
    print('RECEIVED: '+str(ans))
    '''
    if go(set_x, set_y) == 0:
        Xcurent=float(set_x)
        Ycurent=float(set_y)
        print('Current X:'+str(Xcurent)+' Y:'+str(Ycurent))
        upd8curentpos()
    go_worx = False
    button_goto_init.config(text='GO')

def go_button_click():
    global thread_go
    global go_worx
    if go_worx==False:
        go_worx=True
        thread_go = Thread(target=go_function)
        window.after_idle(thread_go.start)
    else:
        #window.after_idle(thread_go.stop)
        go_worx=False

def jog(jog_dir):
    global Xcurent
    global Ycurent
    global max_x
    global max_y
    global AllowEmigration
    print('Going to run jog, emptying buffer:')
    print('RECEIVED: '+str(grbl.read_very_eager()))
    print('Jog '+jog_dir+' button pressed')
    jog_step=10
    jog_speed=1000
    x_new = Xcurent
    y_new = Ycurent
    if jog_dir=='up':
        y_new = y_new-jog_step
        line='$J=G91'+'Y'+str(jog_step)+'F'+str(jog_speed)
    elif jog_dir=='down':
        y_new = y_new+jog_step
        line='$J=G91'+'Y-'+str(jog_step)+'F'+str(jog_speed)
    elif jog_dir=='left':
        x_new = x_new - jog_step
        line='$J=G91'+'X'+str(jog_step)+'F'+str(jog_speed)
    elif jog_dir=='right':
        x_new = x_new + jog_step
        line='$J=G91'+'X-'+str(jog_step)+'F'+str(jog_speed)
    else:
        print('Error: Undefined direction for jog command!')
        return
    if x_new<0 or x_new>max_x or y_new<0 or y_new>max_y:
        if AllowEmigration==False:
            print('Cant jog - coords limit would be exceeded')
            return
        else:
            print('WARNING! GOING TO START MOVING BEYOND PROGRAMMED LIMITS!')
    
    print('SEND: '+line)
    grbl.write(line.encode('utf-8') + b'\n')
    ans=grbl.read_until(b'ok\r\n')
    print('RECEIVED: '+str(ans))
    Xcurent = x_new
    Ycurent = y_new
    upd8curentpos()

def scan_function():
    global ScanWithUnidos1
    global ScanWithUnidos2

    global scan_worx
    scan_worx = True
    button_start.config(text='SCAN\nWORKS...')
    global Xcurent
    global Ycurent
    global max_x
    global max_y
    global AllowEmigration

    lines_nr = int(entry_lines_nr.get())
    X_points = int(entry_X_points.get())
    X_points_distance = int(entry_X_points_distance.get())
    lines_dist= int(entry_lines_dist.get())
    halt = float(entry_haltime.get())
    #TODO: teksty tez powinny byc wczytane zeby ktos nie zmienil w trakcie bez zatrzymywania, wgl moze byc blokada pol tekstowych
    if (Xcurent+X_points*X_points_distance)>max_x or (Ycurent+lines_nr*lines_dist)>max_y:
        #JEDZIE W DOL
        if AllowEmigration==False:
            print('Cant scan - coords limit would be exceeded')
            return
        else:
            print('WARNING! GOING TO START MOVING BEYOND PROGRAMMED LIMITS!')
    line = '$X'
    print('SEND: '+line)
    grbl.write(line.encode('utf-8') + b'\n')
    ans=grbl.read_until(b'ok\r\n')
    print('RECEIVED: '+str(ans))
    print('GOING TO RUN SCAN, EMPTYING BUFFER\nRECEIVED:'+str(grbl.read_very_eager()))
    if ScanWithUnidos1:
        print('Resetting Unidos1...')
        print(u_reset(u_port1))
        print('Starting Unidos1...')
        print(u_start(u_port1))
    if ScanWithUnidos2:
        print('Resetting Unidos2...')
        print(u_reset(u_port2))
        print('Starting Unidos2...')
        print(u_start(u_port2))
    file = open('log.txt','a')

    for scanline in range(lines_nr):
        if scan_worx==False:
            break
        print('scan line '+str(scanline))
        for scanpoint in range(X_points):
            if scan_worx==False:
                break
            print('- point '+str(scanpoint))
            file.write('\r\nLine '+str(scanline)+', point '+str(scanpoint))
            if scanline%2==0:
                #line='G1 X-'+entry_X_points_distance.get()+' F'+entry_speed.get()
                line='$J=G91X-'+entry_X_points_distance.get()+'F'+entry_speed.get()
                Xcurent = Xcurent+X_points_distance
            else:
                #line='G1 X'+entry_X_points_distance.get()+' F'+entry_speed.get()
                line='$J=G91X'+entry_X_points_distance.get()+'F'+entry_speed.get()
                Xcurent = Xcurent-X_points_distance
            print('SEND: '+line)
            grbl.write(line.encode('utf-8') + b'\n')
            ans=grbl.read_until(b'ok\r\n')
            print('RECEIVED: '+str(ans))

            if ScanWithUnidos1 or ScanWithUnidos2 or float(entry_haltime.get())>0:
                while True:
                    line='?'
                    print('SEND: '+line)
                    grbl.write(line.encode('utf-8'))
                    ans=grbl.read_until(b'\r\n')
                    print('RECEIVED: '+str(ans))
                    if str(ans).find('<Idle|')!=-1:
                        file.write(' '+str(ans)+' ')
                        break
                    else:
                        time.sleep(0.5)
                if ScanWithUnidos1:
                    print('Reading Unidos1 value...')
                    u1_ans = u_meas(u_port1)
                    print(u1_ans)
                    file.write(u1_ans)
                if ScanWithUnidos2:
                    print('Reading Unidos2 value...')
                    u2_ans = u_meas(u_port2)
                    print(u2_ans)
                    file.write(u2_ans)
                time.sleep(float(entry_haltime.get()))
            
            '''if halt>0:
                line = 'G4 P'+entry_haltime.get()
                print('sending line: '+line)
                grbl.write(line.encode('utf-8')+b'\n')
                ans=grbl.read_until(b'\r\n')
                print('RECEIVED: '+str(ans))'''
            #ans=grbl.read_until(b'ok\r\n')
            #print('RECEIVED: '+str(ans))
            upd8curentpos()
        #line='G1 Y'+entry_lines_dist.get()+' F'+entry_speed.get()
        line='$J=G91Y-'+entry_lines_dist.get()+'F'+entry_speed.get()
        Ycurent=Ycurent+int(entry_lines_dist.get())
        print('SEND: '+line)
        grbl.write(line.encode('utf-8') + b'\n')
        ans=grbl.read_until(b'ok\r\n')
        print('RECEIVED: '+str(ans))
        upd8curentpos()
    if ScanWithUnidos1:
        print('Holding Unidos1...')
        print(u_hold(u_port1))
        print('Disconnecting Unidos1...')
        print(u_close(u_port1))
    if ScanWithUnidos2:
        print('Holding Unidos2...')
        print(u_hold(u_port2))
        print('Disconnecting Unidos2...')
        print(u_close(u_port2))
    file.close()
    scan_worx = False
    button_start.config(text='START')

def scan_button_click():
    global thread_scan
    global scan_worx
    if scan_worx==False:
        scan_worx=True
        thread_scan = Thread(target=scan_function)
        window.after_idle(thread_scan.start)

def stop_button_click():
    global scan_worx
    scan_worx=False
    #TODO: ADD OTHER FLAG - ONE MAY START OTHER SCAN THREAD WHEN NOT FINISHED!!!

############################# CHECK GRBL CONFIGURATION ########################
if offline==False:
    time.sleep(0.1)
    configrbl()

############################# PREPARE GUI #####################################
window = Tk()
window.title("XY SCANNER")
window.config(bg="skyblue")
window.geometry("1024x648")
############## REFER
frame_refer = Frame(window, width=200, height=100)
frame_refer.grid(row=0, column=0, padx=5, pady=5)
button_refer = Button(master=frame_refer, height = 3, width=10, text='REFER', bg='blue', fg='black', font=(100), command=refer_button_click)
button_refer.grid(row=0, column=0, padx=5, pady=5)
button_close = Button(master=frame_refer, height = 3, width=10, text='CLOSE', bg='black', fg='orange', font=(100))#, command=GRBLclose)
button_close.grid(row=0, column=1, padx=5, pady=5)
button_close = Button(master=frame_refer, height = 3, width=10, text='RESET', bg='red', fg='green', font=(150), command=resetGrbl)
button_close.grid(row=1, column=0, padx=5, pady=5)
button_zero_wout_refer = Button(master=frame_refer, height=3, width=10, text='SET ZERO', bg='black', fg='blue', font=(100), command=zero_wout_refer)
button_zero_wout_refer.grid(row=1, column=1, padx=5, pady=5)

########## INITIAL POSITION
frame_initpos = Frame(window, width=200, height=500)
frame_initpos.grid(row=1, column=0, padx=5, pady=5)
label_initpos_title = Label(master=frame_initpos, text="INITIAL POSITION:")
label_initpos_title.grid(row=0, column=0, padx=5, pady=5)
label_initpos_X = Label(master=frame_initpos, text="X")
label_initpos_X.grid(row=1, column=0, padx=5, pady=5)
entry_initpos_X = Entry(master=frame_initpos)
entry_initpos_X.grid(row=1, column=1, padx=2, pady=5)
label_initpos_Y = Label(master=frame_initpos, text="Y")
label_initpos_Y.grid(row=2, column=0, padx=2, pady=5)
entry_initpos_Y = Entry(master=frame_initpos)
entry_initpos_Y.grid(row=2, column=1, padx=0, pady=5)
button_goto_init = Button(master=frame_initpos, text="GO", height = 3, width=10, bg='green', fg='black', font=(100), command=go_button_click)
button_goto_init.grid(row=3, column=0, padx=5, pady=5)


##################### MOVE PARAMETERS
frame_move_params = Frame(window, width=200, height=500)
frame_move_params.grid(row=0,column=1, padx=5, pady=5)
label_move_params_title = Label(master=frame_move_params, text="MOVE PARAMETERS:")
label_move_params_title.grid(row=0, column=0, padx=5, pady=5)
#X points number
label_X_points = Label(master=frame_move_params, text="X POINTS NUMBER")
label_X_points.grid(row=1, column=0, padx=5, pady=5)
entry_X_points = Entry(master=frame_move_params)
entry_X_points.grid(row=1, column=1, padx=5, pady=5)
#X points distance
label_X_points_distance = Label(master=frame_move_params, text="X POINTS DISTANCE")
label_X_points_distance.grid(row=2, column=0, padx=5, pady=5)
entry_X_points_distance = Entry(master=frame_move_params)
entry_X_points_distance.grid(row=2, column=1, padx=5, pady=5)
#lines number
label_lines_nr = Label(master=frame_move_params, text="LINES NUMBER")
label_lines_nr.grid(row=3, column=0, padx=5, pady=5)
entry_lines_nr = Entry(master=frame_move_params)
entry_lines_nr.grid(row=3, column=1, padx=5, pady=5)
#lines distance
label_lines_dist = Label(master=frame_move_params, text="LINES DISTANCE") 
label_lines_dist.grid(row=4, column=0, padx=5, pady=5)
entry_lines_dist = Entry(master=frame_move_params)
entry_lines_dist.grid(row=4, column=1, padx=5, pady=5)
#halt time in point
label_haltime = Label(master=frame_move_params, text="HALT TIME IN POINT") 
label_haltime.grid(row=5, column=0, padx=5, pady=5)
entry_haltime = Entry(master=frame_move_params)
entry_haltime.grid(row=5, column=1, padx=5, pady=5)
#speed
label_speed = Label(master=frame_move_params, text="SPEED") 
label_speed.grid(row=6, column=0, padx=5, pady=5)
entry_speed = Entry(master=frame_move_params)
entry_speed.grid(row=6, column=1, padx=5, pady=5)
#scan with Unidos
checkedSwU1 = IntVar()
checkedSwU2 = IntVar()
def ToggleSwU1():
    global ScanWithUnidos1
    if checkedSwU1.get()==0:
        ScanWithUnidos1=False
    elif checkedSwU1.get()==1:
        ScanWithUnidos1=True
def ToggleSwU2():
    global ScanWithUnidos2
    if checkedSwU2.get()==0:
        ScanWithUnidos2=False
    elif checkedSwU2.get()==1:
        ScanWithUnidos2=True
checkbox_scan_with_unidos1 = Checkbutton(master= frame_move_params, text='Scan with Unidos1', command=ToggleSwU1, variable=checkedSwU1, offvalue=False, onvalue=True)
checkbox_scan_with_unidos1.grid(row=7, column=0, padx=5, pady=5)
checkbox_scan_with_unidos2 = Checkbutton(master= frame_move_params, text='Scan with Unidos2', command=ToggleSwU2, variable=checkedSwU2, offvalue=False, onvalue=True)
checkbox_scan_with_unidos2.grid(row=7, column=1, padx=5, pady=5)

#buttons
button_start = Button(master=frame_move_params, text="START", height = 3, width=10, bg='green', fg='black', font=(100), command=scan_button_click)
button_start.grid(row=8, column=0, padx=5, pady=5)
button_pause= Button(master=frame_move_params, text="PAUSE", height = 3, width=10, bg='orange', fg='black', font=(100))
button_pause.grid(row=8, column=1, padx=5, pady=5)
button_stop= Button(master=frame_move_params, text="STOP", height = 3, width=10, bg='red', fg='black', font=(100), command=stop_button_click)
button_stop.grid(row=8, column=2, padx=5, pady=5)

############################## JOG BUTTONS
frame_jog = Frame(window, width=200, height=200)
frame_jog.grid(row=1, column=1, padx=5, pady=5)
button_jog_up = Button(master=frame_jog, text='^', height=2, width=2, bg='red', command=lambda:jog('up'))
button_jog_up.grid(row=0, column=1)
button_jog_left = Button(master=frame_jog, text='<', height=2, width=2, bg='red', command=lambda:jog('left'))
button_jog_left.grid(row=1, column=0)
button_jog_right = Button(master=frame_jog, text='>', height=2, width=2, bg='red', command=lambda:jog('right'))
button_jog_right.grid(row=1, column=2)
button_jog_down = Button(master=frame_jog, text='v', height=2, width=2, bg='red', command=lambda:jog('down'))
button_jog_down.grid(row=2, column=1)

############################## CURRENT POSITION
frame_curentpos = Frame(window, width=200, height=500)
frame_curentpos.grid(row=2,column=0, padx=5, pady=5)
label_curentpos = Label(master=frame_curentpos, text="CURRENT POSITION: ", bg="blue", fg="white", font=(200))
label_curentpos.grid(row=0, column=0, padx=5, pady=0)
checkedAE = IntVar()
def ToggleAE():
    global AllowEmigration
    if checkedAE.get()==0:
        AllowEmigration=False
        print('Emigration banned!')
    elif checkedAE.get()==1:
        AllowEmigration=True
        print('Emigration allowed!')
checkbox_alow_emigration = Checkbutton(master=frame_curentpos, text='Allow exceeding programmed limits', command=ToggleAE, variable=checkedAE, offvalue=False, onvalue=True)
checkbox_alow_emigration.grid(row=1, column=0, padx=5, pady=0)

############################# FEEDBACK
frame_feedback = Frame(window, width=200, height=200)
frame_feedback.grid(row=0, column=2, padx=5, pady=5)
label_feedback_title = Label(master=frame_feedback, text="FEEDBACK SIGNALS")
label_feedback_title.grid(row=0, column=0, padx=5, pady=5)
################### FEEDBACK_ENCODERS
label_encoders = Label(master=frame_feedback, text="ENCODERS:")
label_encoders.grid(row=1, column=0, padx=5, pady=5)
################# ENCODERS - X
label_encoders_X = Label(master=frame_feedback, text="X:")
label_encoders_X.grid(row=2, column=0, padx=5, pady=5)
label_X_ok = Label(master=frame_feedback,text="READY",fg="#000",bg="#050")
label_X_ok.grid(row=2, column=1, padx=5, pady=5)
label_X_diff = Label(master=frame_feedback,text="...",fg="#000",bg="#550")
label_X_diff.grid(row=2, column=2, padx=5, pady=5)
label_X_error= Label(master=frame_feedback,text="ERROR",fg="#000",bg="#500")
label_X_error.grid(row=2, column=3, padx=5, pady=5)
label_X_0 = Label(master=frame_feedback, text="0", fg="#000", bg="#123")
label_X_0.grid(row=2, column=4, padx=5, pady=5)
################# ENCODERS - Y
label_encoders_Y = Label(master=frame_feedback, text="Y:")
label_encoders_Y.grid(row=3, column=0, padx=5, pady=5)
label_Y_ok = Label(master=frame_feedback,text="READY",fg="#000",bg="#050")
label_Y_ok.grid(row=3, column=1, padx=5, pady=5)
label_Y_diff = Label(master=frame_feedback,text="...",fg="#000",bg="#550")
label_Y_diff.grid(row=3, column=2, padx=5, pady=5)
label_Y_error= Label(master=frame_feedback,text="ERROR",fg="#000",bg="#500")
label_Y_error.grid(row=3, column=3, padx=5, pady=5)
label_Y_0 = Label(master=frame_feedback, text="0", fg="#000", bg="#123")
label_Y_0.grid(row=3, column=4, padx=5, pady=5)
################ LIMIT SWITCHES
label_limit_switches = Label(master=frame_feedback, text='LIMIT SWITCHES:')
label_limit_switches.grid(row=4, column=0, padx=5, pady=5)

################################## UNIDOS #########################################################
frame_unidos = Frame(window, width=200, height=200)
frame_unidos.grid(row=1, column=2, padx=5, pady=5)
label_unidos = Label(master=frame_unidos, text="UNIDOS")
label_unidos.grid(row=0, column=0, padx=5, pady=0)
button_unidos1 = Button(master=frame_unidos, text='U1', height=2, width=2, bg='green')
button_unidos1.grid(row=1, column=0, padx=5, pady=0)
button_unidos2 = Button(master=frame_unidos, text='U2', height=2, width=2, bg='green')
button_unidos2.grid(row=1, column=1, padx=5, pady=0)
button_unidos2 = Button(master=frame_unidos, text='U1+2', height=2, width=2, bg='green')
button_unidos2.grid(row=1, column=2, padx=5, pady=0)
button_unidosOFF = Button(master=frame_unidos, text='OFF', height=2, width=2, bg='blue')
button_unidosOFF.grid(row=1, column=3, padx=5, pady=0)
label_unidos_filename = Label(master=frame_unidos, text="FILE: ")
label_unidos_filename.grid(row=2, column=0, padx=5, pady=0)
entry_unidos_filename = Entry(master=frame_unidos)
entry_unidos_filename.grid(row=2, column=1, padx=5, pady=0)

button_unidos_start = Button(master=frame_unidos, text='START')
button_unidos_start.grid(row=3, column=0, padx=5, pady=5)
button_unidos_stop = Button(master=frame_unidos, text='STOP')
button_unidos_stop.grid(row=3, column=1, padx=5, pady=5)
button_unidos_reset = Button(master=frame_unidos, text='RESET')
button_unidos_reset.grid(row=3, column=2, padx=5, pady=5)
button_unidos_null = Button(master=frame_unidos, text='NULL')
button_unidos_null.grid(row=3, column=3, padx=5, pady=5)
button_unidos_low = Button(master=frame_unidos, text='LOW')
button_unidos_low.grid(row=3, column=4, padx=5, pady=5)
button_unidos_med = Button(master=frame_unidos, text='MED')
button_unidos_med.grid(row=3, column=5, padx=5, pady=5)
button_unidos_hi = Button(master=frame_unidos, text='HI')
button_unidos_hi.grid(row=3, column=6, padx=5, pady=5)

button_unidos_collect = Button(master=frame_unidos, text='COLLECT DATA')
button_unidos_collect.grid(row=4, column=0, padx=5, pady=5)
button_unidos_pause = Button(master=frame_unidos, text='PAUSE')
button_unidos_pause.grid(row=4, column=1, padx=5, pady=5)
button_unidos_end = Button(master=frame_unidos, text='END')
button_unidos_end.grid(row=4, column=2, padx=5, pady=5)

label_unidos_read1 = Label(master=frame_unidos, text='U1: ')
label_unidos_read1.grid(row=5, column=0, padx=5, pady=5)
label_unidos_read2 = Label(master=frame_unidos, text='U2: ')
label_unidos_read2.grid(row=6, column=0, padx=5, pady=5)
'''

'''
watek=Thread(target=receiveArdu2)
watek2=Thread(target=jog_pilot)
window.update_idletasks() #bez tego okno sie nie pojawia
if offline==False:
    window.after_idle(watek.start)
    window.after_idle(watek2.start)
window.mainloop()
