"""
Maxim Dumortier
Feb. 2017

This is a parent class in order to create some children powersupplies with each tei specification.
More info about the serial API : https://pythonhosted.org/pyserial/pyserial_api.html
"""
import serial

class PowerSupply(object):
    """ Power Supply class extends directly the Serial class
        This make things much easier
    """

    
    def __init__(self, serial_name):
        """ Initialize the power supply.
            Each children an here define non-default values for his specific case
            Input : serial_name, String, is the serial port name (e.g. COM2)
        """
        self.name = "Generic Power Supply"
        self.port = serial_name

        self.baudrate = 9600                 # Default baud rate
        """ Possible baudrate values :
            50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800, 9600, 19200, 38400, 57600, 115200,
            230400, 460800, 500000, 576000, 921600, 1000000, 1152000, 1500000, 2000000, 2500000, 3000000, 3500000, 4000000
        """
        
        self.timeout = 1                     # Default timeout, seconds
        
        self.parity = serial.PARITY_NONE     # Default parity
        """ Possible parities : 
            PARITY_NONE, PARITY_EVEN, PARITY_ODD, PARITY_MARK, PARITY_SPACE
        """
        
        self.stopbits = serial.STOPBITS_ONE  # Default stop bits
        """ Possible stopbits :
             STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE, STOPBITS_TWO
        """
        
        self.bytesize = serial.EIGHTBITS
        """ Possible bytesizes :
            FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS
        """
        self.ser = serial.Serial(self.port, self.baudrate, self.bytesize, self.parity, self.stopbits, timeout=self.timeout) # serial port

        self.max_voltage = 0.0 # Volts
        self.max_current = 0.0 # Amps
        self.max_power   = 0.0 # Watts

    def getID():
        """ Genereic method to get the id of the device
            return : String, the ID
        """
        return ""
    
    def getVoltage(self):
        """ Generic method to get the current voltage in the power supply
            return : float, in Volts
        """
        return 0.0

    def getCurrent(self):
        """ Generic method to get the current current in the power supply
            return : float, in Amps
        """
        return 0.0


    def getPower(self):
        """ Generic method to get the current power in the power supply
            If there is no specific command for getting power consuption, then juste get Voltage and Current and multiply them together
            return : float, in Watts
        """
        return 0.0


    def getMeasures(self):
        """ Generic method to get the all the measures of the power supply
            If there is no specific command for getting power consuption, then juste get Voltage and Current and multiply them together
            return : tuple of float : voltage, current, power
        """
        return 0.0, 0.0, 0.0


    def setRemoteControlOn(self, switch):
        """ Set the Remote Control of power supplies
            Enable the ability to set other values
            Input : Boolean value, True to set ON, False to set OFF
        """ 

            
    def setPowerSupplyOn(self, switch):
        """ Set the output of power supplie On or Off
            Input : Boolean value, True to set ON, False to set OFF
        """ 
        

    def setVoltage(self, volts):
        """ Set the output voltage to power supply
            Input : float volts, value to be set
        """ 


    def setCurrent(self, amps):
        """ Set the output current to power supply
            Input : float amps, value to be set
        """ 
