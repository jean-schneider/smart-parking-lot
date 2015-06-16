#
#### Parking ####
#
# Start ; 05/2015
#

import tkinter as tk
from tkinter import ttk
import time
from random import randint
import serial

############ Fonctions ############


def SetValues():
    global nb_empty_slots
    setvalues = tk.Tk()
    setvalues.wm_title("Parking User Interface - Reinitialization")
    
    av_slots = tk.Entry(setvalues)

    nbp = ttk.Button(setvalues, text="Set: Nb of available slots", command=lambda: SetAvSlots(av_slots))
    av_slots.pack()
    nbp.pack()
    setvalues.mainloop()


def SetAvSlots(av_slots):
    global nb_empty_slots
    global nb_total_slots
    try:
        if int(av_slots.get()) <= nb_total_slots and int(av_slots.get()) >= 0:
            nb_empty_slots = int(av_slots.get())
            GiveOrders(0,0)
            
    except:
        print('ERROR : Invalid value inserted')

def IsValid(var):
    a = False

    length = len(var)
        
    if length > 3:
        a = True

    return a
        
        
def listen_serialport():
    global ser, new_data, action, rcvd_data
    rc = ""
    
    rcvd_data = "0000"
    temp = [None]*4
    data_in = ""
    global nb_empty_slots, start_mark, end_mark, data_in
    rcv_in_prog = False
    
    if ser.inWaiting() > 0 and new_data == False:

        action = True
        j = 0
        rcvd_data = ""
        while ser.inWaiting() > 0 and new_data == False:
            rc = str(ser.read())
            if rcv_in_prog == True:
                if rc != end_mark:
                    if j >=1:
                        try:
                            temp[j-1] = rc[2]
                            rcvd_data += str(temp[j-1])
                        except:
                            break
                else:
                    rcv_in_prog = False
                    new_data = True
            elif rc == start_mark:
                rcv_in_prog = True
            j +=1
    ser.flushInput()
    data_in = rcvd_data
    if IsValid(data_in):
        GiveOrders(0,0)
    else:
        print("ERROR: got invalid data_in value")

def open_gate(gate_nb):
    global gate, action, ot
    ot[gate_nb] = time.time()
    action = True
    if gate_nb == 0:
        GiveOrders("1","0")
    elif gate_nb == 1:
        GiveOrders("0","1")


def close_gate(gate_nb):

    global ot, gate
    if ot[gate_nb]-time.time() <= -5:
        gate[gate_nb] = 'CLOSE'
        ot[gate_nb] = 999999999999

    


def readcontent_open(file_lines, gate):
    
    x1 = file_lines[gate][2]
    x2 = file_lines[gate][3]
    y1 = file_lines[gate][4]
    y2 = file_lines[gate][5]
    
    return x1, x2, y1, y2

def readcontent_close(file_lines, gate):
    
    x1 = file_lines[gate][9]
    x2 = file_lines[gate][10]
    y1 = file_lines[gate][11]
    y2 = file_lines[gate][12]

    return x1, x2, y1, y2

def GiveOrders(overwrite1, overwrite2):
    global data_out, gate, action, nb_empty_slots, new_data, nb_total_slots, ot, data_in
    temp = [None]*5
    data_out = "<"
    temp[0] = str(start_mark)
    temp[4] = str(end_mark)
    new_data = False

    if action == True:
        if nb_empty_slots <= 0:
            temp[3] = "1"

        if data_in[0] == "1" and temp[3] !="1":
            temp[1] = "1"
            nb_empty_slots -=1
            gate[0] = 'OPEN'
            ot[0] = time.time()
            
        if data_in[1] == "1":
            if nb_empty_slots < nb_total_slots:
                nb_empty_slots += 1
                temp[2] = "1"
                gate[1] = 'OPEN'
                ot[1] = time.time()
                temp[3] = "0"

            else:
                temp[2] = "0"
                
 

        if overwrite1 == "1":
            gate[0] = 'OPEN'
            if nb_empty_slots > 0:
                nb_empty_slots -=1
            temp[1] = "1"

        if overwrite2 == "1":
            gate[1] = 'OPEN'
            if nb_empty_slots < nb_total_slots:
                nb_empty_slots += 1
            temp[2] = "1"

       
        for loop in range (3):
            if temp[loop+1] == None:
                temp[loop+1] = 0
            data_out += str(temp[loop+1])
       
        data_out += ">"
        action = False

        ser.write(data_out.encode())
        


