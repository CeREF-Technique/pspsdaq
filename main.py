from threading import Timer, Event
import tkinter as tk  # graphical interface
from tkinter import ttk
import serial  # install pySerial lib first in cmd : pip install pyserial
import sys
import glob
#import matplotlib.pyplot as plt # install pySerial lib first in cmd : pip install matplotlib
import time
from exportData import Export
import logging
import PS
__author__ = 'Maxim Dumortier'

"""
 Feb. - April 2017
 CERISIC, Mons, BELGIUM

The Goal of this code is to talk with a Power supply in serial mode (COM port) and to ask with polling the different kind of measures.
At the end, it will write a Excell file with all the values (absolute time, relative time, Voltage, current, power)
"""

# Global vars : 
ICON_PATH = "./res/PS2DAq.ico" # Path to the PS2Daq icon
flagStartStop = False # Flag for the Start/Stop button

#
# FUNCTIONS :
#

def connect_serial_port():
    """
    Opens a new serial connection if the port name is right
    :return: nothing
    """
    if portChoice.get():
        logging.info("Connection with %s", portChoice.get())
        # some variables must be global (to be used in disconnection function)
        global ps # power supply
        global thread_stop
        
        ps = PS.classDict[psChoice.get()](portChoice.get()) # Instantiate the choosen Power Supply 
        
        connectButton.config(state="disabled")  # change the stat of the connect button to disabled
        disconnectButton.config(state="normal")  # change the stat of the disconnect button to enabled
        portComboBox.config(state="disabled")
        startStopButton.config(state="normal")
        deviceID.set("Serial number : " + ps.getID()) # Show the Device ID
        logging.info("Connected to de device " + deviceID.get())
        
        thread_stop = Event()  # defines a new thread stop for every connection to serial port
        

def disconnect_serial_port():
    """
    Close the current serial connection
    :return: nothing
    """
    if ps.ser:
        logging.info("Disconnection from " + ps.ser.name)
        thread_stop.set()  # stop reading Thread
        try:  # if the buttons are always available, put them into the initial state
            connectButton.config(state="normal")
            disconnectButton.config(state="disabled")
            portComboBox.config(state="normal")
            startStopButton.config(state="disabled")
        except:
            pass
        ps.ser.close()
        thread_stop.clear()
        logging.info("disconnected from serial port")


def goodbye():
    """
    Function used at the exit to close the thread and the connection on window closing
    :return: nothing
    """
    try:
        thread_stop.set()  # stop reading Thread
    except NameError:  # case of the names are not defined yet
        pass

    try:
        if ps.ser:
            ps.ser.close()
            # disconnectPortSerial()  # disconnect port
    except NameError:  # case of the names are not defined yet
        pass
    # destroy the window
    root.destroy()
    logging.info("Window was closed brutally")



def start_mesure():
    """
    Start measuring
    """
    global flagStartStop
    global mesure_number
    global exp
    
    if len(sampleEntry.get()) != 0: # First check that there's something in the textbox
        sampleEntry.set(sampleEntry.get().replace(",","."))
        
        if isfloat(sampleEntry.get()): # Second, check if the entry is a float
            sampleTime = float(sampleEntry.get())
            # Convert the sampletime setted into seconds
            if timeUnitCombobox.get() == "minute(s)":
                sampleTime *= 60
            elif timeUnitCombobox.get() == "hour(s)":
                sampleTime *= 3600
            # Else it is seconds, so no need to convert
                
            if sampleTime > 0: # Third, check that the entry is a positive time (no signification of a negative time)
                
                if flagStartStop: # The User clicked on "STOP"
                    thread_stop.set() # Stop the read thread
                    startStopButton.config(text="Start")
                    flagStartStop = False
                    sampleTimeEntryBox.config(state="normal") # lock the entry and time unit during measurements
                    timeUnitCombobox.config(state="normal")
                    logging.info("Stopped measurement")
                else: # The User clicked on "START"
                    beginTime = time.time()
                    next_call = time.time()
                    fileName = "PowerSupplyData-" + time.strftime("%Y%m%d-%H%M%S")
                    mesure_number = 1 # Initialize de measure number
                    header = ["Measure Number", "Local time", "Relative time (s)", "Voltage (V)", "Current (A)", "Power (W)"] # Header
                    exp = Export(fileName, type="xlsx", header=header) #Initialize the export class (Excel and CSV)
                    
                    if thread_stop.isSet(): # Reset the stop Event
                        thread_stop.clear()
                        
                    read(sampleTime, beginTime, next_call, thread_stop) # Launch the read thread
                        
                    startStopButton.config(text="Stop")
                    flagStartStop = True

                    sampleTimeEntryBox.config(state="disabled")
                    timeUnitCombobox.config(state="disabled")
                    
                    logging.info("Started measurement with %d sec. as sample time", sampleTime)
                    
            elif sampleTime == 0:
                # TODO : make a case that take samples as fast as possible
                sampleEntry.set("1")
            else:
                sampleEntry.set("1")
        else:
            sampleEntry.set("")
            

    
def read(interval, beginTime, next_call, stop_event):
    """
    Read function, reads continuously the data from serial port
    :param interval: sample time
    :param beginTime: begin time
    :param next_call: next call time
    :param stop_event: An event to stop the thread
    :return: nothing
    """

    global mesure_number
    global exp

    # FIRST ask for the measurements :
    if ps.ser:
        currentTime = time.time()
        volt,current,power = ps.getMeasures()
        voltValue.set("%.2f" % volt)
        currValue.set("%.2f" % current)
        powValue.set("%.2f" % power)
        
        deltaTime = '%.1f' % round(currentTime-beginTime, 1)
        
        exp.writerow([mesure_number, time.strftime("%Y/%m/%d-%H:%M:%S"), float(deltaTime), float(voltValue.get()), float(currValue.get()), float(powValue.get())])
        mesure_number += 1
    else:
        logging.error("Read Broke down")


    if not stop_event.is_set():
        next_call += interval
        Timer(next_call - time.time(),read,[interval, beginTime, next_call, stop_event]).start()
             


