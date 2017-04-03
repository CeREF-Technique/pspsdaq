""" Maxim Dumortier
    March 2017
    Class for a special type of Power supply
"""
from PS import powerSupply
import serial

class EA_PS836010T(powerSupply.PowerSupply):
    """ NB : The power supply must be ON before you plug the USB cable ...
    """

    name = "EA PS-8360-10T Big one"
    
    def __init__(self, serial_name):
        self.port = serial_name

        self.baudrate = 57600                 # Default baud rate
        self.timeout = 0.1                     # Default timeout, seconds
        self.parity = serial.PARITY_ODD      # Default parity
        self.stopbits = serial.STOPBITS_ONE  # Default stop bits
        self.bytesize = serial.EIGHTBITS
        self.ser = serial.Serial(self.port, self.baudrate, self.bytesize, self.parity, self.stopbits, timeout=self.timeout) # serial port
        
        self.max_voltage = 360.0 # Volts
        self.max_current =  10.0 # Amps
        self.max_power = 1000.0 # Watts

        
    def constructRequest(self, command, length, data=''):
        """
           The request has to be constructed by a certain way, this method is used for this.
           Input : command : the byte (in HEX) of the object to be requested
           Output : the whole byte array to be send to the Serial port

           SD = start delimiter (first Byte)
           DN = Device node (2nd Byte)
           OBJ = object (3rd Byte) object concerd by the exchange
           DataField = stuff exchanged (3 to 18 Bytes long)
           CS = Check sum (2 last Bytes)

           SD =
           bits 0 - 3 = lenght of the data to b recieved -1
              eg : length = 4 ; bits 0-3 = 0011 = 3
           bit 4 : message direction :
              0 = from device to PC
              1 = from PC to device (this is always or case here)
           bit 5 : cast type
              0 = single cast
              1 = broadcast (our case here)
           bits 6-7 = transmission type
              00 = reserverd
              01 = query data (always our case here)
              10 = answser to a query
              11 = Send data
        """
        
        SD = 0x70 #0111 0000 in binary
        SD = SD + length - 1
        DN = 0x00 # Always = 0 in point to point communication
        OBJ = command
        # No data field here, it's a query
        CS = OBJ + SD + DN
        toreturn = bytes([SD, DN, OBJ])
        if data != '': # in case there is data to send
            for d in data:
                CS += d
                toreturn += bytes([d])
        toreturn += bytes([CS >> 8])
        toreturn += bytes([CS & 0xFF])
        return toreturn


    def constructRequestWithData(self, command, length, data):
        """
           The request has to be constructed by a certain way, this method is used for this.
           Input : command : the byte (in HEX) of the object to be requested
           Output : the whole byte array to be send to the Serial port

           SD = start delimiter (first Byte)
           DN = Device node (2nd Byte)
           OBJ = object (3rd Byte) object concerd by the exchange
           DataField = stuff exchanged (3 to 18 Bytes long)
           CS = Check sum (2 last Bytes)

           SD =
           bits 0 - 3 = lenght of the data to b recieved -1
              eg : length = 4 ; bits 0-3 = 0011 = 3
           bit 4 : message direction :
              0 = from device to PC
              1 = from PC to device (this is always or case here)
           bit 5 : cast type
              0 = single cast
              1 = broadcast (our case here)
           bits 6-7 = transmission type
              00 = reserverd
              01 = query data (always our case here)
              10 = answser to a query
              11 = Send data
        """
        
        SD = 0xF0 #0111 0000 in binary
        SD = SD + length - 1
        DN = 0x00 # Always = 0 in point to point communication
        OBJ = command
        # No data field here, it's a query
        CS = OBJ + SD + DN
        toreturn = bytes([SD, DN, OBJ])
        if data != '': # in case there is data to send
            for d in data:
                CS += d
                toreturn += bytes([d])
        toreturn += bytes([CS >> 8])
        toreturn += bytes([CS & 0xFF])  
        return toreturn

    
    def deconstructAnswer(self, recieved, command, length):
        """
           The request has to be constructed by a certain way, this method is used for this.
           Input : command : the byte (in HEX) of the object to be requested
           Output : the whole byte array to be send to the Serial port

           SD = start delimiter (first Byte)
           DN = Device node (2nd Byte)
           OBJ = object (3rd Byte) object concerd by the exchange
           DataField = stuff exchanged (3 to 18 Bytes long)
           CS = Check sum (2 last Bytes)

           SD =
           bits 0 - 3 = lenght of the data to b recieved -1
              eg : length = 4 ; bits 0-3 = 0011 = 3
           bit 4 : message direction :
              0 = from device to PC (this is always or case here)
              1 = from PC to device 
           bit 5 : cast type
              0 = single cast (our case here)
              1 = broadcast 
           bits 6-7 = transmission type
              00 = reserverd
              01 = query data 
              10 = answser to a query (always our case here)
              11 = Send data
        """
        MASK_LENGTH = 0x0F # 0000 1111 look only the bit 0 to 3 
        NEEDED_LENGTH = (length-1) # lenghts must be the same

        MASK_SENDER = 0x10 # 0001 0000
        NEEDED_SENDER = 0 # must be message from device to PC

        MASK_CAST = 0x20 # 0010 0000
        NEEDED_CAST = 0 # must be single cast
        
        MASK_TRANSMISSION = 0xC0 # 1100 0000 look only the 2 last bits
        NEEDED_ANSWER_TRANSMISSION = 0x80 # 1000 0000 two last bits must be "10"
        if len(recieved)>0:
            SD = recieved[0]
            if SD & MASK_LENGTH != NEEDED_LENGTH:
                print("BAD length for the concerned answer")
                length = (SD & MASK_LENGTH)

            if SD & MASK_SENDER != NEEDED_SENDER:
                print("This message was sent from the PC to the device and is thus not an answer")

            if SD & MASK_CAST != NEEDED_CAST:
                print("Message was not send with the right cast")

            if SD & MASK_TRANSMISSION != NEEDED_ANSWER_TRANSMISSION:
                print("Message recieved is not an answer")
                

            DN = recieved[1]
            if DN != 0x01:
                print("Device node must be 1 in Serial")

                
            OBJ = recieved[2]
            if(OBJ != command):
                print("ERROR, not same object")


            DATA = recieved[3: 3 + length]
            CS0 = recieved[-2]
            CS1 = recieved[-1]

            # No data field here, it's a query
            CS = OBJ + SD + DN 
            for data in DATA:
                CS += data # Add each byte to the calculated check sum
            if (CS & 0xFF) != CS1:
                print("Check sum error")
            elif (CS >> 8) != CS0:
                print("Check sum error")
            #else:
             #   print("Check sum OK")
        else:
            print("Nothing to read")
            DATA = b''
        return DATA

    
    def getFloatValue(self, DATA, max_value):
        """ Convert the byte values to foat value
            Input : DATA = byte array to be converted
                    max_value = maximum value of the value to be converted
            Output : float or int converted
        """
        numData = 0
        length = len(DATA)
        for i in range(length):
            numData += DATA[-i-1] << 8*i
            
        return numData * max_value / 25600


    def getData(self, command, length, endByte = b''):
        """ Get the asked data from the power supply through the Serial port
            Input : command = number of the object to be get
                    length = lenght of the data to be get (in bytes)
                    endByte = terminaison byte (to check the end of the transmission) by default is b''
            Output = Give a byte array of the data answered
        """
        self.ser.write(self.constructRequest(command, length))

        l = bytearray()  # Contains all the letters received for serial port
        try:
            while self.ser:
                r = self.ser.read(1)
                #while self.ser.inWaiting() > 0:
                 #   print( self.ser.read(1))
                #print(r)
                if r != endByte:  # look after the last char
                    l.append(int.from_bytes(r, byteorder='big'))
                else:
                    break
        except Exception as e:
            print("Fail to read")
            print(e)
        return self.deconstructAnswer(l, command, length)


    def setData(self, command, length, value, endByte = b''):
        """ Get the asked data from the power supply through the Serial port
            Input : command = number of the object to be get
                    length = lenght of the data to be get (in bytes)
                    value = value to be set (lenght must be the same as set)
                    endByte = terminaison byte (to check the end of the transmission) by default is b''
        """
        self.ser.write(self.constructRequestWithData(command, length, data=value))

    def getID(self):
        """ Genereic method to get the id of the device
            return : String, the ID
        """
        GET_ID_COMMAND = 0x01 # Object to be get
        GET_ID_LENGHT = 16 # lenght of the response in bytes
        
        DATA_Bytes = self.getData(GET_ID_COMMAND, GET_ID_LENGHT)
        return DATA_Bytes.decode()
    
    def getVoltage(self):
        """ Get the voltage of the power supply
            return : float, in Volts
        """
        return self.getMeasures()[0]


    def getCurrent(self):
        """ Get the current of the power supply
            return : float, in Amps
        """
        return self.getMeasures()[1]


    def getPower(self):
        """ Get the power of the power supply
            return : float, in Watts
        """
        return self.getMeasures()[2]


    def getMeasures(self):
        """ Get the Measures of the current power supplies
            return : tuple of float : voltage, current, power
        """ 
        GET_VALUES_COMMAND = 0x47 # Object to be get
        GET_VALUES_LENGHT = 6 # lenght of the response in bytes
        
        DATA_Bytes = self.getData(GET_VALUES_COMMAND, GET_VALUES_LENGHT)
        if DATA_Bytes != b'':
            volt = self.getFloatValue(DATA_Bytes[0:2], self.max_voltage)
            curr = self.getFloatValue(DATA_Bytes[2:4], self.max_current)
            power = self.getFloatValue(DATA_Bytes[4:6], self.max_current)
        else:
            volt = -1.0
            curr = -1.0
            power = -1.0
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

            

































    
                
