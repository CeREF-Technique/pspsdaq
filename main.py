from threading import Timer, Event
import tkinter as tk  # graphical interface
from tkinter import ttk
import serial  # install pySerial lib first in cmd : pip install pyserial
import sys
import glob
#import matplotlib.pyplot as plt # install pySerial lib first in cmd : pip install matplotlib
import time
import logging
import PS
from util.exportData import Export
from util.properties import readProperties, writeProperties

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
properties = {} # dict of all the properties used in this code
file_type="XLSX" # default file type

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

        ps = PS_name_dict[psChoice.get()](portChoice.get()) # Instantiate the choosen Power Supply 
        
        connectButton.config(state="disabled")  # change the stat of the connect button to disabled
        disconnectButton.config(state="normal")  # change the stat of the disconnect button to enabled
        portComboBox.config(state="disabled")
        psCombobox.config(state="disabled")
        startStopButton.config(state="normal")
        deviceID.set("Serial number : " + ps.getID()) # Show the Device ID
        logging.info("Connected to de device " + deviceID.get())
        
        thread_stop = Event()  # defines a new thread stop for every connection to serial port

        def addMeasure(inputDict, rowNbr):
            tk.Label(root, text=inputDict["label"]).grid(column=0, row=rowNbr, padx=5, pady=5)
            #voltValue = tk.StringVar()
            tk.Label(root, textvariable=inputDict["stringVar"], relief=tk.SOLID).grid(column=1, row=rowNbr, padx=5, pady=5,
                                                                  sticky=tk.N + tk.E + tk.S + tk.W)
            inputDict["stringVar"].set("###")
            tk.Label(root, text=inputDict["units"]).grid(column=2, row=rowNbr, padx=5, pady=5)

        startRowNbr = 3
        rowIndex = 0
        for meas in sorted(ps.availableMeasures.keys()):
            if ps.availableMeasures[meas]["used"]: # show only if it's used
                addMeasure(ps.availableMeasures[meas], startRowNbr + rowIndex)
                rowIndex += 1
        

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
            psCombobox.config(state="normal")
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
        # remove some text if it is shown :
        sampleEntry.set(sampleEntry.get().replace("Too short interval : ",""))
        sampleEntry.set(sampleEntry.get().replace(" sec",""))
        # In case the user put a coma :
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
                    menubar.entryconfig("Configure", state="normal")
                    
                    logging.info("Stopped measurement")
                else: # The User clicked on "START"
                    beginTime = time.time()
                    next_call = time.time()
                    fileName = "PowerSupplyData-" + time.strftime("%Y%m%d-%H%M%S")
                    mesure_number = 1 # Initialize de measure number
                    header = ["Measure Number", "Local time", "Relative time (s)"] #, "Voltage (V)", "Current (A)", "Power (W)"] # Header
                    for meas in sorted(ps.availableMeasures.keys()):
                        if ps.availableMeasures[meas]["used"]: # show only if it's used
                            header.append(ps.availableMeasures[meas]["label"] + " (" + ps.availableMeasures[meas]["units"] + ")")
                    exp = Export(fileName, file_type=file_type, header=header) #Initialize the export class (Excel and CSV)
                    
                    if thread_stop.isSet(): # Reset the stop Event
                        thread_stop.clear()
                        
                    read(sampleTime, beginTime, next_call, thread_stop) # Launch the read thread
                        
                    startStopButton.config(text="Stop")
                    flagStartStop = True

                    sampleTimeEntryBox.config(state="disabled")
                    timeUnitCombobox.config(state="disabled")
                    menubar.entryconfig("Configure",state="disabled")
                    
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
        deltaTime = '%.1f' % round(currentTime-beginTime, 1)
        toWrite = [mesure_number, time.strftime("%Y/%m/%d-%H:%M:%S"), float(deltaTime)]
        for meas in sorted(ps.availableMeasures.keys()):
            if ps.availableMeasures[meas]["used"]: # show only if it's used
                ps.availableMeasures[meas]["stringVar"].set(ps.availableMeasures[meas]["format"] % ps.availableMeasures[meas]["method"]())
                
                if "f" in ps.availableMeasures[meas]["format"]: # Float format
                    toWrite.append(float(ps.availableMeasures[meas]["stringVar"].get()))
                elif "s" in ps.availableMeasures[meas]["format"]: # string format
                    toWrite.append(ps.availableMeasures[meas]["stringVar"].get())
                elif "d" in ps.availableMeasures[meas]["format"]: # int format
                    toWrite.append(int(ps.availableMeasures[meas]["stringVar"].get()))
                else:
                    toWrite.append(ps.availableMeasures[meas]["stringVar"].get())
        
        
        exp.writerow(toWrite)
        mesure_number += 1
    else:
        logging.error("Read Broke down")


    if not stop_event.is_set():
        next_call += interval
        if next_call - time.time() <0:
            # this means the polling time is too short,
            # must adjust it to a higher value
            interval -= next_call - time.time()
            sampleEntry.set("Too short interval : " + "%.3f" % interval + " sec")
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

