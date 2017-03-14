""" Maxim Dumortier
    Feb. - March 2017
    Class for a special type of Power supply
"""
import powerSupply
import serial

class PSI508010A(powerSupply.PowerSupply):

    def __init__(self, serial_name):
        self.name = "EA PSI-5080-10A"
        
        self.port = serial_name
        self.baudrate = 9600                 # Default baud rate
        self.timeout = 1                     # Default timeout, seconds
        self.parity = serial.PARITY_NONE     # Default parity
        self.stopbits = serial.STOPBITS_ONE  # Default stop bits
        self.bytesize = serial.EIGHTBITS
        self.ser = serial.Serial(self.port, self.baudrate, self.bytesize, self.parity, self.stopbits, timeout=self.timeout) # serial port

        self.max_voltage = 80.0 # Volts
        self.max_current =  10.0 # Amps
        self.max_power = 320.0 # Watts


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
            while ser:
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
        GET_VALUES_COMMAND = "".encode()
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
        if switch:
            self.setData(0x36, 2, [0x10, 0x10])
        else:
            self.setData(0x36, 2, [0x10, 0x00])

    def setPowerSupplyOn(self, switch):
        """ Set the output of power supplie On or Off
            Input : Boolean value, True to set ON, False to set OFF
        """ 
        if switch:
            self.setData(0x36, 2, [0x01, 0x01])
        else:
            self.setData(0x36, 2, [0x01, 0x00])

    def setVoltage(self, volts):
        """ Set the output voltage to power supply
            Input : float volts, value to be set
        """ 
        val = round(volts / self.max_voltage * 25600)
        self.setData(0x32, 2, [val>>8, val & 0xFF]) #set voltage % of Unom*256 ==> 10v/42v * 25600 = 6095


    def setCurrent(self, amps):
        """ Set the output current to power supply
            Input : float amps, value to be set
        """ 
        val = round(amps / self.max_current * 25600)
        self.setData(0x33, 2, [val>>8, val & 0xFF])
                
