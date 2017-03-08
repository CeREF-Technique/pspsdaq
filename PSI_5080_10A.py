""" Maxim Dumortier
    Feb. 2017
    Class for a special type of Power supply
"""
import powerSupply

class PSI508010A(powerSupply.PowerSupply):

    def __init__(self, serial_name):
        self.name = "EA PSI-5080-10A"
        
        self.port = serial_name
        self.baudrate = 9600                 # Default baud rate
        self.timeout = 1                     # Default timeout, seconds
        self.parity = serial.PARITY_NONE     # Default parity
        self.stopbits = serial.STOPBITS_ONE  # Default stop bits
        self.bytesize = serial.EIGHTBITS
    
    def getVoltage(self):
        GET_VOLTAGE_COMMAND = "MEASure:VOLTage?".encode() # command to send to the power supply to get the current voltage
        self.open()
        self.write(GET_VOLTAGE_COMMAND)

        l = []  # Contains all the letters received for serial port
        try:
            while ser:
                r = ser.read(1).decode("ascii")
                if r != "\n":  # look after the last char
                    l.append(r)
                else:
                    break
            word = ''.join(l)  # copy the char table into a string word
        except UnicodeDecodeError:
            print("fail to read in ASCII")
        print(word)
        
        return 0.0

    def getCurrent(self):
        GET_VOLTAGE_COMMAND = "MEASure:CURRent?".encode() # command to send to the power supply to get the current voltage
        self.open()
        self.write(GET_VOLTAGE_COMMAND)

        l = []  # Contains all the letters received for serial port
        try:
            while ser:
                r = ser.read(1).decode("ascii")
                if r != "\n":  # look after the last char
                    l.append(r)
                else:
                    break
            word = ''.join(l)  # copy the char table into a string word
        except UnicodeDecodeError:
            print("fail to read in ASCII")
        print(word)

        return 0.0

    def getPower(self):
        GET_VOLTAGE_COMMAND = "MEASure:POWer?".encode() # command to send to the power supply to get the current voltage
        self.open()
        self.write(GET_VOLTAGE_COMMAND)

        l = []  # Contains all the letters received for serial port
        try:
            while ser:
                r = ser.read(1).decode("ascii")
                if r != "\n":  # look after the last char
                    l.append(r)
                else:
                    break
            word = ''.join(l)  # copy the char table into a string word
        except UnicodeDecodeError:
            print("fail to read in ASCII")
        print(word)

        return 0.0
                