def isfloat(strin):
    """
    Function which says if a value can be converted into a float or not
    :param strin: Value to be tested
    :return: True if the parameter can be converted into a float, False otherwise
    """
    try:
        strin = strin.replace(",",".")
        float(strin)
        return True
    except ValueError:
        return False


#
# MAIN routine :
#

logging.basicConfig(filename='PS2DAq.log', format='%(levelname)s\t%(asctime)s\t%(message)s', level=logging.DEBUG)
logging.info("Application Starded")

root = tk.Tk()  # create a new window
root.geometry("800x600")  # set the size of the window
root.title("Python Serial Power Supply Data Acquisition - (PS)²DAq")  # set a title to the window
tk.Label(root, text="Software to read and monitor data of a power supply through USB-serial port")\
    .grid(column=0, row=0, columnspan=4, padx=5, pady=5)  # little explanation of what the window can do
root.iconbitmap(default=ICON_PATH) # set the beatiful icon on the app


# Get the list of all the available ports in a  system (win, linux, cygwin or darwin)
if sys.platform.startswith('win'):
    ports = ['COM%s' % (i + 1) for i in range(256)]
elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
    # this excludes your current terminal "/dev/tty"
    ports = glob.glob('/dev/tty[A-Za-z]*')
elif sys.platform.startswith('darwin'):
    ports = glob.glob('/dev/tty.*')
else:
    logging.exception(EnvironmentError('Unsupported platform'))
    raise EnvironmentError('Unsupported platform')


# Test each available port to check if there is some response
result = []
for port in ports:
    try:
        s = serial.Serial(port)
        s.close()
        result.append(port)
    except (OSError, serial.SerialException):
        pass


connectButton = tk.Button(root, text="Connect...", command=connect_serial_port)
connectButton.grid(column=1, row=1, padx=5, pady=5)

# Put the result in a comboBox to allow the  user to choice the desired one
portChoice = tk.StringVar()
portComboBox = ttk.Combobox(root, textvariable=portChoice)
if not result:
    result.append("No Serial Port Available")
    connectButton.config(state="disabled")
    logging.info("No Serial Port Available")
else:
    logging.debug("Found Serialports : %s", result)
    
portComboBox["values"] = result  # Set the list of the serial ports
if result:
    portComboBox.current(0)  # default select the first on of the list
portComboBox.grid(column=0,row=1, padx=5, pady=5)  # set the combobox at the right place
# Connection Button

disconnectButton = tk.Button(root, text="Disconnect...", state="disabled", command=disconnect_serial_port)
disconnectButton.grid(column=2, row=1, padx=5, pady=5)
deviceID = tk.StringVar()
deviceID.set("")
tk.Label(root,textvariable=deviceID).grid(column=3, row=1, padx=5, pady=5)


#
# Labels with stringVar, their names and their units
#

tk.Label(root, text="Sample Time").grid(column=0, row=2, padx=5, pady=5)
sampleEntry = tk.StringVar()
sampleTimeEntryBox = tk.Entry(root, textvariable=sampleEntry, relief=tk.SOLID)
sampleTimeEntryBox.grid(column=1, row=2, padx=5, pady=5, sticky=tk.N + tk.E + tk.S + tk.W)
sampleEntry.set("2")

psChoice = tk.StringVar()
psCombobox = ttk.Combobox(root, textvariable=psChoice)
psCombobox["values"] = PS.__all__
psCombobox.grid(column=4, row=1, padx=5, pady=5)

timeUnitChoice = tk.StringVar()
timeUnitCombobox = ttk.Combobox(root, textvariable=timeUnitChoice)
timeUnitCombobox["values"] = ["second(s)","minute(s)","hour(s)"]
timeUnitChoice.set("minute(s)")
timeUnitCombobox.grid(column=2,row=2, padx=5, pady=5)

startStopButton = tk.Button(root, text="Start", command=start_mesure, state="disabled")
startStopButton.grid(column=3, row=2, padx=5, pady=5)

# Current sensor value
tk.Label(root, text="Voltage").grid(column=0, row=3, padx=5, pady=5)
voltValue = tk.StringVar()
tk.Label(root, textvariable=voltValue, relief=tk.SOLID).grid(column=1, row=3, padx=5, pady=5,
                                                          sticky=tk.N + tk.E + tk.S + tk.W)
voltValue.set("###")
tk.Label(root, text="V").grid(column=2, row=3, padx=5, pady=5)

# Current temperature value
tk.Label(root, text="Current").grid(column=0, row=4, padx=5, pady=5)
currValue = tk.StringVar()
tk.Label(root, textvariable=currValue, relief=tk.SOLID).grid(column=1, row=4, padx=5, pady=5,
                                                          sticky=tk.N + tk.E + tk.S + tk.W)
currValue.set("###")
tk.Label(root, text="A").grid(column=2, row=4, padx=5, pady=5)

# Target value
tk.Label(root, text="Power").grid(column=0, row=5, padx=5, pady=5)
powValue = tk.StringVar()
tk.Label(root, textvariable=powValue, relief=tk.SOLID).grid(column=1, row=5, padx=5, pady=5,
                                                          sticky=tk.N + tk.E + tk.S + tk.W)
powValue.set("###")
tk.Label(root, text="W").grid(column=2, row=5, padx=5, pady=5)



# Close thread and serial port before exit :
root.protocol("WM_DELETE_WINDOW", goodbye)

# Show main window
root.mainloop()