properties = readProperties() # store the properties from the file


root = tk.Tk()  # create a new window
root.geometry(properties["default.windowSize"])  # set the size of the window
root.title("Python Serial Power Supply Data Acquisition - (PS)²DAq")  # set a title to the window
tk.Label(root, text="Software to read and monitor data of a power supply through USB-serial port")\
    .grid(column=0, row=0, columnspan=4, padx=5, pady=5)  # little explanation of what the window can do
root.iconbitmap(default=ICON_PATH) # set the beatiful icon on the app

def getAvailableSerialPorts(cmBox, connBtn):
    """
    Function which list all the available serial ports and put them into a comboBox
    :param cmBox: Combobox in which the values must be set
    :param connBtn: Connection button the funtion changes his state to enabled or disabled if there are some serial ports or not
    :return: nothing
    """
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
        
    if not result:
        result.append("No Serial Port Available")
        connBtn.config(state="disabled")
        logging.info("No Serial Port Available")
    else:
        connBtn.config(state="normal")
        logging.debug("Found Serialports : %s", result)
        
    cmBox["values"] = result  # Set the list of the serial ports
    
    if result:
        cmBox.current(0)  # default select the first on of the list
    
    
# Connection Button
connectButton = tk.Button(root, text="Connect...", command=connect_serial_port)
connectButton.grid(column=1, row=1, padx=5, pady=5)

# Put the result in a comboBox to allow the  user to choice the desired one
portChoice = tk.StringVar()
portComboBox = ttk.Combobox(root, textvariable=portChoice)
getAvailableSerialPorts(portComboBox, connectButton)
portContextMenu = tk.Menu(root, tearoff=0) # create a context menu to be able to refresh the serial ports
portContextMenu.add_command(label="Refrech Ports", command=lambda : getAvailableSerialPorts(portComboBox, connectButton))

def portContextMenuPopup(event):
    if str(portComboBox["state"]) == "normal": # show the context menu only if the combobox is in normal (no refresh when a serial port is open)
        portContextMenu.post(event.x_root, event.y_root)

# attach popup to frame
portComboBox.bind("<Button-3>", portContextMenuPopup)
portComboBox.grid(column=0,row=1, padx=5, pady=5)  # set the combobox at the right place

# Disconnection Button
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
sampleEntry.set(properties["default.timeValue"])

psChoice = tk.StringVar()
psCombobox = ttk.Combobox(root, textvariable=psChoice)

PS_name_dict = {}
for s in PS.__all__:
    PS_name_dict[(PS.classDict[s].name)] = PS.classDict[s]

psCombobox["values"] = list(PS_name_dict.keys())
psChoice.set(properties["default.powerSupply"])
psCombobox.grid(column=4, row=1, padx=5, pady=5)

timeUnitChoice = tk.StringVar()
timeUnitCombobox = ttk.Combobox(root, textvariable=timeUnitChoice)
timeUnitCombobox["values"] = ["second(s)","minute(s)","hour(s)"]
timeUnitChoice.set(properties["default.timeUnit"])
timeUnitCombobox.grid(column=2,row=2, padx=5, pady=5)

startStopButton = tk.Button(root, text="Start", command=start_mesure, state="disabled")
startStopButton.grid(column=3, row=2, padx=5, pady=5)

def hello():
    print("hello")
menubar = tk.Menu(root)

# create a pulldown menu, and add it to the menu bar
filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="Open", command=hello)
filemenu.add_command(label="Save", command=hello)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="File", menu=filemenu)

# create more pulldown menus
configmenu = tk.Menu(menubar, tearoff=0)

def chooseOutputType(choice): # set the file_type to the selected choice
    file_type=choice
    properties["default.file.type"]=choice # TODO : write the data in the file when change occures
    writeProperties(properties)

if "default.file.type" in properties.keys():
    file_type=properties["default.file.type"]
    
configOutputFileMenu = tk.Menu(configmenu, tearoff=0)
v = tk.StringVar()
for key in sorted(Export.availableExport().keys()): # set the available possibilities into the output file type menu and select the default one
    val = Export.availableExport()[key]
    if file_type.lower() == val.lower():
        v.set(key)
    configOutputFileMenu.add_radiobutton(label=key,variable=v, command=lambda val=val: chooseOutputType(val))
    
configmenu.add_cascade(label="Output File Type", menu=configOutputFileMenu)
configmenu.add_command(label="Output File Path", command=hello)
configmenu.add_command(label="Data to Save", command=hello)
menubar.add_cascade(label="Configure", menu=configmenu)

helpmenu = tk.Menu(menubar, tearoff=0)
helpmenu.add_command(label="About", command=hello)
menubar.add_cascade(label="Help", menu=helpmenu)

# display the menu
root.config(menu=menubar)


# Close thread and serial port before exit :
root.protocol("WM_DELETE_WINDOW", goodbye)

# Show main window
root.mainloop()