def update_can():
    global gate, ot
    global nb_empty_slots
    for loop in range (NB_GATE):
        can.delete(gate_draw[loop])
    #Limit of park
    can.create_line(10,10, 990, 10, width=3)
    can.create_line(990,10, 990, 590, width=3)
    can.create_line(10,590, 990, 590, width=3)
    can.create_line(10,10, 10, 590, width=3)

    #NbPlaces Slider
    rect_x2 = 200+(nb_empty_slots/nb_total_slots)*700
    can.create_rectangle(200,275,900,325,fill="red", outline='red')
    can.create_rectangle(200,275,rect_x2,325,fill="green", outline='green')
    can.create_text((200+rect_x2)/2, 300, text=nb_empty_slots, fill='white')
    xtext=(900-rect_x2)/2+rect_x2
    can.create_text(xtext, 300, text=nb_total_slots-nb_empty_slots, fill='white')

    for loop in range (len(gate)):
        close_gate(loop)

        if gate[loop] == 'OPEN':

            
            coords[loop] = readcontent_open(file_lines, loop)
            gate_draw[loop] = can.create_line(coords[loop][0], coords[loop][1], coords[loop][2], coords[loop][3], width=3, fill='green')
            
        elif gate[loop] == 'CLOSE':
            
            
            coords[loop] = readcontent_close(file_lines, loop)
            gate_draw[loop] = can.create_line(coords[loop][0], coords[loop][1], coords[loop][2], coords[loop][3], width=3, fill='red')

        else:
            print("ERROR: expected OPEN or CLOSE but got; gate[",loop,"] =",gate[loop] )



    listen_serialport()



    if run == 1:
        wdw.after(1000,update_can)
    
############## Main ################
    
NB_GATE = 2
run = 1
nb_empty_slots = 8
nb_total_slots = 8
gate = [None]*NB_GATE
gate_text = [None]*NB_GATE
gate_draw = [None]*NB_GATE
coords = [None]*NB_GATE
file_lines = [None]*NB_GATE
gate[0] = 'CLOSE'
gate[1] = 'CLOSE'
wdw = tk.Tk()
wdw.wm_title("Parking User Interface")
wdw.geometry("1000x700")
wdw.resizable(width=False, height=False)
start_mark = "b'<'"
end_mark = "b'>'"
new_data = False
rcvd_data = "0000"
action = False
ot = [0,0]

### Init ###

try:
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    
    
except:
    print("INFO: unable to open /dev/ttyACM0. Trying /dev/tty/ACM1")
    try:
        ser = serial.Serial('/dev/ttyACM1', 9600, timeout=1)
    except:
        print("ERROR: unable to find Arduino")
ser_str = str(ser)
print("INFO: connected to ", ser_str[43:55])

#Can
can = tk.Canvas(wdw,width=1000, height=600, bg='ivory')
can.grid(row=3, column=5, rowspan=4)

#Limit of park
can.create_line(10,10, 990, 10, width=3)
can.create_line(990,10, 990, 590, width=3)
can.create_line(10,590, 990, 590, width=3)
can.create_line(10,10, 10, 590, width=3)

#NbPlaces Slider
rect_x2 = 200+(nb_empty_slots/nb_total_slots)*700
can.create_rectangle(200,275,900,325,fill="red", outline='red')
can.create_rectangle(200,275,rect_x2,325,fill="green", outline='green')
can.create_text((200+rect_x2)/2, 300, text=nb_empty_slots, fill='white')
xtext=(900-rect_x2)/2+rect_x2
can.create_text(xtext, 300, text=nb_total_slots-nb_empty_slots, fill='white')

for loop in range (len(gate)):
    
    try :
        gate_text[loop] = open('gate_' + str(loop) + '.txt', 'r')
        file_lines[loop] = gate_text[loop].readlines()

    except:
        print("ERROR: file", 'gate_' + str(loop) + '.txt', 'does not exist')
  
    if gate[loop] == 'OPEN':
        
        coords[loop] = readcontent_open(file_lines, loop)
        gate_draw[loop] = can.create_line(coords[loop][0], coords[loop][1], coords[loop][2], coords[loop][3], width=3, fill='green')

    elif gate[loop] == 'CLOSE':
        
        coords[loop] = readcontent_close(file_lines, loop)
        gate_draw[loop] = can.create_line(coords[loop][0], coords[loop][1], coords[loop][2], coords[loop][3], width=3, fill='red')

    else:
        print("ERROR: expected OPEN or CLOSE but got; gate[",loop,"] =",gate[loop] )


#ReInit button
reinit = ttk.Button(wdw, text="Reinitialize", command=SetValues)
reinit.grid(row=10, column=5)

info = ttk.Label(wdw, foreground='green', text=("Connected to " + ser_str[43:55] + ",   Baudrate : " + ser_str[67:71]))
info.grid(row=0, column=5)

#Gate commands
open_0 = ttk.Button(wdw, text="Open", command=lambda: open_gate(0))
open_1 = ttk.Button(wdw, text="Open", command=lambda: open_gate(1))

open_0.grid(row=3, column=0)
open_1.grid(row=5, column=0)

update_can()
wdw.mainloop()




