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

settings.init()
resetGrbl()

def receiveArdu2():
    print("THREAD RECEIVING FEEDBACK DATA STARTED")
    while True:
        l=tn2.read_until(b'\n')
        print('odebrano od Arduino 2:'+str(l))
        if str(l)[2:4]=='01':
            print('V')
            label_X_ok.config(bg="#00FF00")
            label_X_diff.config(bg="#550")
            label_X_error.config(bg="#500")
        elif str(l)[2:4]=='11':
            print("...")
            label_X_ok.config(bg="#050")
            label_X_diff.config(bg="#FFFF00")
            label_X_error.config(bg="#500")
        elif str(l)[2:4]=='00' or str(l)[2:4]=='10':
            print("X")
            label_X_ok.config(bg="#050")
            label_X_diff.config(bg="#550")
            label_X_error.config(bg="#FF0000")
        
        if str(l)[4:6]=='01':
            print('V')
            label_Y_ok.config(bg="#00FF00")
            label_Y_diff.config(bg="#550")
            label_Y_error.config(bg="#500")
        elif str(l)[4:6]=='11':
            print("...")
            label_Y_ok.config(bg="#050")
            label_Y_diff.config(bg="#FFFF00")
            label_Y_error.config(bg="#500")
        elif str(l)[4:6]=='00' or str(l)[4:6]=='10':
            print("X")
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
    jog_step = 1
    global Xcurent
    global Ycurent
    global max_x
    global max_y
    global AllowEmigration

    while True:
        if pilot_buttons != 'F':#0b1111
            line = ''
            x_new = Xcurent
            y_new = Ycurent
            if pilot_buttons == '7':#0b0111up
                y_new = y_new-jog_step
                line='$J=G91'+'Y'+str(jog_step)+'F'+str(jog_speed)
            elif pilot_buttons == '3':#0b0011up-right
                y_new = y_new-jog_step
                x_new = x_new + jog_step
                line='$J=G91'+'X-'+str(jog_step)+'Y'+str(jog_step)+'F'+str(jog_speed)
            elif pilot_buttons == 'B':#0b1011right
                x_new = x_new + jog_step
                line='$J=G91'+'X-'+str(jog_step)+'F'+str(jog_speed)
            elif pilot_buttons == '9':#0b1001right-down
                x_new = x_new + jog_step
                y_new = y_new+jog_step
                line='$J=G91'+'X-'+str(jog_step)+'Y-'+str(jog_step)+'F'+str(jog_speed)
            elif pilot_buttons == 'D':#0b1101down
                y_new = y_new+jog_step
                line='$J=G91'+'Y-'+str(jog_step)+'F'+str(jog_speed)
            elif pilot_buttons == 'C':#0b1100down-left
                y_new = y_new+jog_step
                x_new = x_new - jog_step
                line='$J=G91'+'X'+str(jog_step)+'Y-'+str(jog_step)+'F'+str(jog_speed)
            elif pilot_buttons == 'E':#0b1110left
                x_new = x_new - jog_step
                line='$J=G91'+'X'+str(jog_step)+'F'+str(jog_speed)
            elif pilot_buttons == '6':#0b0110left-up
                x_new = x_new - jog_step
                y_new = y_new-jog_step
                line='$J=G91'+'X'+str(jog_step)+'Y'+str(jog_step)+'F'+str(jog_speed)
            else:
                print('ERROR: Opposite directions chosen on pilot buttons!')
                time.sleep(0.5)
            #check if won't exceed programmed limits:
            #if ((x_new>0 and x_new<max_x and y_new>0 and y_new<max_y) or AllowEmigration==True) and line!='':
            if (x_new>0 and x_new<max_x and y_new>0 and y_new<max_y) or AllowEmigration==True:
                if x_new<0 or x_new>max_x or y_new<0 and y_new>max_y:
                    print('WARNING! Going to move beyond programmed limits!')
                #SEND COMMAND:
                print('Going to run jog, emptying buffer:')
                print('RECEIVED: '+str(grbl.read_very_eager()))
                print('sending line '+line)
                grbl.write(line.encode('utf-8') + b'\n')
                ans=grbl.read_until(b'ok\r\n')
                print('RECEIVED: '+str(ans))
                ans=grbl.read_until(b'ok\r\n', timeout=1)
                print('RECEIVED: '+str(ans))
                Xcurent = x_new
                Ycurent = y_new
                upd8curentpos()
            else:
                print('Cant jog - would exceed programmed limits')
        else:
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


