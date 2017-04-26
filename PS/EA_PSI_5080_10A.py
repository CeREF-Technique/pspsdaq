""" Maxim Dumortier
    Feb. - March 2017
    Class for a special type of Power supply
"""
from PS import powerSupply
import serial
from tkinter import StringVar

class EA_PSI508010A(powerSupply.PowerSupply):

    name = "EA PSI-5080-10A"
    
    def __init__(self, serial_name):
        self.port = serial_name
        self.baudrate = 9600                 # Default baud rate
        self.timeout = 1                     # Default timeout, seconds
        self.parity = serial.PARITY_NONE     # Default parity
        self.stopbits = serial.STOPBITS_ONE  # Default stop bits
        self.bytesize = serial.EIGHTBITS
        if serial_name != "":
            self.ser = serial.Serial(self.port, self.baudrate, self.bytesize, self.parity, self.stopbits, timeout=self.timeout) # serial port
        else:
            self.ser = 0
            
        self.max_voltage = 80.0 # Volts
        self.max_current =  10.0 # Amps
        self.max_power = 320.0 # Watts
        # Available measures for this Device
        # for each, must have label and units
        self.availableMeasures = { "voltage":{"label":"Voltage", "units":"V", "method":self.getVoltage, "stringVar":StringVar(), "used":True, "format":"%.2f"},
                                   "current":{"label":"Current", "units":"A", "method":self.getCurrent, "stringVar":StringVar(), "used":True, "format":"%.2f"},
                                   "power":  {"label":"Power",   "units":"W", "method":self.getPower,   "stringVar":StringVar(), "used":True, "format":"%.2f"}
                                 }


    def getData(self, command):
        """ Get the asked data from the power supply through the Serial port
            Input : command = number of the object to be get
                    length = lenght of the data to be get (in bytes)
                    endByte = terminaison byte (to check the end of the transmission) by default is b''
            Output = Give a byte array of the data answered
        """
        self.ser.write(command)

        l = []  # Contains all the letters received for serial port
        try:
            while self.ser:
                r = self.ser.read(1).decode("ascii")
                if r != "\n":  # look after the last char
                    l.append(r)
                else:
                    break
            word = ''.join(l)  # copy the char table into a string word
        except UnicodeDecodeError:
            print("fail to read in ASCII")
        print(word)
        
        return float(word)

    
    def setData(self, command):
        """ Get the asked data from the power supply through the Serial port
            Input : command = number of the object to be get
                    length = lenght of the data to be get (in bytes)
                    endByte = terminaison byte (to check the end of the transmission) by default is b''
            Output = Give a byte array of the data answered
        """
        self.ser.write(command)

    def getID(self):
        """ Genereic method to get the id of the device
            return : String, the ID
        """
        GET_ID_COMMAND = "*IDN?".encode() # command to send to the power supply to get the current voltage
        return self.getData(GET_ID_COMMAND)
    
    def getVoltage(self):
        GET_VOLTAGE_COMMAND = "MEASure:VOLTage?".encode() # command to send to the power supply to get the current voltage
        return self.getData(GET_VOLTAGE_COMMAND)

    def getCurrent(self):
        GET_CURRENT_COMMAND = "MEASure:CURRent?".encode() # command to send to the power supply to get the current voltage
        return self.getData(GET_CURRENT_COMMAND)

    def getPower(self):
        GET_POWER_COMMAND = "MEASure:POWer?".encode() # command to send to the power supply to get the current voltage
        return self.getData(GET_POWER_COMMAND)

    def getMeasures(self):
        GET_VALUES_COMMAND = "MEASure:ARRay?".encode()
        word = self.getData(GET_VALUES_COMMAND)
        for w in word.split(", "):
            if w.endswith(" V"):
                volt = float(w.replace(" V", ""))
            elif w.endswith(" A"):
                curr = float(w.replace(" A", ""))
            elif w.endswith(" W"):
                power = float(w.replace(" W", ""))
            else:
                # This happens when we connect or disconnect to serial port
                logging.error("Houston, we've got a problem: unable to recognize " + w + " in received string")
        return volt, curr, power

    def setRemoteControlOn(self, switch):
        """ Set the Remote Control of power supplies
            Enable the ability to set other values
            Input : Boolean value, True to set ON, False to set OFF
        """ 
        SET_REMOTE_COMMAND = "".encode()
        self.writeData(SET_REMOTE_COMMAND)

    def setPowerSupplyOn(self, switch):
        """ Set the output of power supplie On or Off
            Input : Boolean value, True to set ON, False to set OFF
        """ 
        SET_PS_ON_COMMAND = "".encode()
        self.writeData(SET_PS_ON_COMMAND)

    def setVoltage(self, volts):
        """ Set the output voltage to power supply
            Input : float volts, value to be set
        """ 
        SET_VOLTAGE_COMMAND = "".encode()
        self.writeData(SET_VOLTAGE_COMMAND)


    def setCurrent(self, amps):
        """ Set the output current to power supply
            Input : float amps, value to be set
        """ 
        SET_CURRENT_COMMAND = "".encode()
        self.writeData(SET_CURRENT_COMMAND)
                