#def check_prog_limits(set_x, set_y):


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
    print('setting 0 coords in Grbl - sending line '+line_set0)
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
    
    print('sending line '+line)
    grbl.write(line.encode('utf-8') + b'\n')
    ans=grbl.read_until(b'ok\r\n')
    print('RECEIVED: '+str(ans))
    Xcurent = x_new
    Ycurent = y_new
    upd8curentpos()

def scan_function():
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
    #TODO: teksty tez powinny byc wczytane zeby ktos nie zmienil w trakcie bez zatrzymywania, wgl moze byc blokada pol tekstowych
    if  (Xcurent+X_points*X_points_distance)>max_x or (Ycurent+lines_nr*lines_dist)>max_y:
        #JEDZIE W DOL
        if AllowEmigration==False:
            print('Cant scan - coords limit would be exceeded')
            return
        else:
            print('WARNING! GOING TO START MOVING BEYOND PROGRAMMED LIMITS!')
    
    for scanline in range(lines_nr):
        print('scan line '+str(scanline))
        for scanpoint in range(X_points):
            print('- point '+str(scanpoint))
            if scanline%2==0:
                #line='G1 X-'+entry_X_points_distance.get()+' F'+entry_speed.get()
                line='$J=G91X-'+entry_X_points_distance.get()+'F'+entry_speed.get()
                Xcurent = Xcurent+X_points_distance
            else:
                #line='G1 X'+entry_X_points_distance.get()+' F'+entry_speed.get()
                line='$J=G91X'+entry_X_points_distance.get()+'F'+entry_speed.get()
                Xcurent = Xcurent-X_points_distance
            print('sending line '+line)
            grbl.write(line.encode('utf-8') + b'\n')
            ans=grbl.read_until(b'ok\r\n')
            print('RECEIVED: '+str(ans))
            upd8curentpos()
        #line='G1 Y'+entry_lines_dist.get()+' F'+entry_speed.get()
        line='$J=G91Y-'+entry_lines_dist.get()+'F'+entry_speed.get()
        Ycurent=Ycurent+int(entry_lines_dist.get())
        print('sending line '+line)
        grbl.write(line.encode('utf-8') + b'\n')
        ans=grbl.read_until(b'ok\r\n')
        print('RECEIVED: '+str(ans))
        upd8curentpos()
    scan_worx = False
    button_start.config(text='START')

def scan_button_click():
    global thread_scan
    global scan_worx
    if scan_worx==False:
        scan_worx=True
        thread_scan = Thread(target=scan_function)
        window.after_idle(thread_scan.start)
    else:
        scan_worx=False

############################# CHECK GRBL CONFIGURATION ########################
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
#buttons
button_start = Button(master=frame_move_params, text="START", height = 3, width=10, bg='green', fg='black', font=(100), command=scan_button_click)
button_start.grid(row=7, column=0, padx=5, pady=5)
button_pause= Button(master=frame_move_params, text="PAUSE", height = 3, width=10, bg='orange', fg='black', font=(100))
button_pause.grid(row=7, column=1, padx=5, pady=5)
button_stop= Button(master=frame_move_params, text="STOP", height = 3, width=10, bg='red', fg='black', font=(100))
button_stop.grid(row=7, column=2, padx=5, pady=5)

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
label_curentpos.grid(row=0, column=0, padx=5, pady=5)
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
checkbox_alow_emigration.grid(row=1, column=0, padx=5, pady=5)

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
'''

'''
watek=Thread(target=receiveArdu2)
watek2=Thread(target=jog_pilot)
window.update_idletasks() #bez tego okno sie nie pojawia
window.after_idle(watek.start)
window.after_idle(watek2.start)
window.mainloop()
